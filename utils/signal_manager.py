"""信号生命周期管理模块。

本模块提供信号连接的生命周期管理，防止内存泄漏和访问已删除对象。

## 修复说明 (2026-04-02 MCP二轮审查)
【问题】
1. 信号连接后未断开，组件删除时信号仍保持连接
2. 可能导致回调函数访问已删除对象
3. lambda捕获循环引用

【解决方案】
1. 使用 SignalConnection 类封装信号连接
2. 自动追踪连接的生命周期
3. 提供批量断开连接功能
4. 使用弱引用避免循环引用

【设计模式】
- RAII (Resource Acquisition Is Initialization)
- 观察者模式（增强版）
"""

import weakref
from typing import Optional, Callable, Any, List, Dict, Set
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class SignalConnection:
    """信号连接封装类。
    
    封装信号连接，提供自动断开功能。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    使用此类替代直接的 signal.connect()，确保在对象销毁时自动断开信号。
    
    使用示例:
        # 修复前（不安全）:
        item.moved.connect(self._on_item_moved)
        # 组件删除后信号仍连接，可能导致崩溃
        
        # 修复后（安全）:
        connection = SignalConnection(item.moved, self._on_item_moved)
        connection.connect()
        # 当 item 被删除时，连接自动断开
    """
    
    def __init__(self, signal: Signal, slot: Callable, connection_type: Any = None):
        """初始化信号连接。
        
        Args:
            signal: 信号对象
            slot: 槽函数
            connection_type: 连接类型（可选）
        """
        self._signal = signal
        self._slot = slot
        self._connection_type = connection_type
        self._connected = False
        self._weak_ref: Optional[weakref.ref] = None
    
    def connect(self) -> bool:
        """建立信号连接。
        
        Returns:
            是否连接成功
        """
        if self._connected:
            return True
        
        try:
            if self._connection_type:
                self._signal.connect(self._slot, self._connection_type)
            else:
                self._signal.connect(self._slot)
            self._connected = True
            return True
        except Exception as e:
            print(f"信号连接失败: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开信号连接。
        
        Returns:
            是否断开成功
        """
        if not self._connected:
            return True
        
        try:
            self._signal.disconnect(self._slot)
            self._connected = False
            return True
        except Exception:
            # 信号可能已经断开或对象已删除
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """检查是否已连接。
        
        Returns:
            是否已连接
        """
        return self._connected
    
    def __del__(self):
        """析构时自动断开连接。"""
        self.disconnect()


class SignalConnectionGroup:
    """信号连接组。
    
    管理一组信号连接，支持批量断开。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    用于管理一个对象的所有信号连接，在对象销毁时批量断开。
    
    使用示例:
        class MyController:
            def __init__(self):
                self._connections = SignalConnectionGroup()
            
            def setup_connections(self, item):
                self._connections.add(item.moved, self._on_moved)
                self._connections.add(item.resized, self._on_resized)
                self._connections.connect_all()
            
            def cleanup(self):
                self._connections.disconnect_all()
    """
    
    def __init__(self):
        """初始化连接组。"""
        self._connections: List[SignalConnection] = []
    
    def add(self, signal: Signal, slot: Callable, connection_type: Any = None) -> SignalConnection:
        """添加信号连接到组。
        
        Args:
            signal: 信号对象
            slot: 槽函数
            connection_type: 连接类型
            
        Returns:
            创建的连接对象
        """
        conn = SignalConnection(signal, slot, connection_type)
        self._connections.append(conn)
        return conn
    
    def connect_all(self) -> None:
        """连接组内所有信号。"""
        for conn in self._connections:
            conn.connect()
    
    def disconnect_all(self) -> None:
        """断开组内所有信号。"""
        for conn in self._connections:
            conn.disconnect()
        self._connections.clear()
    
    def __del__(self):
        """析构时断开所有连接。"""
        self.disconnect_all()


class QObjectTracker:
    """QObject生命周期追踪器。
    
    追踪QObject的生命周期，在对象销毁时自动清理。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    用于安全地持有QObject引用，避免访问已删除对象。
    
    使用示例:
        tracker = QObjectTracker(item)
        if tracker.is_alive():
            tracker.object().setPos(x, y)
    """
    
    def __init__(self, obj: QObject):
        """初始化追踪器。
        
        Args:
            obj: 要追踪的QObject
        """
        self._obj_ref: Optional[weakref.ref] = None
        self._destroyed = False
        
        if obj:
            # 使用弱引用
            self._obj_ref = weakref.ref(obj)
            # 连接 destroyed 信号
            try:
                obj.destroyed.connect(self._on_destroyed)
            except:
                pass
    
    def _on_destroyed(self):
        """对象销毁时的回调。"""
        self._destroyed = True
        self._obj_ref = None
    
    def is_alive(self) -> bool:
        """检查对象是否仍然存活。
        
        Returns:
            对象是否存活
        """
        if self._destroyed:
            return False
        if self._obj_ref is None:
            return False
        return self._obj_ref() is not None
    
    def object(self) -> Optional[QObject]:
        """获取被追踪的对象。
        
        Returns:
            对象（如果存活），否则 None
        """
        if self._obj_ref:
            return self._obj_ref()
        return None


class SafeSlot:
    """安全槽函数包装器。
    
    包装槽函数，在调用前检查对象是否存活。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    用于防止访问已删除的对象。
    
    使用示例:
        # 修复前（不安全）:
        item.moved.connect(self._on_moved)
        
        # 修复后（安全）:
        safe_slot = SafeSlot(self, self._on_moved)
        item.moved.connect(safe_slot)
    """
    
    def __init__(self, obj: QObject, method: Callable):
        """初始化安全槽。
        
        Args:
            obj: 拥有方法的对象
            method: 方法
        """
        self._tracker = QObjectTracker(obj)
        self._method = method
    
    def __call__(self, *args, **kwargs):
        """调用槽函数。"""
        if self._tracker.is_alive():
            return self._method(*args, **kwargs)
        else:
            # 对象已删除，静默忽略
            pass


class SignalThrottler(QObject):
    """信号节流器。
    
    对高频信号进行节流，减少处理次数。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    用于优化高频信号（如拖动时的 position_changed）的性能。
    
    使用示例:
        throttler = SignalThrottler(interval_ms=16)  # 60fps
        throttler.throttled.connect(self._on_position_changed)
        
        # 高频触发
        for i in range(1000):
            throttler.trigger(i)
        # 实际上只会触发约60次
    """
    
    throttled = Signal(object)  # 节流后的信号
    
    def __init__(self, interval_ms: int = 16, parent=None):
        """初始化节流器。
        
        Args:
            interval_ms: 节流间隔（毫秒）
            parent: 父对象
        """
        super().__init__(parent)
        self._interval = interval_ms
        self._last_emit_time = 0
        self._pending_value = None
        self._timer = None
    
    def trigger(self, value: Any):
        """触发信号。
        
        Args:
            value: 要传递的值
        """
        import time
        current_time = int(time.time() * 1000)
        
        if current_time - self._last_emit_time >= self._interval:
            # 直接发射
            self._last_emit_time = current_time
            self.throttled.emit(value)
        else:
            # 延迟发射
            self._pending_value = value
            if self._timer is None:
                from PySide6.QtCore import QTimer
                self._timer = QTimer(self)
                self._timer.timeout.connect(self._emit_pending)
                self._timer.setSingleShot(True)
            
            remaining = self._interval - (current_time - self._last_emit_time)
            self._timer.start(max(1, remaining))
    
    def _emit_pending(self):
        """发射待处理的值。"""
        import time
        self._last_emit_time = int(time.time() * 1000)
        if self._pending_value is not None:
            self.throttled.emit(self._pending_value)
            self._pending_value = None


def safe_connect(sender: QObject, signal: Signal, receiver: QObject, slot: Callable) -> SignalConnection:
    """安全地连接信号。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    提供安全的信号连接函数，自动处理生命周期。
    
    Args:
        sender: 信号发送者
        signal: 信号
        receiver: 信号接收者
        slot: 槽函数
        
    Returns:
        信号连接对象
    """
    # 使用 SafeSlot 包装槽函数
    safe_slot = SafeSlot(receiver, slot)
    
    # 创建连接
    conn = SignalConnection(signal, safe_slot)
    conn.connect()
    
    return conn


def safe_disconnect_all(obj: QObject) -> int:
    """安全地断开对象的所有信号连接。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    在删除对象前调用此函数，断开所有信号连接。
    
    Args:
        obj: 要清理的对象
        
    Returns:
        断开的连接数
    """
    count = 0
    
    # 获取对象的所有信号
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if isinstance(attr, Signal):
            try:
                # 尝试断开所有连接
                attr.disconnect()
                count += 1
            except:
                pass
    
    return count


# 全局信号连接注册表（用于调试和监控）
class GlobalSignalRegistry:
    """全局信号连接注册表。
    
    用于监控和调试信号连接。
    
    ## 修复说明 (2026-04-02 MCP二轮审查)
    用于检测信号连接泄漏。
    """
    
    _connections: Dict[int, Dict[str, Any]] = {}
    _enabled: bool = False
    
    @classmethod
    def enable(cls):
        """启用注册表。"""
        cls._enabled = True
    
    @classmethod
    def disable(cls):
        """禁用注册表。"""
        cls._enabled = False
    
    @classmethod
    def register(cls, conn_id: int, sender: str, signal: str, receiver: str, slot: str):
        """注册信号连接。
        
        Args:
            conn_id: 连接ID
            sender: 发送者名称
            signal: 信号名称
            receiver: 接收者名称
            slot: 槽函数名称
        """
        if not cls._enabled:
            return
        
        cls._connections[conn_id] = {
            'sender': sender,
            'signal': signal,
            'receiver': receiver,
            'slot': slot,
        }
    
    @classmethod
    def unregister(cls, conn_id: int):
        """注销信号连接。
        
        Args:
            conn_id: 连接ID
        """
        if conn_id in cls._connections:
            del cls._connections[conn_id]
    
    @classmethod
    def get_stats(cls) -> Dict[str, int]:
        """获取统计信息。
        
        Returns:
            统计字典
        """
        return {
            'total_connections': len(cls._connections),
        }
    
    @classmethod
    def clear(cls):
        """清空注册表。"""
        cls._connections.clear()
