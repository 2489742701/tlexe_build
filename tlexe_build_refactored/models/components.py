"""组件模型模块。

所有组件模型使用 SignalProperty 声明属性，自动获得：
- 属性变更时 emit 信号
- to_dict/from_dict 自动序列化（基类处理）
- 类型注解

子类只需声明 SignalProperty 和业务方法，无需手写 property/setter/to_dict/from_dict。

例外：需要 _sync_xxx 方法的属性（items/item_labels/images/image_labels）
必须手写 @property + setter，因为赋值时需要调用同步方法。
此时需覆盖 to_dict/from_dict 处理这些手写属性。

命名约定：
- 组件类名：{功能}Model（ButtonModel, LabelModel, LotteryModel）
- comp_type 字符串：snake_case（button, label, text_alternating）
- 枚举值：小写下划线（lottery_animation, start_alternating）
"""

from typing import Dict, Any, Optional, Type, List

from PySide6.QtCore import Signal

from .base import ComponentModel, SignalProperty
from .component_registry import register_component

@register_component('button')
class ButtonModel(ComponentModel):
    """按钮组件模型。"""

    target_window_id: str = SignalProperty("")
    branch_name: str = SignalProperty("")
    open_mode: str = SignalProperty("new_window")
    is_default: bool = SignalProperty(False)
    is_cancel: bool = SignalProperty(False)
    alignment: str = SignalProperty("center")

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 40, text: str = "按钮",
                 parent_id: str = ""):
        super().__init__("button", name, x, y, width, height, text, parent_id)

    @property
    def has_branch(self) -> bool:
        return bool(self.target_window_id)

    @property
    def action_params(self) -> Dict[str, Any]:
        return self._action.params

    @action_params.setter
    def action_params(self, value: Dict[str, Any]) -> None:
        if self._action.params != value:
            self._action.params = value
            self.data_changed.emit()

@register_component('label')
class LabelModel(ComponentModel):
    """标签组件模型。"""

    lottery_finished = Signal(int, str)

    alignment: str = SignalProperty("center")
    word_wrap: bool = SignalProperty(True)
    auto_size: bool = SignalProperty(True)

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 30, text: str = "文本",
                 parent_id: str = ""):
        super().__init__("label", name, x, y, width, height, text, parent_id)
        self._style.background_color = "transparent"
        self._style.border_color = "transparent"
        self._style.border_width = 0

    def lottery_animation(self, candidates: list = None, duration_ms: int = 3000, on_finished=None):
        import random
        if candidates is None:
            candidates = [c.strip() for c in self.text.split('\n') if c.strip()]
        if len(candidates) < 2:
            return
        final_text = random.choice(candidates)
        final_index = candidates.index(final_text)
        from PySide6.QtCore import QTimer, QElapsedTimer, QEasingCurve
        elapsed_timer = QElapsedTimer()
        elapsed_timer.start()

        def update_animation():
            elapsed = elapsed_timer.elapsed()
            progress = min(elapsed / duration_ms, 1.0)
            easing = QEasingCurve(QEasingCurve.Type.OutQuart)
            eased_progress = easing.valueForProgress(progress)
            if progress < 1.0:
                speed = int(50 + eased_progress * 200)
                current_idx = int(elapsed / speed) % len(candidates)
                self.text = candidates[current_idx]
            else:
                self.text = final_text
                self._lottery_timer.stop()
                self._lottery_timer = None
                self.lottery_finished.emit(final_index, final_text)
                if on_finished:
                    on_finished(final_text)

        self._lottery_timer = QTimer(self)
        self._lottery_timer.timeout.connect(update_animation)
        self._lottery_timer.start(50)

@register_component('input')
class InputModel(ComponentModel):
    """输入框组件模型。"""

    placeholder: str = SignalProperty("")
    max_length: int = SignalProperty(32767)
    is_password: bool = SignalProperty(False)
    is_multiline: bool = SignalProperty(False)

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 30, text: str = "",
                 parent_id: str = ""):
        super().__init__("input", name, x, y, width, height, text, parent_id)
        self._style.border_width = 1

