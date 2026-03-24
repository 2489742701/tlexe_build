"""组件模型模块。

本模块包含各种组件模型的具体实现。
"""

from typing import Dict, Any, Optional, Type
from .base import ComponentModel


class ButtonModel(ComponentModel):
    """按钮组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 40, text: str = "按钮",
                 parent_id: str = ""):
        super().__init__("button", name, x, y, width, height, text, parent_id)
        self._target_window_id: str = ""
        self._branch_name: str = ""
        self._open_mode: str = "new_window"
        self._is_default: bool = False
        self._is_cancel: bool = False
    
    @property
    def target_window_id(self) -> str:
        return self._target_window_id
    
    @target_window_id.setter
    def target_window_id(self, value: str):
        if self._target_window_id != value:
            self._target_window_id = value
            self.data_changed.emit()
    
    @property
    def branch_name(self) -> str:
        return self._branch_name
    
    @branch_name.setter
    def branch_name(self, value: str):
        if self._branch_name != value:
            self._branch_name = value
            self.data_changed.emit()
    
    @property
    def open_mode(self) -> str:
        return self._open_mode
    
    @open_mode.setter
    def open_mode(self, value: str):
        if self._open_mode != value:
            self._open_mode = value
            self.data_changed.emit()
    
    @property
    def is_default(self) -> bool:
        return self._is_default
    
    @is_default.setter
    def is_default(self, value: bool):
        if self._is_default != value:
            self._is_default = value
            self.data_changed.emit()
    
    @property
    def is_cancel(self) -> bool:
        return self._is_cancel
    
    @is_cancel.setter
    def is_cancel(self, value: bool):
        if self._is_cancel != value:
            self._is_cancel = value
            self.data_changed.emit()
    
    @property
    def action_params(self) -> Dict[str, Any]:
        """动作参数的便捷访问器。"""
        return self._action.params
    
    @action_params.setter
    def action_params(self, value: Dict[str, Any]):
        if self._action.params != value:
            self._action.params = value
            self.data_changed.emit()
    
    @property
    def has_branch(self) -> bool:
        return bool(self._target_window_id)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['target_window_id'] = self._target_window_id
        data['branch_name'] = self._branch_name
        data['open_mode'] = self._open_mode
        data['is_default'] = self._is_default
        data['is_cancel'] = self._is_cancel
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ButtonModel':
        instance = super().from_dict(data)
        instance._target_window_id = data.get('target_window_id', '')
        instance._branch_name = data.get('branch_name', '')
        instance._open_mode = data.get('open_mode', 'new_window')
        instance._is_default = data.get('is_default', False)
        instance._is_cancel = data.get('is_cancel', False)
        return instance


class LabelModel(ComponentModel):
    """标签组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 30, text: str = "文本",
                 parent_id: str = ""):
        super().__init__("label", name, x, y, width, height, text, parent_id)
        self._alignment: str = "center"
        self._word_wrap: bool = True
        self._auto_size: bool = True
        self._style.background_color = "transparent"
        self._style.border_color = "transparent"
        self._style.border_width = 0
    
    @property
    def alignment(self) -> str:
        return self._alignment
    
    @alignment.setter
    def alignment(self, value: str):
        if self._alignment != value:
            self._alignment = value
            self.data_changed.emit()
    
    @property
    def word_wrap(self) -> bool:
        return self._word_wrap
    
    @word_wrap.setter
    def word_wrap(self, value: bool):
        if self._word_wrap != value:
            self._word_wrap = value
            self.data_changed.emit()
    
    @property
    def auto_size(self) -> bool:
        return self._auto_size
    
    @auto_size.setter
    def auto_size(self, value: bool):
        if self._auto_size != value:
            self._auto_size = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['alignment'] = self._alignment
        data['word_wrap'] = self._word_wrap
        data['auto_size'] = self._auto_size
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LabelModel':
        instance = super().from_dict(data)
        instance._alignment = data.get('alignment', 'center')
        instance._word_wrap = data.get('word_wrap', True)
        instance._auto_size = data.get('auto_size', True)
        return instance


