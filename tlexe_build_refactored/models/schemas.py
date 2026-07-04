"""统一数据模式定义。

纯数据结构使用 Pydantic BaseModel，自动获得序列化/验证/类型安全。
枚举统一在此定义，消除原来 base.py 和 window.py 的 ActionType 重复。

命名约定：
- 枚举类名：PascalCase（ActionType, WindowType, SignalType）
- 枚举值：UPPER_SNAKE_CASE（CLOSE_PROGRAM, TEXT_CHANGED）
- Pydantic 模型：PascalCase + Config/Schema 后缀（StyleConfig, SignalConnectionSchema）
- 枚举继承 str, Enum：使枚举值可直接当字符串使用和比较
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ActionType(str, Enum):
    NONE = "none"
    CLOSE_PROGRAM = "close_program"
    CLOSE_WINDOW = "close_window"
    OPEN_WINDOW = "open_window"
    SWITCH_WINDOW = "switch_window"
    OPEN_EVENT = "open_event"
    OPEN_FILE = "open_file"
    OPEN_URL = "open_url"
    RANDOM_IMAGE = "random_image"
    NEXT_IMAGE = "next_image"
    PREV_IMAGE = "prev_image"
    START_CAROUSEL = "start_carousel"
    STOP_CAROUSEL = "stop_carousel"
    LOTTERY_ANIMATION = "lottery_animation"
    START_ALTERNATING = "start_alternating"
    STOP_ALTERNATING = "stop_alternating"
    CONFIRM_CHECK = "confirm_check"
    SET_TEXT = "set_text"
    SHOW_COMPONENT = "show_component"
    HIDE_COMPONENT = "hide_component"
    SHOW_MESSAGE = "show_message"
    EXECUTE_PYTHON = "execute_python"
    RUN_SCRIPT = "run_script"
    RUN_COMMAND = "run_command"
    RUN_CMD = "run_cmd"
    RUN_POWERSHELL = "run_powershell"
    SET_PROPERTY = "set_property"
    DELAY = "delay"
    GET_SYSTEM_INFO = "get_system_info"
    RUN_AS_ADMIN = "run_as_admin"
    CUSTOM = "custom"

class WindowType(str, Enum):
    MAIN = "main"
    EVENT = "event"

class VariableType(str, Enum):
    NAME = "名字"
    NUMBER = "数字"
    PASSWORD = "密码"
    TEXT = "文本"
    ARRAY = "数组"
    BOOLEAN = "开关"

class SignalType(str, Enum):
    TEXT_CHANGED = "文本改变"
    VALUE_CHANGED = "值改变"
    CLICKED = "点击"
    MATCH_SUCCESS = "配对成功"
    MATCH_FAILED = "配对失败"
    STATE_CHANGED = "状态改变"
    VARIABLE_READ = "读取变量"
    VARIABLE_SET = "设置变量"
    CUSTOM = "自定义"

class CommActionType(str, Enum):
    SET_TEXT = "设置文本"
    SET_VALUE = "设置值"
    SHOW = "显示"
    HIDE = "隐藏"
    ENABLE = "启用"
    DISABLE = "禁用"
    OPEN_WINDOW = "打开窗口"
    CLOSE_WINDOW = "关闭窗口"
    SHOW_MESSAGE = "显示消息"
    READ_VARIABLE = "读取变量"
    SET_VARIABLE = "设置变量"
    MATCH_VARIABLE = "配对变量"
    INCREMENT = "增加数值"
    DECREMENT = "减少数值"
    APPEND_ARRAY = "追加数组"
    CLEAR_ARRAY = "清空数组"
    EXECUTE_CODE = "执行代码"

class StyleConfig(BaseModel):
    background_color: str = "#f0f0f0"
    text_color: str = "#333333"
    border_color: str = "#999999"
    border_width: int = 0
    border_radius: int = 5
    font_family: str = "Microsoft YaHei"
    font_size: int = 12
    font_bold: bool = False
    use_native_style: bool = False

class ActionConfig(BaseModel):
    action_type: str = "none"
    params: Dict[str, Any] = Field(default_factory=dict)
    blockly_xml: str = ""
    python_code: str = ""

    def get_target_component_id(self) -> str:
        return self.params.get("target_component_id", "")

    def get_target_window_id(self) -> str:
        return self.params.get("target_window_id", "")

    def get_action_params(self) -> Dict[str, Any]:
        return self.params.get("action_params", {})

class ActionDefinition(BaseModel):
    action_type: ActionType = ActionType.NONE
    display_name: str = ""
    description: str = ""
    params: Dict[str, Any] = Field(default_factory=dict)

class VariableSchema(BaseModel):
    name: str = ""
    value: Any = None
    var_type: VariableType = VariableType.TEXT
    description: str = ""
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def reset(self) -> None:
        self.value = self.default_value

class BindingConfig(BaseModel):
    component_id: str = ""
    variable_name: str = ""
    component_property: str = "text"
    bidirectional: bool = False

class ConditionalActionConfig(BaseModel):
    condition: str = ""
    true_action: Dict[str, Any] = Field(default_factory=dict)
    false_action: Dict[str, Any] = Field(default_factory=dict)

class SignalConnectionSchema(BaseModel):
    id: str = ""
    source_id: str = ""
    signal_type: str = "自定义"
    target_id: str = ""
    action_type: str = "设置文本"
    action_params: Dict[str, Any] = Field(default_factory=dict)
    condition: Optional[str] = None
    enabled: bool = True

class CommunicationChannelSchema(BaseModel):
    id: str = ""
    name: str = ""
    container_id: str = ""
    member_ids: List[str] = Field(default_factory=list)
    connections: List[SignalConnectionSchema] = Field(default_factory=list)

DEFAULT_ACTIONS: List[ActionDefinition] = [
    ActionDefinition(action_type=ActionType.NONE, display_name="无动作", description="不执行任何动作"),
    ActionDefinition(action_type=ActionType.CLOSE_PROGRAM, display_name="关闭程序", description="关闭整个应用程序"),
    ActionDefinition(action_type=ActionType.CLOSE_WINDOW, display_name="关闭窗口", description="关闭当前窗口"),
    ActionDefinition(action_type=ActionType.OPEN_EVENT, display_name="打开事件", description="打开指定的事件窗口", params={"target_event_id": ""}),
    ActionDefinition(action_type=ActionType.OPEN_FILE, display_name="打开文件", description="使用系统默认程序打开文件", params={"file_path": ""}),
    ActionDefinition(action_type=ActionType.OPEN_URL, display_name="打开网址", description="在浏览器中打开网址", params={"url": ""}),
    ActionDefinition(action_type=ActionType.RUN_SCRIPT, display_name="运行脚本", description="运行 Python 脚本文件", params={"script_path": "", "wait": False}),
    ActionDefinition(action_type=ActionType.RUN_COMMAND, display_name="运行命令", description="执行系统命令", params={"command": "", "wait": False}),
    ActionDefinition(action_type=ActionType.SHOW_MESSAGE, display_name="显示消息", description="显示消息对话框", params={"title": "消息", "message": "", "type": "info"}),
    ActionDefinition(action_type=ActionType.SET_PROPERTY, display_name="设置属性", description="设置组件属性值", params={"component_id": "", "property_name": "", "value": None}),
    ActionDefinition(action_type=ActionType.DELAY, display_name="延时", description="延时执行（毫秒）", params={"milliseconds": 1000}),
    ActionDefinition(action_type=ActionType.CUSTOM, display_name="自定义动作", description="执行自定义的动作链"),
]