"""状态机视图模块。

本模块包含状态机图/蓝图编辑器的实现。
支持节点拖拽、连线、缩放、平移等功能。

## 功能说明
- 节点系统：每个状态是一个可拖拽的方框节点
- 连接系统：节点之间可以有连线，表示状态流转
- 交互功能：拖拽、缩放、平移、右键菜单、双击编辑
- 与现有系统集成：WindowModel 和 ButtonModel

## 使用方式
- 模态弹窗：dialog.exec() - 阻塞父窗口直到关闭
- 非模态弹窗：dialog.show() - 不阻塞父窗口
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsPathItem, QGraphicsTextItem, QMenu, QInputDialog, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QGraphicsObject
)
from PySide6.QtCore import (
    Qt, Signal, QPointF, QRectF, QMarginsF, QUuid, QObject
)
from PySide6.QtGui import (
    QPainter, QPainterPath, QPen, QBrush, QColor, QFont, 
    QTransform, QCursor
)

if TYPE_CHECKING:
    from models import ProjectModel, WindowModel, ButtonModel

@dataclass
class StateNodeData:
    """状态节点数据。
    
    Attributes:
        id: 节点唯一标识符
        name: 节点显示名称
        x: 节点在场景中的X坐标
        y: 节点在场景中的Y坐标
        window_id: 关联的窗口ID（可选）
        is_main: 是否为主窗口节点
    """
    id: str
    name: str
    x: float
    y: float
    window_id: Optional[str] = None
    is_main: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "window_id": self.window_id,
            "is_main": self.is_main
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StateNodeData":
        return cls(
            id=data["id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
            window_id=data.get("window_id"),
            is_main=data.get("is_main", False)
        )

@dataclass
class TransitionData:
    """转换连线数据。
    
    Attributes:
        id: 连线唯一标识符
        source_node_id: 源节点ID
        target_node_id: 目标节点ID
        trigger_button_id: 触发按钮ID（可选）
        label: 连线标签（可选）
    """
    id: str
    source_node_id: str
    target_node_id: str
    trigger_button_id: Optional[str] = None
    label: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "trigger_button_id": self.trigger_button_id,
            "label": self.label
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TransitionData":
        return cls(
            id=data["id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            trigger_button_id=data.get("trigger_button_id"),
            label=data.get("label", "")
        )

@dataclass
class StateMachineModel:
    """状态机数据模型。
    
    Attributes:
        nodes: 节点列表
        transitions: 连线列表
    """
    nodes: List[StateNodeData] = field(default_factory=list)
    transitions: List[TransitionData] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "transitions": [t.to_dict() for t in self.transitions]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StateMachineModel":
        return cls(
            nodes=[StateNodeData.from_dict(n) for n in data.get("nodes", [])],
            transitions=[TransitionData.from_dict(t) for t in data.get("transitions", [])]
        )

    def get_node(self, node_id: str) -> Optional[StateNodeData]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_node_by_window(self, window_id: str) -> Optional[StateNodeData]:
        for node in self.nodes:
            if node.window_id == window_id:
                return node
        return None

class PortItem(QGraphicsEllipseItem):
    """端口图形项 - 节点上的连接点。
    
    用于连线的起点和终点，支持悬停高亮效果。
    """

    PORT_SIZE = 12

    class PortType:
        INPUT = "input"
        OUTPUT = "output"

    def __init__(self, port_type: str, parent=None):
        super().__init__(parent)
        self._port_type = port_type
        self._connections: List["ConnectionItem"] = []

        self.setRect(-self.PORT_SIZE / 2, -self.PORT_SIZE / 2, self.PORT_SIZE, self.PORT_SIZE)
        self.setBrush(QBrush(QColor("#4CAF50")))
        self.setPen(QPen(QColor("#2E7D32"), 1.5))
        self.setAcceptHoverEvents(True)
        self.setZValue(100)

    @property
    def port_type(self) -> str:
        return self._port_type

    def add_connection(self, connection: "ConnectionItem"):
        if connection not in self._connections:
            self._connections.append(connection)

    def remove_connection(self, connection: "ConnectionItem"):
        if connection in self._connections:
            self._connections.remove(connection)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor("#81C784")))
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor("#4CAF50")))
        super().hoverLeaveEvent(event)

class StateNodeItem(QGraphicsObject):
    """状态节点图形项 - 可拖拽的方框节点。
    
    功能：
    1. 支持拖拽移动
    2. 支持右键菜单
    3. 支持双击编辑
    4. 移动时自动通知连线刷新
    
    Signals:
        edit_requested: 双击请求编辑时发射
        delete_requested: 右键菜单删除时发射
    """

    NODE_WIDTH = 180
    NODE_HEIGHT = 80
    HEADER_HEIGHT = 28
    CORNER_RADIUS = 8

    edit_requested = Signal()
    delete_requested = Signal()

    def __init__(self, node_data: StateNodeData, parent=None):
        super().__init__(parent)
        self._node_data = node_data
        self._input_port: Optional[PortItem] = None
        self._output_port: Optional[PortItem] = None
        self._title_item: Optional[QGraphicsTextItem] = None
        self._brush = QBrush(QColor("#424242"))
        self._pen = QPen(QColor("#757575"), 1)

        self.setPos(node_data.x, node_data.y)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)

        self._setup_ui()
        self._update_style()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.NODE_WIDTH, self.NODE_HEIGHT)

    def _setup_ui(self):
        self._title_item = QGraphicsTextItem(self)
        self._title_item.setDefaultTextColor(QColor("#FFFFFF"))
        font = QFont("Microsoft YaHei", 10, QFont.Weight.Bold)
        self._title_item.setFont(font)
        self._title_item.setPos(10, 6)
        self._update_title()

        if not self._node_data.is_main:
            self._input_port = PortItem(PortItem.PortType.INPUT, self)
            self._input_port.setPos(0, self.NODE_HEIGHT / 2)

        self._output_port = PortItem(PortItem.PortType.OUTPUT, self)
        self._output_port.setPos(self.NODE_WIDTH, self.NODE_HEIGHT / 2)

    def _update_title(self):
        icon = "🏠" if self._node_data.is_main else "📄"
        self._title_item.setPlainText(f"{icon} {self._node_data.name}")

    def _update_style(self):
        if self._node_data.is_main:
            gradient_color = QColor("#1976D2")
        else:
            gradient_color = QColor("#424242")

        self._brush = QBrush(gradient_color)
        self._pen = QPen(QColor("#757575"), 1)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        rect = self.boundingRect()
        path.addRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)

        if self.isSelected():
            painter.setPen(QPen(QColor("#2196F3"), 3))
        else:
            painter.setPen(self._pen)

        painter.setBrush(self._brush)
        painter.drawPath(path)

        header_rect = QRectF(0, 0, self.NODE_WIDTH, self.HEADER_HEIGHT)
        header_path = QPainterPath()
        header_path.moveTo(self.CORNER_RADIUS, 0)
        header_path.lineTo(self.NODE_WIDTH - self.CORNER_RADIUS, 0)
        header_path.quadTo(self.NODE_WIDTH, 0, self.NODE_WIDTH, self.CORNER_RADIUS)
        header_path.lineTo(self.NODE_WIDTH, self.HEADER_HEIGHT)
        header_path.lineTo(0, self.HEADER_HEIGHT)
        header_path.lineTo(0, self.CORNER_RADIUS)
        header_path.quadTo(0, 0, self.CORNER_RADIUS, 0)

        if self._node_data.is_main:
            header_color = QColor("#1565C0")
        else:
            header_color = QColor("#616161")

        painter.setBrush(QBrush(header_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(header_path)

    def itemChange(self, change, value):
        if change == QGraphicsObject.GraphicsItemChange.ItemPositionHasChanged:
            self._node_data.x = self.pos().x()
            self._node_data.y = self.pos().y()
            self._update_connections()
        return super().itemChange(change, value)

    def _update_connections(self):
        if self._input_port:
            for conn in self._input_port._connections:
                conn.update_path()
        if self._output_port:
            for conn in self._output_port._connections:
                conn.update_path()

    def mouseDoubleClickEvent(self, event):
        self.edit_requested.emit()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        edit_action = menu.addAction("✏️ 编辑节点")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ 删除节点")
        
        chosen = menu.exec(event.screenPos())
        if chosen == edit_action:
            self.edit_requested.emit()
        elif chosen == delete_action:
            self.delete_requested.emit()

    @property
    def node_data(self) -> StateNodeData:
        return self._node_data

    @property
    def input_port(self) -> Optional[PortItem]:
        return self._input_port

    @property
    def output_port(self) -> Optional[PortItem]:
        return self._output_port

    def update_name(self, name: str):
        self._node_data.name = name
        self._update_title()

class ConnectionItem(QGraphicsPathItem):
    """连接线图形项 - 贝塞尔曲线。
    
    用于连接两个状态节点，支持悬停高亮效果。
    """

    def __init__(self, conn_data: TransitionData, 
                 source_node: StateNodeItem, target_node: StateNodeItem,
                 parent=None):
        super().__init__(parent)
        self._conn_data = conn_data
        self._source_node = source_node
        self._target_node = target_node
        self._label_item: Optional[QGraphicsTextItem] = None

        self.setPen(QPen(QColor("#4CAF50"), 2.5))
        self.setZValue(-1)
        self.setAcceptHoverEvents(True)

        if source_node.output_port:
            source_node.output_port.add_connection(self)
        if target_node.input_port:
            target_node.input_port.add_connection(self)

        self._label_item = QGraphicsTextItem(self)
        self._label_item.setDefaultTextColor(QColor("#FFFFFF"))
        font = QFont("Microsoft YaHei", 8)
        self._label_item.setFont(font)

        self.update_path()

    def update_path(self):
        if not self._source_node.output_port or not self._target_node.input_port:
            return

        start = self._source_node.output_port.scenePos()
        end = self._target_node.input_port.scenePos()

        path = QPainterPath()
        path.moveTo(start)

        dx = abs(end.x() - start.x())
        ctrl_offset = max(50, dx * 0.4)

        ctrl1 = QPointF(start.x() + ctrl_offset, start.y())
        ctrl2 = QPointF(end.x() - ctrl_offset, end.y())
        path.cubicTo(ctrl1, ctrl2, end)

        self.setPath(path)

        if self._conn_data.label:
            mid_point = path.pointAtPercent(0.5)
            self._label_item.setPos(mid_point)
            self._label_item.setPlainText(self._conn_data.label)
            self._label_item.setVisible(True)
        else:
            self._label_item.setVisible(False)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        shadow_path = self.path()
        painter.setPen(QPen(QColor("#000000"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setOpacity(0.2)
        painter.drawPath(shadow_path)

        painter.setOpacity(1.0)
        super().paint(painter, option, widget)

    def hoverEnterEvent(self, event):
        self.setPen(QPen(QColor("#81C784"), 3))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(QPen(QColor("#4CAF50"), 2.5))
        super().hoverLeaveEvent(event)

    @property
    def conn_data(self) -> TransitionData:
        return self._conn_data

    def set_label(self, label: str):
        self._conn_data.label = label
        self.update_path()

class BlueprintScene(QGraphicsScene):
    """蓝图场景 - 管理所有图形项。
    
    Signals:
        node_selected: 节点被选中时发射
        node_double_clicked: 节点被双击时发射
        node_edit_requested: 请求编辑节点时发射
        node_delete_requested: 请求删除节点时发射
        empty_area_clicked: 点击空白区域时发射
    """

    node_selected = Signal(str)
    node_double_clicked = Signal(str)
    node_edit_requested = Signal(str)
    node_delete_requested = Signal(str)
    empty_area_clicked = Signal()
    create_node_requested = Signal(QPointF)

    GRID_SIZE = 20
    GRID_COLOR = QColor("#E0E0E0")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nodes: Dict[str, StateNodeItem] = {}
        self._connections: Dict[str, ConnectionItem] = {}
        self._project_model = None

        self.setSceneRect(-5000, -5000, 10000, 10000)

    def set_project_model(self, model):
        self._project_model = model

    def add_node(self, node_data: StateNodeData) -> StateNodeItem:
        if node_data.id in self._nodes:
            return self._nodes[node_data.id]

        node = StateNodeItem(node_data)
        
        node.edit_requested.connect(lambda: self.node_edit_requested.emit(node_data.id))
        node.delete_requested.connect(lambda: self.node_delete_requested.emit(node_data.id))
        
        self.addItem(node)
        self._nodes[node_data.id] = node
        return node

    def remove_node(self, node_id: str):
        if node_id not in self._nodes:
            return

        node = self._nodes[node_id]

        conns_to_remove = []
        if node.input_port:
            conns_to_remove.extend(node.input_port._connections)
        if node.output_port:
            conns_to_remove.extend(node.output_port._connections)

        for conn in conns_to_remove:
            self.remove_connection(conn.conn_data.id)

        self.removeItem(node)
        del self._nodes[node_id]

    def add_connection(self, conn_data: TransitionData) -> Optional[ConnectionItem]:
        if conn_data.id in self._connections:
            return self._connections[conn_data.id]

        source_node = self._nodes.get(conn_data.source_node_id)
        target_node = self._nodes.get(conn_data.target_node_id)

        if not source_node or not target_node:
            return None

        conn = ConnectionItem(conn_data, source_node, target_node)
        self.addItem(conn)
        self._connections[conn_data.id] = conn
        return conn

    def remove_connection(self, conn_id: str):
        if conn_id not in self._connections:
            return

        conn = self._connections[conn_id]
        self.removeItem(conn)
        del self._connections[conn_id]

    def get_node(self, node_id: str) -> Optional[StateNodeItem]:
        return self._nodes.get(node_id)

    def get_node_at(self, pos: QPointF) -> Optional[StateNodeItem]:
        items = self.items(pos)
        for item in items:
            if isinstance(item, StateNodeItem):
                return item
        return None

    def clear_all(self):
        self.clear()
        self._nodes.clear()
        self._connections.clear()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)

        painter.setPen(QPen(self.GRID_COLOR, 0.5))

        left = int(rect.left()) - (int(rect.left()) % self.GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % self.GRID_SIZE)

        x = left
        while x < rect.right():
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += self.GRID_SIZE

        y = top
        while y < rect.bottom():
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += self.GRID_SIZE

    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if not isinstance(item, (StateNodeItem, PortItem, ConnectionItem)):
            menu = QMenu()
            create_action = menu.addAction("➕ 创建新节点")
            chosen = menu.exec(event.screenPos())
            if chosen == create_action:
                self.create_node_requested.emit(event.scenePos())
            event.accept()
            return
        super().contextMenuEvent(event)

class BlueprintView(QGraphicsView):
    """蓝图视图 - 实现缩放、平移等功能。
    
    交互设计：
    - Ctrl + 滚轮：缩放
    - 中键拖动：平移
    - Delete：删除选中项
    """

    MIN_ZOOM = 0.25
    MAX_ZOOM = 3.0
    ZOOM_STEP = 0.1

    zoom_changed = Signal(float)

    def __init__(self, scene: BlueprintScene, parent=None):
        super().__init__(scene, parent)
        self._scene = scene
        self._zoom_level = 1.0
        self._pan_mode = False
        self._last_pan_pos = QPointF()

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor("#FAFAFA")))

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_mode = True
            self._last_pan_pos = event.position()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan_mode:
            delta = event.position() - self._last_pan_pos
            self._last_pan_pos = event.position()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_mode = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self._delete_selected_items()
        else:
            super().keyPressEvent(event)

    def _delete_selected_items(self):
        for item in self._scene.selectedItems():
            if isinstance(item, StateNodeItem):
                self._scene.remove_node(item.node_data.id)

    def zoom_in(self):
        if self._zoom_level < self.MAX_ZOOM:
            self._zoom_level += self.ZOOM_STEP
            self._apply_zoom()

    def zoom_out(self):
        if self._zoom_level > self.MIN_ZOOM:
            self._zoom_level -= self.ZOOM_STEP
            self._apply_zoom()

    def zoom_reset(self):
        self._zoom_level = 1.0
        self._apply_zoom()

    def _apply_zoom(self):
        self.setTransform(QTransform().scale(self._zoom_level, self._zoom_level))
        self.zoom_changed.emit(self._zoom_level)

    def fit_to_view(self):
        if not self._scene._nodes:
            return

        items = list(self._scene._nodes.values())
        rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            rect = rect.united(item.sceneBoundingRect())

        rect = rect.marginsAdded(QMarginsF(50, 50, 50, 50))
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_level = self.transform().m11()

class StateMachineDialog(QDialog):
    """状态机视图弹窗。
    
    用于可视化展示窗口之间的流转关系，支持节点拖拽、连线、缩放、平移等功能。
    与 LogicTreeView 共享 ProjectModel 数据。
    
    ## 使用方式
    
    ### 模态弹窗（阻塞父窗口）
    ```python
    dialog = StateMachineDialog(project_model, parent)
    dialog.exec()  # 阻塞直到关闭
    ```
    
    ### 非模态弹窗（不阻塞父窗口）
    ```python
    dialog = StateMachineDialog(project_model, parent)
    dialog.show()  # 不阻塞
    ```
    
    ## 信号说明
    
    ### 输出信号（本组件发射）
    - window_selected(str): 选中窗口时发射，参数为 window_id
        - 接收者：MainWindow._on_logic_window_selected
        - 用途：切换当前窗口
        
    - create_event_requested(str): 请求创建事件时发射，参数为 button_id
        - 接收者：MainWindow._on_create_event_requested
        - 用途：创建事件分支
        
    - node_moved(str, float, float): 节点移动时发射，参数为 node_id, x, y
        - 用途：保存节点位置
    
    ### 输入方法（由外部调用）
    - set_project_model(model): 设置项目模型
        - 调用者：MainWindow
        - 用途：初始化状态机视图数据
    """
    
    window_selected = Signal(str)
    create_event_requested = Signal(str)
    node_moved = Signal(str, float, float)

    def __init__(self, project_model=None, parent=None):
        super().__init__(parent)
        self._project_model = project_model
        self._state_model = StateMachineModel()
        self._node_window_map: Dict[str, str] = {}

        self._setup_ui()
        self._connect_signals()
        
        if project_model:
            self._refresh_graph()

    def _setup_ui(self):
        self.setWindowTitle("📊 状态机视图")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scene = BlueprintScene()
        self._view = BlueprintView(self._scene)

        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        layout.addWidget(self._view, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

    def _create_toolbar(self) -> QWidget:
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #fafafa; border-bottom: 1px solid #ddd;")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        btn_zoom_in = QPushButton("➕")
        btn_zoom_in.setFixedSize(28, 28)
        btn_zoom_in.setToolTip("放大 (Ctrl+滚轮向上)")
        btn_zoom_in.clicked.connect(self._view.zoom_in)
        layout.addWidget(btn_zoom_in)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setFixedWidth(45)
        self._zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self._zoom_label)

        btn_zoom_out = QPushButton("➖")
        btn_zoom_out.setFixedSize(28, 28)
        btn_zoom_out.setToolTip("缩小 (Ctrl+滚轮向下)")
        btn_zoom_out.clicked.connect(self._view.zoom_out)
        layout.addWidget(btn_zoom_out)

        btn_fit = QPushButton("适应")
        btn_fit.setFixedHeight(28)
        btn_fit.setToolTip("适应窗口")
        btn_fit.clicked.connect(self._view.fit_to_view)
        layout.addWidget(btn_fit)

        btn_reset = QPushButton("重置")
        btn_reset.setFixedHeight(28)
        btn_reset.setToolTip("重置缩放")
        btn_reset.clicked.connect(self._view.zoom_reset)
        layout.addWidget(btn_reset)

        layout.addStretch()

        btn_auto_layout = QPushButton("📐 自动布局")
        btn_auto_layout.setFixedHeight(28)
        btn_auto_layout.setToolTip("自动排列节点")
        btn_auto_layout.clicked.connect(self._auto_layout)
        layout.addWidget(btn_auto_layout)

        return toolbar

    def _connect_signals(self):
        self._view.zoom_changed.connect(self._on_zoom_changed)
        self._scene.node_edit_requested.connect(self._on_node_edit)
        self._scene.node_delete_requested.connect(self._on_node_delete)
        self._scene.create_node_requested.connect(self._on_create_node)

    def _on_zoom_changed(self, level: float):
        self._zoom_label.setText(f"{int(level * 100)}%")

    def _on_node_edit(self, node_id: str):
        node = self._scene.get_node(node_id)
        if not node:
            return
        
        new_name, ok = QInputDialog.getText(
            self, "编辑节点", "节点名称:", 
            text=node.node_data.name
        )
        if ok and new_name.strip():
            node.update_name(new_name.strip())

    def _on_node_delete(self, node_id: str):
        node = self._scene.get_node(node_id)
        if not node:
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除节点 \"{node.node_data.name}\" 吗？\n相关的连线也会被删除。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._scene.remove_node(node_id)

    def _on_create_node(self, pos: QPointF):
        name, ok = QInputDialog.getText(self, "创建节点", "节点名称:")
        if ok and name.strip():
            node_id = str(QUuid.createUuid())
            node_data = StateNodeData(
                id=node_id,
                name=name.strip(),
                x=pos.x(),
                y=pos.y()
            )
            self._state_model.nodes.append(node_data)
            self._scene.add_node(node_data)

    def set_project_model(self, model):
        self._project_model = model
        self._scene.set_project_model(model)
        self._refresh_graph()

    def _refresh_graph(self):
        if not self._project_model:
            return

        self._scene.clear_all()
        self._state_model = StateMachineModel()
        self._node_window_map.clear()

        main_window = self._project_model.get_main_window()
        if main_window:
            self._build_graph_from_window(main_window, None, 400, 50, 0)

        self._view.fit_to_view()

    def _build_graph_from_window(self, window, parent_node_id, x, y, depth):
        if window.id in self._node_window_map:
            return

        node_id = str(QUuid.createUuid())
        node_data = StateNodeData(
            id=node_id,
            name=window.name,
            x=x,
            y=y,
            window_id=window.id,
            is_main=window.is_main
        )

        self._state_model.nodes.append(node_data)
        self._node_window_map[window.id] = node_id

        node_item = self._scene.add_node(node_data)

        if parent_node_id:
            conn_id = str(QUuid.createUuid())
            conn_data = TransitionData(
                id=conn_id,
                source_node_id=parent_node_id,
                target_node_id=node_id
            )
            self._state_model.transitions.append(conn_data)
            self._scene.add_connection(conn_data)

        components = self._project_model.get_components_for_window(window.id)
        buttons = [c for c in components if c.type == "button" and c.target_window_id]

        for i, button in enumerate(buttons):
            target_window = self._project_model.get_window(button.target_window_id)
            if target_window:
                child_x = x + (i - len(buttons) / 2 + 0.5) * 250
                child_y = y + 150

                self._build_graph_from_window(target_window, node_id, child_x, child_y, depth + 1)

    def _auto_layout(self):
        if not self._state_model.nodes:
            return

        main_node = None
        for node in self._state_model.nodes:
            if node.is_main:
                main_node = node
                break

        if main_node:
            self._layout_node(main_node, 400, 50, 0)

        for node_item in self._scene._nodes.values():
            node_item.setPos(node_item.node_data.x, node_item.node_data.y)
            node_item._update_connections()

    def _layout_node(self, node_data: StateNodeData, x: float, y: float, depth: int):
        node_data.x = x
        node_data.y = y

        child_nodes = []
        for trans in self._state_model.transitions:
            if trans.source_node_id == node_data.id:
                target = self._state_model.get_node(trans.target_node_id)
                if target:
                    child_nodes.append(target)

        for i, child in enumerate(child_nodes):
            child_x = x + (i - len(child_nodes) / 2 + 0.5) * 250
            child_y = y + 150
            self._layout_node(child, child_x, child_y, depth + 1)

    def get_state_data(self) -> dict:
        return self._state_model.to_dict()

    def load_state_data(self, data: dict):
        self._state_model = StateMachineModel.from_dict(data)

        self._scene.clear_all()

        for node_data in self._state_model.nodes:
            self._scene.add_node(node_data)
            if node_data.window_id:
                self._node_window_map[node_data.window_id] = node_data.id

        for conn_data in self._state_model.transitions:
            self._scene.add_connection(conn_data)

# 保持向后兼容
StateMachineView = StateMachineDialog
