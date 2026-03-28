"""基础模型模块。

本模块包含组件基类、项目模型和样式配置等核心数据结构。
"""

import uuid
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal


@dataclass
class ActionConfig:
    """行为配置。
    
    定义组件被触发时执行的操作，如按钮点击后执行的动作。
    
    Attributes:
        action_type: 动作类型，如 "none", "close_program", "open_event" 等
        params: 动作参数字典，根据 action_type 不同而不同
        blockly_xml: Blockly 积木块 XML 代码（预留）
        python_code: Python 脚本代码（预留）
    """
    action_type: str = "none"
    params: Dict[str, Any] = field(default_factory=dict)
    blockly_xml: str = ""
    python_code: str = ""


@dataclass
class StyleConfig:
    """组件样式配置。
    
    Attributes:
        background_color: 背景颜色，十六进制格式如 "#f0f0f0"
        text_color: 文本颜色，十六进制格式
        border_color: 边框颜色，十六进制格式
        border_width: 边框宽度，单位像素
        border_radius: 圆角半径，单位像素
        font_family: 字体名称，如 "Microsoft YaHei"
        font_size: 字体大小，单位磅
        font_bold: 是否加粗，True 为粗体，False 为正常
        use_native_style: 是否使用原生样式，True 为系统原生风格，False 为自定义样式
    """
    background_color: str = "#f0f0f0"
    text_color: str = "#333333"
    border_color: str = "#999999"
    border_width: int = 1
    border_radius: int = 5
    font_family: str = "Microsoft YaHei"
    font_size: int = 12
    font_bold: bool = False
    use_native_style: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'background_color': self.background_color,
            'text_color': self.text_color,
            'border_color': self.border_color,
            'border_width': self.border_width,
            'border_radius': self.border_radius,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_bold': self.font_bold,
            'use_native_style': self.use_native_style,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StyleConfig':
        return cls(
            background_color=data.get('background_color', '#f0f0f0'),
            text_color=data.get('text_color', '#333333'),
            border_color=data.get('border_color', '#999999'),
            border_width=data.get('border_width', 1),
            border_radius=data.get('border_radius', 5),
            font_family=data.get('font_family', 'Microsoft YaHei'),
            font_size=data.get('font_size', 12),
            font_bold=data.get('font_bold', False),
            use_native_style=data.get('use_native_style', False),
        )


