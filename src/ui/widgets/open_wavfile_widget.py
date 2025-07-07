# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QListWidget, QListWidgetItem, QFileDialog, 
                               QMessageBox, QLabel)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon

# Add project root directory to path
import sys
sys.path.insert(0, '.')

from config.config_manager import ConfigManager
from src.utils.audio.audio_file_reader import AudioFileReader


class OpenWavFileWidget(QWidget):
    """File opening widget for audio files.
    
    This widget provides functionality to:
    - Open audio files through file dialog
    - Display list of opened files
    - Load and manage audio file data
    - Show current file information
    """
    
    # Signal definitions
    file_selected = Signal(str)  # File selection signal
    file_removed = Signal(str)   # File deletion signal
    audio_loaded = Signal(object, dict)  # Audio loading signal (audio_data, info)
    stop_playback_requested = Signal()  # Request stop playback signal
    
    def __init__(self, parent=None):
        """Initialize the OpenWavFileWidget.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Initialize audio reader
        self.audio_reader = AudioFileReader()
        
        # Current opened file path
        self.current_file_path = None
        
        # Setup UI
        self._setup_ui()
        
        # Connect signal slots
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup UI layout."""
        layout = QVBoxLayout(self)
        
        # Current file info label
        self.current_file_label = QLabel("当前文件: 无")
        self.current_file_label.setWordWrap(True)
        self.current_file_label.setStyleSheet("QLabel { font-weight: bold; color: white; }")
        layout.addWidget(self.current_file_label)
        
        # Audio info label
        self.audio_info_label = QLabel("音频信息: 无")
        self.audio_info_label.setWordWrap(True)
        layout.addWidget(self.audio_info_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Open file button
        self.open_button = QPushButton("打开文件")
        self.open_button.setToolTip("选择音频文件")
        button_layout.addWidget(self.open_button)
        
        # Remove file button
        self.remove_button = QPushButton("删除选中")
        self.remove_button.setToolTip("删除选中的文件")
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        
        # Clear list button
        self.clear_button = QPushButton("清空列表")
        self.clear_button.setToolTip("清空所有文件")
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setToolTip("双击文件名可以选择文件")  
        layout.addWidget(self.file_list)
        
        # Set minimum size
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
    
    def _connect_signals(self):
        """Connect signal slots."""
        self.open_button.clicked.connect(self.open_file)
        self.remove_button.clicked.connect(self._remove_selected_file)
        self.clear_button.clicked.connect(self._clear_file_list)
        
        # List selection change
        self.file_list.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Double click to select file
        self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def open_file(self):
        """Open file dialog for audio file selection."""
        # Get last opened path
        last_path = self.config_manager.get_last_opened_path()
        if not last_path or not os.path.exists(last_path):
            last_path = os.path.expanduser("~")  # Default to user directory
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频文件",
            last_path,  # Use saved path as starting directory
            "音频文件 (*.wav *.mp3);;所有文件 (*.*)"
        )

        if file_path:
            self._add_file_to_list(file_path)
            # Directly load selected file
            self._load_audio_file(file_path)

            # Save last opened path
            self.config_manager.set_last_opened_path(os.path.dirname(file_path))
    
    def _add_file_to_list(self, file_path):
        """Add file to the list.
        
        Args:
            file_path (str): Path of the file to add.
        """
        # Check if file already exists
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.data(Qt.UserRole) == file_path:
                QMessageBox.information(self, "提示", "文件已经在列表中！")
                return
        
        # Add file to list
        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.UserRole, file_path)  # Store complete path
        item.setToolTip(file_path)  # Set tooltip to show complete path
        self.file_list.addItem(item)
        
        # Enable buttons
        self.remove_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        
        print(f"File added to list: {file_path}")
    
    def _load_audio_file(self, file_path):
        """Load audio file.
        
        Args:
            file_path (str): Path of the audio file to load.
        """
        try:
            # Request to stop current playback before loading new audio file
            self.stop_playback_requested.emit()
            
            # Check file format
            if not AudioFileReader.is_supported_format(file_path):
                QMessageBox.warning(self, "格式错误", "不支持的音频格式！仅支持 .wav 和 .mp3 格式。")
                return
            
            # Load audio file
            if self.audio_reader.load_audio_file(file_path):
                self.current_file_path = file_path
                self._update_file_info()
                
                # Emit audio loaded signal
                audio_info = self.audio_reader.get_audio_info()
                self.audio_loaded.emit(self.audio_reader, audio_info)
                
                print('--- --- --- --- --- ---')
                print(f"Audio file loaded successfully: {file_path}")
                print(f"Audio info: sample_rate={audio_info['sample_rate']}, channels={audio_info['channels']}, duration={audio_info['duration']:.2f}s")
                
            else:
                QMessageBox.critical(self, "加载失败", "音频文件加载失败！请检查文件是否损坏。")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载音频文件时发生错误：\n{str(e)}")
    
    def _update_file_info(self):
        """Update file information display."""
        if self.current_file_path:
            file_name = os.path.basename(self.current_file_path)
            self.current_file_label.setText(f"当前文件: {file_name}")
            
            if self.audio_reader.is_loaded():
                info = self.audio_reader.get_audio_info()
                info_text = (f"采样率: {info['sample_rate']} Hz | "
                           f"通道数: {info['channels']} | "
                           f"时长: {info['duration']:.2f} 秒")
                self.audio_info_label.setText(f"音频信息: {info_text}")
            else:
                self.audio_info_label.setText("音频信息: 加载失败")
        else:
            self.current_file_label.setText("当前文件: 无")
            self.audio_info_label.setText("音频信息: 无")
    
    def _remove_selected_file(self):
        """Remove selected file from list."""
        current_row = self.file_list.currentRow()
        if current_row < 0:
            return
        
        # Get file path to be removed
        file_path = self.file_list.item(current_row).data(Qt.UserRole)
        
        # If removing currently loaded file, clear audio data
        if file_path == self.current_file_path:
            self._clear_current_audio()
        
        # Remove from list
        self.file_list.takeItem(current_row)
        
        # Emit file removed signal
        self.file_removed.emit(file_path)
        
        # If list is empty, disable remove and clear buttons
        if self.file_list.count() == 0:
            self.remove_button.setEnabled(False)
            self.clear_button.setEnabled(False)
    
    def _clear_file_list(self):
        """Clear file list."""
        self.file_list.clear()
        self.remove_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self._clear_current_audio()
        self.file_removed.emit("")  # Emit clear signal
    
    def _clear_current_audio(self):
        """Clear current audio data."""
        self.audio_reader.clear()
        self.current_file_path = None
        self._update_file_info()
    
    def _on_selection_changed(self):
        """Handle selection change."""
        has_selection = self.file_list.currentRow() >= 0
        self.remove_button.setEnabled(has_selection)
    
    def _on_item_double_clicked(self, item):
        """Handle item double click.
        
        Args:
            item (QListWidgetItem): The clicked item.
        """
        file_path = item.data(Qt.UserRole)
        if file_path:
            # Load audio file on double click
            self._load_audio_file(file_path)
        else:
            QMessageBox.warning(self, "警告", "无法获取文件路径！")
    
    def get_opened_files(self):
        """Get list of opened files.
        
        Returns:
            list: List of file paths.
        """
        return [self.file_list.item(i).data(Qt.UserRole) for i in range(self.file_list.count())]
    
    def get_current_audio_reader(self):
        """Get current audio reader.
        
        Returns:
            AudioFileReader or None: Current audio reader if loaded, None otherwise.
        """
        return self.audio_reader if self.audio_reader.is_loaded() else None
    
    def get_current_file_path(self):
        """Get current file path.
        
        Returns:
            str or None: Current file path if available, None otherwise.
        """
        return self.current_file_path
    
    def clear_files(self):
        """Clear file list."""
        self.file_list.clear()
        self.remove_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self._clear_current_audio()

