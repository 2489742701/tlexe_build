"""下拉框渲染器。

本模块包含下拉框组件的渲染逻辑。

"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import QRectF, Qt, QPointF

from models import ComponentModel
from .component_renderer import ComponentRenderer

class ComboBoxRenderer(ComponentRenderer):
    """下拉框渲染器。
    
    负责绘制下拉框组件的外观。
    
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染下拉框组件。
        
        Args:
            painter: Qt 绘制器
            model: 下拉框数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self._get_style(model)
        if not style:
            return
        
        # 绘制背景
        if style.background_color != "transparent":
            brush = QBrush(QColor(style.background_color))
            painter.setBrush(brush)
        else:
            painter.setBrush(QBrush(QColor("#ffffff")))
        
        # 绘制边框
        pen_width = style.border_width
        if is_selected:
            pen = QPen(QColor("#87CEEB"), pen_width + 1, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(style.border_color), pen_width)
        painter.setPen(pen)
        
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 获取显示文本
        items = getattr(model, 'items', [])
        current_index = getattr(model, 'current_index', 0)
        
        if items and 0 <= current_index < len(items):
            display_text = str(items[current_index])
        else:
            display_text = model.text if hasattr(model, 'text') and model.text else "选择..."
        
        # 绘制文字
        painter.setPen(QColor(style.text_color))
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        painter.setFont(font)
        
        margin = 8
        arrow_width = 24
        text_rect = QRectF(margin, 0, rect.width() - arrow_width - margin * 2, rect.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_text)
        
        # 绘制下拉箭头
        arrow_x = rect.width() - arrow_width
        painter.setPen(QPen(QColor("#666666"), 2))
        arrow_center_y = rect.height() / 2
        arrow_margin = 8
        painter.drawLine(
            QPointF(arrow_x + arrow_margin, arrow_center_y - 3),
            QPointF(arrow_x + arrow_width / 2, arrow_center_y + 3)
        )
        painter.drawLine(
            QPointF(arrow_x + arrow_width - arrow_margin, arrow_center_y - 3),
            QPointF(arrow_x + arrow_width / 2, arrow_center_y + 3)
        )
        
        # 绘制分隔线
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(arrow_x, 4), QPointF(arrow_x, rect.height() - 4))
