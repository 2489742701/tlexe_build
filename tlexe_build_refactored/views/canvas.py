"""画布视图模块。

本模块包含设计器画布和组件图形项的实现。

## 设计理念

画布模拟的是 Windows 桌面屏幕，整个画布区域代表用户的显示器屏幕。
用户在画布上设计界面，就像在真实的 Windows 桌面上放置窗口和控件一样。

- **桌面区域**：画布中央的浅色区域，代表实际的显示器屏幕
- **外部区域**：桌面周围的深色区域，代表屏幕边界之外
- **组件**：放置在桌面上的窗口、按钮、标签等控件

## 主要功能

- 桌面模拟：模拟 Windows 桌面屏幕，让用户直观地设计界面布局
- 组件图形项：显示和交互（拖拽、选中、调整大小）
- 缩放功能：Alt+滚轮缩放画布，方便查看细节
- 网格背景：辅助对齐和布局
- 黑框边界：标识桌面区域的边界
"""

from typing import Optional, TYPE_CHECKING
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsObject, 
    QGraphicsRectItem, QGraphicsItem
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QBrush, QColor, QPen, QFont, QPainter

if TYPE_CHECKING:
    from models import ComponentModel

from utils.settings import app_settings

DEFAULT_DESKTOP_WIDTH = 1280
DEFAULT_DESKTOP_HEIGHT = 720

