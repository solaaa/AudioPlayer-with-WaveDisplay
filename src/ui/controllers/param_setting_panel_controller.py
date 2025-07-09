# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Signal
import sys

sys.path.insert(0, '.')
from src.ui.compiled.ui_param_setting_panel import Ui_Form


class ParamSettingPanelController(QWidget):
    """参数设置面板控制器"""
    
    # 定义信号
    param_changed = Signal(str, object)  # 参数名, 参数值
    implement_clicked = Signal()  # 执行按钮点击信号
    reset_clicked = Signal()  # 重置按钮点击信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # 连接信号槽
        self._connect_signals()
        
        # 初始化数据
        self._init_data()
    
    def _connect_signals(self):
        """连接信号槽"""
        # STFT参数控件信号连接
        self.ui.cb_stft_overlap.currentTextChanged.connect(self._on_overlap_changed)
        self.ui.cb_stft_window.currentTextChanged.connect(self._on_window_changed)
        self.ui.comboBox.currentTextChanged.connect(self._on_nfft_changed)
        self.ui.cb_stft_colormap.currentTextChanged.connect(self._on_colormap_changed)
        
        # 按钮信号连接
        self.ui.pb_para_setting_panel_implement.clicked.connect(self._on_implement_clicked)
        self.ui.pb_para_setting_panel_reset.clicked.connect(self._on_reset_clicked)
    
    def _init_data(self):
        """初始化数据"""
        # 设置默认值（UI文件中已设置默认索引）
        pass
    
    def _on_overlap_changed(self, text):
        """处理重叠率变化"""
        # 将百分比文本转换为数值
        overlap_value = int(text.replace('%', '')) / 100.0
        self.param_changed.emit("overlap", overlap_value)
    
    def _on_window_changed(self, text):
        """处理窗函数变化"""
        self.param_changed.emit("window", text)
    
    def _on_nfft_changed(self, text):
        """处理NFFT变化"""
        nfft_value = int(text)
        self.param_changed.emit("nfft", nfft_value)
    
    def _on_colormap_changed(self, text):
        """处理颜色映射变化"""
        self.param_changed.emit("colormap", text)
    
    def _on_implement_clicked(self):
        """处理执行按钮点击"""
        self.implement_clicked.emit()
    
    def _on_reset_clicked(self):
        """处理重置按钮点击"""
        self.reset_clicked.emit()
        self._reset_to_default()
    
    def _reset_to_default(self):
        """重置到默认值"""
        self.ui.cb_stft_overlap.setCurrentIndex(2)  # 50%
        self.ui.cb_stft_window.setCurrentIndex(0)   # hann
        self.ui.comboBox.setCurrentIndex(3)         # 1024
        self.ui.cb_stft_colormap.setCurrentIndex(0) # inferno
    
    def get_param_data(self):
        """获取当前参数数据"""
        overlap_text = self.ui.cb_stft_overlap.currentText()
        overlap_value = int(overlap_text.replace('%', '')) / 100.0
        
        return {
            "overlap": overlap_value,
            "window": self.ui.cb_stft_window.currentText(),
            "nfft": int(self.ui.comboBox.currentText()),
            "colormap": self.ui.cb_stft_colormap.currentText()
        }
    
    def set_param_data(self, data):
        """设置参数数据"""
        if "overlap" in data:
            overlap_percent = f"{int(data['overlap'] * 100)}%"
            index = self.ui.cb_stft_overlap.findText(overlap_percent)
            if index >= 0:
                self.ui.cb_stft_overlap.setCurrentIndex(index)
        
        if "window" in data:
            index = self.ui.cb_stft_window.findText(data["window"])
            if index >= 0:
                self.ui.cb_stft_window.setCurrentIndex(index)
        
        if "nfft" in data:
            nfft_text = str(data["nfft"])
            index = self.ui.comboBox.findText(nfft_text)
            if index >= 0:
                self.ui.comboBox.setCurrentIndex(index)
        
        if "colormap" in data:
            index = self.ui.cb_stft_colormap.findText(data["colormap"])
            if index >= 0:
                self.ui.cb_stft_colormap.setCurrentIndex(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 创建并显示控件
    widget = ParamSettingPanelController()
    widget.setWindowTitle("STFT参数设置面板测试")
    widget.show()
    
    # 连接信号用于测试
    def on_param_changed(param_name, param_value):
        print(f"参数变化: {param_name} = {param_value}")
    
    def on_implement_clicked():
        print("执行按钮被点击")
        print("当前参数:", widget.get_param_data())
    
    def on_reset_clicked():
        print("重置按钮被点击")
    
    widget.param_changed.connect(on_param_changed)
    widget.implement_clicked.connect(on_implement_clicked)
    widget.reset_clicked.connect(on_reset_clicked)
    
    # 设置测试数据
    test_data = {
        "overlap": 0.75,
        "window": "hamming",
        "nfft": 2048,
        "colormap": "turbo"
    }
    widget.set_param_data(test_data)
    
    sys.exit(app.exec())
