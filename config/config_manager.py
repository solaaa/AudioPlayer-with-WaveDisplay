# -*- coding: utf-8 -*-

import json
import os
from typing import Any, Dict

class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _config_file = "config/global_config.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._config = self._load_config()
            self._initialized = True
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 如果配置文件不存在, 则新建文件
                os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
                with open(self._config_file, 'w', encoding='utf-8') as f:
                    default_config = {
                        "software_name": "Speaker Protection Test Platform",
                        "version": "v0.0.1 beta",
                        "theme": "light",
                        "font_size": "middle",
                        "last_opened_path": ""
                    }
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                # 返回默认配置
                return {
                    "software_name": "Speaker Protection Test Platform",
                    "version": "v0.0.1 beta",
                    "theme": "light",
                    "font_size": "middle",
                    "last_opened_path": ""
                }
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def _save_config(self):
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
        self._save_config()
    
    def get_theme(self) -> str:
        """获取主题"""
        return self.get("theme", "light")
    
    def set_theme(self, theme: str):
        """设置主题"""
        self.set("theme", theme)
    
    def get_font_size(self) -> str:
        """获取字体大小"""
        return self.get("font_size", "middle")
    
    def set_font_size(self, font_size: str):
        """设置字体大小"""
        self.set("font_size", font_size)
    
    def get_last_opened_path(self) -> str:
        """获取最后打开的路径"""
        return self.get("last_opened_path", "")
    
    def set_last_opened_path(self, path: str):
        """设置最后打开的路径"""
        self.set("last_opened_path", path)