@register_component('container')
class ContainerModel(ComponentModel):
    """容器组件模型。"""

    children: list = SignalProperty(default_factory=list)
    position_mode: str = SignalProperty("center")
    layout: str = SignalProperty("none")
    padding: int = SignalProperty(10)
    spacing: int = SignalProperty(5)

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 400, height: int = 300, text: str = "容器",
                 parent_id: str = ""):
        super().__init__("container", name, x, y, width, height, text, parent_id)

    def add_child(self, child_id: str) -> None:
        if child_id not in self._children:
            self._children.append(child_id)
            self.data_changed.emit()

    def remove_child(self, child_id: str) -> None:
        if child_id in self._children:
            self._children.remove(child_id)
            self.data_changed.emit()

@register_component('checkbox')
class CheckBoxModel(ComponentModel):
    """复选框组件模型。"""

    checked: bool = SignalProperty(False)
    alignment: str = SignalProperty("left")

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 24, text: str = "复选框",
                 parent_id: str = "", alignment: str = "left"):
        super().__init__("checkbox", name, x, y, width, height, text, parent_id)
        self._alignment = alignment

@register_component('combobox')
class ComboBoxModel(ComponentModel):
    """下拉框组件模型。"""

    items: list = SignalProperty(default_factory=list)
    current_index: int = SignalProperty(0)

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 150, height: int = 28, text: str = "",
                 parent_id: str = ""):
        super().__init__("combobox", name, x, y, width, height, text, parent_id)

@register_component('image')
class ImageModel(ComponentModel):
    """图片组件模型。"""

    image_path: str = SignalProperty("")
    aspect_ratio: bool = SignalProperty(True)
    scale_mode: str = SignalProperty("fit", validator=lambda v: v in ['fill', 'fit', 'stretch', 'center', 'tile', 'keep_aspect'])
    border_radius: int = SignalProperty(0)
    opacity: float = SignalProperty(1.0, validator=lambda v: 0.0 <= v <= 1.0)
    hover_effect: bool = SignalProperty(False)
    click_action: str = SignalProperty("none", validator=lambda v: v in ['none', 'zoom', 'open_original'])
    placeholder_text: str = SignalProperty("点击选择图片")

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 150, text: str = "",
                 parent_id: str = ""):
        super().__init__("image", name, x, y, width, height, text, parent_id)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageModel':
        instance = super().from_dict(data)
        if instance._scale_mode == 'keep_aspect':
            instance._scale_mode = 'fit'
        return instance

@register_component('video')
class VideoModel(ComponentModel):
    """视频组件模型。"""

    video_path: str = SignalProperty("")
    auto_play: bool = SignalProperty(False)
    loop: bool = SignalProperty(False)
    muted: bool = SignalProperty(False)
    controls: bool = SignalProperty(True)
    volume: float = SignalProperty(0.8, validator=lambda v: 0.0 <= v <= 1.0)
    poster_image: str = SignalProperty("")
    playback_rate: float = SignalProperty(1.0, validator=lambda v: 0.25 <= v <= 4.0)
    aspect_ratio: bool = SignalProperty(True)
    placeholder_text: str = SignalProperty("点击选择视频")

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 400, height: int = 300, text: str = "",
                 parent_id: str = ""):
        super().__init__("video", name, x, y, width, height, text, parent_id)

@register_component('progressbar')
class ProgressBarModel(ComponentModel):
    """进度条组件模型。"""

    value: int = SignalProperty(0)
    show_text: bool = SignalProperty(True)
    text_position: str = SignalProperty("center", validator=lambda v: v in ['left', 'center', 'right', 'follow'])
    auto_progress: bool = SignalProperty(False)
    duration: int = SignalProperty(3)
    target_window_id: str = SignalProperty("")
    branch_name: str = SignalProperty("")

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 24, text: str = "",
                 parent_id: str = ""):
        super().__init__("progressbar", name, x, y, width, height, text, parent_id)

    @property
    def has_branch(self) -> bool:
        return bool(self.target_window_id)

    @property
    def action_params(self) -> Dict[str, Any]:
        return self._action.params

    @action_params.setter
    def action_params(self, value: Dict[str, Any]) -> None:
        if self._action.params != value:
            self._action.params = value
            self.data_changed.emit()

@register_component('hidden_button')
class HiddenButtonModel(ComponentModel):
    """隐藏按钮组件模型。"""

    clicked = Signal()

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 100, height: int = 100,
                 parent_id: str = ""):
        super().__init__("hidden_button", name, x, y, width, height, "", parent_id)

    def trigger_click(self) -> None:
        self.clicked.emit()