class InputModel(ComponentModel):
    """输入框组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 30, text: str = "",
                 parent_id: str = ""):
        super().__init__("input", name, x, y, width, height, text, parent_id)
        self._placeholder: str = ""
        self._max_length: int = 32767
        self._is_password: bool = False
        self._is_multiline: bool = False
    
    @property
    def placeholder(self) -> str:
        return self._placeholder
    
    @placeholder.setter
    def placeholder(self, value: str):
        if self._placeholder != value:
            self._placeholder = value
            self.data_changed.emit()
    
    @property
    def max_length(self) -> int:
        return self._max_length
    
    @max_length.setter
    def max_length(self, value: int):
        if self._max_length != value:
            self._max_length = value
            self.data_changed.emit()
    
    @property
    def is_password(self) -> bool:
        return self._is_password
    
    @is_password.setter
    def is_password(self, value: bool):
        if self._is_password != value:
            self._is_password = value
            self.data_changed.emit()
    
    @property
    def is_multiline(self) -> bool:
        return self._is_multiline
    
    @is_multiline.setter
    def is_multiline(self, value: bool):
        if self._is_multiline != value:
            self._is_multiline = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['placeholder'] = self._placeholder
        data['max_length'] = self._max_length
        data['is_password'] = self._is_password
        data['is_multiline'] = self._is_multiline
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputModel':
        instance = super().from_dict(data)
        instance._placeholder = data.get('placeholder', '')
        instance._max_length = data.get('max_length', 32767)
        instance._is_password = data.get('is_password', False)
        instance._is_multiline = data.get('is_multiline', False)
        return instance


class ContainerModel(ComponentModel):
    """容器组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 400, height: int = 300, text: str = "容器",
                 parent_id: str = ""):
        super().__init__("container", name, x, y, width, height, text, parent_id)
        self._children: list = []
        self._position_mode: str = "center"
        self._layout: str = "none"
        self._padding: int = 10
        self._spacing: int = 5
    
    @property
    def children(self) -> list:
        return self._children.copy()
    
    @children.setter
    def children(self, value: list):
        if self._children != value:
            self._children = value
            self.data_changed.emit()
    
    @property
    def position_mode(self) -> str:
        return self._position_mode
    
    @position_mode.setter
    def position_mode(self, value: str):
        if self._position_mode != value:
            self._position_mode = value
            self.data_changed.emit()
    
    @property
    def layout(self) -> str:
        return self._layout
    
    @layout.setter
    def layout(self, value: str):
        if self._layout != value:
            self._layout = value
            self.data_changed.emit()
    
    @property
    def padding(self) -> int:
        return self._padding
    
    @padding.setter
    def padding(self, value: int):
        if self._padding != value:
            self._padding = value
            self.data_changed.emit()
    
    @property
    def spacing(self) -> int:
        return self._spacing
    
    @spacing.setter
    def spacing(self, value: int):
        if self._spacing != value:
            self._spacing = value
            self.data_changed.emit()
    
    def add_child(self, child_id: str):
        if child_id not in self._children:
            self._children.append(child_id)
            self.data_changed.emit()
    
    def remove_child(self, child_id: str):
        if child_id in self._children:
            self._children.remove(child_id)
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['children'] = self._children
        data['position_mode'] = self._position_mode
        data['layout'] = self._layout
        data['padding'] = self._padding
        data['spacing'] = self._spacing
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContainerModel':
        instance = super().from_dict(data)
        instance._children = data.get('children', [])
        instance._position_mode = data.get('position_mode', 'center')
        instance._layout = data.get('layout', 'none')
        instance._padding = data.get('padding', 10)
        instance._spacing = data.get('spacing', 5)
        return instance


