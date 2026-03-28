"""画布视图模块。

本模块包含设计器画布和组件图形项的实现。
支持桌面模拟、Alt+滚轮缩放、黑框边界等功能。

主要功能：
- 组件图形项的显示和交互
- 拖拽移动、选中高亮、大小调整
- 多选操作和撤销支持
- 桌面模拟和缩放功能
"""

from typing import Optional
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsObject, 
    QGraphicsRectItem, QGraphicsItem
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QBrush, QColor, QPen, QFont, QPainter

from models import ComponentModel
from utils.settings import app_settings


DEFAULT_DESKTOP_WIDTH = 1280
DEFAULT_DESKTOP_HEIGHT = 720


class ComponentGraphicsItem(QGraphicsObject):
    """画布上的组件图形项。
    
    支持拖拽移动、选中高亮、大小调整等功能。
    
    Signals:
        moved: 组件移动时发射 (id, new_x, new_y)
        selected: 组件被选中时发射 (id)
        resized: 组件大小改变时发射 (id, new_width, new_height)
        parent_changed: 父容器改变时发射 (id, new_parent_id)
    """
    
    moved = Signal(str, int, int)
    selected = Signal(str)
    resized = Signal(dict)
    parent_changed = Signal(str, str)
    multi_move_finished = Signal(dict)
    
    MIN_SIZE = 20
    TITLE_BAR_HEIGHT = 28
    DRAG_THRESHOLD = 3
    
    def __init__(self, model: ComponentModel, parent: Optional[QGraphicsItem] = None):
        super().__init__(parent)
        self._model = model
        self._model.data_changed.connect(self._on_model_changed)
        
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        
        self.setPos(QPointF(model.x, model.y))
        
        self._resizing = False
        self._resize_handle = -1
        self._resize_start_pos = QPointF()
        self._resize_start_rect = QRectF()
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._resize_old_width = 0
        self._resize_old_height = 0
        self._resize_old_x = 0
        self._resize_old_y = 0
        self._dragging = False
        self._drag_start_pos = QPointF()
        self._selected_items_start_pos = {}
        self._has_actually_moved = False
    
    @property
    def component_id(self) -> str:
        return self._model.id
    
    @property
    def model(self) -> ComponentModel:
        return self._model
    
    TITLE_BAR_HEIGHT = 28
    
    def boundingRect(self) -> QRectF:
        rect = QRectF(0, 0, self._model.width, self._model.height)
        
        if self._model.type == "container":
            rect = QRectF(0, -self.TITLE_BAR_HEIGHT, self._model.width, self._model.height + self.TITLE_BAR_HEIGHT)
        
        if self.isSelected():
            handle_size = app_settings.handle_size
            tolerance = app_settings.handle_click_tolerance
            margin = (handle_size + tolerance) / 2
            rect = rect.adjusted(-margin, -margin, margin, margin)
        
        return rect
    
    def shape(self):
        from PySide6.QtGui import QPainterPath
        
        handle_size = app_settings.handle_size
        
        path = QPainterPath()
        
        if self._model.type == "container":
            path.addRect(0, -self.TITLE_BAR_HEIGHT, self._model.width, self._model.height + self.TITLE_BAR_HEIGHT)
        else:
            path.addRect(0, 0, self._model.width, self._model.height)
        
        if self.isSelected():
            if self._model.type == "container":
                handles = [
                    QPointF(0, -self.TITLE_BAR_HEIGHT),
                    QPointF(self._model.width / 2, -self.TITLE_BAR_HEIGHT),
                    QPointF(self._model.width, -self.TITLE_BAR_HEIGHT),
                    QPointF(self._model.width, self._model.height / 2 - self.TITLE_BAR_HEIGHT / 2),
                    QPointF(self._model.width, self._model.height),
                    QPointF(self._model.width / 2, self._model.height),
                    QPointF(0, self._model.height),
                    QPointF(0, self._model.height / 2 - self.TITLE_BAR_HEIGHT / 2),
                ]
            else:
                handles = [
                    QPointF(0, 0),
                    QPointF(self._model.width / 2, 0),
                    QPointF(self._model.width, 0),
                    QPointF(self._model.width, self._model.height / 2),
                    QPointF(self._model.width, self._model.height),
                    QPointF(self._model.width / 2, self._model.height),
                    QPointF(0, self._model.height),
                    QPointF(0, self._model.height / 2),
                ]
            
            click_area = max(24, handle_size + app_settings.handle_click_tolerance)
            
            for handle_pos in handles:
                handle_rect = QRectF(
                    handle_pos.x() - click_area / 2,
                    handle_pos.y() - click_area / 2,
                    click_area,
                    click_area
                )
                path.addRect(handle_rect)
        
        return path
    
    def _on_model_changed(self):
        if self.pos().x() != self._model.x or self.pos().y() != self._model.y:
            self.setPos(QPointF(self._model.x, self._model.y))
        self.update()
    
    def paint(self, painter: QPainter, option, widget):
        rect = QRectF(0, 0, self._model.width, self._model.height)
        style = self._model.style
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        comp_type = self._model.type
        
        if comp_type == "container":
            self._paint_container(painter, rect, style)
        elif comp_type == "progressbar":
            self._paint_progressbar(painter, rect, style)
        elif comp_type == "combobox":
            self._paint_combobox(painter, rect, style)
        elif comp_type == "checkbox":
            self._paint_checkbox(painter, rect, style)
        else:
            self._paint_component(painter, rect, style)
        
        if self.isSelected():
            if comp_type == "container":
                selection_rect = QRectF(0, -self.TITLE_BAR_HEIGHT, self._model.width, self._model.height + self.TITLE_BAR_HEIGHT)
            else:
                selection_rect = rect
            self._draw_resize_handles(painter, selection_rect)
    
    def _paint_combobox(self, painter: QPainter, rect: QRectF, style):
        """绘制下拉框组件。"""
        if style.background_color != "transparent":
            brush = QBrush(QColor(style.background_color))
            painter.setBrush(brush)
        else:
            painter.setBrush(QBrush(QColor("#ffffff")))
        
        pen_width = style.border_width
        if self.isSelected():
            pen = QPen(QColor("#87CEEB"), pen_width + 1, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(style.border_color), pen_width)
        painter.setPen(pen)
        
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        items = getattr(self._model, 'items', [])
        current_index = getattr(self._model, 'current_index', 0)
        
        if items and 0 <= current_index < len(items):
            display_text = str(items[current_index])
        else:
            display_text = self._model.text or "选择..."
        
        painter.setPen(QColor(style.text_color))
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        painter.setFont(font)
        
        margin = 8
        arrow_width = 24
        text_rect = QRectF(margin, 0, rect.width() - arrow_width - margin * 2, rect.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_text)
        
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
        
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(arrow_x, 4), QPointF(arrow_x, rect.height() - 4))
    
    def _paint_checkbox(self, painter: QPainter, rect: QRectF, style):
        """绘制复选框组件。"""
        check_size = 18
        check_x = 5
        check_y = (rect.height() - check_size) / 2
        
        painter.setBrush(QBrush(QColor("#ffffff")))
        if self.isSelected():
            painter.setPen(QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine))
        else:
            painter.setPen(QPen(QColor("#666666"), 1))
        
        painter.drawRect(QRectF(check_x, check_y, check_size, check_size))
        
        is_checked = getattr(self._model, 'checked', False)
        if is_checked:
            painter.setPen(QPen(QColor("#0078d7"), 2))
            check_margin = 4
            painter.drawLine(
                QPointF(check_x + check_margin, check_y + check_size / 2),
                QPointF(check_x + check_size / 2, check_y + check_size - check_margin)
            )
            painter.drawLine(
                QPointF(check_x + check_size / 2, check_y + check_size - check_margin),
                QPointF(check_x + check_size - check_margin, check_y + check_margin)
            )
        
        display_text = self._model.text or "复选框"
        painter.setPen(QColor(style.text_color))
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        painter.setFont(font)
        
        text_x = check_x + check_size + 8
        text_rect = QRectF(text_x, 0, rect.width() - text_x - 5, rect.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_text)
    
    def _paint_progressbar(self, painter: QPainter, rect: QRectF, style):
        """绘制进度条组件。"""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(style.background_color if style.background_color != "transparent" else "#e0e0e0")))
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        value = getattr(self._model, 'value', 0)
        progress_width = rect.width() * value / 100
        progress_rect = QRectF(0, 0, progress_width, rect.height())
        
        painter.setBrush(QBrush(QColor("#0078d7")))
        painter.setClipRect(rect)
        painter.drawRoundedRect(progress_rect, style.border_radius, style.border_radius)
        painter.setClipping(False)
        
        border_pen = QPen(QColor(style.border_color), style.border_width)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        show_text = getattr(self._model, 'show_text', True)
        if show_text:
            text_position = getattr(self._model, 'text_position', 'center')
            font = QFont(style.font_family, style.font_size)
            font.setBold(True)
            painter.setFont(font)
            text = f"{value}%"
            
            if text_position == 'left':
                painter.setPen(QColor("#333333"))
                text_rect = QRectF(5, 0, rect.width() - 10, rect.height())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            elif text_position == 'right':
                painter.setPen(QColor("#333333"))
                text_rect = QRectF(5, 0, rect.width() - 10, rect.height())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, text)
            elif text_position == 'follow':
                if value > 10:
                    text_x = max(5, progress_width - 40)
                    text_rect = QRectF(text_x, 0, 60, rect.height())
                    painter.setPen(QColor("#ffffff"))
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
                else:
                    painter.setPen(QColor("#333333"))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            else:
                painter.setPen(QColor("#ffffff") if value > 50 else QColor("#333333"))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def _paint_container(self, painter: QPainter, rect: QRectF, style):
        """绘制容器组件（Windows窗口样式）。
        
        rect 是内容区域，标题栏画在上方，不占用内容区域空间。
        这样画布上容器大小与运行时一致。
        """
        title_bar_height = 28
        title_rect = QRectF(0, -title_bar_height, rect.width(), title_bar_height)
        total_rect = QRectF(0, -title_bar_height, rect.width(), rect.height() + title_bar_height)
        
        use_native = getattr(style, 'use_native_style', False)
        
        if use_native:
            bg_color = "#f0f0f0"
            title_color = "#e8e8e8"
            border_color = "#cccccc"
            content_bg = "#ffffff"
            border_radius = 5
        else:
            bg_color = "#f0f0f0"
            title_color = "#e8e8e8"
            border_color = style.border_color if style.border_color else "#cccccc"
            content_bg = style.background_color if style.background_color and style.background_color != "transparent" else "#ffffff"
            border_radius = style.border_radius
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawRoundedRect(total_rect, border_radius, border_radius)
        
        title_gradient = QBrush(QColor(title_color))
        painter.setBrush(title_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(0, -title_bar_height, rect.width(), title_bar_height + border_radius))
        
        border_pen = QPen(QColor(border_color), 1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(total_rect, border_radius, border_radius)
        
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawLine(0, 0, int(rect.width()), 0)
        
        display_text = self._model.text or self._model.name
        painter.setPen(QColor("#333333"))
        font = QFont("Microsoft YaHei", 9)
        font.setBold(True)
        painter.setFont(font)
        text_margin = 8
        text_rect = QRectF(text_margin, -title_bar_height, rect.width() - 70, title_bar_height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_text)
        
        btn_size = 12
        btn_y = -title_bar_height + (title_bar_height - btn_size) / 2
        btn_margin = 8
        
        min_x = rect.width() - btn_margin * 3 - btn_size * 3
        painter.setPen(QPen(QColor("#666666"), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(min_x, btn_y + btn_size/2 - 1, btn_size, 2))
        
        max_x = min_x + btn_size + btn_margin
        painter.drawRect(QRectF(max_x, btn_y, btn_size, btn_size))
        painter.drawRect(QRectF(max_x + 2, btn_y + 2, btn_size - 4, btn_size - 4))
        
        close_x = max_x + btn_size + btn_margin
        painter.setPen(QPen(QColor("#c42b1c"), 2))
        painter.drawLine(int(close_x + 2), int(btn_y + 2), int(close_x + btn_size - 2), int(btn_y + btn_size - 2))
        painter.drawLine(int(close_x + btn_size - 2), int(btn_y + 2), int(close_x + 2), int(btn_y + btn_size - 2))
        
        painter.setBrush(QBrush(QColor(content_bg)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect.adjusted(1, 1, -1, -1))
    
    def _paint_component(self, painter: QPainter, rect: QRectF, style):
        """绘制普通组件。"""
        from PySide6.QtGui import QFontMetrics
        from PySide6.QtCore import QTimer
        
        display_text = self._model.text
        
        if display_text and hasattr(self._model, 'auto_size') and self._model.auto_size:
            font = QFont(style.font_family, style.font_size)
            font.setBold(style.font_bold)
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(display_text)
            text_height = font_metrics.height()
            
            margin = 10
            min_width = text_width + margin * 2
            min_height = text_height + margin
            
            if self._model.width < min_width or self._model.height < min_height:
                new_width = max(self._model.width, min_width)
                new_height = max(self._model.height, min_height)
                
                QTimer.singleShot(0, lambda: self._auto_resize_component(new_width, new_height))
        
        use_native = getattr(style, 'use_native_style', False)
        
        if use_native:
            bg_color = "#f0f0f0"
            text_color = "#333333"
            border_color = "#999999"
            border_width = 1
            border_radius = 4
        else:
            bg_color = style.background_color
            text_color = style.text_color
            border_color = style.border_color
            border_width = style.border_width
            border_radius = style.border_radius
        
        if bg_color != "transparent":
            brush = QBrush(QColor(bg_color))
            painter.setBrush(brush)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        
        pen_width = border_width
        if self.isSelected():
            pen = QPen(QColor("#87CEEB"), pen_width + 1, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(border_color), pen_width)
        painter.setPen(pen)
        
        painter.drawRoundedRect(rect, border_radius, border_radius)
        
        if display_text:
            painter.setPen(QColor(text_color))
            font = QFont(style.font_family, style.font_size)
            font.setBold(style.font_bold)
            painter.setFont(font)
            margin = 5
            text_rect = rect.adjusted(margin, margin, -margin, -margin)
            
            alignment = getattr(self._model, 'alignment', 'center')
            if alignment == 'left':
                text_flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            elif alignment == 'right':
                text_flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            else:
                text_flags = Qt.AlignmentFlag.AlignCenter
            
            painter.drawText(text_rect, text_flags, display_text)
    
    def _auto_resize_component(self, new_width: int, new_height: int):
        """自动调整组件大小。"""
        if self._model.width != new_width or self._model.height != new_height:
            self._model.width = new_width
            self._model.height = new_height
            self.update()
    
    def _draw_resize_handles(self, painter: QPainter, rect: QRectF):
        """绘制调整大小的手柄。"""
        handle_size = app_settings.handle_size
        handle_brush = QBrush(QColor("#87CEEB"))
        handle_pen = QPen(QColor("#ffffff"), 1)
        
        painter.setBrush(handle_brush)
        painter.setPen(handle_pen)
        
        handles = [
            QPointF(rect.left(), rect.top()),
            QPointF(rect.center().x(), rect.top()),
            QPointF(rect.right(), rect.top()),
            QPointF(rect.right(), rect.center().y()),
            QPointF(rect.right(), rect.bottom()),
            QPointF(rect.center().x(), rect.bottom()),
            QPointF(rect.left(), rect.bottom()),
            QPointF(rect.left(), rect.center().y()),
        ]
        
        for pos in handles:
            handle_rect = QRectF(
                pos.x() - handle_size / 2,
                pos.y() - handle_size / 2,
                handle_size,
                handle_size
            )
            painter.drawRect(handle_rect)
    
    def _get_handle_at(self, pos: QPointF) -> int:
        """获取指定位置的手柄索引。"""
        if not self.isSelected():
            return -1
        
        handle_size = app_settings.handle_size
        tolerance = app_settings.handle_click_tolerance
        click_area = max(24, handle_size + tolerance)
        
        if self._model.type == "container":
            rect = QRectF(0, -self.TITLE_BAR_HEIGHT, self._model.width, self._model.height + self.TITLE_BAR_HEIGHT)
        else:
            rect = QRectF(0, 0, self._model.width, self._model.height)
        
        handles = [
            (QPointF(rect.left(), rect.top()), 0),
            (QPointF(rect.center().x(), rect.top()), 1),
            (QPointF(rect.right(), rect.top()), 2),
            (QPointF(rect.right(), rect.center().y()), 3),
            (QPointF(rect.right(), rect.bottom()), 4),
            (QPointF(rect.center().x(), rect.bottom()), 5),
            (QPointF(rect.left(), rect.bottom()), 6),
            (QPointF(rect.left(), rect.center().y()), 7),
        ]
        
        for handle_pos, index in handles:
            handle_rect = QRectF(
                handle_pos.x() - click_area / 2,
                handle_pos.y() - click_area / 2,
                click_area,
                click_area
            )
            if handle_rect.contains(pos):
                return index
        
        return -1
    
    def mousePressEvent(self, event):
        pos = event.pos()
        handle = self._get_handle_at(pos)
        
        if handle >= 0:
            self._resizing = True
            self._resize_handle = handle
            self._resize_start_pos = event.scenePos()
            self._resize_start_rect = QRectF(0, 0, self._model.width, self._model.height)
            self._resize_start_x = self._model.x
            self._resize_start_y = self._model.y
            self._resize_old_width = self._model.width
            self._resize_old_height = self._model.height
            self._resize_old_x = self._model.x
            self._resize_old_y = self._model.y
            event.accept()
            return
        
        modifiers = event.modifiers()
        is_multi_select = (modifiers & Qt.KeyboardModifier.ControlModifier) or \
                         (modifiers & Qt.KeyboardModifier.ShiftModifier)
        
        if self.scene():
            selected_items = [item for item in self.scene().selectedItems() 
                             if isinstance(item, ComponentGraphicsItem)]
            
            if is_multi_select:
                self.setSelected(not self.isSelected())
            else:
                if self not in selected_items:
                    for item in selected_items:
                        item.setSelected(False)
                    self.setSelected(True)
                    self.selected.emit(self.component_id)
            
            selected_items = [item for item in self.scene().selectedItems() 
                             if isinstance(item, ComponentGraphicsItem)]
            
            if len(selected_items) > 0:
                self._dragging = True
                self._drag_start_pos = event.scenePos()
                self._selected_items_start_pos = {
                    item.component_id: (item.pos().x(), item.pos().y())
                    for item in selected_items
                }
                self._has_actually_moved = False
                event.accept()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._resizing:
            self._do_resize(event.scenePos())
        elif self._dragging and self.scene():
            delta = event.scenePos() - self._drag_start_pos
            
            if not self._has_actually_moved:
                if abs(delta.x()) > self.DRAG_THRESHOLD or abs(delta.y()) > self.DRAG_THRESHOLD:
                    self._has_actually_moved = True
            
            if self._has_actually_moved:
                selected_items = [item for item in self.scene().selectedItems() 
                                 if isinstance(item, ComponentGraphicsItem)]
                
                for item in selected_items:
                    if item.component_id in self._selected_items_start_pos:
                        start_x, start_y = self._selected_items_start_pos[item.component_id]
                        new_x = start_x + delta.x()
                        new_y = start_y + delta.y()
                        item.setPos(QPointF(new_x, new_y))
            
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
            self._resize_handle = -1
            
            size_changed = (self._model.width != self._resize_old_width or 
                          self._model.height != self._resize_old_height)
            pos_changed = (self._model.x != self._resize_old_x or 
                          self._model.y != self._resize_old_y)
            
            if size_changed or pos_changed:
                self.resized.emit({
                    'id': self.component_id,
                    'old_width': self._resize_old_width,
                    'old_height': self._resize_old_height,
                    'old_x': self._resize_old_x,
                    'old_y': self._resize_old_y,
                    'new_width': int(self._model.width),
                    'new_height': int(self._model.height),
                    'new_x': int(self._model.x),
                    'new_y': int(self._model.y)
                })
            
            if self.scene():
                self.scene().update()
            event.accept()
        elif self._dragging:
            self._dragging = False
            
            print(f"\n========== 画布组件释放调试 ==========")
            print(f"组件ID: {self.component_id}")
            print(f"实际移动: {self._has_actually_moved}")
            print(f"选中项数量: {len(self.scene().selectedItems()) if self.scene() else 0}")
            
            if self._has_actually_moved and self.scene():
                selected_items = [item for item in self.scene().selectedItems() 
                                 if isinstance(item, ComponentGraphicsItem)]
                
                is_multi_move = len(selected_items) > 1
                print(f"多选移动: {is_multi_move}")
                
                new_positions = {}
                for item in selected_items:
                    new_pos = item.pos()
                    new_positions[item.component_id] = (int(new_pos.x()), int(new_pos.y()))
                    item._check_and_update_parent()
                    
                    if not is_multi_move:
                        print(f"发射单选移动信号: {item.component_id} -> ({int(new_pos.x())}, {int(new_pos.y())})")
                        item.moved.emit(item.component_id, int(new_pos.x()), int(new_pos.y()))
                
                if is_multi_move and self._selected_items_start_pos:
                    print(f"发射多选移动信号: {new_positions}")
                    self.multi_move_finished.emit({
                        'old': self._selected_items_start_pos,
                        'new': new_positions
                    })
                
                self.scene().update()
            else:
                print("未移动或无场景")
            
            print("========================================\n")
            
            self._selected_items_start_pos.clear()
            self._has_actually_moved = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def _check_and_update_parent(self):
        """检查并更新父容器关系。"""
        if self._model.type == "container":
            return
        
        if not self.scene():
            return
        
        scene_pos = self.sceneBoundingRect().center()
        
        new_parent_id = ""
        best_container = None
        
        for item in self.scene().items(scene_pos):
            if isinstance(item, ComponentGraphicsItem) and item != self:
                if item.model.type == "container":
                    container_rect = item.sceneBoundingRect()
                    title_bar_rect = QRectF(
                        container_rect.left(), container_rect.top(),
                        container_rect.width(), self.TITLE_BAR_HEIGHT
                    )
                    
                    content_rect = QRectF(
                        container_rect.left(), container_rect.top() + self.TITLE_BAR_HEIGHT,
                        container_rect.width(), container_rect.height() - self.TITLE_BAR_HEIGHT
                    )
                    
                    if content_rect.contains(scene_pos):
                        if best_container is None or item.model.id == self._model.parent_id:
                            best_container = item
                        elif self._model.parent_id == item.model.id:
                            best_container = item
        
        if best_container:
            new_parent_id = best_container.model.id
        else:
            new_parent_id = ""
        
        if new_parent_id != self._model.parent_id:
            self._model.parent_id = new_parent_id
            self.parent_changed.emit(self.component_id, new_parent_id)
    
    def _do_resize(self, scene_pos: QPointF):
        """执行调整大小操作。"""
        delta = scene_pos - self._resize_start_pos
        handle = self._resize_handle
        
        orig_width = self._resize_start_rect.width()
        orig_height = self._resize_start_rect.height()
        orig_x = self._resize_start_x
        orig_y = self._resize_start_y
        
        dx = delta.x()
        dy = delta.y()
        
        self._model.blockSignals(True)
        
        try:
            if handle in [0, 6, 7]:
                new_width = int(orig_width - dx)
                if new_width < self.MIN_SIZE:
                    dx = orig_width - self.MIN_SIZE
                    new_width = self.MIN_SIZE
                self._model.width = new_width
                self._model.x = int(orig_x + dx)
            
            if handle in [2, 3, 4]:
                new_width = int(orig_width + dx)
                if new_width < self.MIN_SIZE:
                    new_width = self.MIN_SIZE
                self._model.width = new_width
            
            if handle in [0, 1, 2]:
                new_height = int(orig_height - dy)
                if new_height < self.MIN_SIZE:
                    dy = orig_height - self.MIN_SIZE
                    new_height = self.MIN_SIZE
                self._model.height = new_height
                self._model.y = int(orig_y + dy)
            
            if handle in [4, 5, 6]:
                new_height = int(orig_height + dy)
                if new_height < self.MIN_SIZE:
                    new_height = self.MIN_SIZE
                self._model.height = new_height
            
            self.setPos(self._model.x, self._model.y)
        finally:
            self._model.blockSignals(False)
        
        self.update()
    
    def itemChange(self, change, value):
        if change == QGraphicsObject.GraphicsItemChange.ItemPositionChange and self.scene():
            new_pos = value
            
            if app_settings.snap_to_grid:
                grid_size = app_settings.grid_size
                x = round(new_pos.x() / grid_size) * grid_size
                y = round(new_pos.y() / grid_size) * grid_size
                new_pos = QPointF(x, y)
            
            return new_pos
        
        if change == QGraphicsObject.GraphicsItemChange.ItemPositionHasChanged and self.scene():
            self.scene().update()
        
        return super().itemChange(change, value)
    
    def hoverMoveEvent(self, event):
        handle = self._get_handle_at(event.pos())
        
        cursors = {
            0: Qt.CursorShape.SizeFDiagCursor,
            1: Qt.CursorShape.SizeVerCursor,
            2: Qt.CursorShape.SizeBDiagCursor,
            3: Qt.CursorShape.SizeHorCursor,
            4: Qt.CursorShape.SizeFDiagCursor,
            5: Qt.CursorShape.SizeVerCursor,
            6: Qt.CursorShape.SizeBDiagCursor,
            7: Qt.CursorShape.SizeHorCursor,
        }
        
        if handle >= 0:
            self.setCursor(cursors.get(handle, Qt.CursorShape.ArrowCursor))
        else:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        
        super().hoverMoveEvent(event)


class DesignerScene(QGraphicsScene):
    """设计器场景。
    
    支持桌面区域模拟、网格背景、黑框边界等功能。
    """
    
    def __init__(self, desktop_width=DEFAULT_DESKTOP_WIDTH, desktop_height=DEFAULT_DESKTOP_HEIGHT, parent=None):
        super().__init__(parent)
        
        self._desktop_width = desktop_width
        self._desktop_height = desktop_height
        
        margin = 500
        self.setSceneRect(-margin, -margin, desktop_width + margin * 2, desktop_height + margin * 2)
        
        self._grid_color = QColor("#e0e0e0")
        self._desktop_border_color = QColor("#333333")
        self._outside_color = QColor("#1a1a1a")
        self._desktop_bg_color = QColor("#f5f5f5")
        
        self.setBackgroundBrush(QBrush(self._outside_color))
    
    @property
    def desktop_rect(self) -> QRectF:
        return QRectF(0, 0, self._desktop_width, self._desktop_height)
    
    def set_desktop_size(self, width: int, height: int):
        self._desktop_width = width
        self._desktop_height = height
        self.update()
    
    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)
        
        painter.fillRect(rect, self._outside_color)
        
        desktop_rect = self.desktop_rect
        painter.fillRect(desktop_rect, self._desktop_bg_color)
        
        border_pen = QPen(self._desktop_border_color, 3)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(desktop_rect)
        
        if app_settings.show_grid:
            self._draw_grid(painter, desktop_rect)
    
    def _draw_grid(self, painter: QPainter, desktop_rect: QRectF):
        pen = QPen(self._grid_color, 0.5)
        painter.setPen(pen)
        
        grid_size = app_settings.grid_size
        
        left = int(desktop_rect.left())
        top = int(desktop_rect.top())
        right = int(desktop_rect.right())
        bottom = int(desktop_rect.bottom())
        
        x = left
        while x <= right:
            painter.drawLine(x, top, x, bottom)
            x += grid_size
        
        y = top
        while y <= bottom:
            painter.drawLine(left, y, right, y)
            y += grid_size


class DesignerView(QGraphicsView):
    """设计器视图。
    
    主画布视图，支持Alt+滚轮缩放、桌面模拟、居中显示等功能。
    
    Signals:
        zoom_changed: 缩放比例改变时发射 (zoom_factor)
        component_selected: 组件选中时发射 (comp_id)
    """
    
    zoom_changed = Signal(float)
    component_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._scene = DesignerScene(parent=self)
        self.setScene(self._scene)
        
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 4.0
        
        self._items: dict[str, ComponentGraphicsItem] = {}
        
        self._panning = False
        self._pan_start = QPointF()
        self._initial_fit_done = False
        self._project_model = None
        
        self.setAcceptDrops(True)
        
        app_settings.add_change_callback(self._on_settings_changed)
    
    def _on_settings_changed(self, key: str, value):
        """设置变化时刷新画布。"""
        self._scene.update()
        for item in self._items.values():
            item.update()
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self._initial_fit_done:
            self._initial_fit_done = True
            self._fit_desktop_to_view()
    
    def _fit_desktop_to_view(self):
        view_width = self.width()
        view_height = self.height()
        
        if view_width <= 0 or view_height <= 0:
            return
        
        desktop_width = self._scene._desktop_width
        desktop_height = self._scene._desktop_height
        
        scale_x = view_width / desktop_width
        scale_y = view_height / desktop_height
        
        scale = min(scale_x, scale_y) * 0.9
        
        self.resetTransform()
        self.scale(scale, scale)
        self._zoom_factor = scale
        self.zoom_changed.emit(self._zoom_factor)
        
        desktop_center_x = desktop_width / 2
        desktop_center_y = desktop_height / 2
        self.centerOn(desktop_center_x, desktop_center_y)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_desktop_to_view()
    
    def add_component_item(self, model: ComponentModel) -> ComponentGraphicsItem:
        if model.x == 0 and model.y == 0:
            desktop_width = self._scene._desktop_width
            desktop_height = self._scene._desktop_height
            center_x = (desktop_width - model.width) / 2
            center_y = (desktop_height - model.height) / 2
            model.set_position(int(center_x), int(center_y))
        
        item = ComponentGraphicsItem(model)
        item.selected.connect(self.component_selected.emit)
        self._scene.addItem(item)
        self._items[model.id] = item
        
        # 检查并设置父容器关系
        item._check_and_update_parent()
        
        self._update_z_values()
        
        return item
    
    def _update_z_values(self):
        """更新组件的Z值，确保容器在下层，其他组件在上层。"""
        containers = []
        others = []
        
        for item in self._items.values():
            if item.model.type == "container":
                containers.append(item)
            else:
                others.append(item)
        
        for i, item in enumerate(containers):
            item.setZValue(i)
        
        base_z = len(containers)
        for i, item in enumerate(others):
            item.setZValue(base_z + i + 1)
    
    def remove_component_item(self, comp_id: str):
        if comp_id in self._items:
            item = self._items[comp_id]
            self._scene.removeItem(item)
            del self._items[comp_id]
    
    def get_item(self, comp_id: str) -> Optional[ComponentGraphicsItem]:
        return self._items.get(comp_id)
    
    def select_item(self, comp_id: str):
        for item in self._items.values():
            item.setSelected(False)
        
        if comp_id in self._items:
            self._items[comp_id].setSelected(True)
    
    def clear_selection(self):
        for item in self._items.values():
            item.setSelected(False)
    
    def get_selected_items(self) -> list[ComponentGraphicsItem]:
        return [item for item in self._items.values() if item.isSelected()]
    
    def align_selected_items(self, align_type: str):
        """对齐选中的组件。
        
        Args:
            align_type: 对齐类型
                - "left": 左对齐
                - "center": 水平居中
                - "right": 右对齐
                - "top": 顶对齐
                - "v_center": 垂直居中
                - "bottom": 底对齐
        """
        selected = self.get_selected_items()
        if len(selected) < 2:
            return
        
        positions = []
        sizes = []
        for item in selected:
            positions.append((item.pos().x(), item.pos().y()))
            sizes.append((item.model.width, item.model.height))
        
        min_x = min(p[0] for p in positions)
        max_x = max(p[0] + s[0] for p, s in zip(positions, sizes))
        min_y = min(p[1] for p in positions)
        max_y = max(p[1] + s[1] for p, s in zip(positions, sizes))
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        for item in selected:
            old_x, old_y = item.pos().x(), item.pos().y()
            width, height = item.model.width, item.model.height
            new_x, new_y = old_x, old_y
            
            if align_type == "left":
                new_x = min_x
            elif align_type == "center":
                new_x = center_x - width / 2
            elif align_type == "right":
                new_x = max_x - width
            elif align_type == "top":
                new_y = min_y
            elif align_type == "v_center":
                new_y = center_y - height / 2
            elif align_type == "bottom":
                new_y = max_y - height
            
            if new_x != old_x or new_y != old_y:
                item.setPos(new_x, new_y)
                item.model.set_position(int(new_x), int(new_y))
    
    def zoom_in(self):
        self._zoom(1.2)
    
    def zoom_out(self):
        self._zoom(0.8)
    
    def zoom_reset(self):
        self._fit_desktop_to_view()
    
    def _zoom(self, factor: float):
        new_zoom = self._zoom_factor * factor
        
        if self._min_zoom <= new_zoom <= self._max_zoom:
            self._zoom_factor = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self._zoom_factor)
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        event.accept()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            comp_type = event.mimeData().text()
            scene_pos = self.mapToScene(event.pos())
            
            from models import create_component
            model = create_component(comp_type, x=int(scene_pos.x()), y=int(scene_pos.y()))
            
            self.add_component_item(model)
            
            if hasattr(self, '_project_model') and self._project_model:
                self._project_model.add_component(model)
            
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
    
    def clear(self):
        self._items.clear()
        self._scene.clear()
    
    def get_desktop_size(self) -> tuple:
        return (self._scene._desktop_width, self._scene._desktop_height)
    
    def set_desktop_size(self, width: int, height: int):
        self._scene.set_desktop_size(width, height)
        self._fit_desktop_to_view()
    
    def set_project_model(self, model):
        self._project_model = model
