from __future__ import annotations
"""
Galgame示例项目 - 自动生成的窗口程序
生成时间: 2026-03-21 19:56:34

本文件由傻瓜桌面开发工具自动生成。
可以直接运行，也可以导入到工具中编辑。
"""

import sys
import json
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QLineEdit, QCheckBox, QComboBox, QProgressBar, QFrame,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

class ComponentFactory:
    """组件工厂。"""
    
    @staticmethod
    def create_button(data: Dict[str, Any], parent: QWidget, window_manager: WindowManager) -> QPushButton:
        btn = QPushButton(data.get("text", ""), parent)
        btn.setGeometry(data["x"], data["y"], data["width"], data["height"])
        
        style = data.get("style", {})
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {style.get("background_color", "#f0f0f0")};
                color: {style.get("text_color", "#333333")};
                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#999999")};
                border-radius: {style.get("border_radius", 4)}px;
                font-size: {style.get("font_size", 12)}px;
                font-weight: {"bold" if style.get("font_bold") else "normal"};
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        
        target_window = data.get("target_window_id", "")
        if target_window:
            btn.clicked.connect(lambda: window_manager.show_window(target_window))
        else:
            action = data.get("action", {})
            action_type = action.get("action_type", "none")
            if action_type == "close_window":
                btn.clicked.connect(lambda: btn.window().close())
            elif action_type == "show_message":
                msg = action.get("params", {}).get("param", "")
                btn.clicked.connect(lambda: QMessageBox.information(btn.window(), "提示", msg))
        
        return btn
    
    @staticmethod
    def create_label(data: Dict[str, Any], parent: QWidget) -> QLabel:
        lbl = QLabel(data.get("text", ""), parent)
        lbl.setGeometry(data["x"], data["y"], data["width"], data["height"])
        
        style = data.get("style", {})
        alignment = data.get("alignment", "left")
        align_map = {"left": Qt.AlignmentFlag.AlignLeft, "center": Qt.AlignmentFlag.AlignCenter, "right": Qt.AlignmentFlag.AlignRight}
        lbl.setAlignment(align_map.get(alignment, Qt.AlignmentFlag.AlignLeft) | Qt.AlignmentFlag.AlignVCenter)
        
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {style.get("background_color", "transparent")};
                color: {style.get("text_color", "#333333")};
                font-size: {style.get("font_size", 12)}px;
                font-weight: {"bold" if style.get("font_bold") else "normal"};
            }}
        """)
        lbl.setWordWrap(data.get("word_wrap", False))
        
        return lbl
    
    @staticmethod
    def create_input(data: Dict[str, Any], parent: QWidget) -> QLineEdit:
        inp = QLineEdit(parent)
        inp.setGeometry(data["x"], data["y"], data["width"], data["height"])
        inp.setPlaceholderText(data.get("placeholder", ""))
        inp.setMaxLength(data.get("max_length", 32767))
        
        if data.get("is_password", False):
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        
        style = data.get("style", {})
        inp.setStyleSheet(f"""
            QLineEdit {{
                background-color: {style.get("background_color", "#ffffff")};
                color: {style.get("text_color", "#333333")};
                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#cccccc")};
                border-radius: {style.get("border_radius", 4)}px;
                padding: 4px;
                font-size: {style.get("font_size", 12)}px;
            }}
        """)
        
        return inp
    
    @staticmethod
    def create_checkbox(data: Dict[str, Any], parent: QWidget) -> QCheckBox:
        chk = QCheckBox(data.get("text", ""), parent)
        chk.setGeometry(data["x"], data["y"], data["width"], data["height"])
        chk.setChecked(data.get("checked", False))
        
        style = data.get("style", {})
        chk.setStyleSheet(f"""
            QCheckBox {{
                color: {style.get("text_color", "#333333")};
                font-size: {style.get("font_size", 12)}px;
            }}
        """)
        
        return chk
    
    @staticmethod
    def create_combobox(data: Dict[str, Any], parent: QWidget) -> QComboBox:
        cbo = QComboBox(parent)
        cbo.setGeometry(data["x"], data["y"], data["width"], data["height"])
        cbo.addItems(data.get("items", []))
        cbo.setCurrentIndex(data.get("current_index", 0))
        
        style = data.get("style", {})
        cbo.setStyleSheet(f"""
            QComboBox {{
                background-color: {style.get("background_color", "#ffffff")};
                color: {style.get("text_color", "#333333")};
                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#cccccc")};
                border-radius: {style.get("border_radius", 4)}px;
                padding: 4px;
                font-size: {style.get("font_size", 12)}px;
            }}
        """)
        
        return cbo
    
    @staticmethod
    def create_progressbar(data: Dict[str, Any], parent: QWidget) -> QProgressBar:
        pbar = QProgressBar(parent)
        pbar.setGeometry(data["x"], data["y"], data["width"], data["height"])
        pbar.setValue(data.get("value", 0))
        pbar.setTextVisible(data.get("show_text", True))
        
        style = data.get("style", {})
        pbar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {style.get("background_color", "#e0e0e0")};
                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#999999")};
                border-radius: {style.get("border_radius", 4)}px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: #0078d7;
                border-radius: {style.get("border_radius", 4)}px;
            }}
        """)
        
        if data.get("auto_progress", False):
            duration = data.get("duration", 3)
            steps = 100
            interval = int(duration * 1000 / steps)
            
            def update_progress():
                if pbar.value() < 100:
                    pbar.setValue(pbar.value() + 1)
            
            timer = QTimer(pbar)
            timer.timeout.connect(update_progress)
            timer.start(interval)
        
        return pbar