class ComponentModel(QObject):
    """组件数据模型基类。"""
    
    data_changed = Signal()
    position_changed = Signal(int, int)
    size_changed = Signal(int, int)
    style_changed = Signal()
    action_changed = Signal()

    def __init__(self, comp_type: str, name: str = "", x: int = 0, y: int = 0,
                 width: int = 120, height: int = 40, text: str = "",
                 parent_id: str = ""):
        super().__init__()
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
        self._h_align: str = "none"
        self._v_align: str = "none"

    @property
    def id(self) -> str:
        return self._id

    @property
    def type(self) -> str:
        return self._type

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if self._name != value:
            self._name = value
            self.data_changed.emit()

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        if self._x != value:
            self._x = value
            self.position_changed.emit(self._x, self._y)
            self.data_changed.emit()

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        if self._y != value:
            self._y = value
            self.position_changed.emit(self._x, self._y)
            self.data_changed.emit()

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int):
        if self._width != value:
            self._width = value
            self.size_changed.emit(self._width, self._height)
            self.data_changed.emit()

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int):
        if self._height != value:
            self._height = value
            self.size_changed.emit(self._width, self._height)
            self.data_changed.emit()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        if self._text != value:
            self._text = value
            self.data_changed.emit()

    @property
    def parent_id(self) -> str:
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value: str):
        self._parent_id = value

    @property
    def style(self) -> StyleConfig:
        return self._style

    @style.setter
    def style(self, value: StyleConfig):
        if self._style != value:
            self._style = value
            self.style_changed.emit()
            self.data_changed.emit()

    @property
    def action(self) -> ActionConfig:
        return self._action

    @action.setter
    def action(self, value: ActionConfig):
        if self._action != value:
            self._action = value
            self.action_changed.emit()
            self.data_changed.emit()

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        if self._visible != value:
            self._visible = value
            self.data_changed.emit()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if self._enabled != value:
            self._enabled = value
            self.data_changed.emit()

    @property
    def h_align(self) -> str:
        return self._h_align
    
    @h_align.setter
    def h_align(self, value: str):
        if self._h_align != value:
            self._h_align = value
            self.data_changed.emit()
    
    @property
    def v_align(self) -> str:
        return self._v_align
    
    @v_align.setter
    def v_align(self, value: str):
        if self._v_align != value:
            self._v_align = value
            self.data_changed.emit()

    def set_position(self, x: int, y: int):
        if self._x != x or self._y != y:
            self._x = x
            self._y = y
            self.position_changed.emit(x, y)
            self.data_changed.emit()

    def set_size(self, width: int, height: int):
        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            self.size_changed.emit(width, height)
            self.data_changed.emit()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'comp_type': self._type,
            'name': self._name,
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'text': self._text,
            'parent_id': self._parent_id,
            'style': self._style.to_dict(),
            'action': {
                'action_type': self._action.action_type,
                'params': self._action.params,
                'blockly_xml': self._action.blockly_xml,
                'python_code': self._action.python_code,
            },
            'visible': self._visible,
            'enabled': self._enabled,
            'custom_props': self._custom_props,
            'h_align': self._h_align,
            'v_align': self._v_align,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentModel':
        comp_type = data.get('comp_type') or data.get('type', 'component')
        
        import inspect
        sig = inspect.signature(cls.__init__)
        params = list(sig.parameters.keys())
        
        kwargs = {
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
        instance._id = data.get('id', instance._id)
        
        style_data = data.get('style', {})
        instance._style = StyleConfig.from_dict(style_data)
        
        action_data = data.get('action', {})
        instance._action = ActionConfig(
            action_type=action_data.get('action_type', 'none'),
            params=action_data.get('params', {}),
            blockly_xml=action_data.get('blockly_xml', ''),
            python_code=action_data.get('python_code', ''),
        )
        
        instance._visible = data.get('visible', True)
        instance._enabled = data.get('enabled', True)
        instance._custom_props = data.get('custom_props', {})
        instance._h_align = data.get('h_align', 'none')
        instance._v_align = data.get('v_align', 'none')
        
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
        self._name = "新建项目"
        self._components: Dict[str, ComponentModel] = {}
        self._windows: Dict[str, Any] = {}
        self._current_window_id: Optional[str] = None
        self._main_window_id: Optional[str] = None
        self._file_path: Optional[str] = None
        self._dirty: bool = False
        
        self._init_main_window()

    def _init_main_window(self):
        from .window import WindowModel, WindowType
        main_window = WindowModel(
            name="主程序",
            window_type=WindowType.MAIN,
            width=800,
            height=600
        )
        self._windows[main_window.id] = main_window
        self._main_window_id = main_window.id
        self._current_window_id = main_window.id
        main_window.data_changed.connect(lambda: self.window_changed.emit(main_window.id))

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
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

    def get_all_windows(self) -> List[Any]:
        return list(self._windows.values())

    def get_main_window(self):
        if self._main_window_id:
            return self._windows.get(self._main_window_id)
        return None

    def set_current_window(self, window_id: str):
        if window_id in self._windows and window_id != self._current_window_id:
            self._current_window_id = window_id
            self.current_window_changed.emit(window_id)

    def get_components_for_window(self, window_id: str) -> List[ComponentModel]:
        window = self._windows.get(window_id)
        if not window:
            return []
        return [self._components[cid] for cid in window.components if cid in self._components]

    def create_event_for_button(self, button_id: str, event_name: str = "") -> str:
        from .window import WindowModel, WindowType
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
        
        event_window = WindowModel(
            name=event_name,
            window_type=WindowType.EVENT,
            width=600,
            height=400
        )
        
        component.target_window_id = event_window.id
        if isinstance(component, ButtonModel):
            component.branch_name = event_name
        
        self.add_window(event_window, button_id)
        
        return event_window.id

    def clear(self):
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
        }

    def from_dict(self, data: Dict[str, Any]):
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
        
        if not self._windows:
            self._init_main_window()
        
        if not self._current_window_id or self._current_window_id not in self._windows:
            self._current_window_id = self._main_window_id
        
        for comp_data in data.get('components', []):
            from .components import create_component, COMPONENT_TYPE_MAP
            comp_type = comp_data.get('comp_type') or comp_data.get('type', 'component')
            if comp_type in COMPONENT_TYPE_MAP:
                comp = COMPONENT_TYPE_MAP[comp_type].from_dict(comp_data)
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
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            self.mark_clean()
            self.project_saved.emit()
            return True
        except Exception:
            return False

    def load_from_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._file_path = file_path
            self.from_dict(data)
            self.mark_clean()
            return True
        except Exception as e:
            print(f"加载项目失败: {e}")
            import traceback
            traceback.print_exc()
            return False
