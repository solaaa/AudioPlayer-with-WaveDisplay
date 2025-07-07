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
        self.ui.lineEdit.textChanged.connect(self._on_line_edit_changed)
        self.ui.comboBox.currentTextChanged.connect(self._on_combo_box_changed)
        self.ui.spinBox.valueChanged.connect(self._on_spin_box_changed)
        self.ui.textEdit.textChanged.connect(self._on_text_edit_changed)
    
    def _init_data(self):
        """初始化数据"""
        # 设置默认值
        self.ui.lineEdit.setText("默认参数")
        self.ui.spinBox.setValue(0)
        self.ui.textEdit.setPlainText("参数描述...")
    
    def _on_line_edit_changed(self, text):
        """处理文本输入框变化"""
        self.param_changed.emit("name", text)
    
    def _on_combo_box_changed(self, text):
        """处理组合框选择变化"""
        self.param_changed.emit("type", text)
    
    def _on_spin_box_changed(self, value):
        """处理数值输入框变化"""
        self.param_changed.emit("value", value)
    
    def _on_text_edit_changed(self):
        """处理文本编辑器变化"""
        text = self.ui.textEdit.toPlainText()
        self.param_changed.emit("description", text)
    
    def get_param_data(self):
        """获取当前参数数据"""
        return {
            "name": self.ui.lineEdit.text(),
            "type": self.ui.comboBox.currentText(),
            "value": self.ui.spinBox.value(),
            "description": self.ui.textEdit.toPlainText()
        }
    
    def set_param_data(self, data):
        """设置参数数据"""
        if "name" in data:
            self.ui.lineEdit.setText(data["name"])
        if "type" in data:
            index = self.ui.comboBox.findText(data["type"])
            if index >= 0:
                self.ui.comboBox.setCurrentIndex(index)
        if "value" in data:
            self.ui.spinBox.setValue(data["value"])
        if "description" in data:
            self.ui.textEdit.setPlainText(data["description"])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 创建并显示控件
    widget = ParamSettingPanelController()
    widget.setWindowTitle("参数设置面板测试")
    widget.show()
    
    # 连接信号用于测试
    def on_param_changed(param_name, param_value):
        print(f"参数变化: {param_name} = {param_value}")
    
    widget.param_changed.connect(on_param_changed)
    
    # 设置测试数据
    test_data = {
        "name": "测试参数",
        "type": "浮点数",
        "value": 42,
        "description": "这是一个测试参数的描述信息"
    }
    widget.set_param_data(test_data)
    
    sys.exit(app.exec())
