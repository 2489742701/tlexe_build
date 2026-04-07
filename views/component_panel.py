"""组件面板模块。

本模块包含组件面板的实现，提供分类的组件选择功能。
支持功能类、媒体类、容器类、输入类等组件分类。

## 更新说明 (2026-04-07)
【改进】使用黑白SVG图标替换文本图标，提升视觉效果
- 导入 IconManager 管理图标资源
- ComponentButton 使用真实图标而非文本符号
- 支持SVG和Unicode两种图标格式
"""

from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon

from utils.icon_manager import IconManager


COMPONENT_CATEGORIES: Dict[str, Dict[str, str]] = {
    "技术类": {
        "lottery": "抽奖系统",
        "login": "登录表单",
        "form": "表单组",
        "progress_panel": "进度面板",
    },
    "功能类": {
        "button": "按钮",
        "checkbox": "复选框",
        "combobox": "下拉框",
        "progressbar": "进度条",
        "hidden_button": "隐藏按钮",
        "image_button": "图片按钮",
    },
    "媒体类": {
        "image": "图片",
        "video": "视频",
        "image_carousel": "图片轮播",
    },
    "容器类": {
        "container": "容器",
        "group_node": "组节点",
    },
    "输入类": {
        "input": "输入框",
    },
    "显示类": {
        "label": "文本标签",
    },
}

COMPONENT_ICONS: Dict[str, str] = {
    "button": "[B]",
    "checkbox": "[x]",
    "combobox": "[v]",
    "progressbar": "[%]",
    "hidden_button": "[H]",
    "image_button": "[IB]",
    "image": "[IMG]",
    "video": "[VID]",
    "image_carousel": "[SLD]",
    "container": "[C]",
    "input": "[I]",
    "label": "[T]",
}


class ComponentButton(QPushButton):
    """组件按钮。
    
    用于在组件面板中显示单个组件选项。
    使用黑白SVG图标提升视觉效果。
    """
    
    def __init__(self, comp_type: str, display_name: str, parent=None):
        super().__init__(parent)
        self._comp_type = comp_type
        self._display_name = display_name
        
        icon = IconManager.get_icon(comp_type, use_svg=True)
        self.setIcon(icon)
        self.setIconSize(QSize(20, 20))
        self.setText(display_name)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8f4fc;
                border-color: #4a90d9;
            }
            QPushButton:pressed {
                background-color: #d0e8f8;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)


class CategorySection(QWidget):
    """分类区块。
    
    用于显示一个组件分类下的所有组件。
    """
    
    component_clicked = Signal(str)
    
    def __init__(self, category_name: str, components: Dict[str, str], parent=None):
        super().__init__(parent)
        self._category_name = category_name
        self._components = components
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)
        
        title_label = QLabel(f"📁 {self._category_name}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 4px 0px;
            }
        """)
        layout.addWidget(title_label)
        
        for comp_type, display_name in self._components.items():
            btn = ComponentButton(comp_type, display_name)
            btn.clicked.connect(lambda checked, t=comp_type: self.component_clicked.emit(t))
            layout.addWidget(btn)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)


class ComponentPanel(QWidget):
    """组件面板。
    
    提供分类的组件选择界面，用户可以点击组件按钮来添加组件。
    
    Signals:
        component_selected: 组件被选中时发射 (comp_type)
    """
    
    component_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """初始化UI。
        
        【布局说明】
        - 顶部：标题栏（可拖动）
        - 中间：组件列表（可滚动）
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = QLabel("组件面板")
        header.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #555;
                padding: 6px 10px;
                background-color: #fff;
                border-bottom: 1px solid #eee;
            }
        """)
        main_layout.addWidget(header)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #fff; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #fff;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(12)
        
        for category_name, components in COMPONENT_CATEGORIES.items():
            section = CategorySection(category_name, components)
            section.component_clicked.connect(self.component_selected.emit)
            content_layout.addWidget(section)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)
    
    def get_all_component_types(self) -> List[str]:
        """获取所有组件类型列表。"""
        types = []
        for components in COMPONENT_CATEGORIES.values():
            types.extend(components.keys())
        return types
