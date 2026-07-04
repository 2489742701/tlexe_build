"""基础模型模块。

核心设计：
- SignalProperty 描述符：属性变更自动 emit Qt 信号，消除子类样板代码
- ComponentModel：QObject 基类，所有组件模型的父类
- ProjectModel：项目数据模型，管理窗口和组件的集合

命名约定：
- 私有属性：单下划线前缀（self._loading, self._components）
- SignalProperty 存储：self._{属性名}（self._x, self._name）
- Qt Signal：snake_case + 过去分词（data_changed, position_changed）
- 常量：UPPER_SNAKE_CASE（模块级）或类级 PascalCase 常量

序列化约定：
- 属性名 `type` 序列化为 `comp_type`（通过 serialize_as 参数）
- Pydantic 模型用 model_dump() / model_validate()
- 子类有手写 @property 属性时，需覆盖 to_dict/from_dict
"""

import uuid
import json
import inspect
from typing import Dict, Any, List, Optional, Callable, Tuple, Type, Union

from PySide6.QtCore import QObject, Signal

from .schemas import StyleConfig, ActionConfig

class _Sentinel:
    pass

_NOT_SET = _Sentinel()

class SignalProperty:
    """描述符：属性变更时自动发射 Qt 信号。

    用法::

        class MyModel(ComponentModel):
            name: str = SignalProperty("")
            width: int = SignalProperty(100, emit='size_changed')
            items: list = SignalProperty(default_factory=list)
            opacity: float = SignalProperty(1.0, validator=lambda v: 0.0 <= v <= 1.0)
            duration: int = SignalProperty(3000, transform=lambda v: max(500, min(30000, int(v))))

    参数:
        default: 默认值
        default_factory: 可变类型的默认值工厂（如 list, dict）
        validator: 值验证函数，返回 False 时拒绝赋值
        transform: 值变换函数，赋值前自动变换
        emit: 属性变更时 emit 的信号名元组，默认 ('data_changed',)
        emit_args: 信号参数生成器，如 {'size_changed': lambda o: (o._width, o._height)}
        readonly: 只读属性，setter 静默忽略
        serialize_as: 序列化时使用的键名（默认使用属性名）

    行为:
        - 属性变更时自动 emit 指定信号（默认 data_changed）
        - _loading=True 期间不 emit，用于 from_dict 批量加载
        - 值未改变时跳过赋值和信号发射（old == new 检测）
        - 需调用 _sync 方法的属性不能用 SignalProperty，必须手写 @property + setter
    """

    def __init__(
        self,
        default: Any = _NOT_SET,
        *,
        default_factory: Optional[Callable[[], Any]] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        transform: Optional[Callable[[Any], Any]] = None,
        emit: Union[str, Tuple[str, ...]] = ('data_changed',),
        emit_args: Optional[Dict[str, Callable]] = None,
        readonly: bool = False,
        serialize_as: Optional[str] = None,
    ):
        self._default = default
        self._default_factory = default_factory
        self.validator = validator
        self.transform = transform
        if isinstance(emit, str):
            emit = (emit,)
        self.emit_names: Tuple[str, ...] = emit
        self.emit_args: Dict[str, Callable] = emit_args or {}
        self.readonly = readonly
        self.serialize_as = serialize_as
        self.name: str = ''
        self.storage: str = ''

    def __set_name__(self, owner, name: str):
        self.name = name
        self.storage = f'_{name}'

    def _get_default(self) -> Any:
        if self._default_factory is not None:
            return self._default_factory()
        if self._default is _NOT_SET:
            return None
        return self._default

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return getattr(obj, self.storage)
        except AttributeError:
            default = self._get_default()
            setattr(obj, self.storage, default)
            return default

    def __set__(self, obj, value):
        if self.readonly:
            return
        if self.transform:
            value = self.transform(value)
        if self.validator and not self.validator(value):
            return
        try:
            old = getattr(obj, self.storage)
        except AttributeError:
            old = _NOT_SET
        if old is not _NOT_SET and old == value:
            return
        setattr(obj, self.storage, value)
        if not getattr(obj, '_loading', False):
            for emit_name in self.emit_names:
                try:
                    signal = getattr(obj, emit_name)
                    if emit_name in self.emit_args:
                        signal.emit(*self.emit_args[emit_name](obj))
                    else:
                        signal.emit()
                except (AttributeError, RuntimeError, TypeError):
                    pass