class ComponentGraphicsItem(QGraphicsObject):
    """画布上的组件图形项 - 代表 Windows 桌面上的一个窗口或控件。
    
    每个组件图形项对应设计中的一个界面元素，如按钮、标签、容器等。
    组件放置在模拟的 Windows 桌面上，用户可以拖拽、调整大小、选中它们。
    
    ## 设计理念
    
    - 组件就像 Windows 桌面上的窗口，可以自由移动和调整大小
    - 容器组件带有标题栏，模拟 Windows 窗口的外观
    - 支持父子关系，子组件放在父容器内部
    
    ## 交互功能
    
    - 拖拽移动：鼠标拖拽移动组件位置
    - 调整大小：拖拽边角调整组件尺寸
    - 选中高亮：选中时显示蓝色边框和调整手柄
    - 多选操作：Ctrl/Shift+点击多选组件
    
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
    
    def __init__(self, model: 'ComponentModel', parent: Optional[QGraphicsItem] = None):
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
        self._selected_items_cache = []
        self._cache_valid = False
    
    @property
    def component_id(self) -> str:
        return self._model.id
    
    @property
    def model(self) -> 'ComponentModel':
        return self._model
    
    def _get_selected_items_cached(self):
        if not self._cache_valid and self.scene():
            self._selected_items_cache = [
                item for item in self.scene().selectedItems()
                if isinstance(item, ComponentGraphicsItem)
            ]
            self._cache_valid = True
        return self._selected_items_cache
    
    def _invalidate_cache(self):
        self._cache_valid = False
        self._selected_items_cache = []

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
        if self._dragging or self._resizing:
            return
        if self.pos().x() != self._model.x or self.pos().y() != self._model.y:
            self.setPos(QPointF(self._model.x, self._model.y))
        self.update()
    
    def paint(self, painter: QPainter, option, widget):
        rect = QRectF(0, 0, self._model.width, self._model.height)
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        from renderers.renderer_factory import RendererFactory
        renderer = RendererFactory.get_renderer_or_default(self._model.type)
        renderer.render(painter, self._model, rect, self.isSelected())
        
        if self.isSelected():
            if self._model.type == "container":
                selection_rect = QRectF(0, -self.TITLE_BAR_HEIGHT, self._model.width, self._model.height + self.TITLE_BAR_HEIGHT)
            else:
                selection_rect = rect
            self._draw_resize_handles(painter, selection_rect)

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
            selected_items = self._get_selected_items_cached()
            
            if is_multi_select:
                self.setSelected(not self.isSelected())
            else:
                if self not in selected_items:
                    for item in selected_items:
                        item.setSelected(False)
                    self.setSelected(True)
                    self.selected.emit(self.component_id)
            
            self._invalidate_cache()
            selected_items = self._get_selected_items_cached()
            
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
                selected_items = self._get_selected_items_cached()
                
                for item in selected_items:
                    # 如果当前组件的父容器也在被选中的列表中，
                    # 那么移动父容器时 Qt 会自动移动子组件。
                    # 我们跳过这个子组件，防止发生“双倍移动”导致按钮乱飞。
                    if item.parentItem() in selected_items:
                        continue
                        
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
            if self._has_actually_moved and self.scene():
                selected_items = self._get_selected_items_cached()
                
                is_multi_move = len(selected_items) > 1
                
                new_positions = {}
                for item in selected_items:
                    new_pos = item.pos()
                    new_positions[item.component_id] = (int(new_pos.x()), int(new_pos.y()))
                    item._check_and_update_parent()
                    
                    if not is_multi_move:
                        item.moved.emit(item.component_id, int(new_pos.x()), int(new_pos.y()))
                
                if is_multi_move and self._selected_items_start_pos:
                    self.multi_move_finished.emit({
                        'old': self._selected_items_start_pos,
                        'new': new_positions
                    })
                
                self.scene().update()
            
            self._dragging = False
            self._selected_items_start_pos.clear()
            self._has_actually_moved = False
            self._invalidate_cache()
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def _check_and_update_parent(self):
        """检查并更新父容器关系。
        
        当组件被拖动时，检查是否进入或离开容器。
        如果父容器关系发生变化，建立或断开Qt的父子关系，
        使子组件能够跟随父容器移动。
        """
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
            if new_parent_id:
                self._attach_to_parent(best_container)
            else:
                self._detach_from_parent()
            
            self._model.parent_id = new_parent_id
            self.parent_changed.emit(self.component_id, new_parent_id)
    
    def _attach_to_parent(self, parent_item: 'ComponentGraphicsItem'):
        """将组件挂载到父容器上。
        
        建立Qt的父子关系，使子组件能够跟随父容器移动。
        同时将场景坐标转换为父容器的局部坐标。
        
        Args:
            parent_item: 父容器组件
        """
        if not parent_item:
            return
        
        scene_pos = self.scenePos()
        
        local_pos = parent_item.mapFromScene(scene_pos)
        
        self.setParentItem(parent_item)
        
        self.setPos(local_pos)
    
    def _detach_from_parent(self):
        """将组件从父容器中分离。
        
        断开Qt的父子关系，同时将局部坐标转换为场景坐标，
        确保组件在视觉上保持在原来的位置。
        """
        if self.parentItem() is None:
            return
        
        scene_pos = self.scenePos()
        
        self.setParentItem(None)
        
        self.setPos(scene_pos)
    
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
    """设计器场景 - 模拟工作台的画布。
    
    画布区域使用类似于图像编辑器工作台的格子图案，
    周围区域则是淡浅色的背景。
    
    Attributes:
        _window_width: 画布宽度
        _window_height: 画布高度
        _grid_color: 网格线颜色
        _desktop_border_color: 画布边框颜色
        _outside_color: 画布外部区域颜色（淡浅色）
    """
    
    def __init__(self, desktop_width=DEFAULT_DESKTOP_WIDTH, desktop_height=DEFAULT_DESKTOP_HEIGHT, parent=None):
        super().__init__(parent)
        
        # 画布始终固定为桌面屏幕大小，不再跟随项目窗口缩小
        self._desktop_width = 1920  # Windows 桌面标准宽度
        self._desktop_height = 1080
        
        self._grid_color = QColor(0, 0, 0, 30)  # 淡黑色网格线，工作台图纸感
        self._canvas_border_color = QColor("#999999")
        
        # 场景背景（画布外围）使用淡浅色
        self._outside_color = QColor("#f5f5f5")
        self.setBackgroundBrush(QBrush(self._outside_color))
        
        # 画布本身的白色背景
        self._canvas_bg_color = QColor("#ffffff")
        
        # 初始化项目逻辑窗口的默认属性，防止getattr取不到而导致意外
        self._project_window_width = 800
        self._project_window_height = 600
        self._project_window_frameless = False
        
        # 初始化场景大小
        self._update_scene_rect()
    
    # (已移除 _create_checkerboard_brush，改用纯白背景+网格线)
    
    @property
    def window_rect(self) -> QRectF:
        """返回工作台屏幕的物理区域（1920x1080），使其中心正好对准项目的逻辑窗口中心。"""
        pw = self._project_window_width
        ph = self._project_window_height
        dx = (pw - self._desktop_width) / 2
        dy = (ph - self._desktop_height) / 2
        return QRectF(dx, dy, self._desktop_width, self._desktop_height)
    
    def _update_scene_rect(self):
        margin = 1000
        # 确保场景区域足够大，包含偏移后的桌面
        self.setSceneRect(-margin - 1000, -margin - 1000, 
                          self._desktop_width + margin * 2 + 2000, 
                          self._desktop_height + margin * 2 + 2000)
        self.update()

    def update_window_size(self, width: int, height: int, frameless: bool = False):
        """更新项目窗口大小和边框状态。
        
        这会让 1920x1080 的工作台底板重新居中对齐到这个新的项目窗口尺寸。
        """
        self._project_window_width = width
        self._project_window_height = height
        self._project_window_frameless = frameless
        self.update()
    
    def drawBackground(self, painter: QPainter, rect: QRectF):
        # 默认铺满无限淡浅色背景
        super().drawBackground(painter, rect)
        
        # 1. 计算 1920x1080 屏幕底板的区域（居中于项目窗口）
        desktop_rect = self.window_rect
        
        # ── 屏幕底板阴影 ──────────────────────
        shadow_offset = 10
        shadow_color = QColor(0, 0, 0, 30)
        painter.fillRect(desktop_rect.translated(shadow_offset, shadow_offset), shadow_color)
        
        # ── 屏幕底板（工作台图纸，白色带网格） ───────────
        painter.fillRect(desktop_rect, self._canvas_bg_color)
        if app_settings.show_grid:
            self._draw_grid(painter, desktop_rect)
        
        # 屏幕外边框
        painter.setPen(QPen(self._canvas_border_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(desktop_rect)
        
        # 2. 绘制项目的逻辑窗口（真正的程序画布）
        # 这个窗口永远在 (0, 0, pw, ph)，因此现有的组件坐标完全正确
        pw = self._project_window_width
        ph = self._project_window_height
        project_rect = QRectF(0, 0, pw, ph)
        
        # 逻辑窗口的白底和阴影（让它像是一张纸铺在工作台上）
        painter.fillRect(project_rect.translated(4, 4), QColor(0, 0, 0, 40))
        painter.fillRect(project_rect, QColor("#ffffff"))
        
        # 仅当不是无边框窗口时绘制边框
        is_frameless = self._project_window_frameless
        if not is_frameless:
            painter.setPen(QPen(QColor("#666666"), 1))
            painter.drawRect(project_rect)
    
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
    """设计器视图 - Windows 桌面屏幕模拟器的主视图。
    
    这是用户设计界面的主画布，显示模拟的 Windows 桌面屏幕。
    用户可以在这个"虚拟桌面"上放置和调整窗口、按钮等组件。
    
    ## 核心概念
    
    - **画布 = Windows 桌面屏幕**：画布中央的浅色区域模拟用户的显示器
    - **组件 = 窗口/控件**：放置在桌面上的按钮、标签、输入框等
    - **设计 = 布局**：在虚拟桌面上安排界面元素的位置和大小
    
    ## 功能
    
    - Alt+滚轮缩放画布
    - 鼠标拖拽平移画布
    - 居中显示桌面区域
    - 组件选中信号
    
    ## 信号说明
    
    ### 视图事件信号（供Presenter订阅）
    - zoom_changed(float): 缩放比例改变
    - component_selected(str): 组件被选中
    - component_deselected(str): 组件取消选中
    - component_dragged(str, float, float): 组件拖拽中（id, delta_x, delta_y）
    - component_moved(str, int, int): 组件移动完成（id, x, y）
    - component_resized(str, int, int): 组件大小改变（id, width, height）
    - canvas_clicked(float, float): 点击画布空白区域
    - multi_select_finished(list): 框选完成（选中的组件ID列表）
    """
    
    zoom_changed = Signal(float)
    component_selected = Signal(str)
    component_deselected = Signal(str)
    component_dragged = Signal(str, float, float)
    component_moved = Signal(str, int, int)
    component_resized = Signal(str, int, int)
    canvas_clicked = Signal(float, float)
    multi_select_finished = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._scene = DesignerScene(parent=self)
        self.setScene(self._scene)
        
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # 修改缩放锚点为鼠标所在位置，更符合现代设计软件（如 Figma/PS）的直觉
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 4.0
        self._user_scale = None
        
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
        
        desktop_rect = self._scene.window_rect
        desktop_width = desktop_rect.width()
        desktop_height = desktop_rect.height()
        
        scale_x = view_width / desktop_width
        scale_y = view_height / desktop_height
        
        scale = min(scale_x, scale_y) * 0.95
        
        self.resetTransform()
        self.scale(scale, scale)
        self._zoom_factor = scale
        self.zoom_changed.emit(self._zoom_factor)
        
        # 视野对齐到项目窗口的中心 (这也会正好是 1920x1080 桌面的中心)
        pw = getattr(self._scene, '_project_window_width', 800)
        ph = getattr(self._scene, '_project_window_height', 600)
        self.centerOn(pw / 2, ph / 2)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)

    def reset_to_fit_window(self):
        """重置为自动适应窗口模式。"""
        self._fit_desktop_to_view()
    
    def set_user_scale(self, scale: float):
        """设置用户手动缩放比例。"""
        self._user_scale = scale
        self._zoom_factor = scale
        self.resetTransform()
        self.scale(scale, scale)
        pw = getattr(self._scene, '_project_window_width', 800)
        ph = getattr(self._scene, '_project_window_height', 600)
        self.centerOn(pw / 2, ph / 2)
        self.zoom_changed.emit(scale)
        
    def update_window_size(self, width: int, height: int, frameless: bool = False):
        self._scene.update_window_size(width, height, frameless)
    
    def add_component_item(self, model: 'ComponentModel') -> ComponentGraphicsItem:
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
        self.reset_to_fit_window()
    
    def _zoom(self, factor: float):
        new_zoom = self._zoom_factor * factor
        
        if self._min_zoom <= new_zoom <= self._max_zoom:
            self._user_scale = new_zoom
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
        self._scene._desktop_width = width
        self._scene._desktop_height = height
        self._scene._update_scene_rect()
        if not self._initial_fit_done:
            self._fit_desktop_to_view()
    
    def set_project_model(self, model):
        self._project_model = model