@register_component('image_button')
class ImageButtonModel(ComponentModel):
    """图片按钮组件模型。"""

    clicked = Signal()

    image_path: str = SignalProperty("")
    hover_image_path: str = SignalProperty("")
    pressed_image_path: str = SignalProperty("")

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 40,
                 parent_id: str = ""):
        super().__init__("image_button", name, x, y, width, height, "", parent_id)

    def trigger_click(self) -> None:
        self.clicked.emit()


@register_component('image_carousel')
class ImageCarouselModel(ComponentModel):
    """图片轮播组件模型。"""

    current_index_changed = Signal(int)
    lottery_finished = Signal(int, str)

    current_index: int = SignalProperty(0, emit=('current_index_changed', 'data_changed'))
    interval: int = SignalProperty(2000)
    auto_play: bool = SignalProperty(False)
    loop: bool = SignalProperty(True)

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 300, height: int = 200,
                 text: str = "", parent_id: str = ""):
        super().__init__("image_carousel", name, x, y, width, height, text, parent_id)
        self._images: list = []
        self._image_labels: list = []
        self._is_animating: bool = False

    @property
    def images(self) -> list:
        return self._images

    @images.setter
    def images(self, value: list):
        new_images = list(value) if value else []
        if self._images != new_images:
            self._images = new_images
            self._sync_image_labels()
            self.data_changed.emit()

    @property
    def image_labels(self) -> list:
        return self._image_labels

    @image_labels.setter
    def image_labels(self, value: list):
        new_labels = list(value) if value else []
        if self._image_labels != new_labels:
            self._image_labels = new_labels
            self._sync_image_labels()
            self.data_changed.emit()

    @property
    def is_animating(self) -> bool:
        return self._is_animating

    def _sync_image_labels(self) -> None:
        if len(self._image_labels) > len(self._images):
            self._image_labels = self._image_labels[:len(self._images)]
        elif len(self._image_labels) < len(self._images):
            defaults = [f"图片{i+1}" for i in range(len(self._images) - len(self._image_labels))]
            self._image_labels.extend(defaults)

    def next_image(self) -> None:
        if not self._images:
            return
        if self._loop:
            self.current_index = (self._current_index + 1) % len(self._images)
        elif self._current_index < len(self._images) - 1:
            self.current_index = self._current_index + 1

    def prev_image(self) -> None:
        if not self._images:
            return
        if self._loop:
            self.current_index = (self._current_index - 1) % len(self._images)
        elif self._current_index > 0:
            self.current_index = self._current_index - 1

    def random_image(self) -> None:
        import random
        if len(self._images) > 1:
            self.current_index = random.randint(0, len(self._images) - 1)

    def lottery_animation(self, duration_ms: int = 3000, on_finished=None):
        import random
        from PySide6.QtCore import QTimer, QElapsedTimer, QEasingCurve
        if not self._images or len(self._images) < 2 or self._is_animating:
            return
        final_index = random.randint(0, len(self._images) - 1)
        elapsed_timer = QElapsedTimer()
        elapsed_timer.start()
        self._is_animating = True
        self._lottery_timer = QTimer(self)
        self._lottery_timer.timeout.connect(
            lambda: self._update_lottery(elapsed_timer, duration_ms, final_index, on_finished)
        )
        self._lottery_timer.start(50)

    def _update_lottery(self, elapsed_timer, duration_ms, final_index, on_finished):
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
            self._is_animating = False
            self.current_index = final_index
            winner_image = self._images[final_index] if final_index < len(self._images) else ""
            self.lottery_finished.emit(final_index, winner_image)
            if on_finished:
                on_finished(final_index)
    def stop_lottery(self) -> None:
        if hasattr(self, '_lottery_timer') and self._lottery_timer:
            self._lottery_timer.stop()

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['images'] = self._images
        data['image_labels'] = self._image_labels
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageCarouselModel':
        instance = super().from_dict(data)
        instance._images = data.get('images', [])
        instance._image_labels = data.get('image_labels', [])
        instance._sync_image_labels()
        return instance