class WindowManager:
    """窗口管理器。"""
    
    def __init__(self):
        self._windows: Dict[str, QMainWindow] = {}
        self._main_window_id = ""
    
    def register_window(self, window_id: str, window: QMainWindow):
        self._windows[window_id] = window
    
    def get_window(self, window_id: str) -> Optional[QMainWindow]:
        return self._windows.get(window_id)
    
    def close_all(self):
        for window in self._windows.values():
            window.close()
    
    def show_window(self, window_id: str):
        window = self.get_window(window_id)
        if window:
            window.show()
            window.raise_()
            window.activateWindow()

class 主界面(QMainWindow):
    """主界面窗口。"""
    
    def __init__(self, window_manager: WindowManager):
        super().__init__()
        self._window_manager = window_manager
        self.setWindowTitle("主界面")
        self.resize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self._components: Dict[str, QWidget] = {}
        self._create_components(central_widget)
    
    def _create_components(self, parent: QWidget):
        """创建组件。"""
        # 开始按钮
        self._components["btn001"] = ComponentFactory.create_button(
            {
                        "id": "btn001",
                        "type": "button",
                        "name": "开始按钮",
                        "x": 300,
                        "y": 200,
                        "width": 200,
                        "height": 50,
                        "text": "开始游戏",
                        "parent_id": "cont001",
                        "style": {
                                    "background_color": "#4CAF50",
                                    "text_color": "#ffffff",
                                    "border_color": "#45a049",
                                    "border_width": 1,
                                    "border_radius": 8,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 14,
                                    "font_bold": true
                        },
                        "action": {
                                    "action_type": "none",
                                    "params": {},
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "target_window_id": "event001",
                        "branch_name": "开始游戏",
                        "is_default": false,
                        "is_cancel": false
            },
            parent,
            self._window_manager
        )
        # 设置按钮
        self._components["btn002"] = ComponentFactory.create_button(
            {
                        "id": "btn002",
                        "type": "button",
                        "name": "设置按钮",
                        "x": 300,
                        "y": 280,
                        "width": 200,
                        "height": 50,
                        "text": "设置",
                        "parent_id": "cont001",
                        "style": {
                                    "background_color": "#2196F3",
                                    "text_color": "#ffffff",
                                    "border_color": "#1976D2",
                                    "border_width": 1,
                                    "border_radius": 8,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 14,
                                    "font_bold": true
                        },
                        "action": {
                                    "action_type": "none",
                                    "params": {},
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "target_window_id": "event002",
                        "branch_name": "设置",
                        "is_default": false,
                        "is_cancel": false
            },
            parent,
            self._window_manager
        )
        # 标题
        self._components["lbl001"] = ComponentFactory.create_label(
            {
                        "id": "lbl001",
                        "type": "label",
                        "name": "标题",
                        "x": 250,
                        "y": 130,
                        "width": 300,
                        "height": 40,
                        "text": "欢迎来到Galgame示例",
                        "parent_id": "cont001",
                        "style": {
                                    "background_color": "transparent",
                                    "text_color": "#333333",
                                    "border_color": "#999999",
                                    "border_width": 0,
                                    "border_radius": 0,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 18,
                                    "font_bold": true
                        },
                        "action": {
                                    "action_type": "none",
                                    "params": {},
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "alignment": "center",
                        "word_wrap": false
            },
            parent,
            self._window_manager
        )

class 开始游戏(QMainWindow):
    """开始游戏窗口。"""
    
    def __init__(self, window_manager: WindowManager):
        super().__init__()
        self._window_manager = window_manager
        self.setWindowTitle("开始游戏")
        self.resize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self._components: Dict[str, QWidget] = {}
        self._create_components(central_widget)
    
    def _create_components(self, parent: QWidget):
        """创建组件。"""
        # 游戏内容
        self._components["lbl002"] = ComponentFactory.create_label(
            {
                        "id": "lbl002",
                        "type": "label",
                        "name": "游戏内容",
                        "x": 200,
                        "y": 250,
                        "width": 400,
                        "height": 100,
                        "text": "这里是游戏内容区域\n点击返回按钮回到主菜单",
                        "parent_id": "",
                        "style": {
                                    "background_color": "transparent",
                                    "text_color": "#666666",
                                    "border_color": "#999999",
                                    "border_width": 0,
                                    "border_radius": 0,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 14,
                                    "font_bold": false
                        },
                        "action": {
                                    "action_type": "none",
                                    "params": {},
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "alignment": "center",
                        "word_wrap": true
            },
            parent,
            self._window_manager
        )
        # 返回按钮
        self._components["btn003"] = ComponentFactory.create_button(
            {
                        "id": "btn003",
                        "type": "button",
                        "name": "返回按钮",
                        "x": 300,
                        "y": 400,
                        "width": 200,
                        "height": 50,
                        "text": "返回主菜单",
                        "parent_id": "",
                        "style": {
                                    "background_color": "#f44336",
                                    "text_color": "#ffffff",
                                    "border_color": "#d32f2f",
                                    "border_width": 1,
                                    "border_radius": 8,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 14,
                                    "font_bold": true
                        },
                        "action": {
                                    "action_type": "close_window",
                                    "params": {},
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "target_window_id": "",
                        "branch_name": "",
                        "is_default": false,
                        "is_cancel": true
            },
            parent,
            self._window_manager
        )

class 设置(QMainWindow):
    """设置窗口。"""
    
    def __init__(self, window_manager: WindowManager):
        super().__init__()
        self._window_manager = window_manager
        self.setWindowTitle("设置")
        self.resize(600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self._components: Dict[str, QWidget] = {}
        self._create_components(central_widget)
    
    def _create_components(self, parent: QWidget):
        """创建组件。"""
        # 设置标题
        self._components["lbl003"] = ComponentFactory.create_label(
            {
                        "id": "lbl003",
                        "type": "label",
                        "name": "设置标题",
                        "x": 200,
                        "y": 80,
                        "width": 200,
                        "height": 30,
                        "text": "玩家名称:",
                        "parent_id": "",
                        "style": {
                                    "background_color": "transparent",
                                    "text_color": "#333333",
                                    "border_color": "#999999",
                                    "border_width": 0,
                                    "border_radius": 0,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 12,
                                    "font_bold": false
                        },
                        "action": {
                                    "action_type": "none",
                                    "params": {},
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "alignment": "right",
                        "word_wrap": false
            },
            parent,
            self._window_manager
        )
        # 玩家名称输入
        self._components["inp001"] = ComponentFactory.create_input(
            {
                        "id": "inp001",
                        "type": "input",
                        "name": "玩家名称输入",
                        "x": 200,
                        "y": 120,
                        "width": 200,
                        "height": 35,
                        "text": "",
                        "parent_id": "",
                        "style": {
                                    "background_color": "#ffffff",
                                    "text_color": "#333333",
                                    "border_color": "#cccccc",
                                    "border_width": 1,
                                    "border_radius": 4,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 12,
                                    "font_bold": false
                        },
                        "action": {
                                    "action_type": "none",
                                    "params": {},
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "placeholder": "请输入玩家名称",
                        "is_password": false,
                        "is_multiline": false,
                        "max_length": 20
            },
            parent,
            self._window_manager
        )
        # 保存设置
        self._components["btn004"] = ComponentFactory.create_button(
            {
                        "id": "btn004",
                        "type": "button",
                        "name": "保存设置",
                        "x": 200,
                        "y": 200,
                        "width": 200,
                        "height": 40,
                        "text": "保存并返回",
                        "parent_id": "",
                        "style": {
                                    "background_color": "#4CAF50",
                                    "text_color": "#ffffff",
                                    "border_color": "#45a049",
                                    "border_width": 1,
                                    "border_radius": 8,
                                    "font_family": "Microsoft YaHei",
                                    "font_size": 12,
                                    "font_bold": true
                        },
                        "action": {
                                    "action_type": "show_message",
                                    "params": {
                                                "param": "设置已保存!"
                                    },
                                    "blockly_xml": "",
                                    "python_code": ""
                        },
                        "visible": true,
                        "enabled": true,
                        "target_window_id": "",
                        "branch_name": "",
                        "is_default": true,
                        "is_cancel": false
            },
            parent,
            self._window_manager
        )

def get_project_data() -> Dict[str, Any]:
    """获取项目数据（用于导入回编辑器）。"""
    return {
        "name": "Galgame示例项目",
        "main_window_id": "main001",
        "current_window_id": "main001",
        "windows": [{"id": "main001", "name": "主界面", "window_type": "main", "width": 800, "height": 600, "components": ["cont001", "btn001", "btn002", "lbl001"]}, {"id": "event001", "name": "开始游戏", "window_type": "event", "width": 800, "height": 600, "components": ["lbl002", "btn003"]}, {"id": "event002", "name": "设置", "window_type": "event", "width": 600, "height": 400, "components": ["lbl003", "inp001", "btn004"]}],
        "components": [{"id": "cont001", "type": "container", "name": "主容器", "x": 150, "y": 100, "width": 500, "height": 400, "text": "游戏主菜单", "parent_id": "", "style": {"background_color": "#f5f5f5", "text_color": "#333333", "border_color": "#999999", "border_width": 1, "border_radius": 5, "font_family": "Microsoft YaHei", "font_size": 12, "font_bold": false}, "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true}, {"id": "btn001", "type": "button", "name": "开始按钮", "x": 300, "y": 200, "width": 200, "height": 50, "text": "开始游戏", "parent_id": "cont001", "style": {"background_color": "#4CAF50", "text_color": "#ffffff", "border_color": "#45a049", "border_width": 1, "border_radius": 8, "font_family": "Microsoft YaHei", "font_size": 14, "font_bold": true}, "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "target_window_id": "event001", "branch_name": "开始游戏", "is_default": false, "is_cancel": false}, {"id": "btn002", "type": "button", "name": "设置按钮", "x": 300, "y": 280, "width": 200, "height": 50, "text": "设置", "parent_id": "cont001", "style": {"background_color": "#2196F3", "text_color": "#ffffff", "border_color": "#1976D2", "border_width": 1, "border_radius": 8, "font_family": "Microsoft YaHei", "font_size": 14, "font_bold": true}, "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "target_window_id": "event002", "branch_name": "设置", "is_default": false, "is_cancel": false}, {"id": "lbl001", "type": "label", "name": "标题", "x": 250, "y": 130, "width": 300, "height": 40, "text": "欢迎来到Galgame示例", "parent_id": "cont001", "style": {"background_color": "transparent", "text_color": "#333333", "border_color": "#999999", "border_width": 0, "border_radius": 0, "font_family": "Microsoft YaHei", "font_size": 18, "font_bold": true}, "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "alignment": "center", "word_wrap": false}, {"id": "lbl002", "type": "label", "name": "游戏内容", "x": 200, "y": 250, "width": 400, "height": 100, "text": "这里是游戏内容区域\n点击返回按钮回到主菜单", "parent_id": "", "style": {"background_color": "transparent", "text_color": "#666666", "border_color": "#999999", "border_width": 0, "border_radius": 0, "font_family": "Microsoft YaHei", "font_size": 14, "font_bold": false}, "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "alignment": "center", "word_wrap": true}, {"id": "btn003", "type": "button", "name": "返回按钮", "x": 300, "y": 400, "width": 200, "height": 50, "text": "返回主菜单", "parent_id": "", "style": {"background_color": "#f44336", "text_color": "#ffffff", "border_color": "#d32f2f", "border_width": 1, "border_radius": 8, "font_family": "Microsoft YaHei", "font_size": 14, "font_bold": true}, "action": {"action_type": "close_window", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "target_window_id": "", "branch_name": "", "is_default": false, "is_cancel": true}, {"id": "lbl003", "type": "label", "name": "设置标题", "x": 200, "y": 80, "width": 200, "height": 30, "text": "玩家名称:", "parent_id": "", "style": {"background_color": "transparent", "text_color": "#333333", "border_color": "#999999", "border_width": 0, "border_radius": 0, "font_family": "Microsoft YaHei", "font_size": 12, "font_bold": false}, "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "alignment": "right", "word_wrap": false}, {"id": "inp001", "type": "input", "name": "玩家名称输入", "x": 200, "y": 120, "width": 200, "height": 35, "text": "", "parent_id": "", "style": {"background_color": "#ffffff", "text_color": "#333333", "border_color": "#cccccc", "border_width": 1, "border_radius": 4, "font_family": "Microsoft YaHei", "font_size": 12, "font_bold": false}, "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "placeholder": "请输入玩家名称", "is_password": false, "is_multiline": false, "max_length": 20}, {"id": "btn004", "type": "button", "name": "保存设置", "x": 200, "y": 200, "width": 200, "height": 40, "text": "保存并返回", "parent_id": "", "style": {"background_color": "#4CAF50", "text_color": "#ffffff", "border_color": "#45a049", "border_width": 1, "border_radius": 8, "font_family": "Microsoft YaHei", "font_size": 12, "font_bold": true}, "action": {"action_type": "show_message", "params": {"param": "设置已保存!"}, "blockly_xml": "", "python_code": ""}, "visible": true, "enabled": true, "target_window_id": "", "branch_name": "", "is_default": true, "is_cancel": false}],
    }

def main():
    """主函数。"""
    app = QApplication(sys.argv)
    
    window_manager = WindowManager()
    
    main001_window = 主界面(window_manager)
    window_manager.register_window("main001", main001_window)
    event001_window = 开始游戏(window_manager)
    window_manager.register_window("event001", event001_window)
    event002_window = 设置(window_manager)
    window_manager.register_window("event002", event002_window)
    
    window_manager._main_window_id = "main001"
    window_manager.show_window("{main_window_id}")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()