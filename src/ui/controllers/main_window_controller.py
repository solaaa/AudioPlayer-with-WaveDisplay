# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import (QMainWindow, QApplication, QDockWidget, 
                               QMessageBox, QWidget)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QFont, QActionGroup

import qdarktheme

# Add project root directory to path
sys.path.insert(0, '.')

from src.ui.widgets.display_panel import DisplayPanel
from src.ui.widgets.open_wavfile_widget import OpenWavFileWidget
from src.ui.controllers.param_setting_panel_controller import ParamSettingPanelController
from config.config_manager import ConfigManager
from src.ui.widgets.display_wav_widget import CustomPlotWidget

class MainWindowController(QMainWindow):
    """Main window controller for the system.
    
    This class manages the main application window, including UI layout,
    menu creation, dock widgets, and signal handling between components.
    
    Attributes:
        config_manager (ConfigManager): Configuration management instance
        current_font_size (str): Current font size setting
        display_panel (DisplayPanel): Central display panel for audio visualization
        file_widget (OpenWavFileWidget): File operation widget
        param_panel (ParamSettingPanelController): Parameter setting panel
    """
    
    def __init__(self, parent=None):
        """Initialize the main window controller.
        
        Args:
            parent: Parent widget, defaults to None
        """
        super().__init__(parent)
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Current font size setting
        self.current_font_size = "middle"
        
        # Initialize components
        self._init_components()
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals and slots
        self._connect_signals()
        
        # Setup window properties
        self._setup_window()
        
        # Apply saved configuration
        self._apply_saved_config()
    
    def _init_components(self):
        """Initialize all UI components."""
        # Central display panel
        self.display_panel = DisplayPanel()
        
        # File operation widget
        self.file_widget = OpenWavFileWidget()
        
        # Parameter setting panel
        self.param_panel = ParamSettingPanelController()
    
    def _setup_ui(self):
        """Setup UI layout and components."""
        # Set central widget
        self.setCentralWidget(self.display_panel)
        
        # Create dock widgets
        self._create_dock_widgets()
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_dock_widgets(self):
        """Create and configure dock widgets."""
        # File operation dock widget
        self.file_dock = QDockWidget("文件操作", self)
        self.file_dock.setWidget(self.file_widget)
        self.file_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.file_dock.setFeatures(
            QDockWidget.DockWidgetMovable | 
            QDockWidget.DockWidgetClosable |
            QDockWidget.DockWidgetFloatable
        )
        
        # Parameter setting dock widget
        self.param_dock = QDockWidget("参数设置", self)
        self.param_dock.setWidget(self.param_panel)
        self.param_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.param_dock.setFeatures(
            QDockWidget.DockWidgetMovable | 
            QDockWidget.DockWidgetClosable |
            QDockWidget.DockWidgetFloatable
        )
        
        # Add dock widgets to main window (left side, overlapped as tabs)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.param_dock)
        
        # Set tab mode overlapping display
        self.tabifyDockWidget(self.file_dock, self.param_dock)
        
        # Show file operation tab by default
        self.file_dock.raise_()
    
    def _create_menu_bar(self):
        """Create and configure the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("文件(&F)")
        
        # Open file action
        open_action = QAction("打开音频文件(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("打开音频文件")
        open_action.triggered.connect(self.file_widget.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("视图(&V)")
        
        # Show/hide dock widget actions
        view_menu.addAction(self.file_dock.toggleViewAction())
        view_menu.addAction(self.param_dock.toggleViewAction())
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu("主题(&T)")
        self.theme_group = QActionGroup(self)
        
        # Light theme
        light_action = QAction("浅色主题(&L)", self)
        light_action.setCheckable(True)
        light_action.setData("light")
        light_action.triggered.connect(lambda: self._set_theme("light"))
        self.theme_group.addAction(light_action)
        theme_menu.addAction(light_action)
        
        # Dark theme
        dark_action = QAction("深色主题(&D)", self)
        dark_action.setCheckable(True)
        dark_action.setData("dark")
        dark_action.triggered.connect(lambda: self._set_theme("dark"))
        self.theme_group.addAction(dark_action)
        theme_menu.addAction(dark_action)
        
        # Font submenu
        font_menu = view_menu.addMenu("字体(&F)")
        self.font_group = QActionGroup(self)
        
        font_sizes = [
            ("小字体(&S)", "small"),
            ("中字体(&M)", "middle"),
            ("大字体(&L)", "large"),
            ("超大字体(&X)", "XLarge")
        ]
        
        for name, size in font_sizes:
            font_action = QAction(name, self)
            font_action.setCheckable(True)
            font_action.setData(size)
            font_action.triggered.connect(lambda checked, s=size: self._set_font_size(s))
            self.font_group.addAction(font_action)
            font_menu.addAction(font_action)
        
        # Help menu
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create and configure the status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪", 2000)
    
    def _connect_signals(self):
        """Connect signals and slots between components."""
        # file_widget signals
        self.file_widget.file_removed.connect(self._on_file_removed)
        self.file_widget.audio_loaded.connect(self._on_audio_loaded)
        self.file_widget.stop_playback_requested.connect(self._on_stop_playback_requested)
        
        # Parameter change signals
        self.param_panel.param_changed.connect(self._on_param_changed)
        
        # Playback control signals - now handled internally by DisplayPanel's AudioPlayer
        # Here we mainly handle status updates
        self.display_panel.play_clicked.connect(self._on_play_state_changed)
        self.display_panel.pause_clicked.connect(self._on_pause_state_changed)
        self.display_panel.stop_clicked.connect(self._on_stop_state_changed)
        self.display_panel.position_changed.connect(self._on_position_state_changed)
    
    def _setup_window(self):
        """Setup window properties and attributes."""
        self.resize(1600, 800)
        
        # Set minimum window size
        self.setMinimumSize(1200, 600)
        
        # Center window on screen
        self._center_window()
    
    def _center_window(self):
        """Center the window on the primary screen."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def _apply_saved_config(self):
        """Apply saved configuration settings."""
        # Apply theme
        saved_theme = self.config_manager.get_theme()
        self._set_theme(saved_theme, save_config=False)
        
        # Set theme menu selection state
        for action in self.theme_group.actions():
            if action.data() == saved_theme:
                action.setChecked(True)
                break
        
        # Apply font
        saved_font_size = self.config_manager.get_font_size()
        self.current_font_size = saved_font_size
        self._set_font_size(saved_font_size, save_config=False)
        
        # Set font menu selection state
        for action in self.font_group.actions():
            if action.data() == saved_font_size:
                action.setChecked(True)
                break
    
    def _set_theme(self, theme: str, save_config: bool = True):
        """Set the application theme.
        
        Args:
            theme: Theme name ("dark" or "light")
            save_config: Whether to save the theme setting, defaults to True
        """
        if theme == "dark":
            qdarktheme.setup_theme("dark")
        else:
            qdarktheme.setup_theme("light")
        
        # Reapply font settings after theme change
        self._apply_font_to_all_widgets()
        
        if save_config:
            self.config_manager.set_theme(theme)
        
        self.status_bar.showMessage(f"主题已切换为: {'深色' if theme == 'dark' else '浅色'}", 2000)
    
    def _set_font_size(self, font_size: str, save_config: bool = True):
        """Set the application font size.
        
        Args:
            font_size: Font size identifier ("small", "middle", "large", "XLarge")
            save_config: Whether to save the font setting, defaults to True
        """
        self.current_font_size = font_size
        
        # Apply font to all widgets
        self._apply_font_to_all_widgets()
        
        if save_config:
            self.config_manager.set_font_size(font_size)
        
        size_names = {
            "small": "小",
            "middle": "中",
            "large": "大",
            "XLarge": "超大"
        }
        
        self.status_bar.showMessage(f"字体大小已设置为: {size_names.get(font_size, '中')}", 2000)
    
    def _apply_font_to_all_widgets(self):
        """Recursively apply font settings to all widgets."""
        font_sizes = {
            "small": 8,
            "middle": 12,
            "large": 14,
            "XLarge": 18
        }
        
        size = font_sizes.get(self.current_font_size, 12)
        
        # Create new font
        font = QFont()
        font.setPointSize(size)
        # font.setFamily("Microsoft YaHei UI")  # Set Chinese-friendly font
        font.setFamily("consolas")  # Set monospace font
        
        # Set application default font
        QApplication.setFont(font)
        
        # Recursively apply to all child widgets
        self._apply_font_recursive(self, font)
    
    def _apply_font_recursive(self, widget: QWidget, font: QFont):
        """Recursively apply font to widget and all its children.
        
        Args:
            widget: Target widget to apply font to
            font: Font object to apply
        """
        try:
            widget.setFont(font)
            # Recursively set font for all child widgets
            for child in widget.findChildren(QWidget):
                if isinstance(child, CustomPlotWidget):
                    smaller_size = 10
                    child.set_axis_font_size(smaller_size)
                else:
                    child.setFont(font)
                    
        except Exception as e:
            print(f"Error setting font: {e}")
    
    def _show_about(self):
        """Display the about dialog."""
        QMessageBox.about(
            self,
            "关于",
            ""
            # "扬声器保护系统 v1.0\n\n"
            # "这是一个用于扬声器保护的音频处理软件。\n"
            # "使用PySide6开发。"
        )
    
    def closeEvent(self, event):
        """Handle window close event.
        
        Args:
            event: Close event object
        """
        # Stop audio playback
        audio_player = self.display_panel.get_audio_player()
        if audio_player:
            audio_player.stop()
            audio_player.wait()  # Wait for playback thread to finish
        
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    

    @Slot(object, dict)
    def _on_audio_loaded(self, audio_reader, audio_info):
        """Handle audio file loading event.
        
        Args:
            audio_reader: Audio reader object
            audio_info: Dictionary containing audio file information
        """
        try:
            file_name = os.path.basename(audio_info['file_path']) if audio_info['file_path'] else 'Unknown file'
            
            # Plot waveform in display panel (first channel)
            self.display_panel.plot_audio_waveform(audio_reader, channel=0)
            
            # Update status bar
            status_text = (f"音频已加载: {file_name} | "
                         f"采样率: {audio_info['sample_rate']}Hz | "
                         f"通道数: {audio_info['channels']} | "
                         f"时长: {audio_info['duration']:.2f}s")
            self.status_bar.showMessage(status_text, 5000)
            
            print(f"Audio file loaded and displayed: {audio_info}")
            
        except Exception as e:
            print(f"Error handling audio loading: {e}")
            QMessageBox.critical(self, "错误", f"显示音频波形时发生错误：\n{str(e)}")

    @Slot(str)
    def _on_file_removed(self, file_path):
        """Handle file removal event.
        
        Args:
            file_path: Path of the removed file, empty string for clear operation
        """
        if file_path:  # If not a clear operation
            self.status_bar.showMessage(f"已删除文件: {os.path.basename(file_path)}", 3000)
            print(f"File removed: {file_path}")
        else:  # Clear operation
            self.display_panel.clear_plots()
            self.status_bar.showMessage("文件列表已清空", 3000)
            print("File list cleared, plots cleared")
    
    @Slot(str, object)
    def _on_param_changed(self, param_name, param_value):
        """Handle parameter change event.
        
        Args:
            param_name: Name of the changed parameter
            param_value: New value of the parameter
        """
        self.status_bar.showMessage(f"参数已更新: {param_name}", 2000)
        print(f"Parameter changed: {param_name} = {param_value}")
        # TODO: Add parameter processing logic here
    
    @Slot()
    def _on_play_state_changed(self):
        """Handle play state change event."""
        self.status_bar.showMessage("正在播放音频", 2000)
        print("Audio playback state: Playing")
    
    @Slot()
    def _on_pause_state_changed(self):
        """Handle pause state change event."""
        self.status_bar.showMessage("音频播放已暂停", 2000)
        print("Audio playback state: Paused")
    
    @Slot()
    def _on_stop_state_changed(self):
        """Handle stop state change event."""
        self.status_bar.showMessage("音频播放已停止", 2000)
        print("Audio playback state: Stopped")
    
    @Slot(int)
    def _on_position_state_changed(self, position):
        """Handle playback position change event.
        
        Args:
            position: Current playback position
        """
        # Additional position change handling logic can be added here
        # For example, updating status bar with current playback time
        audio_player = self.display_panel.get_audio_player()
        if audio_player and audio_player.is_loaded():
            current_time = audio_player.get_current_position()
            total_time = audio_player.get_duration()
            time_text = f"播放时间: {current_time:.1f}s / {total_time:.1f}s"
            self.status_bar.showMessage(time_text, 100)  # Brief display, frequent updates
    
    @Slot()
    def _on_stop_playback_requested(self):
        """Handle stop playback request event."""
        # Simulate user clicking stop button
        audio_player = self.display_panel.get_audio_player()
        if audio_player:
            audio_player.stop()
        print("Auto-stop playback before loading new audio")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("扬声器保护系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Audio Systems")
    
    # Create main window
    main_window = MainWindowController()
    main_window.show()
    
    sys.exit(app.exec())
