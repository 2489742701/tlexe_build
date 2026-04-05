"""EventBus模块初始化。

本模块统一导出EventBus及事件类，提供统一的访问入口。

## 可用类
- EventBus: 统一事件总线
- ComponentMovedEvent: 组件移动事件
- ComponentResizedEvent: 组件调整大小事件
- ComponentCreatedEvent: 组件创建事件
- ComponentDeletedEvent: 组件删除事件
- ComponentSelectedEvent: 组件选中事件
- ProjectOpenedEvent: 项目打开事件
- ProjectSavedEvent: 项目保存事件
- ProjectClosedEvent: 项目关闭事件
- WindowCreatedEvent: 窗口创建事件
- WindowDeletedEvent: 窗口删除事件
- WindowSwitchedEvent: 窗口切换事件
- ViewScaledEvent: 视图缩放事件
"""

from .event_bus import (
    EventBus,
    ComponentEvent,
    ComponentMovedEvent,
    ComponentResizedEvent,
    ComponentCreatedEvent,
    ComponentDeletedEvent,
    ComponentSelectedEvent,
    ProjectEvent,
    ProjectOpenedEvent,
    ProjectSavedEvent,
    ProjectClosedEvent,
    WindowEvent,
    WindowCreatedEvent,
    WindowDeletedEvent,
    WindowSwitchedEvent,
    ViewEvent,
    ViewScaledEvent,
    event_bus,
)

__all__ = [
    "EventBus",
    "ComponentEvent",
    "ComponentMovedEvent",
    "ComponentResizedEvent",
    "ComponentCreatedEvent",
    "ComponentDeletedEvent",
    "ComponentSelectedEvent",
    "ProjectEvent",
    "ProjectOpenedEvent",
    "ProjectSavedEvent",
    "ProjectClosedEvent",
    "WindowEvent",
    "WindowCreatedEvent",
    "WindowDeletedEvent",
    "WindowSwitchedEvent",
    "ViewEvent",
    "ViewScaledEvent",
    "event_bus",
]
