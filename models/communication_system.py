"""通信系统模块。

本模块实现组件间的通信机制，让用户可以：
1. 配置组件间的信号连接
2. 实现输入框读取变量值
3. 实现配对验证后触发事件
4. 实现容器管理子组件通信

设计原则：
- 可视化配置：通过界面连接组件
- 简单易懂：用"发送"和"接收"的概念
- 树状结构：容器作为通信节点
- 自动绑定：子组件自动继承容器的通信通道

使用示例：
    # 创建通信管理器
    comm_manager = CommunicationManager()
    
    # 创建信号连接
    conn = comm_manager.create_connection(
        source_id="input001",
        signal_name="text_changed",
        target_id="label001",
        slot_name="set_text"
    )
    
    # 发送信号
    comm_manager.emit_signal("input001", "text_changed", "新文本")
"""

from typing import Dict, Any, List, Optional, Callable, Set
from enum import Enum
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal


class SignalType(Enum):
    """信号类型枚举。
    
    定义组件可以发送和接收的信号类型。
    
    类型说明：
    - TEXT_CHANGED: 文本改变（输入框、标签）
    - VALUE_CHANGED: 值改变（复选框、下拉框、进度条）
    - CLICKED: 点击（按钮）
    - MATCH_SUCCESS: 配对成功
    - MATCH_FAILED: 配对失败
    - STATE_CHANGED: 状态改变（可见性、可用性）
    - VARIABLE_READ: 读取变量
    - VARIABLE_SET: 设置变量
    """
    TEXT_CHANGED = "文本改变"
    VALUE_CHANGED = "值改变"
    CLICKED = "点击"
    MATCH_SUCCESS = "配对成功"
    MATCH_FAILED = "配对失败"
    STATE_CHANGED = "状态改变"
    VARIABLE_READ = "读取变量"
    VARIABLE_SET = "设置变量"
    CUSTOM = "自定义"


class ActionType(Enum):
    """动作类型枚举。
    
    定义信号触发后可以执行的动作。
    """
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


@dataclass
class SignalConnection:
    """信号连接配置。
    
    定义一个信号从源组件到目标组件的连接。
    
    Attributes:
        id: 连接唯一标识
        source_id: 源组件ID
        signal_type: 信号类型
        target_id: 目标组件ID
        action_type: 动作类型
        action_params: 动作参数
        condition: 触发条件（可选）
        enabled: 是否启用
    """
    id: str
    source_id: str
    signal_type: SignalType
    target_id: str
    action_type: ActionType
    action_params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "signal_type": self.signal_type.value,
            "target_id": self.target_id,
            "action_type": self.action_type.value,
            "action_params": self.action_params,
            "condition": self.condition,
            "enabled": self.enabled,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SignalConnection':
        return cls(
            id=data.get("id", ""),
            source_id=data.get("source_id", ""),
            signal_type=SignalType(data.get("signal_type", "自定义")),
            target_id=data.get("target_id", ""),
            action_type=ActionType(data.get("action_type", "设置文本")),
            action_params=data.get("action_params", {}),
            condition=data.get("condition"),
            enabled=data.get("enabled", True),
        )


@dataclass
class CommunicationChannel:
    """通信通道。
    
    容器组件可以创建通信通道，子组件可以加入通道进行通信。
    
    Attributes:
        id: 通道ID
        name: 通道名称
        container_id: 所属容器ID
        member_ids: 成员组件ID列表
        connections: 通道内的信号连接
    """
    id: str
    name: str
    container_id: str
    member_ids: Set[str] = field(default_factory=set)
    connections: List[SignalConnection] = field(default_factory=list)
    
    def add_member(self, component_id: str):
        """添加成员。"""
        self.member_ids.add(component_id)
    
    def remove_member(self, component_id: str):
        """移除成员。"""
        self.member_ids.discard(component_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "container_id": self.container_id,
            "member_ids": list(self.member_ids),
            "connections": [c.to_dict() for c in self.connections],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommunicationChannel':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            container_id=data.get("container_id", ""),
            member_ids=set(data.get("member_ids", [])),
            connections=[SignalConnection.from_dict(c) for c in data.get("connections", [])],
        )


