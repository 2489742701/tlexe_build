"""组件模型模块。

本模块包含各种组件模型的具体实现。
"""

from typing import Dict, Any, Optional, Type, List
from PySide6.QtCore import Signal
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
        self._scale_mode: str = "fit"  # fill, fit, stretch, center, tile (兼容 keep_aspect)
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
        valid_modes = ['fill', 'fit', 'stretch', 'center', 'tile', 'keep_aspect']  # 兼容旧值
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
        # 兼容旧的 scale_mode 值
        scale_mode = data.get('scale_mode', 'fit')
        if scale_mode == 'keep_aspect':
            scale_mode = 'fit'  # 将旧值映射到新值
        instance._scale_mode = scale_mode
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


class HiddenButtonModel(ComponentModel):
    """隐藏按钮组件模型。
    
    透明但可点击的按钮，用于创建热区或隐藏触发区域。
    
    Attributes:
        clicked: 点击信号
        action: 按钮动作类型
        action_params: 动作参数
    """
    
    clicked = Signal()
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 100, height: int = 100,
                 parent_id: str = ""):
        super().__init__("hidden_button", name, x, y, width, height, "", parent_id)
        self._action: str = "none"
        self._action_params: Dict[str, Any] = {}
    
    @property
    def action(self) -> str:
        return self._action
    
    @action.setter
    def action(self, value: str):
        if self._action != value:
            self._action = value
            self.data_changed.emit()
    
    @property
    def action_params(self) -> Dict[str, Any]:
        return self._action_params
    
    @action_params.setter
    def action_params(self, value: Dict[str, Any]):
        if self._action_params != value:
            self._action_params = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['action'] = self._action
        data['action_params'] = self._action_params
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HiddenButtonModel':
        instance = super().from_dict(data)
        instance._action = data.get('action', 'none')
        instance._action_params = data.get('action_params', {})
        return instance
    
    def get_editor_tabs(self) -> list:
        return super().get_editor_tabs() + [
            {
                "label": "动作类型",
                "property": "action",
                "type": "combo",
                "options": ["none", "zoom", "open_original"],
                "description": "点击后执行的动作"
            }
        ]
    
    def trigger_click(self):
        """触发点击事件。"""
        self.clicked.emit()


class ImageButtonModel(ComponentModel):
    """图片按钮组件模型。
    
    使用图片作为按钮外观，支持不同状态显示不同图片。
    
    Attributes:
        clicked: 点击信号
        image_path: 默认图片路径
        hover_image_path: 悬停图片路径
        pressed_image_path: 按下图片路径
    """
    
    clicked = Signal()
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 40,
                 parent_id: str = ""):
        super().__init__("image_button", name, x, y, width, height, "", parent_id)
        self._image_path: str = ""
        self._hover_image_path: str = ""
        self._pressed_image_path: str = ""
        self._action: str = "none"
        self._action_params: Dict[str, Any] = {}
    
    @property
    def image_path(self) -> str:
        return self._image_path
    
    @image_path.setter
    def image_path(self, value: str):
        if self._image_path != value:
            self._image_path = value
            self.data_changed.emit()
    
    @property
    def hover_image_path(self) -> str:
        return self._hover_image_path
    
    @hover_image_path.setter
    def hover_image_path(self, value: str):
        if self._hover_image_path != value:
            self._hover_image_path = value
            self.data_changed.emit()
    
    @property
    def pressed_image_path(self) -> str:
        return self._pressed_image_path
    
    @pressed_image_path.setter
    def pressed_image_path(self, value: str):
        if self._pressed_image_path != value:
            self._pressed_image_path = value
            self.data_changed.emit()
    
    @property
    def action(self) -> str:
        return self._action
    
    @action.setter
    def action(self, value: str):
        if self._action != value:
            self._action = value
            self.data_changed.emit()
    
    @property
    def action_params(self) -> Dict[str, Any]:
        return self._action_params
    
    @action_params.setter
    def action_params(self, value: Dict[str, Any]):
        if self._action_params != value:
            self._action_params = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['image_path'] = self._image_path
        data['hover_image_path'] = self._hover_image_path
        data['pressed_image_path'] = self._pressed_image_path
        data['action'] = self._action
        data['action_params'] = self._action_params
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageButtonModel':
        instance = super().from_dict(data)
        instance._image_path = data.get('image_path', '')
        instance._hover_image_path = data.get('hover_image_path', '')
        instance._pressed_image_path = data.get('pressed_image_path', '')
        instance._action = data.get('action', 'none')
        instance._action_params = data.get('action_params', {})
        return instance
    
    def get_editor_tabs(self) -> list:
        return super().get_editor_tabs() + [
            {
                "label": "默认图片",
                "property": "image_path",
                "type": "image_select",
                "description": "按钮默认显示的图片"
            },
            {
                "label": "悬停图片",
                "property": "hover_image_path",
                "type": "image_select",
                "description": "鼠标悬停时显示的图片"
            },
            {
                "label": "按下图片",
                "property": "pressed_image_path",
                "type": "image_select",
                "description": "鼠标按下时显示的图片"
            },
            {
                "label": "动作类型",
                "property": "action",
                "type": "combo",
                "options": ["none", "zoom", "open_original", "random_image"],
                "description": "点击后执行的动作"
            }
        ]
    
    def trigger_click(self):
        """触发点击事件。"""
        self.clicked.emit()