@register_component('alternating')
class AlternatingModel(ComponentModel):
    """交替变换基类。

    可以用来轮播文本（如名单）或图片。
    提供 start_alternating, stop_alternating 方法供其他组件联动。
    """
    
    # 定义自定义信号（用于支持动作联动）
    started = Signal()
    stopped = Signal(int, str)          # 参数: 停止时的索引, 停止时的值(文字或路径)
    current_index_changed = Signal(int)

    current_index: int = SignalProperty(0)
    animation_duration: int = SignalProperty(3000, transform=lambda v: max(500, min(30000, int(v))))
    display_mode: str = SignalProperty("text")
    toggle_mode: str = SignalProperty("same", validator=lambda v: v in ('same', 'separate'))

    def __init__(self, comp_type: str = "alternating", **kwargs):
        kwargs.setdefault('name', '交替变换')
        kwargs.setdefault('width', 300)
        kwargs.setdefault('height', 180)
        super().__init__(comp_type, **kwargs)
        self._items: list = []
        self._item_labels: list = []
        self._alternating_timer = None
        self._is_running: bool = False

    @property
    def items(self) -> list:
        return self._items

    @items.setter
    def items(self, value: list):
        new_items = list(value) if value else []
        if self._items != new_items:
            self._items = new_items
            self._sync_item_labels()
            self.data_changed.emit()

    @property
    def item_labels(self) -> list:
        return self._item_labels

    @item_labels.setter
    def item_labels(self, value: list):
        new_labels = list(value) if value else []
        if self._item_labels != new_labels:
            self._item_labels = new_labels
            self._sync_item_labels()
            self.data_changed.emit()

    @property
    def is_running(self) -> bool:
        return self._is_running

    def _sync_item_labels(self) -> None:
        if len(self._item_labels) < len(self._items):
            for i in range(len(self._item_labels), len(self._items)):
                item = self._items[i]
                label = item.replace('.png', '').replace('.jpg', '') if isinstance(item, str) else str(item)
                self._item_labels.append(label)
        elif len(self._item_labels) > len(self._items):
            self._item_labels = self._item_labels[:len(self._items)]

    def start_alternating(self, duration_ms: int = None):
        import random
        from PySide6.QtCore import QTimer, QElapsedTimer
        if not self._items or len(self._items) < 2 or self._is_running:
            return
        if duration_ms is None:
            duration_ms = self._animation_duration
        self._final_index = random.randint(0, len(self._items) - 1)
        elapsed_timer = QElapsedTimer()
        elapsed_timer.start()
        self._is_running = True
        self.started.emit()
        self._alternating_timer = QTimer(self)
        self._alternating_timer.timeout.connect(
            lambda: self._update_alternating(elapsed_timer, duration_ms, self._final_index)
        )
        self._alternating_timer.start(50)

    def _update_alternating(self, elapsed_timer, duration_ms, final_index):
        from PySide6.QtCore import QEasingCurve
        elapsed = elapsed_timer.elapsed()
        progress = min(elapsed / duration_ms, 1.0)
        easing = QEasingCurve(QEasingCurve.Type.OutQuart)
        eased_progress = easing.valueForProgress(progress)
        if progress < 1.0:
            speed = int(50 + eased_progress * 300)
            if self._alternating_timer.interval() != speed:
                self._alternating_timer.setInterval(speed)
            self._current_index = (self._current_index + 1) % len(self._items)
            self.current_index_changed.emit(self._current_index)
            self.data_changed.emit()
        else:
            self._finish_alternating(final_index)

    def _finish_alternating(self, final_index):
        self._alternating_timer.stop()
        self._is_running = False
        self._current_index = final_index
        self.current_index_changed.emit(final_index)
        final_value = self._item_labels[final_index] if final_index < len(self._item_labels) else str(self._items[final_index])
        self.stopped.emit(final_index, final_value)

    def stop_alternating(self):
        if self._alternating_timer:
            self._alternating_timer.stop()
            self._alternating_timer = None
        if self._is_running:
            self._is_running = False
            idx = self._current_index
            val = self._item_labels[idx] if idx < len(self._item_labels) else (str(self._items[idx]) if idx < len(self._items) else "")
            self.stopped.emit(idx, val)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['items'] = self._items
        data['item_labels'] = self._item_labels
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlternatingModel':
        instance = super().from_dict(data)
        instance._items = data.get('items', [])
        instance._item_labels = data.get('item_labels', [])
        instance._sync_item_labels()
        return instance

