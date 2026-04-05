"""隐藏按钮渲染器。

本模块包含隐藏按钮组件的渲染逻辑。

隐藏按钮是透明但可点击的区域，用于创建热区。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer


class HiddenButtonRenderer(ComponentRenderer):
    """隐藏按钮渲染器。
    
    负责绘制隐藏按钮组件的外观。
    隐藏按钮在正常运行时完全透明，在设计模式下显示虚线边框。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染隐藏按钮组件。
        
        Args:
            painter: Qt 绘制器
            model: 隐藏按钮数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 隐藏按钮在设计模式下显示虚线边框
        # 在运行时完全透明
        
        # 绘制半透明背景（设计模式提示）
        brush = QBrush(QColor(0, 0, 0, 10))  # 几乎透明
        painter.setBrush(brush)
        
        # 绘制虚线边框
        if is_selected:
            pen = QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor("#CCCCCC"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        
        painter.drawRect(rect)
        
        # 绘制提示文字（设计模式）
        painter.setPen(QColor("#AAAAAA"))
        from PySide6.QtGui import QFont
        font = QFont("Arial", 8)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "[隐藏按钮]")
