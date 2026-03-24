"""傻瓜桌面开发工具 - 单文件版本。

这是一个完整的可运行版本，包含所有核心功能。
"""

import sys
import uuid
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QColorDialog,
    QGraphicsView, QGraphicsScene, QGraphicsObject, QGraphicsItem,
    QFileDialog, QMessageBox, QMenu, QToolBar, QStatusBar,
    QScrollArea, QFrame, QInputDialog
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QAction, QBrush, QColor, QPen, QFont, QPainter


# ==================== 数据模型 ====================

@dataclass
class StyleConfig:
    """样式配置。"""
    background_color: str = "#f0f0f0"
    text_color: str = "#333333"
    border_color: str = "#999999"
    border_width: int = 1
    border_radius: int = 5
    font_family: str = "Microsoft YaHei"
    font_size: int = 12
    font_bold: bool = False


@dataclass
class ActionConfig:
    """行为配置。"""
    action_type: str = "none"
    params: Dict[str, Any] = field(default_factory=dict)


class ComponentModel:
    """组件模型基类。"""
    
    def __init__(self, comp_type: str, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 40, text: str = "", parent_id: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.type = comp_type
        self.name = name or f"{comp_type}_{self.id}"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.parent_id = parent_id
        self.style = StyleConfig()
        self.action = ActionConfig()
        self.enabled = True
        self.visible = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'text': self.text,
            'parent_id': self.parent_id,
            'style': self.style.__dict__,
            'action': self.action.__dict__,
            'enabled': self.enabled,
            'visible': self.visible,
        }


class ButtonModel(ComponentModel):
    """按钮模型。"""
    
    def __init__(self, x: int = 0, y: int = 0, text: str = "按钮", **kwargs):
        super().__init__("button", x=x, y=y, text=text, width=100, height=36, **kwargs)
        self.style.background_color = "#4a90d9"
        self.style.text_color = "#ffffff"
        self.target_window_id = ""
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['target_window_id'] = self.target_window_id
        return data


class LabelModel(ComponentModel):
    """文本模型。"""
    
    def __init__(self, x: int = 0, y: int = 0, text: str = "文本", **kwargs):
        super().__init__("label", x=x, y=y, text=text, width=120, height=30, **kwargs)
        self.style.background_color = "transparent"
        self.style.border_width = 0


class InputModel(ComponentModel):
    """输入框模型。"""
    
    def __init__(self, x: int = 0, y: int = 0, text: str = "", **kwargs):
        super().__init__("input", x=x, y=y, text=text, width=200, height=32, **kwargs)
        self.placeholder = "请输入..."
        self.is_password = False


class ContainerModel(ComponentModel):
    """容器模型。"""
    
    def __init__(self, x: int = 0, y: int = 0, text: str = "容器", **kwargs):
        super().__init__("container", x=x, y=y, text=text, width=400, height=300, **kwargs)
        self.name = f"容器-{self.id}"


class WindowModel:
    """窗口模型。"""
    
    def __init__(self, name: str = "主窗口", is_main: bool = False):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.is_main = is_main
        self.components: List[str] = []
        self.width = 800
        self.height = 600


class ProjectModel:
    """项目模型。"""
    
    def __init__(self):
        self.name = "新建项目"
        self.windows: Dict[str, WindowModel] = {}
        self.components: Dict[str, ComponentModel] = {}
        self.main_window_id: Optional[str] = None
        self._current_window_id: Optional[str] = None
        
        self._create_main_window()
    
    def _create_main_window(self):
        main = WindowModel("主窗口", is_main=True)
        self.windows[main.id] = main
        self.main_window_id = main.id
        self._current_window_id = main.id
    
    @property
    def current_window(self) -> Optional[WindowModel]:
        return self.windows.get(self._current_window_id) if self._current_window_id else None
    
    def add_component(self, comp: ComponentModel, window_id: str):
        self.components[comp.id] = comp
        if window_id in self.windows:
            self.windows[window_id].components.append(comp.id)
    
    def get_components_for_window(self, window_id: str) -> List[ComponentModel]:
        if window_id not in self.windows:
            return []
        return [self.components[cid] for cid in self.windows[window_id].components if cid in self.components]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'main_window_id': self.main_window_id,
            'windows': {wid: {'id': w.id, 'name': w.name, 'is_main': w.is_main, 
                             'components': w.components, 'width': w.width, 'height': w.height}
                       for wid, w in self.windows.items()},
            'components': {cid: c.to_dict() for cid, c in self.components.items()},
        }