class CheckBoxModel(ComponentModel):
    """复选框组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 24, text: str = "复选框",
                 parent_id: str = ""):
        super().__init__("checkbox", name, x, y, width, height, text, parent_id)
        self._checked: bool = False
    
    @property
    def checked(self) -> bool:
        return self._checked
    
    @checked.setter
    def checked(self, value: bool):
        if self._checked != value:
            self._checked = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['checked'] = self._checked
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckBoxModel':
        instance = super().from_dict(data)
        instance._checked = data.get('checked', False)
        return instance


class ComboBoxModel(ComponentModel):
    """下拉框组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 150, height: int = 28, text: str = "",
                 parent_id: str = ""):
        super().__init__("combobox", name, x, y, width, height, text, parent_id)
        self._items: list = []
        self._current_index: int = 0
    
    @property
    def items(self) -> list:
        return self._items.copy()
    
    @items.setter
    def items(self, value: list):
        if self._items != value:
            self._items = value
            self.data_changed.emit()
    
    @property
    def current_index(self) -> int:
        return self._current_index
    
    @current_index.setter
    def current_index(self, value: int):
        if self._current_index != value:
            self._current_index = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['items'] = self._items
        data['current_index'] = self._current_index
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComboBoxModel':
        instance = super().from_dict(data)
        instance._items = data.get('items', [])
        instance._current_index = data.get('current_index', 0)
        return instance


class ProgressBarModel(ComponentModel):
    """进度条组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 24, text: str = "",
                 parent_id: str = ""):
        super().__init__("progressbar", name, x, y, width, height, text, parent_id)
        self._value: int = 0
        self._show_text: bool = True
        self._text_position: str = "center"
        self._auto_progress: bool = False
        self._duration: int = 3
        self._signals: list = []
    
    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, value: int):
        if self._value != value:
            self._value = value
            self.data_changed.emit()
    
    @property
    def show_text(self) -> bool:
        return self._show_text
    
    @show_text.setter
    def show_text(self, value: bool):
        if self._show_text != value:
            self._show_text = value
            self.data_changed.emit()
    
    @property
    def text_position(self) -> str:
        return self._text_position
    
    @text_position.setter
    def text_position(self, value: str):
        valid_positions = ['left', 'center', 'right', 'follow']
        if value in valid_positions and self._text_position != value:
            self._text_position = value
            self.data_changed.emit()
    
    @property
    def auto_progress(self) -> bool:
        return self._auto_progress
    
    @auto_progress.setter
    def auto_progress(self, value: bool):
        if self._auto_progress != value:
            self._auto_progress = value
            self.data_changed.emit()
    
    @property
    def duration(self) -> int:
        return self._duration
    
    @duration.setter
    def duration(self, value: int):
        if self._duration != value:
            self._duration = value
            self.data_changed.emit()
    
    @property
    def signals(self) -> list:
        return self._signals
    
    @signals.setter
    def signals(self, value: list):
        self._signals = value
        self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['value'] = self._value
        data['show_text'] = self._show_text
        data['text_position'] = self._text_position
        data['auto_progress'] = self._auto_progress
        data['duration'] = self._duration
        data['signals'] = self._signals
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressBarModel':
        instance = super().from_dict(data)
        instance._value = data.get('value', 0)
        instance._show_text = data.get('show_text', True)
        instance._text_position = data.get('text_position', 'center')
        instance._auto_progress = data.get('auto_progress', False)
        instance._duration = data.get('duration', 3)
        instance._signals = data.get('signals', [])
        return instance


COMPONENT_TYPE_MAP: Dict[str, Type[ComponentModel]] = {
    'button': ButtonModel,
    'label': LabelModel,
    'input': InputModel,
    'container': ContainerModel,
    'checkbox': CheckBoxModel,
    'combobox': ComboBoxModel,
    'progressbar': ProgressBarModel,
}


def create_component(comp_type: str, **kwargs) -> ComponentModel:
    """创建组件实例。
    
    Args:
        comp_type: 组件类型
        **kwargs: 组件参数
        
    Returns:
        组件实例
        
    Raises:
        ValueError: 未知的组件类型
    """
    comp_class = COMPONENT_TYPE_MAP.get(comp_type)
    if comp_class:
        return comp_class(**kwargs)
    raise ValueError(f"未知的组件类型: {comp_type}")