class CommunicationManager(QObject):
    """通信管理器。
    
    管理组件间的信号连接和通信通道。
    
    功能说明：
    1. 信号连接：创建组件间的信号-动作连接
    2. 通信通道：容器管理子组件的通信
    3. 信号发射：触发信号并执行对应动作
    4. 配对验证：结合变量系统进行验证
    
    Signals:
        connection_created: 连接创建时发射 (connection_id)
        connection_removed: 连接删除时发射 (connection_id)
        signal_emitted: 信号发射时发射 (source_id, signal_type, value)
        action_executed: 动作执行时发射 (target_id, action_type, result)
    
    使用示例：
        manager = CommunicationManager()
        
        # 创建连接：输入框文本改变时，更新标签
        manager.create_connection(
            source_id="input001",
            signal_type=SignalType.TEXT_CHANGED,
            target_id="label001",
            action_type=ActionType.SET_TEXT,
        )
        
        # 发射信号
        manager.emit_signal("input001", SignalType.TEXT_CHANGED, "新文本")
    """
    
    connection_created = Signal(str)
    connection_removed = Signal(str)
    signal_emitted = Signal(str, str, object)
    action_executed = Signal(str, str, object)
    
    def __init__(self):
        super().__init__()
        self._connections: Dict[str, SignalConnection] = {}
        self._channels: Dict[str, CommunicationChannel] = {}
        self._component_channels: Dict[str, Set[str]] = {}
        
        self._action_handlers: Dict[ActionType, Callable] = {
            ActionType.SET_TEXT: self._handle_set_text,
            ActionType.SET_VALUE: self._handle_set_value,
            ActionType.SHOW: self._handle_show,
            ActionType.HIDE: self._handle_hide,
            ActionType.ENABLE: self._handle_enable,
            ActionType.DISABLE: self._handle_disable,
            ActionType.SHOW_MESSAGE: self._handle_show_message,
            ActionType.READ_VARIABLE: self._handle_read_variable,
            ActionType.SET_VARIABLE: self._handle_set_variable,
            ActionType.MATCH_VARIABLE: self._handle_match_variable,
            ActionType.INCREMENT: self._handle_increment,
            ActionType.DECREMENT: self._handle_decrement,
            ActionType.APPEND_ARRAY: self._handle_append_array,
            ActionType.CLEAR_ARRAY: self._handle_clear_array,
        }
        
        self._components: Dict[str, Any] = {}
    
    def register_component(self, component_id: str, component: Any):
        """注册组件。
        
        组件需要注册后才能接收信号动作。
        
        Args:
            component_id: 组件ID
            component: 组件对象
        """
        self._components[component_id] = component
    
    def unregister_component(self, component_id: str):
        """注销组件。"""
        if component_id in self._components:
            del self._components[component_id]
    
    def get_component(self, component_id: str) -> Optional[Any]:
        """获取注册的组件。"""
        return self._components.get(component_id)
    
    def create_connection(self, source_id: str, signal_type: SignalType,
                          target_id: str, action_type: ActionType,
                          action_params: Optional[Dict[str, Any]] = None,
                          condition: Optional[str] = None) -> str:
        """创建信号连接。
        
        Args:
            source_id: 源组件ID
            signal_type: 信号类型
            target_id: 目标组件ID
            action_type: 动作类型
            action_params: 动作参数
            condition: 触发条件
        
        Returns:
            连接ID
        
        使用示例：
            conn_id = manager.create_connection(
                source_id="input001",
                signal_type=SignalType.TEXT_CHANGED,
                target_id="label001",
                action_type=ActionType.SET_TEXT,
            )
        """
        import uuid
        conn_id = str(uuid.uuid4())[:8]
        
        connection = SignalConnection(
            id=conn_id,
            source_id=source_id,
            signal_type=signal_type,
            target_id=target_id,
            action_type=action_type,
            action_params=action_params or {},
            condition=condition,
        )
        
        self._connections[conn_id] = connection
        self.connection_created.emit(conn_id)
        
        return conn_id
    
    def remove_connection(self, connection_id: str) -> bool:
        """删除信号连接。"""
        if connection_id in self._connections:
            del self._connections[connection_id]
            self.connection_removed.emit(connection_id)
            return True
        return False
    
    def get_connections_for_source(self, source_id: str) -> List[SignalConnection]:
        """获取源组件的所有连接。"""
        return [c for c in self._connections.values() if c.source_id == source_id]
    
    def get_connections_for_target(self, target_id: str) -> List[SignalConnection]:
        """获取目标组件的所有连接。"""
        return [c for c in self._connections.values() if c.target_id == target_id]
    
    def emit_signal(self, source_id: str, signal_type: SignalType, value: Any = None):
        """发射信号。
        
        触发源组件的所有匹配连接，执行对应动作。
        
        Args:
            source_id: 源组件ID
            signal_type: 信号类型
            value: 信号携带的值
        
        使用示例：
            manager.emit_signal("input001", SignalType.TEXT_CHANGED, "新文本")
        """
        self.signal_emitted.emit(source_id, signal_type.value, value)
        
        for conn in self._connections.values():
            if conn.source_id == source_id and conn.signal_type == signal_type and conn.enabled:
                self._execute_action(conn, value)
    
    def _execute_action(self, connection: SignalConnection, signal_value: Any):
        """执行动作。"""
        handler = self._action_handlers.get(connection.action_type)
        if handler:
            result = handler(connection.target_id, connection.action_params, signal_value)
            self.action_executed.emit(connection.target_id, connection.action_type.value, result)
    
    def _handle_set_text(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理设置文本动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'setText'):
            text = params.get('text', str(value) if value is not None else '')
            component.setText(text)
            return True
        return False
    
    def _handle_set_value(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理设置值动作。"""
        component = self.get_component(target_id)
        if component:
            if hasattr(component, 'setValue'):
                component.setValue(value if value is not None else params.get('value', 0))
                return True
            elif hasattr(component, 'setChecked'):
                component.setChecked(bool(value if value is not None else params.get('value', False)))
                return True
            elif hasattr(component, 'setCurrentIndex'):
                component.setCurrentIndex(value if value is not None else params.get('value', 0))
                return True
        return False
    
    def _handle_show(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理显示动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'show'):
            component.show()
            return True
        return False
    
    def _handle_hide(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理隐藏动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'hide'):
            component.hide()
            return True
        return False
    
    def _handle_enable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理启用动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'setEnabled'):
            component.setEnabled(True)
            return True
        return False
    
    def _handle_disable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理禁用动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'setEnabled'):
            component.setEnabled(False)
            return True
        return False
    
    def _handle_show_message(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理显示消息动作。"""
        from PySide6.QtWidgets import QMessageBox
        message = params.get('message', str(value) if value is not None else '')
        title = params.get('title', '提示')
        QMessageBox.information(None, title, message)
        return True
    
    def _handle_read_variable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理读取变量动作。
        
        从变量系统读取值，设置到目标组件。
        """
        from .variable_system import get_variable_manager
        
        var_name = params.get('variable_name', '')
        if not var_name:
            return False
        
        var_manager = get_variable_manager()
        var_value = var_manager.get_variable(var_name)
        
        if var_value is not None:
            component = self.get_component(target_id)
            if component:
                if hasattr(component, 'setText'):
                    component.setText(str(var_value))
                    return True
                elif hasattr(component, 'setValue'):
                    component.setValue(var_value)
                    return True
        
        return False
    
    def _handle_set_variable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理设置变量动作。
        
        将值保存到变量系统。
        """
        from .variable_system import get_variable_manager, VariableType
        
        var_name = params.get('variable_name', '')
        var_type = VariableType(params.get('variable_type', '文本'))
        
        if not var_name:
            return False
        
        var_manager = get_variable_manager()
        var_manager.set_variable(var_name, value, var_type)
        
        return True
    
    def _handle_match_variable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理配对变量动作。
        
        验证输入值是否与变量匹配，匹配成功触发成功事件。
        """
        from .variable_system import get_variable_manager
        
        var_name = params.get('variable_name', '')
        if not var_name:
            return False
        
        var_manager = get_variable_manager()
        is_match = var_manager.match_variable(var_name, value)
        
        if is_match:
            success_action = params.get('on_success')
            if success_action:
                self.emit_signal(target_id, SignalType.MATCH_SUCCESS, value)
        else:
            fail_action = params.get('on_fail')
            if fail_action:
                self.emit_signal(target_id, SignalType.MATCH_FAILED, value)
        
        return is_match
    
    def _handle_increment(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理增加数值动作。"""
        from .variable_system import get_variable_manager
        
        var_name = params.get('variable_name', '')
        amount = params.get('amount', 1)
        
        if not var_name:
            return False
        
        var_manager = get_variable_manager()
        return var_manager.increment(var_name, amount)
    
    def _handle_decrement(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理减少数值动作。"""
        from .variable_system import get_variable_manager
        
        var_name = params.get('variable_name', '')
        amount = params.get('amount', 1)
        
        if not var_name:
            return False
        
        var_manager = get_variable_manager()
        return var_manager.decrement(var_name, amount)
    
    def _handle_append_array(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理追加数组动作。"""
        from .variable_system import get_variable_manager
        
        var_name = params.get('variable_name', '')
        
        if not var_name:
            return False
        
        var_manager = get_variable_manager()
        return var_manager.append_to_array(var_name, value)
    
    def _handle_clear_array(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        """处理清空数组动作。"""
        from .variable_system import get_variable_manager
        
        var_name = params.get('variable_name', '')
        
        if not var_name:
            return False
        
        var_manager = get_variable_manager()
        return var_manager.clear_array(var_name)
    
    def create_channel(self, channel_id: str, name: str, container_id: str) -> CommunicationChannel:
        """创建通信通道。
        
        容器可以创建通道，子组件加入后可以相互通信。
        """
        channel = CommunicationChannel(
            id=channel_id,
            name=name,
            container_id=container_id,
        )
        self._channels[channel_id] = channel
        return channel
    
    def remove_channel(self, channel_id: str) -> bool:
        """删除通信通道。"""
        if channel_id in self._channels:
            channel = self._channels[channel_id]
            for member_id in channel.member_ids:
                if member_id in self._component_channels:
                    self._component_channels[member_id].discard(channel_id)
            del self._channels[channel_id]
            return True
        return False
    
    def join_channel(self, channel_id: str, component_id: str) -> bool:
        """组件加入通道。"""
        if channel_id not in self._channels:
            return False
        
        self._channels[channel_id].add_member(component_id)
        
        if component_id not in self._component_channels:
            self._component_channels[component_id] = set()
        self._component_channels[component_id].add(channel_id)
        
        return True
    
    def leave_channel(self, channel_id: str, component_id: str) -> bool:
        """组件离开通道。"""
        if channel_id not in self._channels:
            return False
        
        self._channels[channel_id].remove_member(component_id)
        
        if component_id in self._component_channels:
            self._component_channels[component_id].discard(channel_id)
        
        return True
    
    def get_component_channels(self, component_id: str) -> List[CommunicationChannel]:
        """获取组件所属的所有通道。"""
        if component_id not in self._component_channels:
            return []
        
        return [self._channels[cid] for cid in self._component_channels[component_id] if cid in self._channels]
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典。"""
        return {
            "connections": [c.to_dict() for c in self._connections.values()],
            "channels": [c.to_dict() for c in self._channels.values()],
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载。"""
        self._connections.clear()
        for conn_data in data.get("connections", []):
            conn = SignalConnection.from_dict(conn_data)
            self._connections[conn.id] = conn
        
        self._channels.clear()
        for channel_data in data.get("channels", []):
            channel = CommunicationChannel.from_dict(channel_data)
            self._channels[channel.id] = channel


_communication_manager_instance: Optional[CommunicationManager] = None


def get_communication_manager() -> CommunicationManager:
    """获取全局通信管理器实例。"""
    global _communication_manager_instance
    if _communication_manager_instance is None:
        _communication_manager_instance = CommunicationManager()
    return _communication_manager_instance