# ==================== 图形项 ====================

class ComponentGraphicsItem(QGraphicsObject):
    """组件图形项。"""
    
    moved = Signal(str, int, int)
    selected = Signal(str)
    resized = Signal(str, int, int)
    
    HANDLE_SIZE = 8
    MIN_SIZE = 20
    
    def __init__(self, model: ComponentModel, parent: Optional[QGraphicsItem] = None):
        super().__init__(parent)
        self._model = model
        
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        
        self.setPos(QPointF(model.x, model.y))
        self._resizing = False
        self._resize_handle = -1
        self._grid_size = 10
        self._snap_to_grid = True
    
    @property
    def component_id(self) -> str:
        return self._model.id
    
    @property
    def model(self) -> ComponentModel:
        return self._model
    
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._model.width, self._model.height)
    
    def paint(self, painter: QPainter, option, widget):
        rect = self.boundingRect()
        style = self._model.style
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._model.type == "container":
            self._paint_container(painter, rect, style)
        else:
            self._paint_component(painter, rect, style)
        
        if self.isSelected():
            self._draw_resize_handles(painter, rect)
    
    def _paint_container(self, painter: QPainter, rect: QRectF, style):
        title_bar_height = 28
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.drawRoundedRect(rect, 8, 8)
        
        painter.setBrush(QBrush(QColor("#e8e8e8")))
        painter.drawRect(QRectF(0, 0, rect.width(), title_bar_height))
        
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 8, 8)
        
        painter.setPen(QColor("#333333"))
        font = QFont("Microsoft YaHei", 9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(8, 0, rect.width() - 70, title_bar_height), 
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 
                        self._model.text or self._model.name)
        
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(1, title_bar_height, rect.width() - 2, rect.height() - title_bar_height - 1))
    
    def _paint_component(self, painter: QPainter, rect: QRectF, style):
        if style.background_color != "transparent":
            painter.setBrush(QBrush(QColor(style.background_color)))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        
        if self.isSelected():
            pen = QPen(QColor("#0078d7"), style.border_width + 1, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(style.border_color), style.border_width)
        painter.setPen(pen)
        
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        if self._model.text:
            painter.setPen(QColor(style.text_color))
            font = QFont(style.font_family, style.font_size)
            font.setBold(style.font_bold)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._model.text)
    
    def _draw_resize_handles(self, painter: QPainter, rect: QRectF):
        handle_size = self.HANDLE_SIZE
        painter.setBrush(QBrush(QColor("#0078d7")))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        
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
            painter.drawRect(QRectF(pos.x() - handle_size/2, pos.y() - handle_size/2, 
                                    handle_size, handle_size))
    
    def _get_handle_at(self, pos: QPointF) -> int:
        if not self.isSelected():
            return -1
        rect = self.boundingRect()
        handle_size = self.HANDLE_SIZE + 4
        
        handles = [
            (QRectF(rect.left() - handle_size/2, rect.top() - handle_size/2, handle_size, handle_size), 0),
            (QRectF(rect.center().x() - handle_size/2, rect.top() - handle_size/2, handle_size, handle_size), 1),
            (QRectF(rect.right() - handle_size/2, rect.top() - handle_size/2, handle_size, handle_size), 2),
            (QRectF(rect.right() - handle_size/2, rect.center().y() - handle_size/2, handle_size, handle_size), 3),
            (QRectF(rect.right() - handle_size/2, rect.bottom() - handle_size/2, handle_size, handle_size), 4),
            (QRectF(rect.center().x() - handle_size/2, rect.bottom() - handle_size/2, handle_size, handle_size), 5),
            (QRectF(rect.left() - handle_size/2, rect.bottom() - handle_size/2, handle_size, handle_size), 6),
            (QRectF(rect.left() - handle_size/2, rect.center().y() - handle_size/2, handle_size, handle_size), 7),
        ]
        
        for handle_rect, index in handles:
            if handle_rect.contains(pos):
                return index
        return -1
    
    def mousePressEvent(self, event):
        handle = self._get_handle_at(event.pos())
        if handle >= 0:
            self._resizing = True
            self._resize_handle = handle
            self._resize_start_pos = event.scenePos()
            self._resize_start_rect = self.boundingRect()
            self._resize_start_x = self._model.x
            self._resize_start_y = self._model.y
        else:
            super().mousePressEvent(event)
            self.selected.emit(self.component_id)
    
    def mouseMoveEvent(self, event):
        if self._resizing:
            self._do_resize(event.scenePos())
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
            self._resize_handle = -1
            self.resized.emit(self.component_id, int(self._model.width), int(self._model.height))
            if self.scene():
                self.scene().update()
        else:
            super().mouseReleaseEvent(event)
            new_pos = self.pos()
            self.moved.emit(self.component_id, int(new_pos.x()), int(new_pos.y()))
            if self.scene():
                self.scene().update()
    
    def _do_resize(self, scene_pos: QPointF):
        delta = scene_pos - self._resize_start_pos
        handle = self._resize_handle
        
        orig_width = self._resize_start_rect.width()
        orig_height = self._resize_start_rect.height()
        orig_x = self._resize_start_x
        orig_y = self._resize_start_y
        
        dx = delta.x()
        dy = delta.y()
        
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
        self.update()
    
    def itemChange(self, change, value):
        if change == QGraphicsObject.GraphicsItemChange.ItemPositionChange and self.scene():
            new_pos = value
            if self._snap_to_grid:
                x = round(new_pos.x() / self._grid_size) * self._grid_size
                y = round(new_pos.y() / self._grid_size) * self._grid_size
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
    """设计器场景。"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._desktop_width = 800
        self._desktop_height = 600
        self.setSceneRect(-100, -100, self._desktop_width + 200, self._desktop_height + 200)
        self.setBackgroundBrush(QBrush(QColor("#1a1a1a")))
    
    @property
    def desktop_rect(self) -> QRectF:
        return QRectF(0, 0, self._desktop_width, self._desktop_height)
    
    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)
        painter.fillRect(rect, QColor("#1a1a1a"))
        painter.fillRect(self.desktop_rect, QColor("#f5f5f5"))
        painter.setPen(QPen(QColor("#333333"), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.desktop_rect)


class DesignerView(QGraphicsView):
    """设计器视图。"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = DesignerScene(self)
        self.setScene(self._scene)
        
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self._zoom_factor = 1.0
        self._items: Dict[str, ComponentGraphicsItem] = {}
    
    def showEvent(self, event):
        super().showEvent(event)
        self._fit_to_view()
    
    def _fit_to_view(self):
        if self.width() <= 0 or self.height() <= 0:
            return
        scale = min(self.width() / self._scene._desktop_width, 
                   self.height() / self._scene._desktop_height) * 0.9
        self.resetTransform()
        self.scale(scale, scale)
        self._zoom_factor = scale
        self.centerOn(self._scene._desktop_width / 2, self._scene._desktop_height / 2)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_to_view()
    
    def add_component_item(self, model: ComponentModel) -> ComponentGraphicsItem:
        if model.type == "container" and model.x == 0 and model.y == 0:
            center_x = (self._scene._desktop_width - model.width) / 2
            center_y = (self._scene._desktop_height - model.height) / 2
            model.x = int(center_x)
            model.y = int(center_y)
        
        item = ComponentGraphicsItem(model)
        self._scene.addItem(item)
        self._items[model.id] = item
        return item
    
    def remove_component_item(self, comp_id: str):
        if comp_id in self._items:
            self._scene.removeItem(self._items[comp_id])
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
    
    def clear(self):
        self._items.clear()
        self._scene.clear()
    
    def get_desktop_size(self) -> tuple:
        return (self._scene._desktop_width, self._scene._desktop_height)
    
    def zoom_in(self):
        self._zoom(1.2)
    
    def zoom_out(self):
        self._zoom(0.8)
    
    def zoom_reset(self):
        self._fit_to_view()
    
    def _zoom(self, factor: float):
        new_zoom = self._zoom_factor * factor
        if 0.1 <= new_zoom <= 4.0:
            self._zoom_factor = new_zoom
            self.scale(factor, factor)
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        event.accept()


