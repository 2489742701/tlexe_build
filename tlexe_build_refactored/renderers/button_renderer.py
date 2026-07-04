"""按钮渲染器。

本模块包含按钮组件的渲染逻辑。

"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer

class ButtonRenderer(ComponentRenderer):
    """按钮渲染器。
    
    负责绘制按钮组件的外观。
    
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染按钮组件。
        
        Args:
            painter: Qt 绘制器
            model: 按钮数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 绘制背景
        if style.background_color != "transparent":
            brush = QBrush(QColor(style.background_color))
            painter.setBrush(brush)
        else:
            painter.setBrush(QBrush(QColor("#f0f0f0")))
        
        # 绘制边框
        pen_width = style.border_width
        if is_selected:
            pen = QPen(QColor("#87CEEB"), pen_width + 1, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(style.border_color), pen_width)
        painter.setPen(pen)
        
        # 绘制圆角矩形
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 绘制文字
        painter.setPen(QColor(style.text_color))
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        painter.setFont(font)
        
        text = model.text if hasattr(model, 'text') else "按钮"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
