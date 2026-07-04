"""容器渲染器。

本模块包含容器组件的渲染逻辑。

"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont, QLinearGradient
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer

class ContainerRenderer(ComponentRenderer):
    """容器渲染器。
    
    负责绘制容器组件的外观（Windows 窗口样式）。
    
    """
    
    TITLE_BAR_HEIGHT = 28
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染容器组件。
        
        Args:
            painter: Qt 绘制器
            model: 容器数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 绘制标题栏背景（渐变）
        title_rect = QRectF(rect.x(), rect.y() - self.TITLE_BAR_HEIGHT, rect.width(), self.TITLE_BAR_HEIGHT)
        gradient = QLinearGradient(title_rect.topLeft(), title_rect.bottomLeft())
        gradient.setColorAt(0, QColor("#ffffff"))
        gradient.setColorAt(1, QColor("#e0e0e0"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#c0c0c0"), 1))
        painter.drawRect(title_rect)
        
        # 绘制标题栏文字
        painter.setPen(QColor("#333333"))
        font = QFont(style.font_family, style.font_size)
        font.setBold(True)
        painter.setFont(font)
        
        title = model.text if hasattr(model, 'text') else "窗口"
        title_text_rect = QRectF(title_rect.x() + 10, title_rect.y(), title_rect.width() - 20, title_rect.height())
        painter.drawText(title_text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
        
        # 绘制内容区域背景
        if style.background_color != "transparent":
            painter.setBrush(QBrush(QColor(style.background_color)))
        else:
            painter.setBrush(QBrush(QColor("#f5f5f5")))
        
        # 绘制边框
        if is_selected:
            pen = QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(style.border_color), style.border_width)
        painter.setPen(pen)
        
        painter.drawRect(rect)
