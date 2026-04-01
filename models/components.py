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
        self._alignment: str = "center"
    
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
    
    @property
    def alignment(self) -> str:
        return self._alignment
    
    @alignment.setter
    def alignment(self, value: str):
        if self._alignment != value:
            self._alignment = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['target_window_id'] = self._target_window_id
        data['branch_name'] = self._branch_name
        data['open_mode'] = self._open_mode
        data['is_default'] = self._is_default
        data['is_cancel'] = self._is_cancel
        data['alignment'] = self._alignment
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ButtonModel':
        instance = super().from_dict(data)
        instance._target_window_id = data.get('target_window_id', '')
        instance._branch_name = data.get('branch_name', '')
        instance._open_mode = data.get('open_mode', 'new_window')
        instance._is_default = data.get('is_default', False)
        instance._is_cancel = data.get('is_cancel', False)
        instance._alignment = data.get('alignment', 'center')
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


class ImageModel(ComponentModel):
    """图片组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 150, text: str = "",
                 parent_id: str = ""):
        super().__init__("image", name, x, y, width, height, text, parent_id)
        self._image_path: str = ""
        self._aspect_ratio: bool = True
        self._scale_mode: str = "keep_aspect"  # keep_aspect, stretch, center
        self._border_radius: int = 0
        self._opacity: float = 1.0
        self._hover_effect: bool = False
        self._click_action: str = "none"  # none, zoom, open_original
        self._placeholder_text: str = "点击选择图片"
    
    @property
    def image_path(self) -> str:
        return self._image_path
    
    @image_path.setter
    def image_path(self, value: str):
        if self._image_path != value:
            self._image_path = value
            self.data_changed.emit()
    
    @property
    def aspect_ratio(self) -> bool:
        return self._aspect_ratio
    
    @aspect_ratio.setter
    def aspect_ratio(self, value: bool):
        if self._aspect_ratio != value:
            self._aspect_ratio = value
            self.data_changed.emit()
    
    @property
    def scale_mode(self) -> str:
        return self._scale_mode
    
    @scale_mode.setter
    def scale_mode(self, value: str):
        valid_modes = ['keep_aspect', 'stretch', 'center']
        if value in valid_modes and self._scale_mode != value:
            self._scale_mode = value
            self.data_changed.emit()
    
    @property
    def border_radius(self) -> int:
        return self._border_radius
    
    @border_radius.setter
    def border_radius(self, value: int):
        if self._border_radius != value:
            self._border_radius = value
            self.data_changed.emit()
    
    @property
    def opacity(self) -> float:
        return self._opacity
    
    @opacity.setter
    def opacity(self, value: float):
        if 0.0 <= value <= 1.0 and self._opacity != value:
            self._opacity = value
            self.data_changed.emit()
    
    @property
    def hover_effect(self) -> bool:
        return self._hover_effect
    
    @hover_effect.setter
    def hover_effect(self, value: bool):
        if self._hover_effect != value:
            self._hover_effect = value
            self.data_changed.emit()
    
    @property
    def click_action(self) -> str:
        return self._click_action
    
    @click_action.setter
    def click_action(self, value: str):
        valid_actions = ['none', 'zoom', 'open_original']
        if value in valid_actions and self._click_action != value:
            self._click_action = value
            self.data_changed.emit()
    
    @property
    def placeholder_text(self) -> str:
        return self._placeholder_text
    
    @placeholder_text.setter
    def placeholder_text(self, value: str):
        if self._placeholder_text != value:
            self._placeholder_text = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['image_path'] = self._image_path
        data['aspect_ratio'] = self._aspect_ratio
        data['scale_mode'] = self._scale_mode
        data['border_radius'] = self._border_radius
        data['opacity'] = self._opacity
        data['hover_effect'] = self._hover_effect
        data['click_action'] = self._click_action
        data['placeholder_text'] = self._placeholder_text
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageModel':
        instance = super().from_dict(data)
        instance._image_path = data.get('image_path', '')
        instance._aspect_ratio = data.get('aspect_ratio', True)
        instance._scale_mode = data.get('scale_mode', 'keep_aspect')
        instance._border_radius = data.get('border_radius', 0)
        instance._opacity = data.get('opacity', 1.0)
        instance._hover_effect = data.get('hover_effect', False)
        instance._click_action = data.get('click_action', 'none')
        instance._placeholder_text = data.get('placeholder_text', '点击选择图片')
        return instance


class VideoModel(ComponentModel):
    """视频组件模型。"""
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 400, height: int = 300, text: str = "",
                 parent_id: str = ""):
        super().__init__("video", name, x, y, width, height, text, parent_id)
        self._video_path: str = ""
        self._auto_play: bool = False
        self._loop: bool = False
        self._muted: bool = False
        self._controls: bool = True
        self._volume: float = 0.8
        self._poster_image: str = ""
        self._playback_rate: float = 1.0
        self._aspect_ratio: bool = True
        self._placeholder_text: str = "点击选择视频"
    
    @property
    def video_path(self) -> str:
        return self._video_path
    
    @video_path.setter
    def video_path(self, value: str):
        if self._video_path != value:
            self._video_path = value
            self.data_changed.emit()
    
    @property
    def auto_play(self) -> bool:
        return self._auto_play
    
    @auto_play.setter
    def auto_play(self, value: bool):
        if self._auto_play != value:
            self._auto_play = value
            self.data_changed.emit()
    
    @property
    def loop(self) -> bool:
        return self._loop
    
    @loop.setter
    def loop(self, value: bool):
        if self._loop != value:
            self._loop = value
            self.data_changed.emit()
    
    @property
    def muted(self) -> bool:
        return self._muted
    
    @muted.setter
    def muted(self, value: bool):
        if self._muted != value:
            self._muted = value
            self.data_changed.emit()
    
    @property
    def controls(self) -> bool:
        return self._controls
    
    @controls.setter
    def controls(self, value: bool):
        if self._controls != value:
            self._controls = value
            self.data_changed.emit()
    
    @property
    def volume(self) -> float:
        return self._volume
    
    @volume.setter
    def volume(self, value: float):
        if 0.0 <= value <= 1.0 and self._volume != value:
            self._volume = value
            self.data_changed.emit()
    
    @property
    def poster_image(self) -> str:
        return self._poster_image
    
    @poster_image.setter
    def poster_image(self, value: str):
        if self._poster_image != value:
            self._poster_image = value
            self.data_changed.emit()
    
    @property
    def playback_rate(self) -> float:
        return self._playback_rate
    
    @playback_rate.setter
    def playback_rate(self, value: float):
        if 0.25 <= value <= 4.0 and self._playback_rate != value:
            self._playback_rate = value
            self.data_changed.emit()
    
    @property
    def aspect_ratio(self) -> bool:
        return self._aspect_ratio
    
    @aspect_ratio.setter
    def aspect_ratio(self, value: bool):
        if self._aspect_ratio != value:
            self._aspect_ratio = value
            self.data_changed.emit()
    
    @property
    def placeholder_text(self) -> str:
        return self._placeholder_text
    
    @placeholder_text.setter
    def placeholder_text(self, value: str):
        if self._placeholder_text != value:
            self._placeholder_text = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['video_path'] = self._video_path
        data['auto_play'] = self._auto_play
        data['loop'] = self._loop
        data['muted'] = self._muted
        data['controls'] = self._controls
        data['volume'] = self._volume
        data['poster_image'] = self._poster_image
        data['playback_rate'] = self._playback_rate
        data['aspect_ratio'] = self._aspect_ratio
        data['placeholder_text'] = self._placeholder_text
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoModel':
        instance = super().from_dict(data)
        instance._video_path = data.get('video_path', '')
        instance._auto_play = data.get('auto_play', False)
        instance._loop = data.get('loop', False)
        instance._muted = data.get('muted', False)
        instance._controls = data.get('controls', True)
        instance._volume = data.get('volume', 0.8)
        instance._poster_image = data.get('poster_image', '')
        instance._playback_rate = data.get('playback_rate', 1.0)
        instance._aspect_ratio = data.get('aspect_ratio', True)
        instance._placeholder_text = data.get('placeholder_text', '点击选择视频')
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
        self._target_window_id: str = ""
        self._branch_name: str = ""
    
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
    def has_branch(self) -> bool:
        return bool(self._target_window_id)
    
    @property
    def action_params(self) -> Dict[str, Any]:
        return self._action.params
    
    @action_params.setter
    def action_params(self, value: Dict[str, Any]):
        if self._action.params != value:
            self._action.params = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['value'] = self._value
        data['show_text'] = self._show_text
        data['text_position'] = self._text_position
        data['auto_progress'] = self._auto_progress
        data['duration'] = self._duration
        data['target_window_id'] = self._target_window_id
        data['branch_name'] = self._branch_name
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressBarModel':
        instance = super().from_dict(data)
        instance._value = data.get('value', 0)
        instance._show_text = data.get('show_text', True)
        instance._text_position = data.get('text_position', 'center')
        instance._auto_progress = data.get('auto_progress', False)
        instance._duration = data.get('duration', 3)
        instance._target_window_id = data.get('target_window_id', '')
        instance._branch_name = data.get('branch_name', '')
        return instance


COMPONENT_TYPE_MAP: Dict[str, Type[ComponentModel]] = {
    'button': ButtonModel,
    'label': LabelModel,
    'input': InputModel,
    'container': ContainerModel,
    'checkbox': CheckBoxModel,
    'combobox': ComboBoxModel,
    'image': ImageModel,
    'video': VideoModel,
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
