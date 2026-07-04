"""组节点渲染器。

本模块包含组节点组件的渲染逻辑。
组节点是逻辑分组容器，在设计模式下显示虚线边框。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer

class GroupNodeRenderer(ComponentRenderer):
    """组节点渲染器。

    负责绘制组节点组件的外观。
    组节点在设计模式下显示虚线边框和标题，运行时可选显示。
    """

    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染组节点组件。

        Args:
            painter: Qt 绘制器
            model: 组节点数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        show_border = getattr(model, 'show_border', True)
        border_style = getattr(model, 'border_style', 'dashed')

        if show_border:
            brush = QBrush(QColor(0, 0, 0, 5))
            painter.setBrush(brush)

            pen_style = {
                'solid': Qt.PenStyle.SolidLine,
                'dashed': Qt.PenStyle.DashLine,
                'dotted': Qt.PenStyle.DotLine,
                'none': Qt.PenStyle.NoPen,
            }.get(border_style, Qt.PenStyle.DashLine)

            if is_selected:
                pen = QPen(QColor("#87CEEB"), 2, pen_style)
            else:
                pen = QPen(QColor("#999999"), 1, pen_style)
            painter.setPen(pen)

            border_radius = getattr(model.style, 'border_radius', 5)
            painter.drawRoundedRect(rect, border_radius, border_radius)

        name = getattr(model, 'name', '') or getattr(model, 'text', '')
        if name:
            painter.setPen(QColor("#888888"))
            font = QFont("Arial", 8)
            painter.setFont(font)
            margin = 4
            name_rect = QRectF(rect.x() + margin, rect.y() + margin, rect.width() - margin * 2, 16)
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, name)
