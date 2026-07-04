"""EventBus模块。

本模块提供统一的事件总线，实现模块间解耦通信。

## 设计原则
1. **类型安全**：使用事件类封装参数
2. **统一接口**：提供subscribe/publish方法
3. **向后兼容**：保留原有Signal参数格式

## 事件流
Model信号 → Presenter → EventBus → View/其他Presenter

## 使用示例
```python
from eventbus.event_bus import event_bus, ComponentMovedEvent

# 订阅事件
event_bus.component_moved.connect(self.on_component_moved)

# 发布事件
event = ComponentMovedEvent("btn_1", 100, 200)
event_bus.publish(event_bus.component_moved, event)
```
"""

from PySide6.QtCore import QObject, Signal
from typing import Any, Callable, Dict, List, Optional

class ComponentEvent:
    """组件事件基类。
    
    所有组件相关事件的基类，包含组件ID。
    
    Attributes:
        component_id: 组件唯一标识符
    """
    
    def __init__(self, component_id: str):
        self.component_id = component_id

class ComponentMovedEvent(ComponentEvent):
    """组件移动事件。
    
    当组件位置发生变化时触发。
    
    Attributes:
        x: 新的X坐标
        y: 新的Y坐标
    """
    
    def __init__(self, component_id: str, x: int, y: int):
        super().__init__(component_id)
        self.x = x
        self.y = y

class ComponentResizedEvent(ComponentEvent):
    """组件调整大小事件。
    
    当组件尺寸发生变化时触发。
    
    Attributes:
        width: 新的宽度
        height: 新的高度
    """
    
    def __init__(self, component_id: str, width: int, height: int):
        super().__init__(component_id)
        self.width = width
        self.height = height

class ComponentCreatedEvent(ComponentEvent):
    """组件创建事件。
    
    当新组件被添加到项目时触发。
    """
    pass

class ComponentDeletedEvent(ComponentEvent):
    """组件删除事件。
    
    当组件从项目中移除时触发。
    """
    pass

class ComponentSelectedEvent(ComponentEvent):
    """组件选中事件。
    
    当组件被用户选中时触发。
    """
    pass

class ProjectEvent:
    """项目事件基类。
    
    所有项目相关事件的基类。
    
    Attributes:
        project_path: 项目文件路径
    """
    
    def __init__(self, project_path: str = ""):
        self.project_path = project_path

class ProjectOpenedEvent(ProjectEvent):
    """项目打开事件。"""
    pass

class ProjectSavedEvent(ProjectEvent):
    """项目保存事件。"""
    pass

class ProjectClosedEvent(ProjectEvent):
    """项目关闭事件。"""
    pass

class WindowEvent:
    """窗口事件基类。
    
    所有窗口相关事件的基类。
    
    Attributes:
        window_id: 窗口唯一标识符
    """
    
    def __init__(self, window_id: str):
        self.window_id = window_id

class WindowCreatedEvent(WindowEvent):
    """窗口创建事件。"""
    pass

class WindowDeletedEvent(WindowEvent):
    """窗口删除事件。"""
    pass

class WindowSwitchedEvent(WindowEvent):
    """窗口切换事件。"""
    pass

class ViewEvent:
    """视图事件基类。
    
    所有视图相关事件的基类。
    
    Attributes:
        factor: 缩放因子或其他数值参数
    """
    
    def __init__(self, factor: float = 1.0):
        self.factor = factor

class ViewScaledEvent(ViewEvent):
    """视图缩放事件。"""
    pass

class EventBus(QObject):
    """统一事件总线。
    
    集中管理所有跨模块事件，提供统一的订阅和发布接口。
    作为全局事件中介，实现模块间解耦通信。
    
    ## 信号定义
    
    ### 组件事件
    - component_created: 组件创建
    - component_deleted: 组件删除
    - component_selected: 组件选中
    - component_moved: 组件移动
    - component_resized: 组件调整大小
    
    ### 项目事件
    - project_opened: 项目打开
    - project_saved: 项目保存
    - project_closed: 项目关闭
    
    ### 窗口事件
    - window_created: 窗口创建
    - window_deleted: 窗口删除
    - window_switched: 窗口切换
    
    ### 视图事件
    - view_scaled: 视图缩放
    """
    
    # ==================== 组件事件 ====================
    component_created = Signal(str)
    component_deleted = Signal(str)
    component_selected = Signal(str)
    component_moved = Signal(ComponentMovedEvent)
    component_resized = Signal(ComponentResizedEvent)
    
    # ==================== 项目事件 ====================
    project_opened = Signal(ProjectOpenedEvent)
    project_saved = Signal(ProjectSavedEvent)
    project_closed = Signal(ProjectClosedEvent)
    
    # ==================== 窗口事件 ====================
    window_created = Signal(WindowCreatedEvent)
    window_deleted = Signal(WindowDeletedEvent)
    window_switched = Signal(WindowSwitchedEvent)
    
    # ==================== 视图事件 ====================
    view_scaled = Signal(ViewScaledEvent)
    
    def __init__(self):
        super().__init__()
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, signal: Signal, callback: Callable, filter_fn: Optional[Callable] = None):
        """订阅事件。
        
        注册回调函数，当事件发生时被调用。
        可选地提供过滤函数，只处理满足条件的事件。
        
        Args:
            signal: 要订阅的信号
            callback: 事件回调函数
            filter_fn: 可选的事件过滤函数，返回True时才调用callback
        
        Example:
            ```python
            # 基本订阅
            event_bus.subscribe(event_bus.component_moved, self.on_moved)
            
            # 带过滤器的订阅（只处理特定组件）
            event_bus.subscribe(
                event_bus.component_moved,
                self.on_button_moved,
                filter_fn=lambda e: e.component_id.startswith("btn_")
            )
            ```
        """
        if filter_fn:
            def filtered_callback(event):
                if filter_fn(event):
                    callback(event)
            signal.connect(filtered_callback)
            signal_name = signal.signal
            if signal_name not in self._subscribers:
                self._subscribers[signal_name] = []
            self._subscribers[signal_name].append(filtered_callback)
        else:
            signal.connect(callback)
            signal_name = signal.signal
            if signal_name not in self._subscribers:
                self._subscribers[signal_name] = []
            self._subscribers[signal_name].append(callback)
    
    def publish(self, signal: Signal, event: Any):
        """发布事件。
        
        触发指定信号，通知所有订阅者。
        
        Args:
            signal: 要触发的信号
            event: 事件对象或参数
        
        Example:
            ```python
            event = ComponentMovedEvent("btn_1", 100, 200)
            event_bus.publish(event_bus.component_moved, event)
            ```
        """
        signal.emit(event)
    
    def unsubscribe_all(self, signal: Signal):
        """取消指定信号的所有订阅。
        
        断开所有连接到指定信号的回调函数。
        
        Args:
            signal: 要取消订阅的信号
        """
        signal_name = signal.signal
        if signal_name in self._subscribers:
            for callback in self._subscribers[signal_name]:
                try:
                    signal.disconnect(callback)
                except RuntimeError:
                    pass
            self._subscribers[signal_name].clear()

# 全局EventBus实例
event_bus = EventBus()
