"""抽奖组件渲染器。

本模块包含抽奖组件的渲染逻辑。
根据 display_mode 分派图片模式或文字大字模式渲染。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPixmap, QFont, QPainterPath
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer


class LotteryRenderer(ComponentRenderer):
    """抽奖组件渲染器。
    
    根据 display_mode 分派：
    - image: 图片轮播模式
    - text: 文字大字模式
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        style = self.get_style(model)
        if not style:
            return
        
        display_mode = getattr(model, 'display_mode', 'image')
        
        if display_mode == 'text':
            self._render_text_mode(painter, model, rect)
        else:
            self._render_image_mode(painter, model, rect)
        
        self._draw_indicators(painter, rect, len(model.items) if hasattr(model, 'items') else 0,
                             model.current_index if hasattr(model, 'current_index') else 0)
        
        if is_selected:
            painter.setPen(QPen(QColor("#4CAF50"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
            painter.drawRect(rect)
    
    def _render_image_mode(self, painter: QPainter, model, rect: QRectF):
        items = getattr(model, 'items', [])
        current_index = getattr(model, 'current_index', 0)
        
        if items and 0 <= current_index < len(items):
            image_path = items[current_index]
            pixmap = QPixmap(image_path)
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
                label = ""
                item_labels = getattr(model, 'item_labels', [])
                if current_index < len(item_labels):
                    label = item_labels[current_index]
                self._draw_placeholder(painter, rect, label or image_path)
        else:
            self._draw_placeholder(painter, rect, "抽奖（图片模式）")
    
    def _render_text_mode(self, painter: QPainter, model, rect: QRectF):
        items = getattr(model, 'items', [])
        item_labels = getattr(model, 'item_labels', [])
        current_index = getattr(model, 'current_index', 0)
        
        if items and 0 <= current_index < len(items):
            text = item_labels[current_index] if current_index < len(item_labels) else str(items[current_index])
            
            font = QFont("Microsoft YaHei", 28, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor("#333333")))
            
            text_rect = QRectF(rect.x() + 10, rect.y() + 10, rect.width() - 20, rect.height() - 30)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
        else:
            self._draw_placeholder(painter, rect, "抽奖（文字模式）")
    
    def _draw_placeholder(self, painter: QPainter, rect: QRectF, text: str):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#e0e0e0")))
        painter.drawRoundedRect(rect, 5, 5)
        
        painter.setPen(QPen(QColor("#999999")))
        font = QFont("Microsoft YaHei", 12)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def _draw_indicators(self, painter: QPainter, rect: QRectF, total: int, current: int):
        if total <= 1:
            return
        
        indicator_size = 6
        spacing = 4
        total_width = total * indicator_size + (total - 1) * spacing
        start_x = rect.x() + (rect.width() - total_width) / 2
        y = rect.y() + rect.height() - indicator_size - 4
        
        for i in range(total):
            x = start_x + i * (indicator_size + spacing)
            if i == current:
                painter.setBrush(QBrush(QColor("#4CAF50")))
            else:
                painter.setBrush(QBrush(QColor("#cccccc")))
            painter.setPen(Qt.PenStyle.NoPen)
            from PySide6.QtCore import QPointF
            painter.drawEllipse(QPointF(x + indicator_size / 2, y + indicator_size / 2),
                              indicator_size / 2, indicator_size / 2)