# ==================== 属性面板 ====================

class PropertyPanel(QWidget):
    """属性面板。"""
    
    property_changed = Signal(str, str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_model: Optional[ComponentModel] = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        title = QLabel("属性面板")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._scroll.setWidget(self._content)
        layout.addWidget(self._scroll)
        
        self._no_selection = QLabel("请选择一个组件")
        self._no_selection.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_selection.setStyleSheet("color: #999;")
        self._content_layout.addWidget(self._no_selection)
    
    def set_model(self, model: Optional[ComponentModel]):
        self._current_model = model
        self._update_ui()
    
    def _update_ui(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self._current_model:
            label = QLabel("请选择一个组件")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #999;")
            self._content_layout.addWidget(label)
            return
        
        model = self._current_model
        
        name_edit = QLineEdit(model.name)
        name_edit.textChanged.connect(lambda v: self._update_property("name", v))
        self._add_row("名称:", name_edit)
        
        text_edit = QLineEdit(model.text)
        text_edit.textChanged.connect(lambda v: self._update_property("text", v))
        self._add_row("文本:", text_edit)
        
        x_spin = QSpinBox()
        x_spin.setRange(0, 9999)
        x_spin.setValue(model.x)
        x_spin.valueChanged.connect(lambda v: self._update_property("x", v))
        self._add_row("X:", x_spin)
        
        y_spin = QSpinBox()
        y_spin.setRange(0, 9999)
        y_spin.setValue(model.y)
        y_spin.valueChanged.connect(lambda v: self._update_property("y", v))
        self._add_row("Y:", y_spin)
        
        w_spin = QSpinBox()
        w_spin.setRange(20, 9999)
        w_spin.setValue(model.width)
        w_spin.valueChanged.connect(lambda v: self._update_property("width", v))
        self._add_row("宽度:", w_spin)
        
        h_spin = QSpinBox()
        h_spin.setRange(20, 9999)
        h_spin.setValue(model.height)
        h_spin.valueChanged.connect(lambda v: self._update_property("height", v))
        self._add_row("高度:", h_spin)
        
        self._content_layout.addStretch()
    
    def _add_row(self, label: str, widget: QWidget):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(widget)
        self._content_layout.addLayout(row)
    
    def _update_property(self, prop: str, value):
        if self._current_model:
            setattr(self._current_model, prop, value)
            self.property_changed.emit(self._current_model.id, prop, value)
    
    def clear(self):
        self._current_model = None
        self._update_ui()


# ==================== 逻辑树 ====================

class LogicTreeView(QWidget):
    """逻辑树视图。"""
    
    window_selected = Signal(str)
    component_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_model: Optional[ProjectModel] = None
        self._node_map: Dict[str, QTreeWidgetItem] = {}
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        title = QLabel("程序逻辑树")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.currentItemChanged.connect(self._on_item_changed)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree)
    
    def set_project_model(self, model: ProjectModel):
        self._project_model = model
        self._refresh()
    
    def _refresh(self):
        self._tree.clear()
        self._node_map.clear()
        
        if not self._project_model:
            return
        
        for window in self._project_model.windows.values():
            self._add_window_node(window)
    
    def _add_window_node(self, window: WindowModel):
        icon = "🏠" if window.is_main else "📄"
        item = QTreeWidgetItem(self._tree)
        item.setText(0, f"{icon} {window.name}")
        item.setData(0, Qt.ItemDataRole.UserRole, {"type": "window", "id": window.id})
        self._node_map[window.id] = item
        
        for comp in self._project_model.get_components_for_window(window.id):
            self._add_component_node(comp, item)
        
        self._tree.expandItem(item)
    
    def _add_component_node(self, comp: ComponentModel, parent_item: QTreeWidgetItem):
        icons = {"button": "🔘", "label": "📝", "input": "✏️", "container": "📦"}
        icon = icons.get(comp.type, "❓")
        
        item = QTreeWidgetItem(parent_item)
        item.setText(0, f"{icon} {comp.text or comp.name}")
        item.setData(0, Qt.ItemDataRole.UserRole, {"type": "component", "id": comp.id})
        self._node_map[comp.id] = item
    
    def _on_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        if not current:
            return
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == "window":
            self.window_selected.emit(data["id"])
        elif data["type"] == "component":
            self.component_selected.emit(data["id"])
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data["type"] != "component":
            return
        
        comp = self._project_model.components.get(data["id"])
        if comp and comp.type == "button" and hasattr(comp, "target_window_id") and comp.target_window_id:
            self.window_selected.emit(comp.target_window_id)
    
    def select_component(self, comp_id: str):
        if comp_id in self._node_map:
            self._tree.setCurrentItem(self._node_map[comp_id])


# ==================== 主窗口 ====================

class MainWindow(QMainWindow):
    """主窗口。"""
    
    add_component = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("傻瓜桌面开发工具")
        self.resize(1200, 800)
        
        self._project_model = ProjectModel()
        self._current_component: Optional[ComponentModel] = None
        
        self._init_ui()
        self._init_toolbar()
        self._init_statusbar()
    
    def _init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        
        self.logic_tree = LogicTreeView()
        self.logic_tree.set_project_model(self._project_model)
        self.logic_tree.component_selected.connect(self._on_component_selected)
        splitter.addWidget(self.logic_tree)
        
        self.designer_view = DesignerView()
        splitter.addWidget(self.designer_view)
        
        self.property_panel = PropertyPanel()
        self.property_panel.property_changed.connect(self._on_property_changed)
        splitter.addWidget(self.property_panel)
        
        splitter.setSizes([200, 700, 300])
    
    def _init_toolbar(self):
        toolbar = QToolBar("工具栏")
        self.addToolBar(toolbar)
        
        toolbar.addAction("新建", self._on_new)
        toolbar.addAction("保存", self._on_save)
        toolbar.addSeparator()
        toolbar.addAction("+容器", lambda: self._add_comp("container"))
        toolbar.addAction("+按钮", lambda: self._add_comp("button"))
        toolbar.addAction("+文本", lambda: self._add_comp("label"))
        toolbar.addAction("+输入框", lambda: self._add_comp("input"))
        toolbar.addSeparator()
        toolbar.addAction("运行", self._on_run)
    
    def _init_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("就绪")
    
    def _add_comp(self, comp_type: str):
        current_window = self._project_model.current_window
        if not current_window:
            return
        
        desktop_width, desktop_height = self.designer_view.get_desktop_size()
        
        container = None
        for c in self._project_model.get_components_for_window(current_window.id):
            if c.type == "container":
                container = c
                break
        
        if comp_type == "container":
            comp = ContainerModel()
        elif comp_type == "button":
            comp = ButtonModel()
        elif comp_type == "label":
            comp = LabelModel()
        elif comp_type == "input":
            comp = InputModel()
        else:
            return
        
        if comp_type == "container":
            comp.x = int((desktop_width - comp.width) / 2)
            comp.y = int((desktop_height - comp.height) / 2)
        else:
            if container:
                comp.x = container.x + 50
                comp.y = container.y + 50
                comp.parent_id = container.id
            else:
                comp.x = int((desktop_width - comp.width) / 2)
                comp.y = int((desktop_height - comp.height) / 2)
        
        self._project_model.add_component(comp, current_window.id)
        self.designer_view.add_component_item(comp)
        self._select_component(comp)
        self.logic_tree._refresh()
        self.statusBar().showMessage(f"添加: {comp.name}")
    
    def _select_component(self, comp: ComponentModel):
        self._current_component = comp
        self.designer_view.select_item(comp.id)
        self.property_panel.set_model(comp)
    
    def _on_component_selected(self, comp_id: str):
        comp = self._project_model.components.get(comp_id)
        if comp:
            self._select_component(comp)
    
    def _on_property_changed(self, comp_id: str, prop: str, value):
        item = self.designer_view.get_item(comp_id)
        if item:
            item.update()
        self.logic_tree._refresh()
    
    def _on_new(self):
        self._project_model = ProjectModel()
        self.designer_view.clear()
        self.property_panel.clear()
        self.logic_tree.set_project_model(self._project_model)
        self.statusBar().showMessage("新建项目")
    
    def _on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "保存项目", "", "项目文件 (*.fool)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._project_model.to_dict(), f, ensure_ascii=False, indent=2)
            self.statusBar().showMessage(f"已保存: {file_path}")
    
    def _on_run(self):
        self.statusBar().showMessage("运行功能开发中...")


# ==================== 入口 ====================

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