@register_component('group_node')
class GroupNodeModel(ComponentModel):
    """组节点模型。"""

    children: List[str] = SignalProperty(default_factory=list)
    layout_mode: str = SignalProperty("none", validator=lambda v: v in ['none', 'vertical', 'horizontal', 'grid'])
    spacing: int = SignalProperty(10, validator=lambda v: v >= 0)
    padding: int = SignalProperty(10, validator=lambda v: v >= 0)
    auto_size: bool = SignalProperty(False)
    show_border: bool = SignalProperty(True)
    border_style: str = SignalProperty("dashed", validator=lambda v: v in ['solid', 'dashed', 'dotted', 'none'])

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 300, height: int = 200, text: str = "",
                 parent_id: str = ""):
        super().__init__("group_node", name, x, y, width, height, text, parent_id)
        self._style.background_color = "transparent"
        self._style.border_color = "#999999"
        self._style.border_width = 1
        self._style.border_radius = 5

    def add_child(self, child_id: str) -> None:
        if child_id not in self.children:
            self.children.append(child_id)
            self.data_changed.emit()

    def remove_child(self, child_id: str) -> None:
        if child_id in self.children:
            self.children.remove(child_id)
            self.data_changed.emit()

    def has_child(self, child_id: str) -> bool:
        return child_id in self.children

@register_component('confirm_button')
class ConfirmButtonModel(ComponentModel):
    """确认按钮模型。"""

    all_confirmed = Signal(str)
    confirmed_changed = Signal(str, bool)

    confirm_group: str = SignalProperty("default")
    is_confirmed: bool = SignalProperty(False)

    def __init__(self, **kwargs):
        kwargs.setdefault('comp_type', 'confirm_button')
        kwargs.setdefault('name', '确认按钮')
        kwargs.setdefault('width', 120)
        kwargs.setdefault('height', 40)
        super().__init__(**kwargs)

    def toggle(self) -> None:
        self.is_confirmed = not self._is_confirmed



# ─────────────────────────────────────────────────────────────────────────────
# 以下三个类是对 textarea / listwidget / groupbox 独立 Model 的正式定义。
# 旧版本中它们被错误地注册为 InputModel / ComboBoxModel / ContainerModel 的别名，
# 导致各自的属性编辑器、工厂函数和类型检查全部失效。
# 现在每个类型都有自己的 Model，完整支持类型特定属性扩展。
# ─────────────────────────────────────────────────────────────────────────────

@register_component('textarea')
class TextAreaModel(ComponentModel):
    """多行文本框组件模型。

    继承 ComponentModel 而不是 InputModel，是因为多行文本框有独立的
    滚动策略、行高等属性，与单行输入框在语义上不同。
    """

    placeholder: str = SignalProperty("")
    max_length: int = SignalProperty(32767)
    auto_scroll: bool = SignalProperty(True)     # 内容超长时是否自动滚动到底部
    line_wrap: bool = SignalProperty(True)        # 是否自动换行

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 80, text: str = "",
                 parent_id: str = ""):
        super().__init__("textarea", name, x, y, width, height, text, parent_id)
        self._style.border_width = 1

@register_component('listwidget')
class ListWidgetModel(ComponentModel):
    """列表控件组件模型。

    独立于 ComboBoxModel，因为列表控件支持多选、排序等
    下拉框不具备的功能。
    """

    items: list = SignalProperty(default_factory=list)
    current_index: int = SignalProperty(-1)       # -1 表示无选中项
    selection_mode: str = SignalProperty(
        "single",
        validator=lambda v: v in ["single", "multi", "extended", "none"]
    )
    show_scrollbar: bool = SignalProperty(True)

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 150, text: str = "",
                 parent_id: str = ""):
        super().__init__("listwidget", name, x, y, width, height, text, parent_id)

@register_component('groupbox')
class GroupBoxModel(ComponentModel):
    """分组框组件模型。

    独立于 ContainerModel，因为分组框的语义是「带标题标签的视觉分组」，
    而不是「可嵌套子组件的布局容器」。
    """

    title: str = SignalProperty("")               # 分组框标题（区别于 text）
    checkable: bool = SignalProperty(False)        # 分组框是否可勾选
    checked: bool = SignalProperty(True)           # checkable=True 时的初始勾选状态
    flat: bool = SignalProperty(False)             # 是否使用扁平样式（只显示顶部线条）

    def __init__(self, name: str = "", x: int = 0, y: int = 0,
                 width: int = 200, height: int = 150, text: str = "分组",
                 parent_id: str = ""):
        super().__init__("groupbox", name, x, y, width, height, text, parent_id)
        # title 默认与 text 保持同步，方便序列化兼容
        self._title = text

def create_component(comp_type: str, **kwargs) -> ComponentModel:
    from models.component_registry import ComponentRegistry
    model_class = ComponentRegistry.get_model_class(comp_type)
    if model_class:
        return model_class(**kwargs)
    raise ValueError(f"未知的组件类型: {comp_type}")

