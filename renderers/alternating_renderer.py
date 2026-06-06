"""交替变换渲染器。

根据 model 的 display_mode 属性分派文字/图片模式渲染。
文字大字模式（28号粗体居中）或图片轮播模式（KeepAspectRatioByExpanding）。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPixmap, QFont
from PySide6.QtCore import QRectF, Qt, QPointF

from models import ComponentModel
from .component_renderer import ComponentRenderer


class AlternatingRenderer(ComponentRenderer):
    """交替变换渲染器（文字/图片通用）。"""

    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        style = self._get_style(model)
        if not style:
            return

        display_mode = getattr(model, 'display_mode', 'text')
        items = getattr(model, 'items', [])
        item_labels = getattr(model, 'item_labels', [])
        current_index = getattr(model, 'current_index', 0)
        placeholder = "文字交替变换" if display_mode == 'text' else "图片交替变换"

        if display_mode == 'text':
            self._render_text(painter, items, item_labels, current_index, rect, placeholder)
        else:
            self._render_image(painter, items, item_labels, current_index, rect, placeholder)

        self._draw_indicators(painter, rect, len(items), current_index)

        if is_selected:
            painter.setPen(QPen(QColor("#2196F3"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
            painter.drawRoundedRect(rect, 5, 5)

    def _render_text(self, painter, items, item_labels, current_index, rect, placeholder):
        if items and 0 <= current_index < len(items):
            text = item_labels[current_index] if current_index < len(item_labels) else str(items[current_index])
            font = QFont("Microsoft YaHei", 28, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor("#333333")))
            text_rect = QRectF(rect.x() + 10, rect.y() + 10, rect.width() - 20, rect.height() - 30)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
        else:
            self._draw_placeholder(painter, rect, placeholder)

    def _render_image(self, painter, items, item_labels, current_index, rect, placeholder):
        if items and 0 <= current_index < len(items):
            pixmap = QPixmap(items[current_index])
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    int(rect.width()), int(rect.height()),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                x = rect.x() + (rect.width() - scaled.width()) / 2
                y = rect.y() + (rect.height() - scaled.height()) / 2
                painter.drawPixmap(int(x), int(y), scaled)
            else:
                label = item_labels[current_index] if current_index < len(item_labels) else str(items[current_index])
                self._draw_placeholder(painter, rect, label)
        else:
            self._draw_placeholder(painter, rect, placeholder)

    def _draw_placeholder(self, painter, rect, text):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#e0e0e0")))
        painter.drawRoundedRect(rect, 5, 5)
        painter.setPen(QPen(QColor("#999999")))
        painter.setFont(QFont("Microsoft YaHei", 12))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_indicators(self, painter, rect, total, current):
        if total <= 1:
            return
        dot_size, spacing = 6, 4
        total_w = total * dot_size + (total - 1) * spacing
        start_x = rect.x() + (rect.width() - total_w) / 2
        y = rect.y() + rect.height() - dot_size - 4
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(total):
            x = start_x + i * (dot_size + spacing)
            painter.setBrush(QBrush(QColor("#2196F3") if i == current else QColor("#cccccc")))
            painter.drawEllipse(QPointF(x + dot_size / 2, y + dot_size / 2), dot_size / 2, dot_size / 2)
