"""通信系统模块。

SignalConnection/CommunicationChannel 使用 Pydantic Schema，自动序列化。
CommunicationManager 保留 QObject + Signal，提供运行时信号分发。

设计原则：
- Schema 层（Pydantic）：纯数据，负责序列化和验证
- Manager 层（QObject）：运行时逻辑，负责信号分发和动作执行
- 外部代码通过 Manager 的公开方法操作，不直接访问 _connections 等私有属性
"""

from typing import Dict, Any, List, Optional, Callable, Set

from PySide6.QtCore import QObject, Signal

from .schemas import SignalType, CommActionType, SignalConnectionSchema, CommunicationChannelSchema

class CommunicationManager(QObject):
    """通信管理器。"""

    connection_created = Signal(str)
    connection_removed = Signal(str)
    signal_emitted = Signal(str, str, object)
    action_executed = Signal(str, str, object)

    def __init__(self):
        super().__init__()
        self._connections: Dict[str, SignalConnectionSchema] = {}
        self._channels: Dict[str, CommunicationChannelSchema] = {}
        self._component_channels: Dict[str, Set[str]] = {}
        self._action_handlers: Dict[CommActionType, Callable] = {
            CommActionType.SET_TEXT: self._handle_set_text,
            CommActionType.SET_VALUE: self._handle_set_value,
            CommActionType.SHOW: self._handle_show,
            CommActionType.HIDE: self._handle_hide,
            CommActionType.ENABLE: self._handle_enable,
            CommActionType.DISABLE: self._handle_disable,
            CommActionType.SHOW_MESSAGE: self._handle_show_message,
            CommActionType.READ_VARIABLE: self._handle_read_variable,
            CommActionType.SET_VARIABLE: self._handle_set_variable,
            CommActionType.MATCH_VARIABLE: self._handle_match_variable,
            CommActionType.INCREMENT: self._handle_increment,
            CommActionType.DECREMENT: self._handle_decrement,
            CommActionType.APPEND_ARRAY: self._handle_append_array,
            CommActionType.CLEAR_ARRAY: self._handle_clear_array,
            CommActionType.EXECUTE_CODE: self._handle_execute_code,
        }
        self._components: Dict[str, Any] = {}

    def register_component(self, component_id: str, component: Any) -> None:
        self._components[component_id] = component

    def unregister_component(self, component_id: str) -> None:
        if component_id in self._components:
            del self._components[component_id]

    def get_component(self, component_id: str) -> Optional[Any]:
        return self._components.get(component_id)

    def create_connection(self, source_id: str, signal_type: SignalType,
                          target_id: str, action_type: CommActionType,
                          action_params: Optional[Dict[str, Any]] = None,
                          condition: Optional[str] = None) -> str:
        import uuid
        conn_id = str(uuid.uuid4())[:8]
        connection = SignalConnectionSchema(
            id=conn_id, source_id=source_id,
            signal_type=signal_type.value, target_id=target_id,
            action_type=action_type.value,
            action_params=action_params or {}, condition=condition,
        )
        self._connections[conn_id] = connection
        self.connection_created.emit(conn_id)
        return conn_id

    def remove_connection(self, connection_id: str) -> bool:
        if connection_id in self._connections:
            del self._connections[connection_id]
            self.connection_removed.emit(connection_id)
            return True
        return False

    def get_connections_for_source(self, source_id: str) -> List[SignalConnectionSchema]:
        return [c for c in self._connections.values() if c.source_id == source_id]

    def get_connections_for_target(self, target_id: str) -> List[SignalConnectionSchema]:
        return [c for c in self._connections.values() if c.target_id == target_id]

    def get_all_connections(self) -> List[SignalConnectionSchema]:
        return list(self._connections.values())

    def get_connection(self, connection_id: str) -> Optional[SignalConnectionSchema]:
        return self._connections.get(connection_id)

    def emit_signal(self, source_id: str, signal_type: SignalType, value: Any = None) -> None:
        self.signal_emitted.emit(source_id, signal_type.value, value)
        for conn in self._connections.values():
            if conn.source_id == source_id and conn.signal_type == signal_type.value and conn.enabled:
                self._execute_action(conn, value)

    def _execute_action(self, connection: SignalConnectionSchema, signal_value: Any) -> None:
        try:
            action_type = CommActionType(connection.action_type)
        except ValueError:
            return
        handler = self._action_handlers.get(action_type)
        if handler:
            result = handler(connection.target_id, connection.action_params, signal_value)
            self.action_executed.emit(connection.target_id, connection.action_type, result)

    def _handle_set_text(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        component = self.get_component(target_id)
        if component and hasattr(component, 'setText'):
            text = params.get('text', str(value) if value is not None else '')
            component.setText(text)
            return True
        return False

    def _handle_set_value(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
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
        component = self.get_component(target_id)
        if component and hasattr(component, 'show'):
            component.show()
            return True
        return False

    def _handle_hide(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        component = self.get_component(target_id)
        if component and hasattr(component, 'hide'):
            component.hide()
            return True
        return False

    def _handle_enable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        component = self.get_component(target_id)
        if component and hasattr(component, 'setEnabled'):
            component.setEnabled(True)
            return True
        return False

    def _handle_disable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        component = self.get_component(target_id)
        if component and hasattr(component, 'setEnabled'):
            component.setEnabled(False)
            return True
        return False

    def _handle_show_message(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        from PySide6.QtWidgets import QMessageBox
        message = params.get('message', str(value) if value is not None else '')
        title = params.get('title', '提示')
        QMessageBox.information(None, title, message)
        return True

    def _handle_read_variable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
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
        from .variable_system import get_variable_manager
        from .schemas import VariableType
        var_name = params.get('variable_name', '')
        var_type = VariableType(params.get('variable_type', '文本'))
        if not var_name:
            return False
        var_manager = get_variable_manager()
        var_manager.set_variable(var_name, value, var_type)
        return True

    def _handle_match_variable(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
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
        from .variable_system import get_variable_manager
        var_name = params.get('variable_name', '')
        amount = params.get('amount', 1)
        if not var_name:
            return False
        return get_variable_manager().increment(var_name, amount)

    def _handle_decrement(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        from .variable_system import get_variable_manager
        var_name = params.get('variable_name', '')
        amount = params.get('amount', 1)
        if not var_name:
            return False
        return get_variable_manager().decrement(var_name, amount)

    def _handle_append_array(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        from .variable_system import get_variable_manager
        var_name = params.get('variable_name', '')
        if not var_name:
            return False
        return get_variable_manager().append_to_array(var_name, value)

    def _handle_clear_array(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        from .variable_system import get_variable_manager
        var_name = params.get('variable_name', '')
        if not var_name:
            return False
        return get_variable_manager().clear_array(var_name)

    def _handle_execute_code(self, target_id: str, params: Dict[str, Any], value: Any) -> bool:
        code = params.get('code', '') or (str(value) if value is not None else '')
        if not code:
            return False
        try:
            exec(code, {"__builtins__": {}})
            return True
        except Exception:
            return False

    def create_channel(self, channel_id: str, name: str, container_id: str) -> CommunicationChannelSchema:
        channel = CommunicationChannelSchema(id=channel_id, name=name, container_id=container_id)
        self._channels[channel_id] = channel
        return channel

    def remove_channel(self, channel_id: str) -> bool:
        if channel_id in self._channels:
            channel = self._channels[channel_id]
            for member_id in channel.member_ids:
                if member_id in self._component_channels:
                    self._component_channels[member_id].discard(channel_id)
            del self._channels[channel_id]
            return True
        return False

    def join_channel(self, channel_id: str, component_id: str) -> bool:
        if channel_id not in self._channels:
            return False
        channel = self._channels[channel_id]
        channel.member_ids = list(set(channel.member_ids) | {component_id})
        if component_id not in self._component_channels:
            self._component_channels[component_id] = set()
        self._component_channels[component_id].add(channel_id)
        return True

    def leave_channel(self, channel_id: str, component_id: str) -> bool:
        if channel_id not in self._channels:
            return False
        channel = self._channels[channel_id]
        channel.member_ids = [m for m in channel.member_ids if m != component_id]
        if component_id in self._component_channels:
            self._component_channels[component_id].discard(channel_id)
        return True

    def get_component_channels(self, component_id: str) -> List[CommunicationChannelSchema]:
        if component_id not in self._component_channels:
            return []
        return [self._channels[cid] for cid in self._component_channels[component_id] if cid in self._channels]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connections": [c.model_dump() for c in self._connections.values()],
            "channels": [c.model_dump() for c in self._channels.values()],
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self._connections.clear()
        for conn_data in data.get("connections", []):
            conn = SignalConnectionSchema.model_validate(conn_data)
            self._connections[conn.id] = conn
        self._channels.clear()
        for channel_data in data.get("channels", []):
            channel = CommunicationChannelSchema.model_validate(channel_data)
            self._channels[channel.id] = channel

_communication_manager_instance: Optional[CommunicationManager] = None

def get_communication_manager() -> CommunicationManager:
    global _communication_manager_instance
    if _communication_manager_instance is None:
        _communication_manager_instance = CommunicationManager()
    return _communication_manager_instance
