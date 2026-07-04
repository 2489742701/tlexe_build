"""面板样式模块。

本模块定义所有面板相关的CSS样式，包括：
1. 属性面板样式
2. 组件面板样式
3. 欢迎页样式

## 使用方法
```python
from styles import PropertyPanelStyles

# 应用分组框样式
group.setStyleSheet(PropertyPanelStyles.GROUP_STYLE)

# 应用标题头部样式
frame.setStyleSheet(PropertyPanelStyles.TITLE_FRAME)
```
"""

from .theme import Colors, Fonts, Theme

class PropertyPanelStyles:
    """属性面板样式定义类。
    
    提供属性面板中所有UI元素的CSS样式。
    
    样式分类：
    - 容器样式：滚动区域、内容区域
    - 标题样式：组件名称、类型标签
    - 表单样式：标签、输入框、按钮
    - 分组样式：属性分组框
    
    Example:
        group.setStyleSheet(PropertyPanelStyles.GROUP_STYLE)
        title_label.setStyleSheet(PropertyPanelStyles.TITLE_LABEL)
    """
    
    # ============================================================
    # 分组框样式（重要！不要随意修改）
    #
    # 【分组框样式规范】
    # - font-size: 13px: 标题字号，适中大小
    # - border: 1px solid #e0e0e0: 淡灰色边框，不突兀
    # - border-radius: 10px: 圆角，现代感
    # - margin-top: 20px: 标题区域高度，给标题留出空间
    # - padding: 20px 14px 14px 14px: 内边距，上20px左右14px下14px
    # - background-color: #f8f9fa: 淡灰色背景，区分内容区域
    #
    # 【注意事项】
    # - margin-top 必须足够大以容纳标题
    # - padding 上边距要大于其他边距，避免内容紧贴标题
    # - 背景色要比滚动区域背景稍深，形成层次感
    # ============================================================
    GROUP_STYLE: str = """
        QGroupBox {
            font-weight: bold;
            font-size: 13px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            margin-top: 20px;
            padding: 16px 10px 10px 10px;
            background-color: #f8f9fa;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 10px;
            color: #444444;
        }
        QGroupBox > QWidget {
            /* 确保子控件不被压缩 */
            margin: 0;
        }
    """
    
    # ============================================================
    # 滚动区域样式（重要！不要随意修改）
    #
    # 【滚动条样式规范】
    # - QScrollArea: 无边框，白色背景
    # - QScrollBar:vertical: 淡灰色背景(#f0f0f0)，宽度10px
    # - QScrollBar::handle: 灰色滑块(#c0c0c0)，圆角5px，最小高度20px
    # - QScrollBar::handle:hover: 悬停时颜色加深(#a0a0a0)
    # - QScrollBar::add-line/sub-line: 高度0px，隐藏上下箭头
    #
    # 【注意事项】
    # - width: 10px 是合适的滚动条宽度，太小不易操作，太大占用空间
    # - border-radius: 5px 让滚动条更美观
    # - 隐藏箭头可以节省空间，现代UI通常不需要箭头
    # ============================================================
    SCROLL_AREA: str = """
        QScrollArea {
            border: none;
            background-color: #ffffff;
        }
        QScrollBar:vertical {
            border: none;
            background-color: #f0f0f0;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #c0c0c0;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #a0a0a0;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """
    
    # ============================================================
    # 标题头部样式（重要！不要随意修改）
    #
    # 【标题头部样式规范】
    # - background-color: #f1f6fc: 淡蓝色背景，突出显示
    # - border: 1px solid #d8e4ff: 淡蓝色边框，与背景协调
    # - border-radius: 12px: 较大圆角，柔和感
    # - padding: 12px 16px: 内边距，上下12px左右16px
    #
    # 【标题标签规范】
    # - font-size: 18px: 较大字号，醒目
    # - font-weight: bold: 粗体
    # - color: #2563eb: 蓝色，与背景协调
    # ============================================================
    TITLE_FRAME: str = """
        QFrame {
            background-color: #f1f6fc;
            border: 1px solid #d8e4ff;
            border-radius: 12px;
            padding: 12px 16px;
        }
    """
    
    TITLE_LABEL: str = """
        font-size: 18px;
        font-weight: bold;
        color: #2563eb;
    """
    
    HELP_BUTTON: str = """
        QPushButton {
            background-color: #e0e7ff;
            color: #4f6df5;
            border: 1px solid #b8caff;
            border-radius: 11px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d0deff;
            border-color: #8faaff;
        }
    """
    
    TYPE_BADGE: str = """
        font-size: 10px;
        color: #888888;
        background-color: transparent;
        padding: 2px 8px;
        border: 1px solid #dddddd;
        border-radius: 10px;
    """
    
    # ============================================================
    # 标签样式
    # ============================================================
    LABEL_SECONDARY: str = "color: #666666;"
    LABEL_MONOSPACE: str = "color: #666; font-family: monospace;"
    LABEL_HINT: str = "color: #555;"
    LABEL_INFO: str = "color: #888; font-size: 11px;"
    
    # ============================================================
    # 输入框样式
    # ============================================================
    SPINBOX: str = """
        QSpinBox {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 2px 4px;
            background-color: #ffffff;
        }
        QSpinBox:focus {
            border-color: #1a56db;
        }
    """
    
    COMBOBOX: str = """
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 2px 4px;
            background-color: #ffffff;
        }
        QComboBox:focus {
            border-color: #1a56db;
        }
    """
    
    # ============================================================
    # 按钮样式
    # ============================================================
    BUTTON_PRIMARY: str = """
        QPushButton {
            background-color: #4CAF50;
            color: #ffffff;
            border: 1px solid #45a049;
            border-radius: 5px;
            padding: 4px 12px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """
    
    BUTTON_SECONDARY: str = """
        QPushButton {
            background-color: #f0f0f0;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 4px 12px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
    """
    
    # ============================================================
    # 颜色选择器样式
    # ============================================================
    @staticmethod
    def color_button(color: str) -> str:
        """生成颜色选择按钮样式。
        
        Args:
            color: 颜色值（十六进制）
            
        Returns:
            完整的按钮CSS样式字符串
        """
        return f"background-color: {color}; border: 1px solid #999; border-radius: 3px;"