class ImageCarouselModel(ComponentModel):
    """图片轮播组件模型。
    
    显示多张图片的轮播效果，支持自动播放和手动切换。
    
    Attributes:
        images: 图片路径列表
        image_labels: 图片标签列表（如候选人姓名）
        current_index: 当前显示的图片索引
        interval: 轮播间隔（毫秒）
        auto_play: 是否自动播放
        loop: 是否循环播放
    
    Signals:
        current_index_changed: 当前索引改变信号
        lottery_finished: 抽奖动画结束信号，携带(中奖索引, 中奖图片路径)
    """
    
    current_index_changed = Signal(int)
    lottery_finished = Signal(int, str)
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 300, height: int = 200,
                 text: str = "", parent_id: str = ""):
        super().__init__("image_carousel", name, x, y, width, height, text, parent_id)
        self._images: list = []
        self._image_labels: list = []
        self._current_index: int = 0
        self._interval: int = 2000
        self._auto_play: bool = False
        self._loop: bool = True
    
    @property
    def images(self) -> list:
        return self._images
    
    @images.setter
    def images(self, value: list):
        if self._images != value:
            self._images = value
            self._sync_image_labels()
            self.data_changed.emit()
    
    @property
    def image_labels(self) -> list:
        return self._image_labels
    
    @image_labels.setter
    def image_labels(self, value: list):
        if self._image_labels != value:
            self._image_labels = value
            self._sync_images_to_labels()
            self.data_changed.emit()
    
    def _sync_image_labels(self):
        """同步图片标签列表长度与图片列表一致。"""
        if len(self._image_labels) > len(self._images):
            self._image_labels = self._image_labels[:len(self._images)]
        elif len(self._image_labels) < len(self._images):
            default_labels = [f"图片{i+1}" for i in range(len(self._images) - len(self._image_labels))]
            self._image_labels.extend(default_labels)
    
    def _sync_images_to_labels(self):
        """同步图片列表长度与标签列表一致（截断多余图片）。"""
        if len(self._images) > len(self._image_labels) and self._image_labels:
            self._images = self._images[:len(self._image_labels)]
    
    @property
    def current_index(self) -> int:
        return self._current_index
    
    @current_index.setter
    def current_index(self, value: int):
        if self._current_index != value:
            self._current_index = value
            self.current_index_changed.emit(value)
            self.data_changed.emit()
    
    @property
    def interval(self) -> int:
        return self._interval
    
    @interval.setter
    def interval(self, value: int):
        if self._interval != value:
            self._interval = value
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
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['images'] = self._images
        data['image_labels'] = self._image_labels
        data['current_index'] = self._current_index
        data['interval'] = self._interval
        data['auto_play'] = self._auto_play
        data['loop'] = self._loop
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageCarouselModel':
        instance = super().from_dict(data)
        instance._images = data.get('images', [])
        instance._image_labels = data.get('image_labels', [])
        instance._current_index = data.get('current_index', 0)
        instance._interval = data.get('interval', 2000)
        instance._auto_play = data.get('auto_play', False)
        instance._loop = data.get('loop', True)
        return instance
    
    def get_editor_tabs(self) -> list:
        return super().get_editor_tabs() + [
            {
                "label": "图片列表",
                "property": "images",
                "type": "image_list",
                "description": "轮播的图片列表"
            },
            {
                "label": "图片标签",
                "property": "image_labels",
                "type": "string_list",
                "description": "每张图片对应的标签（如候选人姓名）"
            },
            {
                "label": "轮播间隔",
                "property": "interval",
                "type": "number",
                "min": 100,
                "max": 10000,
                "description": "图片切换间隔（毫秒）"
            },
            {
                "label": "自动播放",
                "property": "auto_play",
                "type": "checkbox",
                "description": "是否自动轮播"
            },
            {
                "label": "循环播放",
                "property": "loop",
                "type": "checkbox",
                "description": "是否循环播放"
            }
        ]
    
    def next_image(self):
        """切换到下一张图片。"""
        if not self._images:
            return
        if self._loop:
            self.current_index = (self._current_index + 1) % len(self._images)
        else:
            if self._current_index < len(self._images) - 1:
                self.current_index = self._current_index + 1
    
    def prev_image(self):
        """切换到上一张图片。"""
        if not self._images:
            return
        if self._loop:
            self.current_index = (self._current_index - 1) % len(self._images)
        else:
            if self._current_index > 0:
                self.current_index = self._current_index - 1
    
    def random_image(self):
        """随机切换到一张图片。"""
        import random
        if len(self._images) > 1:
            new_index = random.randint(0, len(self._images) - 1)
            self.current_index = new_index
    
    def lottery_animation(self, duration_ms: int = 3000, on_finished=None):
        """执行抽奖动画。
        
        图片快速轮播，然后逐渐减速停止在随机位置。
        
        Args:
            duration_ms: 动画总时长（毫秒）
            on_finished: 动画完成回调函数
        """
        import random
        from PySide6.QtCore import QTimer, QElapsedTimer
        
        if not self._images or len(self._images) < 2:
            return
        
        final_index = random.randint(0, len(self._images) - 1)
        
        elapsed_timer = QElapsedTimer()
        elapsed_timer.start()
        
        self._lottery_timer = QTimer()
        self._lottery_timer.timeout.connect(
            lambda: self._update_lottery_animation(
                elapsed_timer, duration_ms, final_index, on_finished
            )
        )
        self._lottery_timer.start(50)
    
    def _update_lottery_animation(self, elapsed_timer, duration_ms, final_index, on_finished):
        """更新抽奖动画状态。"""
        from PySide6.QtCore import QEasingCurve
        
        elapsed = elapsed_timer.elapsed()
        progress = min(elapsed / duration_ms, 1.0)
        
        easing = QEasingCurve(QEasingCurve.Type.OutQuart)
        eased_progress = easing.valueForProgress(progress)
        
        if progress < 1.0:
            speed = int(50 + eased_progress * 300)
            if self._lottery_timer.interval() != speed:
                self._lottery_timer.setInterval(speed)
            
            self.next_image()
        else:
            self._lottery_timer.stop()
            self.current_index = final_index
            
            winner_image = self._images[final_index] if final_index < len(self._images) else ""
            self.lottery_finished.emit(final_index, winner_image)
            
            if on_finished:
                on_finished(final_index)
    
    def stop_lottery(self):
        """停止抽奖动画。"""
        if hasattr(self, '_lottery_timer') and self._lottery_timer:
            self._lottery_timer.stop()


