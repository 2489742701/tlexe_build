"""窗口/事件模型定义。"""

import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from PySide6.QtCore import QObject, Signal


class WindowType(Enum):
    """窗口类型枚举。"""
    MAIN = "main"
    EVENT = "event"


class ActionType(Enum):
    """动作类型枚举。"""
    NONE = "none"
    CLOSE_PROGRAM = "close_program"
    RUN_SCRIPT = "run_script"
    OPEN_EVENT = "open_event"
    CUSTOM = "custom"


@dataclass
class ActionDefinition:
    """动作定义。"""
    action_type: ActionType
    display_name: str
    description: str
    params: Dict[str, Any] = field(default_factory=dict)


DEFAULT_ACTIONS: List[ActionDefinition] = [
    ActionDefinition(
        action_type=ActionType.CLOSE_PROGRAM,
        display_name="关闭程序",
        description="关闭整个应用程序",
        params={}
    ),
    ActionDefinition(
        action_type=ActionType.RUN_SCRIPT,
        display_name="运行脚本",
        description="打开并运行其他脚本文件",
        params={"script_path": "", "wait": True}
    ),
    ActionDefinition(
        action_type=ActionType.OPEN_EVENT,
        display_name="打开事件",
        description="打开指定的事件窗口",
        params={"target_event_id": ""}
    ),
    ActionDefinition(
        action_type=ActionType.CUSTOM,
        display_name="自定义动作",
        description="执行自定义的动作链",
        params={}
    ),
]


class WindowModel(QObject):
    """窗口模型。"""
    
    data_changed = Signal()
    component_added = Signal(str)
    component_removed = Signal(str)
    
    def __init__(self, name: str = "新窗口", window_type: WindowType = WindowType.EVENT,
                 width: int = 800, height: int = 600, window_id: str = ""):
        super().__init__()
        self._id = window_id or str(uuid.uuid4())[:8]
        self._name = name
        self._window_type = window_type
        self._width = width
        self._height = height
        self._components: List[str] = []
        self._title = name
        self._trigger_button_id: Optional[str] = None
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if self._name != value:
            self._name = value
            self._title = value
            self.data_changed.emit()
    
    @property
    def window_type(self) -> WindowType:
        return self._window_type
    
    @window_type.setter
    def window_type(self, value: WindowType):
        if self._window_type != value:
            self._window_type = value
            self.data_changed.emit()
    
    @property
    def is_main(self) -> bool:
        return self._window_type == WindowType.MAIN
    
    @property
    def is_event(self) -> bool:
        return self._window_type == WindowType.EVENT
    
    @property
    def width(self) -> int:
        return self._width
    
    @width.setter
    def width(self, value: int):
        if self._width != value:
            self._width = value
            self.data_changed.emit()
    
    @property
    def height(self) -> int:
        return self._height
    
    @height.setter
    def height(self, value: int):
        if self._height != value:
            self._height = value
            self.data_changed.emit()
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str):
        if self._title != value:
            self._title = value
            self.data_changed.emit()
    
    @property
    def trigger_button_id(self) -> Optional[str]:
        return self._trigger_button_id
    
    @trigger_button_id.setter
    def trigger_button_id(self, value: Optional[str]):
        self._trigger_button_id = value
    
    @property
    def components(self) -> List[str]:
        return self._components.copy()
    
    def add_component(self, comp_id: str):
        if comp_id not in self._components:
            self._components.append(comp_id)
            self.component_added.emit(comp_id)
            self.data_changed.emit()
    
    def remove_component(self, comp_id: str):
        if comp_id in self._components:
            self._components.remove(comp_id)
            self.component_removed.emit(comp_id)
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'name': self._name,
            'window_type': self._window_type.value,
            'width': self._width,
            'height': self._height,
            'title': self._title,
            'components': self._components,
            'trigger_button_id': self._trigger_button_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WindowModel':
        window_type = WindowType(data.get('window_type', 'event'))
        instance = cls(
            name=data.get('name', '新窗口'),
            window_type=window_type,
            width=data.get('width', 800),
            height=data.get('height', 600),
            window_id=data.get('id', ''),
        )
        instance._title = data.get('title', instance._name)
        instance._components = data.get('components', [])
        instance._trigger_button_id = data.get('trigger_button_id')
        return instance
