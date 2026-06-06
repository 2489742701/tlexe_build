"""画布Presenter模块。

本模块负责管理画布视图与组件模型之间的交互。

## 职责
1. 订阅组件模型信号，桥接到EventBus
2. 订阅EventBus事件，更新视图
3. 处理视图事件，更新模型

## 事件流
视图事件 → Presenter → Model → EventBus → 其他视图

## 使用示例
```python
from presenters import CanvasPresenter

# 在ProjectController中创建
self.canvas_presenter = CanvasPresenter(
    canvas_view=self.window.designer_view,
    project_model=self.project_model
)
```
"""

from PySide6.QtCore import QObject, QPointF
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models import ProjectModel, ComponentModel
    from views.canvas import DesignerView


class CanvasPresenter(QObject):
    """画布Presenter。
    
    管理CanvasView与ComponentModel之间的交互。
    作为视图和模型之间的中介，通过EventBus实现解耦。
    
    ## 架构角色
    
    在MVP架构中，Presenter负责：
    - 订阅视图的用户交互信号
    - 更新模型数据
    - 订阅模型变化，发布EventBus事件
    - 订阅EventBus事件，更新视图
    
    ## 信号流向
    
    ```
    用户操作 → View信号 → Presenter → Model更新
                              ↓
                         EventBus事件 → 其他View/Presenter
    ```
    
    Attributes:
        _canvas_view: 画布视图引用
        _project_model: 项目数据模型引用
        _component_connections: 组件信号连接记录
    """
    
    def __init__(self, canvas_view: 'DesignerView', project_model: 'ProjectModel', parent=None):
        """初始化画布Presenter。
        
        Args:
            canvas_view: 画布视图实例
            project_model: 项目数据模型实例
            parent: 父对象（可选）
        """
        super().__init__(parent)
        self._canvas_view = canvas_view
        self._project_model = project_model
        self._component_connections: Dict[str, Dict[str, Any]] = {}
        
        self._setup_model_listeners()
        self._setup_event_bus_listeners()
        self._setup_view_listeners()
    
    def _setup_model_listeners(self):
        """设置模型信号监听，桥接到EventBus。
        
        监听项目模型的变化，当组件添加或移除时，
        自动连接或断开组件信号，并将事件桥接到EventBus。
        """
        for comp in self._project_model.get_all_components():
            self._connect_component_signals(comp)
        
        self._project_model.component_added.connect(self._on_component_added)
        self._project_model.component_removed.connect(self._on_component_removed)
    
    def _connect_component_signals(self, comp: 'ComponentModel'):
        """连接单个组件的信号到EventBus。
        
        将组件的位置和大小变化信号桥接到EventBus事件。
        
        Args:
            comp: 要连接信号的组件模型
        """
        if comp.id in self._component_connections:
            return
        
        from eventbus import event_bus, ComponentMovedEvent, ComponentResizedEvent
        
        def on_position_changed(x: int, y: int, component_id: str = comp.id):
            """位置变化回调，发布ComponentMovedEvent。"""
            event = ComponentMovedEvent(component_id, x, y)
            event_bus.publish(event_bus.component_moved, event)
        
        def on_size_changed(width: int, height: int, component_id: str = comp.id):
            """大小变化回调，发布ComponentResizedEvent。"""
            event = ComponentResizedEvent(component_id, width, height)
            event_bus.publish(event_bus.component_resized, event)
        
        comp.position_changed.connect(on_position_changed)
        comp.size_changed.connect(on_size_changed)
        
        self._component_connections[comp.id] = {
            'position': on_position_changed,
            'size': on_size_changed
        }
        
        from models.components import ContainerModel
        if isinstance(comp, ContainerModel):
            def on_data_changed(component_id: str = comp.id):
                c = self._project_model.get_component(component_id)
                if c and isinstance(c, ContainerModel) and getattr(c, 'layout', 'none') != 'none':
                    from services.layout import LayoutEngine
                    engine = LayoutEngine(self._project_model)
                    engine.relayout(c)
            
            comp.data_changed.connect(on_data_changed)
            self._component_connections[comp.id]['data_changed'] = on_data_changed
    
    def _disconnect_component_signals(self, comp_id: str):
        """断开组件信号连接。
        
        当组件被删除时，断开其信号连接并清理资源。
        
        Args:
            comp_id: 要断开连接的组件ID
        """
        if comp_id not in self._component_connections:
            return
        
        comp = self._project_model.get_component(comp_id)
        if comp:
            conn = self._component_connections[comp_id]
            try:
                comp.position_changed.disconnect(conn['position'])
                comp.size_changed.disconnect(conn['size'])
            except RuntimeError:
                pass
        
        del self._component_connections[comp_id]
    
    def _on_component_added(self, comp_id: str):
        """组件添加时的处理。
        
        当新组件添加到项目时，连接其信号并发布创建事件。
        
        Args:
            comp_id: 新添加的组件ID
        """
        comp = self._project_model.get_component(comp_id)
        if comp:
            self._connect_component_signals(comp)
            
            from eventbus import event_bus
            event_bus.component_created.emit(comp_id)
    
    def _on_component_removed(self, comp_id: str):
        """组件删除时的处理。
        
        当组件从项目中移除时，断开其信号并发布删除事件。
        
        Args:
            comp_id: 被删除的组件ID
        """
        self._disconnect_component_signals(comp_id)
        
        from eventbus import event_bus
        event_bus.component_deleted.emit(comp_id)
    
    def _setup_event_bus_listeners(self):
        """设置EventBus事件监听。
        
        订阅EventBus上的组件事件，更新画布视图。
        """
        from eventbus import event_bus
        
        event_bus.component_moved.connect(self._on_component_moved_event)
        event_bus.component_resized.connect(self._on_component_resized_event)
    
    def _on_component_moved_event(self, event):
        """处理组件移动事件。
        
        当EventBus发布组件移动事件时，更新画布上对应图形项的位置。
        
        Args:
            event: ComponentMovedEvent实例
        """
        item = self._canvas_view.get_item(event.component_id)
        if item:
            item.setPos(QPointF(event.x, event.y))
            item.update()
    
    def _on_component_resized_event(self, event):
        """处理组件调整大小事件。
        
        当EventBus发布组件调整大小事件时，更新画布上对应图形项。
        
        Args:
            event: ComponentResizedEvent实例
        """
        comp = self._project_model.get_component(event.component_id)
        if comp:
            item = self._canvas_view.get_item(event.component_id)
            if item:
                item.update()
    
    def _setup_view_listeners(self):
        """设置视图信号监听。
        
        订阅画布视图的用户交互信号，更新模型数据。
        """
        if hasattr(self._canvas_view, 'component_dragged'):
            self._canvas_view.component_dragged.connect(self._on_view_component_dragged)
        
        if hasattr(self._canvas_view, 'component_moved'):
            self._canvas_view.component_moved.connect(self._on_view_component_moved)
        
        if hasattr(self._canvas_view, 'component_resized'):
            self._canvas_view.component_resized.connect(self._on_view_component_resized)
        
        if hasattr(self._canvas_view, 'component_selected'):
            self._canvas_view.component_selected.connect(self._on_view_component_selected)
    
    def _on_view_component_dragged(self, comp_id: str, dx: float, dy: float):
        """处理视图组件拖拽中事件。
        
        用户正在拖拽组件时调用，可用于实时更新UI。
        
        Args:
            comp_id: 被拖拽的组件ID
            dx: X方向移动量
            dy: Y方向移动量
        """
        pass
    
    def _on_view_component_moved(self, comp_id: str, x: int, y: int):
        """处理视图组件移动完成事件。
        
        用户完成组件拖拽时调用，更新模型数据。
        
        Args:
            comp_id: 被移动的组件ID
            x: 新的X坐标
            y: 新的Y坐标
        """
        comp = self._project_model.get_component(comp_id)
        if comp:
            comp.set_position(x, y)
    
    def _on_view_component_resized(self, comp_id: str, width: int, height: int):
        """处理视图组件调整大小事件。
        
        用户调整组件大小时调用，更新模型数据。
        
        Args:
            comp_id: 被调整的组件ID
            width: 新的宽度
            height: 新的高度
        """
        comp = self._project_model.get_component(comp_id)
        if comp:
            comp.set_size(width, height)
    
    def _on_view_component_selected(self, comp_id: str):
        """处理视图组件选中事件。
        
        用户选中组件时调用，发布EventBus选中事件。
        
        Args:
            comp_id: 被选中的组件ID
        """
        from eventbus import event_bus
        event_bus.component_selected.emit(comp_id)
    
    def cleanup(self):
        """清理资源。
        
        断开所有信号连接，释放资源。
        在销毁Presenter前调用。
        """
        from eventbus import event_bus
        
        try:
            event_bus.component_moved.disconnect(self._on_component_moved_event)
            event_bus.component_resized.disconnect(self._on_component_resized_event)
        except RuntimeError:
            pass
        
        for comp_id in list(self._component_connections.keys()):
            self._disconnect_component_signals(comp_id)
        
        self._component_connections.clear()