class ComponentPanelStyles:
    """组件面板样式定义类。
    
    提供组件面板（左侧添加组件列表）的CSS样式。
    
    Example:
        category_label.setStyleSheet(ComponentPanelStyles.CATEGORY_LABEL)
        item_button.setStyleSheet(ComponentPanelStyles.ITEM_BUTTON)
    """
    
    # 分类标题样式
    CATEGORY_LABEL: str = """
        font-weight: bold;
        font-size: 12px;
        color: #555555;
        padding: 5px;
        background-color: transparent;
    """
    
    # 组件项按钮样式
    ITEM_BUTTON: str = """
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 8px;
            text-align: left;
            color: #333333;
        }
        QPushButton:hover {
            background-color: #f5f5f5;
            border-color: #c0c0c0;
        }
        QPushButton:pressed {
            background-color: #e8e8e8;
        }
    """
    
    # 组件图标样式
    ITEM_ICON: str = """
        font-size: 16px;
    """

class WelcomePageStyles:
    """欢迎页样式定义类。
    
    提供欢迎页的CSS样式。
    """
    
    # 标题样式
    TITLE_LABEL: str = """
        font-size: 24px;
        font-weight: bold;
        color: #333333;
    """
    
    # 示例卡片样式
    EXAMPLE_CARD: str = """
        QFrame {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        QFrame:hover {
            border-color: #1a56db;
            background-color: #f8faff;
        }
    """
    
    # 示例标题样式
    EXAMPLE_TITLE: str = """
        font-size: 14px;
        font-weight: bold;
        color: #333333;
    """
    
    # 示例描述样式
    EXAMPLE_DESC: str = """
        font-size: 11px;
        color: #666666;
    """