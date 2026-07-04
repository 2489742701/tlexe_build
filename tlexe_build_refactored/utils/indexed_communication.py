"""索引优化的通信管理模块。

本模块提供性能优化的通信管理，使用索引避免遍历所有连接。

【设计模式】
- 索引模式（Index Pattern）
- 空间换时间
"""

from typing import Dict, List, Tuple, Any, Optional, Callable, Set
from collections import defaultdict
from PySide6.QtCore import QObject, Signal
import weakref

class IndexedConnection:
    """索引优化的连接类。
    
    """
    
    def __init__(self, conn_id: str, source_id: str, signal_type: str,
                 target_id: str, action_type: str, action_params: Optional[Dict] = None):
        self.id = conn_id
        self.source_id = source_id
        self.signal_type = signal_type
        self.target_id = target_id
        self.action_type = action_type
        self.action_params = action_params or {}
        self.enabled = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "signal_type": self.signal_type,
            "target_id": self.target_id,
            "action_type": self.action_type,
            "action_params": self.action_params,
            "enabled": self.enabled,
        }

class IndexedCommunicationManager(QObject):
    """索引优化的通信管理器。
    
    Attributes:
        signal_emitted: 信号发射时触发 (source_id, signal_type, value)
        action_executed: 动作执行时触发 (target_id, action_type, result)
        error_occurred: 错误发生时触发 (conn_id, error)
    """
    
    signal_emitted = Signal(str, str, object)
    action_executed = Signal(str, str, object)
    error_occurred = Signal(str, object)
    
    def __init__(self, variable_manager=None):
        """初始化通信管理器。
        
        Args:
            variable_manager: 变量管理器（依赖注入）
        """
        super().__init__()
        
        # 存储所有连接
        self._connections: Dict[str, IndexedConnection] = {}
        
        # 信号索引: (source_id, signal_type) -> set(conn_id)
        # ## 修复说明 (2026-04-02 MCP三轮审查)
        # 核心优化：直接定位匹配连接，避免遍历
        self._signal_index: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        
        # 目标索引: target_id -> set(conn_id)
        # 用于快速查找影响某个目标的所有连接
        self._target_index: Dict[str, Set[str]] = defaultdict(set)
        
        # 组件注册表（弱引用，避免内存泄漏）
        # ## 修复说明 (2026-04-02 MCP三轮审查)
        # 使用弱引用，组件删除后自动清理
        self._components: Dict[str, weakref.ref] = {}
        
        # 变量管理器（依赖注入，避免循环导入）
        self._variable_manager = variable_manager
        
        # 动作处理器注册表
        self._action_handlers: Dict[str, Callable] = {}
        self._register_builtin_handlers()
    
    def _register_builtin_handlers(self):
        """注册内置动作处理器。"""
        # ## 修复说明 (2026-04-02 MCP三轮审查)
        # 动态注册，支持扩展
        self._action_handlers.update({
            'SET_TEXT': self._handle_set_text,
            'SET_VALUE': self._handle_set_value,
            'SHOW': self._handle_show,
            'HIDE': self._handle_hide,
            'ENABLE': self._handle_enable,
            'DISABLE': self._handle_disable,
            'READ_VARIABLE': self._handle_read_variable,
            'SET_VARIABLE': self._handle_set_variable,
            'MATCH_VARIABLE': self._handle_match_variable,
            'INCREMENT': self._handle_increment,
            'DECREMENT': self._handle_decrement,
            'APPEND_ARRAY': self._handle_append_array,
            'CLEAR_ARRAY': self._handle_clear_array,
        })
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """注册动作处理器。
        
        Args:
            action_type: 动作类型标识
            handler: 处理函数
        """
        self._action_handlers[action_type] = handler
    
    def add_connection(self, source_id: str, signal_type: str,
                       target_id: str, action_type: str,
                       action_params: Optional[Dict] = None) -> str:
        """添加信号连接。
        
        Args:
            source_id: 源组件ID
            signal_type: 信号类型
            target_id: 目标组件ID
            action_type: 动作类型
            action_params: 动作参数
            
        Returns:
            连接ID
        """
        import uuid
        conn_id = str(uuid.uuid4())[:8]
        
        conn = IndexedConnection(
            conn_id=conn_id,
            source_id=source_id,
            signal_type=signal_type,
            target_id=target_id,
            action_type=action_type,
            action_params=action_params
        )
        
        self._connections[conn_id] = conn
        
        # 更新索引
        signal_key = (source_id, signal_type)
        self._signal_index[signal_key].add(conn_id)
        self._target_index[target_id].add(conn_id)
        
        return conn_id
    
    def remove_connection(self, conn_id: str) -> bool:
        """移除信号连接。
        
        Args:
            conn_id: 连接ID
            
        Returns:
            是否移除成功
        """
        if conn_id not in self._connections:
            return False
        
        conn = self._connections.pop(conn_id)
        
        # 更新索引
        signal_key = (conn.source_id, conn.signal_type)
        self._signal_index[signal_key].discard(conn_id)
        if not self._signal_index[signal_key]:
            del self._signal_index[signal_key]
        
        self._target_index[conn.target_id].discard(conn_id)
        if not self._target_index[conn.target_id]:
            del self._target_index[conn.target_id]
        
        return True
    
    def emit_signal(self, source_id: str, signal_type: str, value: Any = None):
        """发射信号。
        
        Args:
            source_id: 源组件ID
            signal_type: 信号类型
            value: 信号值
        """
        self.signal_emitted.emit(source_id, signal_type, value)
        
        # 使用索引快速查找匹配连接
        signal_key = (source_id, signal_type)
        conn_ids = self._signal_index.get(signal_key, set())
        
        for conn_id in list(conn_ids):  # 转换为列表避免遍历时修改
            conn = self._connections.get(conn_id)
            if conn and conn.enabled:
                self._execute_action(conn, value)
    
    def _execute_action(self, conn: IndexedConnection, value: Any):
        """执行动作。
        
        Args:
            conn: 连接对象
            value: 信号值
        """
        try:
            handler = self._action_handlers.get(conn.action_type)
            if handler:
                result = handler(conn.target_id, conn.action_params, value)
                self.action_executed.emit(conn.target_id, conn.action_type, result)
            else:
                self.error_occurred.emit(conn.id, f"Unknown action type: {conn.action_type}")
        except Exception as e:
            self.error_occurred.emit(conn.id, e)
    
    def register_component(self, component_id: str, component: Any):
        """注册组件。
        
        Args:
            component_id: 组件ID
            component: 组件对象
        """
        self._components[component_id] = weakref.ref(component)
    
    def unregister_component(self, component_id: str):
        """注销组件。
        
        Args:
            component_id: 组件ID
        """
        # 移除组件
        if component_id in self._components:
            del self._components[component_id]
        
        # 清理相关连接
        conn_ids_to_remove = []
        for conn_id, conn in self._connections.items():
            if conn.source_id == component_id or conn.target_id == component_id:
                conn_ids_to_remove.append(conn_id)
        
        for conn_id in conn_ids_to_remove:
            self.remove_connection(conn_id)
    
    def get_component(self, component_id: str) -> Any:
        """获取组件。
        
        Args:
            component_id: 组件ID
            
        Returns:
            组件对象（如果存活），否则 None
        """
        ref = self._components.get(component_id)
        if ref:
            obj = ref()
            if obj is None:
                # 组件已删除，清理引用
                del self._components[component_id]
            return obj
        return None
    
    def get_connections_for_signal(self, source_id: str, signal_type: str) -> List[IndexedConnection]:
        """获取指定信号的所有连接。
        
        Args:
            source_id: 源组件ID
            signal_type: 信号类型
            
        Returns:
            连接列表
        """
        signal_key = (source_id, signal_type)
        conn_ids = self._signal_index.get(signal_key, set())
        return [self._connections[cid] for cid in conn_ids if cid in self._connections]
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息。
        
        Returns:
            统计字典
        """
        return {
            'total_connections': len(self._connections),
            'signal_index_entries': len(self._signal_index),
            'target_index_entries': len(self._target_index),
            'registered_components': len(self._components),
        }
    
    # 动作处理器实现
    def _handle_set_text(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理设置文本动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'setText'):
            text = params.get('text', str(value) if value is not None else '')
            component.setText(text)
            return True
        return False
    
    def _handle_set_value(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理设置值动作。"""
        component = self.get_component(target_id)
        if not component:
            return False
        
        if hasattr(component, 'setValue'):
            component.setValue(value if value is not None else params.get('value', 0))
            return True
        elif hasattr(component, 'setChecked'):
            component.setChecked(bool(value if value is not None else params.get('value', False)))
            return True
        return False
    
    def _handle_show(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理显示动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'show'):
            component.show()
            return True
        return False
    
    def _handle_hide(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理隐藏动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'hide'):
            component.hide()
            return True
        return False
    
    def _handle_enable(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理启用动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'setEnabled'):
            component.setEnabled(True)
            return True
        return False
    
    def _handle_disable(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理禁用动作。"""
        component = self.get_component(target_id)
        if component and hasattr(component, 'setEnabled'):
            component.setEnabled(False)
            return True
        return False
    
    def _handle_read_variable(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理读取变量动作。"""
        if not self._variable_manager:
            return False
        
        var_name = params.get('variable_name', '')
        if not var_name:
            return False
        
        var_value = self._variable_manager.get_variable(var_name)
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
    
    def _handle_set_variable(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理设置变量动作。"""
        if not self._variable_manager:
            return False
        
        var_name = params.get('variable_name', '')
        if not var_name:
            return False
        
        self._variable_manager.set_variable(var_name, value)
        return True
    
    def _handle_match_variable(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理配对变量动作。"""
        if not self._variable_manager:
            return False
        
        var_name = params.get('variable_name', '')
        if not var_name:
            return False
        
        return self._variable_manager.match_variable(var_name, value)
    
    def _handle_increment(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理增加数值动作。"""
        if not self._variable_manager:
            return False
        
        var_name = params.get('variable_name', '')
        amount = params.get('amount', 1)
        return self._variable_manager.increment(var_name, amount)
    
    def _handle_decrement(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理减少数值动作。"""
        if not self._variable_manager:
            return False
        
        var_name = params.get('variable_name', '')
        amount = params.get('amount', 1)
        return self._variable_manager.decrement(var_name, amount)
    
    def _handle_append_array(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理追加数组动作。"""
        if not self._variable_manager:
            return False
        
        var_name = params.get('variable_name', '')
        return self._variable_manager.append_to_array(var_name, value)
    
    def _handle_clear_array(self, target_id: str, params: Dict, value: Any) -> bool:
        """处理清空数组动作。"""
        if not self._variable_manager:
            return False
        
        var_name = params.get('variable_name', '')
        return self._variable_manager.clear_array(var_name)
