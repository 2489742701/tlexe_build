"""复选框渲染器。

本模块包含复选框组件的渲染逻辑。

"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import QRectF, Qt, QPointF

from models import ComponentModel
from .component_renderer import ComponentRenderer

class CheckBoxRenderer(ComponentRenderer):
    """复选框渲染器。
    
    负责绘制复选框组件的外观。
    
    """
    
    CHECK_SIZE = 18
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染复选框组件。
        
        Args:
            painter: Qt 绘制器
            model: 复选框数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self._get_style(model)
        if not style:
            return
        
        # 计算复选框位置
        check_x = 5
        check_y = (rect.height() - self.CHECK_SIZE) / 2
        
        # 绘制复选框背景
        painter.setBrush(QBrush(QColor("#ffffff")))
        if is_selected:
            painter.setPen(QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine))
        else:
            painter.setPen(QPen(QColor("#666666"), 1))
        
        painter.drawRect(QRectF(check_x, check_y, self.CHECK_SIZE, self.CHECK_SIZE))
        
        # 绘制勾选标记
        is_checked = getattr(model, 'checked', False)
        if is_checked:
            painter.setPen(QPen(QColor("#0078d7"), 2))
            check_margin = 4
            painter.drawLine(
                QPointF(check_x + check_margin, check_y + self.CHECK_SIZE / 2),
                QPointF(check_x + self.CHECK_SIZE / 2, check_y + self.CHECK_SIZE - check_margin)
            )
            painter.drawLine(
                QPointF(check_x + self.CHECK_SIZE / 2, check_y + self.CHECK_SIZE - check_margin),
                QPointF(check_x + self.CHECK_SIZE - check_margin, check_y + check_margin)
            )
        
        # 绘制文字
        display_text = model.text if hasattr(model, 'text') and model.text else "复选框"
        painter.setPen(QColor(style.text_color))
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        painter.setFont(font)
        
        text_x = check_x + self.CHECK_SIZE + 8
        text_rect = QRectF(text_x, 0, rect.width() - text_x - 5, rect.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_text)
