from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QSlider, QFrame, QApplication)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon
import sys
import numpy as np

# Add project root directory to Python path
import os
sys.path.insert(0, '.')
from src.ui.widgets.display_wav_widget import CustomPlotWidget
from src.utils.audio.audio_player import AudioPlayer
from src.utils.downsample import downsample_plot_data

# from src.core.algorithm_test.sliding_window_calculator import SlidingWindowCalculator
from src.core.algorithm.spectrogram.spectrogram import Spectrogram

# Import resource files
try:
    from src.ui.resources import resources_rc
    print("Resource file loaded successfully")
except ImportError:
    print("Warning: Resource file not found, using default icons")
    resources_rc = None

# Enable OpenGL acceleration
# pg.setConfigOptions(antialias=True)
# pg.setConfigOption('useOpenGL', True)


class DisplayPanel(QWidget):
    """Display panel widget for audio visualization and playback control.
    
    This widget provides:
    - Plot1: 1D audio waveform display
    - Plot2: 2D spectrogram display (synchronized x-axis with plot1)
    - Audio playback controls (play/pause/stop)
    - Progress slider for seeking
    - Optimized plotting for large datasets
    """
    
    # Signal definitions
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    position_changed = Signal(int)

    FLAG_OPTIMIZE_PLOT = True  # Optimize plotting performance flag
    MAX_DISPLAY_LEN_1D = 10000

    PROGRESS_SLIDER_MAX = 10000.0
    
    def __init__(self, parent=None):
        """Initialize the DisplayPanel widget.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Data cache for optimizing plotting
        # plot1: 1D data, plot2: 2D data
        self.cached_data = {
            'plot1': {'x': None, 'y': None, 'name': None, 'type': '1d'},
            'plot2': {'x': None, 'y': None, 'data2d': None, 'name': None, 'type': '2d'}
        }
        
        # Initialize audio player
        self.audio_player = AudioPlayer()
        self._setup_audio_player_signals()
        
        self.setup_ui()
        self.connect_signals()
        self.setup_plot_sync()  # Add subplot synchronization setup
        self.setup_algo()
        self._sync_in_progress = False  # Flag to prevent circular synchronization
        
        # Timeline display related
        self.current_timeline = 0.0
        self.max_timeline = 0.0
        
        # If optimization is enabled, connect range change signals
        if self.FLAG_OPTIMIZE_PLOT:
            self.setup_range_optimization()
        
        # Add playback state flag
        self.is_playing = False
        
        # Add drag state tracking
        self._was_playing_before_drag = False

    def _setup_audio_player_signals(self):
        """Setup audio player signal connections."""
        self.audio_player.position_changed.connect(self._on_playback_position_changed)
        self.audio_player.playback_started.connect(self._on_playback_started)
        self.audio_player.playback_paused.connect(self._on_playback_paused)
        self.audio_player.playback_stopped.connect(self._on_playback_stopped)
        self.audio_player.playback_finished.connect(self._on_playback_finished)
        self.audio_player.error_occurred.connect(self._on_playback_error)
    
    def setup_algo(self):
        """Setup algorithm related parameters."""
        # self.algo = SlidingWindowCalculator(1000) # only for test
        self.algo = Spectrogram(fft_points=1024)  # Initialize spectrogram algorithm

    def setup_ui(self):
        """Setup UI layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Create two custom subplots
        self.plot1 = CustomPlotWidget()
        self.plot1.setTitle('音频波形')
        
        self.plot2 = CustomPlotWidget()
        self.plot2.setTitle('时频图')
        
        main_layout.addWidget(self.plot1)
        main_layout.addWidget(self.plot2)
        
        # Playback control area
        control_frame = self.create_control_frame()
        main_layout.addWidget(control_frame)
        
        # Set stretch factors to let charts occupy more space
        main_layout.setStretchFactor(self.plot1, 1)
        main_layout.setStretchFactor(self.plot2, 1)
        main_layout.setStretchFactor(control_frame, 0)

    def create_control_frame(self):
        """Create playback control area.
        
        Returns:
            QFrame: Control frame widget.
        """
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Box)
        control_frame.setMaximumHeight(80)
        
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(10, 10, 10, 10)
        
        # Button control area
        button_layout = QHBoxLayout()
        
        # Stop button
        self.stop_button = QPushButton()
        if resources_rc:
            self.stop_button.setIcon(QIcon(":/resources/icons/stop.png"))
        # self.stop_button.setText("停止")
        self.stop_button.setMinimumSize(25, 25)
        
        # Play/Pause toggle button
        self.play_pause_button = QPushButton()
        if resources_rc:
            self.play_pause_button.setIcon(QIcon(":/resources/icons/play.png"))
        # self.play_pause_button.setText("播放")
        self.play_pause_button.setMinimumSize(25, 25)
        
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.play_pause_button)
        button_layout.addStretch()
        
        # Progress bar
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(self.PROGRESS_SLIDER_MAX)  
        self.progress_slider.setValue(0)
        
        control_layout.addLayout(button_layout)
        control_layout.addWidget(self.progress_slider)
        
        return control_frame
    
    def connect_signals(self):
        """Connect signal slots."""
        self.stop_button.clicked.connect(self._on_stop_button_clicked)
        self.play_pause_button.clicked.connect(self._on_play_pause_button_clicked)
        # 使用sliderReleased信号，只在拖拽完成时触发
        self.progress_slider.sliderReleased.connect(self._on_progress_slider_released)
        # 添加valueChanged信号用于实时更新时间线
        self.progress_slider.valueChanged.connect(self._on_progress_slider_value_changed)
        # 添加sliderPressed信号用于处理拖拽开始
        self.progress_slider.sliderPressed.connect(self._on_progress_slider_pressed)

    def _on_play_pause_button_clicked(self):
        """Handle play/pause button click."""
        if self.is_playing:
            # Currently playing, click to pause
            self.audio_player.pause()
        else:
            # Currently not playing, click to play
            if self.audio_player.is_loaded():
                self.audio_player.play()
            else:
                print("No audio data available for playback")
    
    def _update_play_pause_button(self, is_playing):
        """Update play/pause button state.
        
        Args:
            is_playing (bool): Whether audio is currently playing.
        """
        self.is_playing = is_playing
        if is_playing:
            if resources_rc:
                self.play_pause_button.setIcon(QIcon(":/resources/icons/pause.png"))
            # self.play_pause_button.setText("暂停")
        else:
            if resources_rc:
                self.play_pause_button.setIcon(QIcon(":/resources/icons/play.png"))
            # self.play_pause_button.setText("播放")
    
    def _on_stop_button_clicked(self):
        """Handle stop button click."""
        self.audio_player.stop()
    
    def _on_progress_slider_pressed(self):
        """Handle progress slider pressed - drag start."""
        if self.audio_player.is_loaded():
            # Record current playback state
            playback_state = self.audio_player.get_playback_state()
            self._was_playing_before_drag = playback_state['is_playing'] and not playback_state['is_paused']
            
            # If currently playing, pause
            if self._was_playing_before_drag:
                self.audio_player.pause()
                print("Drag started, auto pause playback")

    def _on_progress_slider_value_changed(self, value):
        """Handle progress slider value change - real-time timeline update.
        
        Args:
            value (int): Current slider value.
        """
        if self.audio_player.is_loaded() and self.progress_slider.isSliderDown():
            # Only update timeline when user is dragging, avoid conflict with playback position updates
            duration = self.audio_player.get_duration()
            if duration > 0:
                # Calculate target time position
                target_time = (value / self.PROGRESS_SLIDER_MAX) * duration
                
                # Update current timeline position and redraw
                self.current_timeline = target_time
                self._update_timeline_display()
    
    def _on_progress_slider_released(self):
        """Handle progress slider drag release."""
        if self.audio_player.is_loaded():
            # Get current slider value
            value = self.progress_slider.value()
            
            # Calculate target time position
            target_time = (value / self.PROGRESS_SLIDER_MAX) * self.audio_player.get_duration()
            
            # Seek to specified position
            self.audio_player.seek(target_time)
            
            # Decide whether to continue playing based on pre-drag state
            if self._was_playing_before_drag:
                # If was playing before drag, continue playing after jump
                self.audio_player.play()
                print(f"Drag ended, resume playback at: {target_time:.2f}s")
            else:
                print(f"Drag ended, jumped to: {target_time:.2f}s (remain paused)")
            
            # Reset pre-drag state flag
            self._was_playing_before_drag = False

    def _on_playback_position_changed(self, position_seconds):
        """Handle playback position change.
        
        Args:
            position_seconds (float): Current playback position in seconds.
        """
        self.current_timeline = position_seconds
   
        
        # Update progress slider - only when user is not manually dragging
        duration = self.audio_player.get_duration()
        if duration > 0 and not self.progress_slider.isSliderDown():
            progress = int((position_seconds / duration) * self.PROGRESS_SLIDER_MAX)   
            
            # Prevent signal loop triggering
            self.progress_slider.blockSignals(True)
            self.progress_slider.setValue(progress)
            self.progress_slider.blockSignals(False)
            
            # Emit position change signal
            self.position_changed.emit(progress)
        
        # Update timeline display
        self._update_timeline_display()

    def _on_playback_started(self):
        """Handle playback started."""
        print("Playback started")
        self._update_play_pause_button(True)
        self.play_clicked.emit()
        
        # Ensure timer is running
        print(f"Timer running status: {self.audio_player.position_timer.isActive()}")

    def _on_playback_paused(self):
        """Handle playback paused."""
        print("Playback paused")
        self._update_play_pause_button(False)
        self.pause_clicked.emit()
    
    def _on_playback_stopped(self):
        """Handle playback stopped."""
        print("Playback stopped")
        self.current_timeline = 0.0
        self.set_progress(0)
        self._update_timeline_display()
        self._update_play_pause_button(False)
        self.stop_clicked.emit()
    
    def _on_playback_finished(self):
        """Handle playback finished."""
        print("Playback finished")
        self.current_timeline = 0.0
        self.set_progress(0)
        self._update_timeline_display()
        self._update_play_pause_button(False)
        
        # Emit stop signal instead of playback finished specific signal to maintain UI state consistency
        self.stop_clicked.emit()
    
    def _on_playback_error(self, error_message):
        """Handle playback error.
        
        Args:
            error_message (str): Error message description.
        """
        print(f"Playback error: {error_message}")
    
    def set_progress(self, value):
        """Set progress slider position.
        
        Args:
            value (int): Progress value to set.
        """
        self.progress_slider.blockSignals(True)
        self.progress_slider.setValue(value)
        self.progress_slider.blockSignals(False)
    
    def set_progress_range(self, minimum, maximum):
        """Set progress slider range.
        
        Args:
            minimum (int): Minimum value.
            maximum (int): Maximum value.
        """
        self.progress_slider.setRange(minimum, maximum)
    
    def get_plot1(self):
        """Get the first subplot.
        
        Returns:
            CustomPlotWidget: First plot widget.
        """
        return self.plot1
    
    def get_plot2(self):
        """Get the second subplot.
        
        Returns:
            CustomPlotWidget: Second plot widget.
        """
        return self.plot2
    
    def setup_plot_sync(self):
        """Setup subplot synchronization functionality."""
        # Get view boxes of both subplots
        self.view_box1 = self.plot1.getPlotItem().getViewBox()
        self.view_box2 = self.plot2.getPlotItem().getViewBox()
        
        # Connect view range change signals
        self.view_box1.sigRangeChanged.connect(lambda: self._on_plot_range_changed('plot1'))
        self.view_box2.sigRangeChanged.connect(lambda: self._on_plot_range_changed('plot2'))
    
    def _on_plot_range_changed(self, plot_str):
        """Handle plot range change for synchronization.
        
        Args:
            plot_str (str): Which plot's range changed ('plot1' or 'plot2').
        """
        if self._sync_in_progress:
            return
        self._sync_in_progress = True
        
        try:
            # Get view range
            view_range = self.view_box1.viewRange() if plot_str == 'plot1' else self.view_box2.viewRange()
            # Set the other subplot's x-axis range (only synchronize x-axis)
            if plot_str == 'plot1':
                # plot1 changed, sync x-axis to plot2
                self.view_box2.setRange(xRange=view_range[0], padding=0)
            else:
                # plot2 changed, sync x-axis to plot1
                self.view_box1.setRange(xRange=view_range[0], padding=0)
                
        finally:
            self._sync_in_progress = False
    
    def setup_range_optimization(self):
        """Setup range change optimization."""
        # Connect range change signals to optimization handler
        self.plot1.sigRangeChanged.connect(lambda: self._on_plot_range_changed_optimize('plot1'))
        self.plot2.sigRangeChanged.connect(lambda: self._on_plot_range_changed_optimize('plot2'))
    
    def _on_plot_range_changed_optimize(self, plot_name):
        """When display range changes, only draw data in visible area.
        
        Args:
            plot_name (str): Name of the plot that changed ('plot1' or 'plot2').
        """
        if not self.FLAG_OPTIMIZE_PLOT:
            return
            
        plot_widget = self.plot1 if plot_name == 'plot1' else self.plot2
        cached_data = self.cached_data[plot_name]
        
        # Check if cached data exists
        if cached_data['x'] is None:
            return
        
        # Get current x-axis display range
        view_range = plot_widget.getViewBox().viewRange()
        x_min, x_max = view_range[0]
        
        # Add buffer to ensure smooth scrolling
        buffer = (x_max - x_min) * 0.1
        x_min_buffered = x_min - buffer
        x_max_buffered = x_max + buffer
        
        # Handle different data types
        if cached_data['type'] == '1d':
            self._optimize_1d_plot(plot_widget, cached_data, x_min_buffered, x_max_buffered, plot_name)
        elif cached_data['type'] == '2d':
            self._optimize_2d_plot(plot_widget, cached_data, x_min_buffered, x_max_buffered, plot_name)

    def _optimize_1d_plot(self, plot_widget, cached_data, x_min, x_max, plot_name):
        """Optimize 1D plot display.
        
        Args:
            plot_widget: Plot widget instance
            cached_data: Cached data dictionary
            x_min, x_max: X-axis range
            plot_name: Plot name
        """
        if cached_data['y'] is None:
            return
            
        # Find data indices within display range
        full_x = cached_data['x']
        full_y = cached_data['y']
        
        mask = (full_x >= x_min) & (full_x <= x_max)
        visible_x = full_x[mask]
        visible_y = full_y[mask]
        
        # Downsampling processing
        if len(visible_x) > self.MAX_DISPLAY_LEN_1D:
            step = len(visible_x) // self.MAX_DISPLAY_LEN_1D
            if step < 1:
                step = 1

            visible_x, visible_y = downsample_plot_data(
                visible_x, visible_y, method='abs_max', step=step
            )
        
        # Redraw optimized data
        plot_widget.clear()
        pen_color = 'y' if plot_name == 'plot1' else 'g'
        plot_widget.plot(visible_x, visible_y, pen=pen_color, name=cached_data['name'])

        # Draw timeline if in visible range
        if x_min <= self.current_timeline <= x_max:
            plot_widget.draw_timeline(self.current_timeline, color='red', width=2)

    def _optimize_2d_plot(self, plot_widget, cached_data, x_min, x_max, plot_name):
        """Optimize 2D plot display.
        
        Args:
            plot_widget: Plot widget instance
            cached_data: Cached data dictionary
            x_min, x_max: X-axis range
            plot_name: Plot name
        """
        if cached_data['data2d'] is None or cached_data['y'] is None:
            return
            
        full_x = cached_data['x']
        full_y = cached_data['y']  # frequency axis
        full_data2d = cached_data['data2d']
        
        # Find x-axis indices within display range
        x_mask = (full_x >= x_min) & (full_x <= x_max)
        x_indices = np.where(x_mask)[0]
        
        if len(x_indices) == 0:
            return
            
        # Extract visible data
        visible_x = full_x[x_indices]
        visible_data2d = full_data2d[:, x_indices]  # Keep all frequencies, subset time
        
        # Optional: downsample in time dimension if too many points
        if len(visible_x) > self.MAX_DISPLAY_LEN_1D:
            step = len(visible_x) // self.MAX_DISPLAY_LEN_1D
            if step < 1:
                step = 1
            visible_x = visible_x[::step]
            visible_data2d = visible_data2d[:, ::step]
        
        # Redraw 2D data
        plot_widget.clear()
        plot_widget.plot2d(visible_x, full_y, visible_data2d)
        
        # Draw timeline if in visible range
        if x_min <= self.current_timeline <= x_max:
            plot_widget.draw_timeline(self.current_timeline, color='red', width=2)

    def plot_data_optimized(self, plot_name, x_data, y_data, name="数据", pen_color='b'):
        """Optimized data plotting method.
        
        Args:
            plot_name (str): 'plot1' or 'plot2'.
            x_data (np.ndarray): X-axis data.
            y_data (np.ndarray): Y-axis data.
            name (str): Data name.
            pen_color (str): Line color.
        """
        plot_widget = self.plot1 if plot_name == 'plot1' else self.plot2
        
        if self.FLAG_OPTIMIZE_PLOT:
            # Cache complete data
            self.cached_data[plot_name] = {
                'x': np.array(x_data),
                'y': np.array(y_data),
                'name': name,
                'type': '1d'
            }
            
            # Initial drawing (if data is large, downsample first)
            if len(x_data) > self.MAX_DISPLAY_LEN_1D:
                step = len(x_data) // self.MAX_DISPLAY_LEN_1D
                if step < 1:
                    step = 1

                plot_x, plot_y = downsample_plot_data(
                    # x_data, y_data, method='bypass', step=step
                    x_data, y_data, method='abs_max', step=step
                )
            else:
                plot_x = x_data
                plot_y = y_data
            
            plot_widget.clear()
            plot_widget.plot(plot_x, plot_y, pen=pen_color, name=name)
            plot_widget.autoRange()
        else:
            # Draw all data directly
            plot_widget.clear()
            plot_widget.plot(x_data, y_data, pen=pen_color, name=name)
            plot_widget.autoRange()

    def plot_data_2d(self, plot_name, x_axis, y_axis, data2d, name="2D数据"):
        """Plot 2D data with optimization support.
        
        Args:
            plot_name (str): 'plot1' or 'plot2'.
            x_axis (np.ndarray): X-axis data (time).
            y_axis (np.ndarray): Y-axis data (frequency).
            data2d (np.ndarray): 2D data array (frequency x time).
            name (str): Data name.
        """
        plot_widget = self.plot1 if plot_name == 'plot1' else self.plot2
        
        if self.FLAG_OPTIMIZE_PLOT and 0:
            # Cache 2D data
            self.cached_data[plot_name] = {
                'x': np.array(x_axis),
                'y': np.array(y_axis),
                'data2d': np.array(data2d),
                'name': name,
                'type': '2d'
            }
            
            # Initial drawing with potential downsampling
            if len(x_axis) > self.MAX_DISPLAY_LEN_1D:
                step = len(x_axis) // self.MAX_DISPLAY_LEN_1D
                if step < 1:
                    step = 1
                plot_x = x_axis[::step]
                plot_data2d = data2d[:, ::step]
            else:
                plot_x = x_axis
                plot_data2d = data2d
            
            plot_widget.clear()
            plot_widget.plot2d(plot_x, y_axis, plot_data2d)
            plot_widget.autoRange()
        else:
            # Draw all data directly
            plot_widget.clear()
            plot_widget.plot2d(x_axis, y_axis, data2d)
            plot_widget.autoRange()
            
            # Store data info for timeline drawing
            self.cached_data[plot_name] = {
                'x': np.array(x_axis),
                'y': np.array(y_axis),
                'data2d': np.array(data2d),
                'name': name,
                'type': '2d'
            }

    def plot_audio_waveform(self, audio_reader, channel=0):
        """Plot audio waveform (optimized version).
        
        Args:
            audio_reader: AudioFileReader instance.
            channel (int): Channel to plot (default 0, first channel).
        """
        if not audio_reader or not audio_reader.is_loaded():
            print("Audio reader has no loaded data")
            return
        
        # Get time axis and audio data
        time_axis = audio_reader.get_time_axis()
        audio_data = audio_reader.get_channel_data(channel)
        
        if time_axis is None or audio_data is None:
            print("Unable to get audio data")
            return
        
        # Load audio data to player
        if self.audio_player.load_audio_data(audio_reader):
            print("Audio data loaded to player")
            self.max_timeline = self.audio_player.get_duration()
            
            # Update progress slider range
            self.set_progress_range(0, self.PROGRESS_SLIDER_MAX)
        else:
            print("Failed to load audio data to player")
        
        # Store audio reader reference
        self.audio_reader = audio_reader
        audio_info = audio_reader.get_audio_info()
        
        # Plot 1D waveform in plot1
        name1 = f'音频波形 - 通道{channel+1}'
        self.plot_data_optimized('plot1', time_axis, audio_data, name1, 'y')
        
        # Calculate and plot 2D spectrogram in plot2
        try:
            freq_axis, time_axis_spec, spec, spec_db = self.apply_algorithm(audio_data)
            name2 = f'时频图 - 通道{channel+1}'
            
            # Use spectrogram in dB for better visualization
            self.plot_data_2d('plot2', time_axis_spec, freq_axis, spec_db, name2)
            
            print(f"Spectrogram plotted - Shape: {spec_db.shape}, Time range: {time_axis_spec[0]:.2f}-{time_axis_spec[-1]:.2f}s, Freq range: {freq_axis[0]:.1f}-{freq_axis[-1]:.1f}Hz")
            
        except Exception as e:
            print(f"Error calculating spectrogram: {e}")
            # Fallback: clear plot2 if spectrogram calculation fails
            self.plot2.clear()
            self.cached_data['plot2'] = {'x': None, 'y': None, 'data2d': None, 'name': None, 'type': '2d'}

        print(f"Audio waveform plotted (optimization mode: {self.FLAG_OPTIMIZE_PLOT}) - Channel{channel+1}, Duration: {audio_info['duration']:.2f}s")
        if self.FLAG_OPTIMIZE_PLOT:
            print(f"Total data length: {len(time_axis)}, Current display length: {min(len(time_axis), self.MAX_DISPLAY_LEN_1D)}")
    
    def clear_plots(self):
        """Clear all plots."""
        # Stop playback
        self.audio_player.stop()
        
        self.plot1.clear()
        self.plot2.clear()
        
        # Clear cached data
        self.cached_data = {
            'plot1': {'x': None, 'y': None, 'name': None, 'type': '1d'},
            'plot2': {'x': None, 'y': None, 'data2d': None, 'name': None, 'type': '2d'}
        }
        
        # Reset timeline
        self.current_timeline = 0.0
        self.max_timeline = 0.0
        
        self.set_progress(0)
        self._update_play_pause_button(False)
        print("Plots cleared, playback stopped")

    def _update_timeline_display(self):
        """Update timeline display for both 1D and 2D plots."""
        # Draw timeline on both subplots
        self.plot1.draw_timeline(self.current_timeline, color='red', width=2)
        self.plot2.draw_timeline(self.current_timeline, color='red', width=2)

    def get_audio_player(self):
        """Get audio player instance.
        
        Returns:
            AudioPlayer: Audio player instance.
        """
        return self.audio_player
    
    def apply_algorithm(self, data):
        """Apply algorithm to process data.
        
        Args:
            data (np.ndarray): Input data.
            
        Returns:
            np.ndarray: Processed result.
        """
        if not self.algo:
            print("Algorithm not initialized")
            return
        
        # result = self.algo.calculate(data)
        # result = self.algo.calculate_vectorized(data)
        # ret = result['max']

        audio_info = self.audio_reader.get_audio_info()
        ret = self.algo.calculate(data, fs=audio_info['sample_rate'], overlap_percent=50)

        return ret['frequencies'], ret['t'], ret['spectrogram'].T, ret['spectrogram_db'].T

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Create main window
    window = DisplayPanel()
    window.setWindowTitle('DisplayPanel Debug Window - 1D/2D Mixed Display Demo')
    window.resize(800, 600)
    
    # Generate sample data for testing
    # 1D data for plot1
    t1 = np.linspace(0, 10, 10000)
    y1 = np.sin(2 * np.pi * t1) * np.exp(-t1/5) + 0.2 * np.random.normal(size=len(t1))
    
    # 2D data for plot2 (simulated spectrogram)
    t2 = np.linspace(0, 10, 100)  # Time axis for spectrogram
    f2 = np.linspace(0, 1000, 128)  # Frequency axis
    # Create synthetic spectrogram data
    spec_data = np.zeros((len(f2), len(t2)))
    for i, freq in enumerate(f2):
        for j, time in enumerate(t2):
            # Create some patterns
            spec_data[i, j] = np.exp(-(freq-200)**2/10000) * np.sin(2*np.pi*time) + \
                             np.exp(-(freq-600)**2/20000) * np.cos(4*np.pi*time) + \
                             0.1 * np.random.random()
    
    # Convert to dB scale
    spec_data_db = 20 * np.log10(np.maximum(spec_data, 1e-10))
    
    # Use optimized plotting methods
    window.plot_data_optimized('plot1', t1, y1, 'Test Signal', 'b')
    window.plot_data_2d('plot2', t2, f2, spec_data_db, 'Test Spectrogram')
    
    print(f"Mixed plotting demo - 1D data: {len(t1)} points, 2D data: {spec_data.shape}")
    print(f"Optimization enabled: {window.FLAG_OPTIMIZE_PLOT}")
    
    # Dynamic timeline parameters
    current_time = 0.0
    time_step = 0.05
    max_time = 10.0
    is_playing = False
    
    def update_timeline():
        """Update timeline position."""
        global current_time
        if is_playing:
            # Draw timeline on both subplots
            window.plot1.draw_timeline(current_time, color='g', width=2)
            window.plot2.draw_timeline(current_time, color='orange', width=2)
            
            # Update progress bar
            progress = int((current_time / max_time) * 100)
            window.set_progress(progress)
            
            current_time += time_step
            if current_time > max_time:
                current_time = 0.0  # Restart
    
    # Create timer for timeline animation
    timer = QTimer()
    timer.timeout.connect(update_timeline)
    timer.start(50)  # Update every 50ms
    
    # Connect signals to control playback state
    def on_play():
        global is_playing
        is_playing = True
        print("Play button clicked - Start animation")
    
    def on_pause():
        global is_playing
        is_playing = False
        print("Pause button clicked - Pause animation")
    
    def on_stop():
        global is_playing, current_time
        is_playing = False
        current_time = 0.0
        window.set_progress(0)
        # Clear timeline
        window.plot1.draw_timeline(0, color='g', width=2)
        window.plot2.draw_timeline(0, color='orange', width=2)
        print("Stop button clicked - Reset animation")
    
    def on_position_changed(value):
        global current_time
        current_time = (value / window.PROGRESS_SLIDER_MAX) * max_time  
        print(f"Progress position: {value/4:.2f}% - Time: {current_time:.2f}s")
    
    window.play_clicked.connect(on_play)
    window.pause_clicked.connect(on_pause)
    window.stop_clicked.connect(on_stop)
    window.position_changed.connect(on_position_changed)
    
    # Initial state setup
    window.set_progress_range(0, 100)
    
    window.show()
    sys.exit(app.exec())