class ComponentModel(QObject):
    """组件数据模型基类。

    所有组件模型的父类。基础属性用 SignalProperty 声明，
    to_dict/from_dict 自动收集所有 SignalProperty 字段进行序列化。

    子类只需声明 SignalProperty 和业务方法，无需手写 property/setter/to_dict/from_dict。
    如有手写 @property 属性（如 items/item_labels），需覆盖 to_dict/from_dict。

    Signals:
        data_changed: 任何属性变更时发射
        position_changed: 位置变更时发射 (x, y)
        size_changed: 尺寸变更时发射 (width, height)
        style_changed: 样式变更时发射
        action_changed: 动作配置变更时发射
    """

    data_changed = Signal()
    position_changed = Signal(int, int)
    size_changed = Signal(int, int)
    style_changed = Signal()
    action_changed = Signal()

    id: str = SignalProperty("")
    type: str = SignalProperty("", readonly=True, serialize_as="comp_type")
    name: str = SignalProperty("")
    x: int = SignalProperty(0, emit=('position_changed', 'data_changed'), emit_args={'position_changed': lambda o: (o._x, o._y)})
    y: int = SignalProperty(0, emit=('position_changed', 'data_changed'), emit_args={'position_changed': lambda o: (o._x, o._y)})
    width: int = SignalProperty(120, emit=('size_changed', 'data_changed'), emit_args={'size_changed': lambda o: (o._width, o._height)})
    height: int = SignalProperty(40, emit=('size_changed', 'data_changed'), emit_args={'size_changed': lambda o: (o._width, o._height)})
    text: str = SignalProperty("")
    parent_id: str = SignalProperty("")
    style: StyleConfig = SignalProperty(default_factory=StyleConfig, emit=('style_changed', 'data_changed'))
    action: ActionConfig = SignalProperty(default_factory=ActionConfig, emit=('action_changed', 'data_changed'))
    visible: bool = SignalProperty(True)
    enabled: bool = SignalProperty(True)
    custom_props: Dict[str, Any] = SignalProperty(default_factory=dict)
    h_align: str = SignalProperty("none")
    v_align: str = SignalProperty("none")

    def __init__(self, comp_type: str = "component", name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 40, text: str = "", parent_id: str = ""):
        super().__init__()
        self._loading = True
        self._id = str(uuid.uuid4())[:8]
        self._type = comp_type
        self._name = name or f"{comp_type}_{self._id}"
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._text = text
        self._parent_id = parent_id
        self._style = StyleConfig()
        self._action = ActionConfig()
        self._visible = True
        self._enabled = True
        self._custom_props: Dict[str, Any] = {}
        self._h_align = "none"
        self._v_align = "none"
        self._loading = False

    @classmethod
    def _get_base_property_names(cls) -> set:
        if not hasattr(ComponentModel, '_base_prop_cache'):
            base_props = set()
            for attr_name, attr_val in vars(ComponentModel).items():
                if isinstance(attr_val, SignalProperty):
                    base_props.add(attr_name)
            ComponentModel._base_prop_cache = base_props
        return ComponentModel._base_prop_cache

    @classmethod
    def _get_extra_properties(cls) -> Dict[str, SignalProperty]:
        cache_key = f'_extra_prop_cache_{cls.__name__}'
        if not hasattr(cls, cache_key):
            base_names = cls._get_base_property_names()
            result: Dict[str, SignalProperty] = {}
            for klass in reversed(cls.__mro__):
                if klass is ComponentModel:
                    continue
                for attr_name, attr_val in vars(klass).items():
                    if isinstance(attr_val, SignalProperty) and attr_name not in base_names:
                        result[attr_name] = attr_val
            setattr(cls, cache_key, result)
        return getattr(cls, cache_key)

    def set_position(self, x: int, y: int) -> None:
        if self._x != x or self._y != y:
            self._x, self._y = x, y
            self.position_changed.emit(x, y)
            self.data_changed.emit()

    def set_size(self, width: int, height: int) -> None:
        if self._width != width or self._height != height:
            self._width, self._height = width, height
            self.size_changed.emit(width, height)
            self.data_changed.emit()

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'id': self._id,
            'comp_type': self._type,
            'name': self._name,
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'text': self._text,
            'parent_id': self._parent_id,
            'style': self._style.model_dump(),
            'action': self._action.model_dump(),
            'visible': self._visible,
            'enabled': self._enabled,
            'custom_props': self._custom_props,
            'h_align': self._h_align,
            'v_align': self._v_align,
        }
        for name, prop in self._get_extra_properties().items():
            value = getattr(self, name)
            if hasattr(value, 'model_dump'):
                value = value.model_dump()
            key = prop.serialize_as or name
            data[key] = value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentModel':
        comp_type = data.get('comp_type') or data.get('type', 'component')
        sig = inspect.signature(cls.__init__)
        params = list(sig.parameters.keys())

        kwargs: Dict[str, Any] = {
            'name': data.get('name', ''),
            'x': data.get('x', 0),
            'y': data.get('y', 0),
            'width': data.get('width', 120),
            'height': data.get('height', 40),
            'text': data.get('text', ''),
            'parent_id': data.get('parent_id', ''),
        }
        if 'comp_type' in params:
            kwargs['comp_type'] = comp_type

        instance = cls(**kwargs)
        instance._loading = True
        instance._id = data.get('id', instance._id)

        style_data = data.get('style', {})
        instance._style = StyleConfig.model_validate(style_data) if style_data else StyleConfig()

        action_data = data.get('action', {})
        instance._action = ActionConfig.model_validate(action_data) if action_data else ActionConfig()

        instance._visible = data.get('visible', True)
        instance._enabled = data.get('enabled', True)
        instance._custom_props = data.get('custom_props', {})
        instance._h_align = data.get('h_align', 'none')
        instance._v_align = data.get('v_align', 'none')

        for name, prop in cls._get_extra_properties().items():
            key = prop.serialize_as or name
            if key in data:
                setattr(instance, prop.storage, data[key])

        instance._loading = False
        return instance

