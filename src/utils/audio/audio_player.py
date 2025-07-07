import numpy as np
import sounddevice as sd
from PySide6.QtCore import QThread, Signal, QTimer, QMutex, QMutexLocker
from PySide6.QtWidgets import QApplication
import time


class AudioPlayer(QThread):
    """Audio player class based on QThread for multi-threaded audio playback."""
    
    # Signal definitions
    position_changed = Signal(float)  # Playback position changed (seconds)
    playback_finished = Signal()     # Playback finished
    playback_started = Signal()      # Playback started
    playback_paused = Signal()       # Playback paused
    playback_stopped = Signal()      # Playback stopped
    error_occurred = Signal(str)     # Error occurred

    TIMER_INTERVAL = 20  # Timer update interval (milliseconds)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Playback state
        self.is_playing = False
        self.is_paused = False
        self.should_stop = False
        
        # Audio data
        self.audio_data = None
        self.sample_rate = None
        self.channels = None
        self.duration = 0.0
        
        # Playback control
        self.current_position = 0.0  # Current playback position (seconds)
        self.start_position = 0.0    # Start playback position (seconds)
        
        # Thread synchronization
        self.mutex = QMutex()
        
        # Audio stream
        self.stream = None
        
        # Position update timer - ensure created in main thread
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self._emit_position)
        self.position_timer.moveToThread(QApplication.instance().thread())
        
        print("AudioPlayer initialization completed")
    
    def load_audio_data(self, audio_reader):
        """Load audio data.
        
        Args:
            audio_reader: AudioFileReader instance.
            
        Returns:
            True if successfully loaded, False otherwise.
        """
        with QMutexLocker(self.mutex):
            if not audio_reader or not audio_reader.is_loaded():
                print("Audio reader has no loaded data")
                return False
            
            try:
                # Get audio information
                audio_info = audio_reader.get_audio_info()
                self.sample_rate = audio_info['sample_rate']
                self.channels = audio_info['channels']
                self.duration = audio_info['duration']
                
                # Get audio data - for multi-channel, get all channels
                if self.channels == 1:
                    self.audio_data = audio_reader.get_channel_data(0).reshape(-1, 1)
                else:
                    # Multi-channel audio, combine all channels
                    audio_channels = []
                    for ch in range(self.channels):
                        channel_data = audio_reader.get_channel_data(ch)
                        if channel_data is not None:
                            audio_channels.append(channel_data)
                    
                    if audio_channels:
                        self.audio_data = np.column_stack(audio_channels)
                    else:
                        print("Unable to get audio channel data")
                        return False
                
                # Reset playback position
                self.current_position = 0.0
                self.start_position = 0.0
                
                print(f"Audio data loaded: {self.audio_data.shape}, sample rate: {self.sample_rate}, duration: {self.duration:.2f}s")
                return True
                
            except Exception as e:
                print(f"Error loading audio data: {e}")
                self.error_occurred.emit(f"Failed to load audio data: {str(e)}")
                return False
    
    def play(self):
        """Start playback."""
        with QMutexLocker(self.mutex):
            if self.audio_data is None:
                print("No audio data to play")
                return
            
            # If already playing and not paused, no need to repeat
            if self.is_playing and not self.is_paused:
                print("Already playing")
                return
            
            # If paused, directly resume playback
            if self.is_paused:
                self.is_paused = False
                # Start timer
                if not self.position_timer.isActive():
                    self.position_timer.start(self.TIMER_INTERVAL)
                self.playback_started.emit()
                print(f"Resume playback, position: {self.current_position:.2f}s")
                return
            
            # Check if playback is complete, restart if so
            if self.current_position >= self.duration:
                self.current_position = 0.0
                self.start_position = 0.0
            
            self.is_playing = True
            self.is_paused = False
            self.should_stop = False
        
        # Start position update timer
        if not self.position_timer.isActive():
            self.position_timer.start(self.TIMER_INTERVAL)
            print("Position update timer started")
        
        # Start playback thread
        if not self.isRunning():
            self.start()  # Start QThread, will call run() method
        
        print(f"Start playback, position: {self.current_position:.2f}s")
    
    def pause(self):
        """Pause playback."""
        with QMutexLocker(self.mutex):
            if not self.is_playing or self.is_paused:
                return
            
            self.is_paused = True
        
        # Stop timer
        if self.position_timer.isActive():
            self.position_timer.stop()
            print("Stop position update timer on pause")
        
        self.playback_paused.emit()
        print(f"Playback paused, position: {self.current_position:.2f}s")
    
    def stop(self):
        """Stop playback."""
        with QMutexLocker(self.mutex):
            self.should_stop = True
            self.is_playing = False
            self.is_paused = False
        
        # Stop position update timer
        if self.position_timer.isActive():
            self.position_timer.stop()
        
        # Stop audio stream
        self._stop_playback()
        
        # Wait for thread to finish
        if self.isRunning():
            self.wait(3000)  # Wait up to 3 seconds
        
        # Reset position
        with QMutexLocker(self.mutex):
            self.current_position = 0.0
            self.start_position = 0.0
        
        self.playback_stopped.emit()
        print("Playback stopped")
    
    def seek(self, position_seconds):
        """Seek to specified position.
        
        Args:
            position_seconds: Target position in seconds.
        """
        with QMutexLocker(self.mutex):
            if self.audio_data is None:
                return
            
            # Limit position range
            position_seconds = max(0.0, min(position_seconds, self.duration))
            old_position = self.current_position
            self.current_position = position_seconds
            self.start_position = position_seconds
            
            # Record current playback state
            was_playing = self.is_playing and not self.is_paused
        
        # If playing, need to restart playback to implement seeking
        if was_playing:
            self._restart_playback()
        else:
            # Even if not playing, emit position change signal to update UI
            self.position_changed.emit(position_seconds)
        
        print(f"Seek: {old_position:.2f}s -> {position_seconds:.2f}s, playing state: {was_playing}")

    def get_current_position(self):
        """Get current playback position."""
        with QMutexLocker(self.mutex):
            return self.current_position
    
    def get_duration(self):
        """Get total audio duration."""
        with QMutexLocker(self.mutex):
            return self.duration
    
    def is_loaded(self):
        """Check if audio is loaded."""
        with QMutexLocker(self.mutex):
            return self.audio_data is not None
    
    def get_playback_state(self):
        """Get current playback state.
        
        Returns:
            dict: State dictionary containing is_playing, is_paused, position.
        """
        with QMutexLocker(self.mutex):
            return {
                'is_playing': self.is_playing,
                'is_paused': self.is_paused,
                'position': self.current_position
            }
    
    @property
    def is_playing_property(self):
        """Playback state property accessor."""
        with QMutexLocker(self.mutex):
            return self.is_playing and not self.is_paused
    
    def is_currently_playing(self):
        """Check if currently playing (not paused)."""
        with QMutexLocker(self.mutex):
            return self.is_playing and not self.is_paused

    
    def run(self):
        """Thread run method."""
        try:
            self._audio_playback_loop()
        except Exception as e:
            print(f"Playback thread error: {e}")
            self.error_occurred.emit(f"Playback error: {str(e)}")
        finally:
            self._cleanup_playback()
    
    def _audio_playback_loop(self):
        """Audio playback loop."""
        self.playback_started.emit()
        
        try:
            # 计算起始采样点
            start_sample = int(self.start_position * self.sample_rate)
            
            # 创建音频流
            def audio_callback(outdata, frames, time_info, status):
                return self._audio_callback(outdata, frames, time_info, status, start_sample)
            
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                blocksize=1024,
                dtype=np.float32
            ) as stream:
                self.stream = stream
                
                # 等待播放完成或停止
                while True:
                    if self.should_stop:
                        break
                    
                    if not self.is_paused:
                        # 检查是否播放完成
                        if self.current_position >= self.duration:
                            break
                    
                    time.sleep(0.01)  # 10ms检查间隔
        
        finally:
            # 停止定时器
            if self.position_timer.isActive():
                self.position_timer.stop()
                print("位置更新定时器已停止")
            
            # 检查是否正常播放完成
            with QMutexLocker(self.mutex):
                if not self.should_stop and self.current_position >= self.duration:
                    # 播放完成，重置状态
                    self.is_playing = False
                    self.is_paused = False
                    self.playback_finished.emit()
                    print("播放完成")
            
            self.stream = None
    
    def _audio_callback(self, outdata, frames, time_info, status, start_sample):
        """音频回调函数"""
        if self.should_stop or self.is_paused:
            outdata.fill(0)
            return
        
        try:
            # 计算当前采样位置
            current_sample = start_sample + int((self.current_position - self.start_position) * self.sample_rate)
            
            # 检查是否超出数据范围
            if current_sample >= len(self.audio_data):
                outdata.fill(0)
                return
            
            # 计算需要的采样数
            remaining_samples = len(self.audio_data) - current_sample
            actual_frames = min(frames, remaining_samples)
            
            if actual_frames > 0:
                # 复制音频数据
                audio_chunk = self.audio_data[current_sample:current_sample + actual_frames]
                outdata[:actual_frames] = audio_chunk.astype(np.float32)
                
                # 填充剩余部分
                if actual_frames < frames:
                    outdata[actual_frames:].fill(0)
                
                # 更新位置
                self.current_position += actual_frames / self.sample_rate
            else:
                outdata.fill(0)
        
        except Exception as e:
            print(f"音频回调错误: {e}")
            outdata.fill(0)
    
    def _emit_position(self):
        """发射位置更新信号"""
        with QMutexLocker(self.mutex):
            # 检查播放状态并获取当前位置
            should_emit = self.is_playing and not self.is_paused and not self.should_stop
            current_pos = self.current_position
        
        # 在锁外发射信号，避免死锁
        if should_emit:
            self.position_changed.emit(current_pos)
    
    def _pause_playback(self):
        """暂停播放实现"""
        # sounddevice流会在回调中处理暂停
        pass
    
    def _resume_playback(self):
        """恢复播放实现"""
        with QMutexLocker(self.mutex):
            self.is_paused = False
        self.playback_started.emit()
    
    def _stop_playback(self):
        """停止播放实现"""
        if self.stream:
            try:
                self.stream.close()
            except:
                pass
    
    def _restart_playback(self):
        """重启播放（用于跳转）"""
        # 停止当前播放
        with QMutexLocker(self.mutex):
            old_should_stop = self.should_stop
            self.should_stop = True
        
        # 停止定时器
        if self.position_timer.isActive():
            self.position_timer.stop()
        
        self._stop_playback()
        
        # 等待当前播放线程结束
        if self.isRunning():
            self.wait(1000)
        
        # 重新设置状态并启动播放
        with QMutexLocker(self.mutex):
            self.should_stop = False
            self.is_playing = True
            self.is_paused = False
        
        # 重新启动定时器
        if not self.position_timer.isActive():
            self.position_timer.start(self.TIMER_INTERVAL)
            print("跳转后重新启动位置更新定时器")
        
        # 重启播放线程
        if not self.isRunning():
            self.start()
    
    def _cleanup_playback(self):
        """清理播放资源"""
        # 确保定时器停止
        QTimer.singleShot(0, lambda: self.position_timer.stop())
        
        with QMutexLocker(self.mutex):
            self.is_playing = False
            self.is_paused = False
    
    def __del__(self):
        """析构函数"""
        self.stop()
        self.wait()
        self.wait()
        self.stop()
        self.wait()
        self.wait()