class GroupNodeModel(ComponentModel):
    """组节点模型。
    
    组节点是一个特殊的组件类型，用于将多个组件组合在一起。
    组节点可以包含子组件，并提供统一的布局管理。
    
    Attributes:
        children: 子组件ID列表
        layout_mode: 布局模式 (none, vertical, horizontal, grid)
        spacing: 子组件间距
        padding: 内边距
        auto_size: 是否自动调整大小以适应子组件
    """
    
    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 300, height: int = 200, text: str = "",
                 parent_id: str = ""):
        super().__init__("group_node", name, x, y, width, height, text, parent_id)
        self._children: List[str] = []
        self._layout_mode: str = "none"
        self._spacing: int = 10
        self._padding: int = 10
        self._auto_size: bool = False
        self._show_border: bool = True
        self._border_style: str = "dashed"
        
        self._style.background_color = "transparent"
        self._style.border_color = "#999999"
        self._style.border_width = 1
        self._style.border_radius = 5
    
    @property
    def children(self) -> List[str]:
        return self._children.copy()
    
    @children.setter
    def children(self, value: List[str]):
        if self._children != value:
            self._children = value
            self.data_changed.emit()
    
    def add_child(self, child_id: str) -> None:
        """添加子组件。"""
        if child_id not in self._children:
            self._children.append(child_id)
            self.data_changed.emit()
    
    def remove_child(self, child_id: str) -> None:
        """移除子组件。"""
        if child_id in self._children:
            self._children.remove(child_id)
            self.data_changed.emit()
    
    def has_child(self, child_id: str) -> bool:
        """检查是否包含指定子组件。"""
        return child_id in self._children
    
    @property
    def layout_mode(self) -> str:
        return self._layout_mode
    
    @layout_mode.setter
    def layout_mode(self, value: str):
        valid_modes = ['none', 'vertical', 'horizontal', 'grid']
        if value in valid_modes and self._layout_mode != value:
            self._layout_mode = value
            self.data_changed.emit()
    
    @property
    def spacing(self) -> int:
        return self._spacing
    
    @spacing.setter
    def spacing(self, value: int):
        if value >= 0 and self._spacing != value:
            self._spacing = value
            self.data_changed.emit()
    
    @property
    def padding(self) -> int:
        return self._padding
    
    @padding.setter
    def padding(self, value: int):
        if value >= 0 and self._padding != value:
            self._padding = value
            self.data_changed.emit()
    
    @property
    def auto_size(self) -> bool:
        return self._auto_size
    
    @auto_size.setter
    def auto_size(self, value: bool):
        if self._auto_size != value:
            self._auto_size = value
            self.data_changed.emit()
    
    @property
    def show_border(self) -> bool:
        return self._show_border
    
    @show_border.setter
    def show_border(self, value: bool):
        if self._show_border != value:
            self._show_border = value
            self.data_changed.emit()
    
    @property
    def border_style(self) -> str:
        return self._border_style
    
    @border_style.setter
    def border_style(self, value: str):
        valid_styles = ['solid', 'dashed', 'dotted', 'none']
        if value in valid_styles and self._border_style != value:
            self._border_style = value
            self.data_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['children'] = self._children
        data['layout_mode'] = self._layout_mode
        data['spacing'] = self._spacing
        data['padding'] = self._padding
        data['auto_size'] = self._auto_size
        data['show_border'] = self._show_border
        data['border_style'] = self._border_style
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroupNodeModel':
        instance = super().from_dict(data)
        instance._children = data.get('children', [])
        instance._layout_mode = data.get('layout_mode', 'none')
        instance._spacing = data.get('spacing', 10)
        instance._padding = data.get('padding', 10)
        instance._auto_size = data.get('auto_size', False)
        instance._show_border = data.get('show_border', True)
        instance._border_style = data.get('border_style', 'dashed')
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
    'hidden_button': HiddenButtonModel,
    'image_button': ImageButtonModel,
    'image_carousel': ImageCarouselModel,
    'group_node': GroupNodeModel,
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
