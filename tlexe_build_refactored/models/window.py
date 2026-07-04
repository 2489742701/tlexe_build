"""窗口模型定义。"""

import uuid
from typing import Dict, Any, List, Optional

from PySide6.QtCore import QObject, Signal

from .schemas import WindowType
from .base import SignalProperty

class WindowModel(QObject):
    """窗口模型。"""

    data_changed = Signal()
    component_added = Signal(str)
    component_removed = Signal(str)

    id: str = SignalProperty("", readonly=True)
    name: str = SignalProperty("")
    window_type: str = SignalProperty("event")
    width: int = SignalProperty(800)
    height: int = SignalProperty(600)
    title: str = SignalProperty("")
    trigger_button_id: str = SignalProperty("", readonly=True)
    frameless: bool = SignalProperty(False)
    window_color: str = SignalProperty("")

    def __init__(self, name: str = "新窗口", window_type: WindowType = WindowType.EVENT,
                 width: int = 800, height: int = 600, window_id: str = "",
                 frameless: bool = False, window_color: str = ""):
        super().__init__()
        self._loading = True
        self._id = window_id or str(uuid.uuid4())[:8]
        self._name = name
        self._window_type = window_type.value if isinstance(window_type, WindowType) else window_type
        self._width = width
        self._height = height
        self._components: List[str] = []
        self._title = name
        self._trigger_button_id: Optional[str] = None
        self._frameless = frameless
        self._window_color = window_color
        self._loading = False

    @property
    def is_main(self) -> bool:
        return self._window_type == WindowType.MAIN.value

    @property
    def is_event(self) -> bool:
        return self._window_type == WindowType.EVENT.value

    @property
    def components(self) -> List[str]:
        return self._components.copy()

    def add_component(self, comp_id: str) -> None:
        if comp_id not in self._components:
            self._components.append(comp_id)
            self.component_added.emit(comp_id)
            self.data_changed.emit()

    def remove_component(self, comp_id: str) -> None:
        if comp_id in self._components:
            self._components.remove(comp_id)
            self.component_removed.emit(comp_id)
            self.data_changed.emit()

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self._id,
            'name': self._name,
            'window_type': self._window_type,
            'width': self._width,
            'height': self._height,
            'title': self._title,
            'components': self._components,
            'trigger_button_id': self._trigger_button_id,
        }
        if self._frameless:
            result['frameless'] = True
        if self._window_color:
            result['window_color'] = self._window_color
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WindowModel':
        wt = data.get('window_type', 'event')
        window_type = WindowType(wt) if wt in [e.value for e in WindowType] else WindowType.EVENT
        instance = cls(
            name=data.get('name', '新窗口'),
            window_type=window_type,
            width=data.get('width', 800),
            height=data.get('height', 600),
            window_id=data.get('id', ''),
            frameless=data.get('frameless', False),
            window_color=data.get('window_color', ''),
        )
        instance._title = data.get('title', instance._name)
        instance._components = data.get('components', [])
        instance._trigger_button_id = data.get('trigger_button_id')
        return instance
