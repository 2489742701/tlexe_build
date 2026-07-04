"""组件样式模块。

本模块定义所有组件相关的CSS样式，将样式从Python逻辑代码中分离出来，
便于维护和修改。

## 样式分类
1. 基础组件样式：按钮、标签、输入框等
2. 特殊组件样式：隐藏按钮、图片按钮、轮播组件等
3. 容器样式：容器、分组框等

## 使用方法
```python
from styles import ComponentStyles

# 应用隐藏按钮样式
button.setStyleSheet(ComponentStyles.HIDDEN_BUTTON)

# 应用容器样式
container.setStyleSheet(ComponentStyles.container_style("#f5f5f5"))
```
"""

from .theme import Colors, Fonts, Theme

class ComponentStyles:
    """组件样式定义类。
    
    提供所有组件的CSS样式字符串，支持动态参数替换。
    
    样式命名规则：
    - 大写常量：静态样式，直接使用
    - 小写方法：动态样式，需要传入参数
    
    Example:
        button.setStyleSheet(ComponentStyles.HIDDEN_BUTTON)
        container.setStyleSheet(ComponentStyles.container_style("#f5f5f5"))
    """
    
    # ============================================================
    # 隐藏按钮样式
    # ============================================================
    HIDDEN_BUTTON: str = """
        QPushButton {
            background-color: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: rgba(200, 200, 200, 0.1);
        }
    """
    
    # ============================================================
    # 容器样式
    # ============================================================
    @staticmethod
    def container_style(bg_color: str = None) -> str:
        """生成容器样式。
        
        Args:
            bg_color: 背景颜色，默认使用Colors.GRAY_100
            
        Returns:
            完整的容器CSS样式字符串
        """
        bg = bg_color or Colors.GRAY_100
        return f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 5px;
            }}
        """
    
    # ============================================================
    # 进度条样式
    # ============================================================
    PROGRESSBAR: str = """
        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 3px;
            background-color: #f0f0f0;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 2px;
        }
    """
    
    # ============================================================
    # 输入框样式
    # ============================================================
    @staticmethod
    def input_style(placeholder_color: str = None) -> str:
        """生成输入框样式。
        
        Args:
            placeholder_color: 占位符文本颜色
            
        Returns:
            完整的输入框CSS样式字符串
        """
        ph_color = placeholder_color or Colors.GRAY_400
        return f"""
            QLineEdit {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 3px;
                padding: 4px 8px;
                background-color: {Colors.BACKGROUND_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {Colors.PRIMARY};
            }}
            QLineEdit::placeholder {{
                color: {ph_color};
            }}
        """
    
    # ============================================================
    # 下拉框样式
    # ============================================================
    COMBOBOX: str = """
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 4px 8px;
            background-color: #ffffff;
        }
        QComboBox:focus {
            border-color: #1a56db;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            selection-background-color: #f0f4ff;
        }
    """
    
    # ============================================================
    # 复选框样式
    # ============================================================
    CHECKBOX: str = """
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #999999;
            border-radius: 3px;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            background-color: #4CAF50;
            border-color: #45a049;
        }
        QCheckBox::indicator:hover {
            border-color: #1a56db;
        }
    """
    
    # ============================================================
    # 分组框样式
    # ============================================================
    GROUPBOX: str = """
        QGroupBox {
            font-weight: bold;
            font-size: 12px;
            border: 1px solid #c0c0c0;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 8px;
            background-color: #fafafa;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #333333;
        }
    """

class StyleHelper:
    """样式辅助类。
    
    提供样式应用和字体处理的辅助方法。
    这个类保持向后兼容，原有的代码可以继续使用。
    """
    
    # 直接引用ComponentStyles中的常量
    GROUP_STYLE = ComponentStyles.GROUPBOX
    
    @staticmethod
    def generate_stylesheet(style_config) -> str:
        """根据样式配置生成样式表字符串。
        
        Args:
            style_config: StyleConfig 对象，包含样式配置
            
        Returns:
            生成的CSS样式字符串
        """
        if not style_config:
            return ""
        
        parts = []
        
        if style_config.background_color and style_config.background_color != "transparent":
            parts.append(f"background-color: {style_config.background_color};")
        
        if style_config.text_color:
            parts.append(f"color: {style_config.text_color};")
        
        if style_config.border_color:
            border_width = style_config.border_width or 1
            parts.append(f"border: {border_width}px solid {style_config.border_color};")
        
        if style_config.border_radius:
            parts.append(f"border-radius: {style_config.border_radius}px;")
        
        if style_config.font_family:
            parts.append(f"font-family: '{style_config.font_family}';")
        
        if style_config.font_size:
            parts.append(f"font-size: {style_config.font_size}px;")
        
        if style_config.font_bold:
            parts.append("font-weight: bold;")
        
        return " ".join(parts)
    
    @staticmethod
    def apply_style(widget, style_config) -> None:
        """应用样式到控件。
        
        Args:
            widget: Qt控件对象
            style_config: StyleConfig 对象或样式字符串
        """
        if not widget or not style_config:
            return
        
        try:
            if isinstance(style_config, str):
                stylesheet = style_config
            else:
                stylesheet = StyleHelper.generate_stylesheet(style_config)
            
            if stylesheet:
                widget.setStyleSheet(stylesheet)
        except Exception:
            pass
    
    @staticmethod
    def get_font(style_config) -> 'QFont':
        """根据样式配置获取字体对象。
        
        Args:
            style_config: StyleConfig 对象
            
        Returns:
            QFont 字体对象
        """
        from PySide6.QtGui import QFont
        
        font = QFont(Theme.get_font_family())
        
        if style_config.font_size:
            font.setPointSize(style_config.font_size)
        
        if style_config.font_bold:
            font.setBold(True)
        
        return font
    
    @staticmethod
    def is_native_style(style_config) -> bool:
        """检查是否使用原生样式（无自定义样式）。
        
        Args:
            style_config: StyleConfig 对象
            
        Returns:
            是否使用原生样式
        """
        if not style_config:
            return True
        
        native_indicators = [
            style_config.background_color in [None, "transparent", ""],
            style_config.border_color in [None, "", "#cccccc"],
            not style_config.border_width or style_config.border_width <= 1,
        ]
        
        return all(native_indicators)