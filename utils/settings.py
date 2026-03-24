"""应用设置管理模块。

本模块包含应用程序全局设置的管理。
"""

import json
import os
from pathlib import Path
from typing import Any


class AppSettings:
    """应用设置管理类。
    
    单例模式，管理应用程序的全局设置。
    支持设置的持久化存储。
    """
    
    _instance = None
    
    DEFAULT_SETTINGS = {
        "handle_size": 8,
        "handle_click_tolerance": 24,
        "grid_size": 10,
        "snap_to_grid": True,
        "show_grid": True,
        "font_family": "Microsoft YaHei",
        "font_size": 10,
        "show_create_window_hint": True,
        "user_name": "",
        "is_registered": False,
        "undo_max_steps": 50,
        "debug_verbose": True,
        "debug_show_position": True,
        "debug_show_component_details": True,
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._settings = dict(self.DEFAULT_SETTINGS)
        self._callbacks = []
        self._settings_file = self._get_settings_file_path()
        self._load_settings()
    
    def _get_settings_file_path(self) -> Path:
        """获取设置文件路径。"""
        app_data = os.getenv('APPDATA') or os.getenv('HOME', '')
        settings_dir = Path(app_data) / "FoolDesktopTool"
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir / "settings.json"
    
    def _load_settings(self):
        """从文件加载设置。"""
        try:
            if self._settings_file.exists():
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._settings.update(loaded)
        except (json.JSONDecodeError, IOError):
            pass
    
    def _save_settings(self):
        """保存设置到文件。"""
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值。"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置值。"""
        if self._settings.get(key) != value:
            self._settings[key] = value
            self._save_settings()
            self._notify_callbacks(key, value)
    
    def _notify_callbacks(self, key: str, value: Any):
        """通知所有回调函数。"""
        for callback in self._callbacks:
            try:
                callback(key, value)
            except Exception:
                pass
    
    def add_change_callback(self, callback):
        """添加设置变化回调。"""
        self._callbacks.append(callback)
    
    def remove_change_callback(self, callback):
        """移除设置变化回调。"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    @property
    def handle_size(self) -> int:
        """手柄大小。"""
        return self.get("handle_size", 8)
    
    @handle_size.setter
    def handle_size(self, value: int):
        self.set("handle_size", value)
    
    @property
    def handle_click_tolerance(self) -> int:
        """手柄点击容差。"""
        return self.get("handle_click_tolerance", 24)
    
    @handle_click_tolerance.setter
    def handle_click_tolerance(self, value: int):
        self.set("handle_click_tolerance", value)
    
    @property
    def grid_size(self) -> int:
        """网格大小。"""
        return self.get("grid_size", 10)
    
    @grid_size.setter
    def grid_size(self, value: int):
        self.set("grid_size", value)
    
    @property
    def snap_to_grid(self) -> bool:
        """是否对齐网格。"""
        return self.get("snap_to_grid", True)
    
    @snap_to_grid.setter
    def snap_to_grid(self, value: bool):
        self.set("snap_to_grid", value)
    
    @property
    def show_grid(self) -> bool:
        """是否显示网格。"""
        return self.get("show_grid", True)
    
    @show_grid.setter
    def show_grid(self, value: bool):
        self.set("show_grid", value)
    
    @property
    def font_family(self) -> str:
        """字体名称。"""
        return self.get("font_family", "Microsoft YaHei")
    
    @font_family.setter
    def font_family(self, value: str):
        self.set("font_family", value)
    
    @property
    def font_size(self) -> int:
        """字体大小。"""
        return self.get("font_size", 10)
    
    @font_size.setter
    def font_size(self, value: int):
        self.set("font_size", value)
    
    @property
    def show_create_window_hint(self) -> bool:
        """是否显示创建窗口提示。"""
        return self.get("show_create_window_hint", True)
    
    @show_create_window_hint.setter
    def show_create_window_hint(self, value: bool):
        self.set("show_create_window_hint", value)
    
    @property
    def user_name(self) -> str:
        """用户名。"""
        return self.get("user_name", "")
    
    @user_name.setter
    def user_name(self, value: str):
        self.set("user_name", value)
    
    @property
    def is_registered(self) -> bool:
        """是否已注册。"""
        return self.get("is_registered", False)
    
    @is_registered.setter
    def is_registered(self, value: bool):
        self.set("is_registered", value)
    
    @property
    def undo_max_steps(self) -> int:
        """撤销最大步数。"""
        return self.get("undo_max_steps", 50)
    
    @undo_max_steps.setter
    def undo_max_steps(self, value: int):
        self.set("undo_max_steps", value)
    
    @property
    def debug_verbose(self) -> bool:
        """是否启用详细调试输出。"""
        return self.get("debug_verbose", True)
    
    @debug_verbose.setter
    def debug_verbose(self, value: bool):
        self.set("debug_verbose", value)
    
    @property
    def debug_show_position(self) -> bool:
        """是否显示位置调试信息。"""
        return self.get("debug_show_position", True)
    
    @debug_show_position.setter
    def debug_show_position(self, value: bool):
        self.set("debug_show_position", value)
    
    @property
    def debug_show_component_details(self) -> bool:
        """是否显示组件详细信息。"""
        return self.get("debug_show_component_details", True)
    
    @debug_show_component_details.setter
    def debug_show_component_details(self, value: bool):
        self.set("debug_show_component_details", value)
    
    def reset_to_defaults(self):
        """重置为默认设置。"""
        self._settings = dict(self.DEFAULT_SETTINGS)
        self._save_settings()
        for key, value in self._settings.items():
            self._notify_callbacks(key, value)


app_settings = AppSettings()
