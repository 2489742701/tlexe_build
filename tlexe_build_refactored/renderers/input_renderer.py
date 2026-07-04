"""输入框渲染器。

本模块包含输入框组件的渲染逻辑。

"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer

class InputRenderer(ComponentRenderer):
    """输入框渲染器。
    
    负责绘制输入框组件的外观。
    
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染输入框组件。
        
        Args:
            painter: Qt 绘制器
            model: 输入框数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self._get_style(model)
        if not style:
            return
        
        # 绘制背景
        painter.setBrush(QBrush(QColor("#ffffff")))
        
        # 绘制边框
        if is_selected:
            pen = QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(style.border_color), style.border_width)
        painter.setPen(pen)
        
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 绘制文字或占位符
        painter.setPen(QColor(style.text_color))
        font = QFont(style.font_family, style.font_size)
        painter.setFont(font)
        
        # 获取文本内容
        text = ""
        if hasattr(model, 'text') and model.text:
            text = model.text
        elif hasattr(model, 'placeholder') and model.placeholder:
            text = model.placeholder
            painter.setPen(QColor("#999999"))  # 占位符使用灰色
        
        # 留出边距
        margin = 8
        text_rect = QRectF(rect.x() + margin, rect.y(), rect.width() - margin * 2, rect.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
