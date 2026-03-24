"""流程图预览模块。

本模块提供项目流程图预览功能，展示窗口和事件之间的流转关系。
"""

from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGraphicsView, QGraphicsScene, QGraphicsItem
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QBrush, QColor, QPen, QFont, QPainter


class FlowNodeItem(QGraphicsItem):
    """流程图节点项。"""
    
    def __init__(self, node_id: str, name: str, node_type: str, parent=None):
        super().__init__(parent)
        self._node_id = node_id
        self._name = name
        self._node_type = node_type
        self._width = 120
        self._height = 60
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
    
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)
    
    def paint(self, painter: QPainter, option, widget):
        if self._node_type == "main":
            color = QColor("#4a90d9")
        else:
            color = QColor("#67c23a")
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawRoundedRect(0, 0, self._width, self._height, 8, 8)
        
        painter.setPen(QColor("#ffffff"))
        font = QFont("Microsoft YaHei", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, self._width, self._height), 
                        Qt.AlignmentFlag.AlignCenter, self._name)


class FlowPreviewWidget(QWidget):
    """流程图预览窗口。"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_data: Dict[str, Any] = {}
        self._nodes: Dict[str, FlowNodeItem] = {}
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setBackgroundBrush(QBrush(QColor("#f5f5f5")))
        layout.addWidget(self._view)
    
    def set_project_data(self, data: Dict[str, Any]):
        self._project_data = data
        self._refresh()
    
    def _refresh(self):
        self._scene.clear()
        self._nodes.clear()
        
        if not self._project_data:
            return
        
        windows = self._project_data.get('windows', [])
        x_offset = 50
        y_offset = 50
        
        for i, window in enumerate(windows):
            node = FlowNodeItem(
                window.get('id', ''),
                window.get('name', '窗口'),
                window.get('window_type', 'event')
            )
            node.setPos(x_offset + i * 150, y_offset)
            self._scene.addItem(node)
            self._nodes[window.get('id', '')] = node
    
    def zoom_in(self):
        self._view.scale(1.2, 1.2)
    
    def zoom_out(self):
        self._view.scale(0.8, 0.8)
    
    def zoom_reset(self):
        self._view.resetTransform()


class FlowPreviewWindow(QWidget):
    """流程图预览窗口。"""
    
    def __init__(self, project_data: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self._project_data = project_data or {}
        self._init_ui()
        
        if project_data:
            self._flow_view.set_project_data(project_data)
    
    def _init_ui(self):
        self.setWindowTitle("流程图预览")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        toolbar = QHBoxLayout()
        
        zoom_in_btn = QPushButton("放大")
        zoom_in_btn.clicked.connect(self._on_zoom_in)
        toolbar.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("缩小")
        zoom_out_btn.clicked.connect(self._on_zoom_out)
        toolbar.addWidget(zoom_out_btn)
        
        zoom_reset_btn = QPushButton("重置")
        zoom_reset_btn.clicked.connect(self._on_zoom_reset)
        toolbar.addWidget(zoom_reset_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self._flow_view = FlowPreviewWidget()
        layout.addWidget(self._flow_view)
    
    def _on_zoom_in(self):
        self._flow_view.zoom_in()
    
    def _on_zoom_out(self):
        self._flow_view.zoom_out()
    
    def _on_zoom_reset(self):
        self._flow_view.zoom_reset()
    
    def set_project_data(self, data: Dict[str, Any]):
        self._project_data = data
        self._flow_view.set_project_data(data)