class ProjectModel(QObject):
    """项目数据模型。"""

    component_added = Signal(str)
    component_removed = Signal(str)
    component_changed = Signal(str)
    window_added = Signal(str)
    window_removed = Signal(str)
    window_changed = Signal(str)
    current_window_changed = Signal(str)
    project_loaded = Signal()
    project_saved = Signal()

    def __init__(self):
        super().__init__()
        self._name: str = "新建项目"
        self._components: Dict[str, ComponentModel] = {}
        self._windows: Dict[str, Any] = {}
        self._current_window_id: Optional[str] = None
        self._main_window_id: Optional[str] = None
        self._file_path: Optional[str] = None
        self._dirty: bool = False
        self._linkages: List[Dict[str, Any]] = []
        self._init_main_window()

    def _init_main_window(self) -> None:
        from .window import WindowModel
        from .schemas import WindowType
        main_window = WindowModel(name="主程序", window_type=WindowType.MAIN, width=800, height=600)
        self._windows[main_window.id] = main_window
        self._main_window_id = main_window.id
        self._current_window_id = main_window.id
        main_window.data_changed.connect(lambda: self.window_changed.emit(main_window.id))

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self) -> None:
        self._dirty = True

    def mark_clean(self) -> None:
        self._dirty = False

    @property
    def current_window_id(self) -> Optional[str]:
        return self._current_window_id

    @property
    def main_window_id(self) -> Optional[str]:
        return self._main_window_id

    @property
    def current_window(self):
        if self._current_window_id:
            return self._windows.get(self._current_window_id)
        return None

    def get_component(self, comp_id: str) -> Optional[ComponentModel]:
        return self._components.get(comp_id)

    def get_all_components(self) -> List[ComponentModel]:
        return list(self._components.values())

    def add_component(self, comp: ComponentModel, window_id: Optional[str] = None) -> str:
        self._components[comp.id] = comp
        comp.data_changed.connect(lambda: self.component_changed.emit(comp.id))
        comp.data_changed.connect(self.mark_dirty)
        target_window_id = window_id or self._current_window_id
        if target_window_id and target_window_id in self._windows:
            self._windows[target_window_id].add_component(comp.id)
        self.mark_dirty()
        self.component_added.emit(comp.id)
        return comp.id

    def remove_component(self, comp_id: str) -> bool:
        if comp_id in self._components:
            comp = self._components[comp_id]
            try:
                comp.data_changed.disconnect()
            except TypeError:
                pass
            del self._components[comp_id]
            self.mark_dirty()
            self.component_removed.emit(comp_id)
            return True
        return False

    def add_window(self, window, trigger_button_id: Optional[str] = None) -> str:
        self._windows[window.id] = window
        if trigger_button_id:
            window.trigger_button_id = trigger_button_id
        window.data_changed.connect(lambda: self.window_changed.emit(window.id))
        window.data_changed.connect(self.mark_dirty)
        self.mark_dirty()
        self.window_added.emit(window.id)
        return window.id

    def remove_window(self, window_id: str) -> bool:
        if window_id in self._windows:
            window = self._windows[window_id]
            if window.is_main:
                return False
            for comp_id in window.components:
                if comp_id in self._components:
                    comp = self._components[comp_id]
                    try:
                        comp.data_changed.disconnect()
                    except TypeError:
                        pass
                    del self._components[comp_id]
            try:
                window.data_changed.disconnect()
            except TypeError:
                pass
            del self._windows[window_id]
            self.mark_dirty()
            self.window_removed.emit(window_id)
            if self._current_window_id == window_id:
                self._current_window_id = self._main_window_id
                self.current_window_changed.emit(self._current_window_id)
            return True
        return False

    def get_window(self, window_id: str):
        return self._windows.get(window_id)

    def get_all_windows(self) -> list:
        return list(self._windows.values())

    @property
    def linkages(self) -> List[Dict[str, Any]]:
        return self._linkages

    @linkages.setter
    def linkages(self, value: List[Dict[str, Any]]) -> None:
        self._linkages = value or []
        self.mark_dirty()

    def get_main_window(self):
        if self._main_window_id:
            return self._windows.get(self._main_window_id)
        return None

    def set_current_window(self, window_id: str) -> None:
        if window_id in self._windows and window_id != self._current_window_id:
            self._current_window_id = window_id
            self.current_window_changed.emit(window_id)

    def get_components_for_window(self, window_id: str) -> List[ComponentModel]:
        window = self._windows.get(window_id)
        if not window:
            return []
        return [self._components[cid] for cid in window.components if cid in self._components]

    def create_event_for_button(self, button_id: str, event_name: str = "") -> str:
        from .window import WindowModel
        from .schemas import WindowType
        from .components import ButtonModel, ProgressBarModel

        component = self._components.get(button_id)
        if not component:
            return ""
        if not isinstance(component, (ButtonModel, ProgressBarModel)):
            return ""
        if not event_name:
            if isinstance(component, ButtonModel):
                event_name = f"{component.text}事件"
            elif isinstance(component, ProgressBarModel):
                event_name = f"{component.name}完成事件"
            else:
                event_name = "新事件"
        event_window = WindowModel(name=event_name, window_type=WindowType.EVENT, width=600, height=400)
        component.target_window_id = event_window.id
        component.branch_name = event_name
        self.add_window(event_window, button_id)
        return event_window.id

    def clear(self) -> None:
        self._components.clear()
        self._windows.clear()
        self._current_window_id = None
        self._main_window_id = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self._name,
            'windows': [w.to_dict() for w in self._windows.values()],
            'components': [c.to_dict() for c in self._components.values()],
            'main_window_id': self._main_window_id,
            'current_window_id': self._current_window_id,
            'linkages': self._linkages,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        from .window import WindowModel

        self._name = data.get('name', '新建项目')
        self._components.clear()
        self._windows.clear()

        for win_data in data.get('windows', []):
            window = WindowModel.from_dict(win_data)
            self._windows[window.id] = window
            window.data_changed.connect(lambda wid=window.id: self.window_changed.emit(wid))

        self._main_window_id = data.get('main_window_id')
        self._current_window_id = data.get('current_window_id')
        self._linkages = data.get('linkages', [])

        if not self._windows:
            self._init_main_window()
        if not self._current_window_id or self._current_window_id not in self._windows:
            self._current_window_id = self._main_window_id

        for comp_data in data.get('components', []):
            from .component_registry import ComponentRegistry
            comp_type = comp_data.get('comp_type') or comp_data.get('type', 'component')
            model_class = ComponentRegistry.get_model_class(comp_type)
            if model_class:
                comp = model_class.from_dict(comp_data)
            else:
                comp = ComponentModel.from_dict(comp_data)
            self._components[comp.id] = comp
            comp.data_changed.connect(lambda cid=comp.id: self.component_changed.emit(cid))
            comp.data_changed.connect(self.mark_dirty)

        self.mark_clean()
        self.project_loaded.emit()

    def save_to_file(self, file_path: str) -> bool:
        try:
            self._file_path = file_path
            from utils.py_project_format import dict_to_python_code, is_itexe_project_file
            if is_itexe_project_file(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            else:
                code = dict_to_python_code(self.to_dict(), self.name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
            self.mark_clean()
            self.project_saved.emit()
            return True
        except Exception:
            return False

    def load_from_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            from utils.py_project_format import python_code_to_dict
            data = python_code_to_dict(content)
            self._file_path = file_path
            self.from_dict(data)
            self.mark_clean()
            return True
        except Exception as e:
            print(f"加载项目失败: {e}")
            import traceback
            traceback.print_exc()
            return False
