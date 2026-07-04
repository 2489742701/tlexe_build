"""信号-事件系统 - 可扩展、防内存泄漏架构。

【架构设计原则】
1. 接口隔离：使用抽象基类定义契约
2. 依赖注入：通过构造函数注入依赖
3. 工厂模式：支持动态创建不同类型的信号和事件
4. 弱引用：避免循环引用导致的内存泄漏
5. 观察者模式：信号状态变化通知监听者

【内存管理策略】
1. 使用 weakref 避免 Signal 和 Event 之间的循环引用
2. Signal 断开连接时自动清理
3. 使用上下文管理器确保资源释放
4. 父对象销毁时自动清理子对象
"""

import uuid
import json
import weakref
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Set, Type, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto

from PySide6.QtCore import QObject, Signal as QtSignal, Slot

logger = logging.getLogger(__name__)

class SignalType(Enum):
    """信号类型枚举。"""
    CLICK = auto()
    HOVER = auto()
    CHANGE = auto()
    CUSTOM = auto()

class EventType(Enum):
    """事件类型枚举。"""
    NAVIGATE = auto()
    SHOW_MESSAGE = auto()
    EXECUTE_SCRIPT = auto()
    CUSTOM = auto()

# ============================================================================
# 接口定义（抽象基类）
# ============================================================================

class IEvent(ABC):
    """事件接口。
    
    所有事件类型必须实现此接口。
    """
    
    @property
    @abstractmethod
    def id(self) -> str:
        """获取事件唯一标识。"""
        pass
    
    @property
    @abstractmethod
    def event_type(self) -> EventType:
        """获取事件类型。"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """执行事件。
        
        Args:
            context: 执行上下文
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IEvent':
        """从字典反序列化。"""
        pass

class ISignal(ABC):
    """信号接口。
    
    所有信号类型必须实现此接口。
    """
    
    @property
    @abstractmethod
    def id(self) -> str:
        """获取信号唯一标识。"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """获取信号名称。"""
        pass
    
    @property
    @abstractmethod
    def signal_type(self) -> SignalType:
        """获取信号类型。"""
        pass
    
    @abstractmethod
    def trigger(self, **kwargs) -> None:
        """触发信号。"""
        pass
    
    @abstractmethod
    def attach_event(self, event: IEvent) -> None:
        """附加事件。"""
        pass
    
    @abstractmethod
    def detach_event(self) -> None:
        """分离事件。"""
        pass
    
    @abstractmethod
    def get_event(self) -> Optional[IEvent]:
        """获取关联的事件。"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        pass

# ============================================================================
# 具体实现
# ============================================================================

@dataclass
class EventData:
    """事件数据基类。"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

class Event(IEvent):
    """事件基类实现。
    
    【内存管理】
    - 使用 dataclass 减少内存占用
    - 避免循环引用
    - 支持序列化/反序列化
    """
    
    def __init__(self, 
                 name: str = "",
                 event_type: EventType = EventType.CUSTOM,
                 action: str = "",
                 params: Optional[Dict[str, Any]] = None):
        """初始化事件。
        
        Args:
            name: 事件名称
            event_type: 事件类型
            action: 执行的动作
            params: 动作参数
        """
        self._data = EventData(name=name)
        self._event_type = event_type
        self._action = action
        self._params = params or {}
        self._enabled = True
        
        logger.debug(f"创建事件: {self.id} ({name})")
    
    @property
    def id(self) -> str:
        return self._data.id
    
    @property
    def name(self) -> str:
        return self._data.name
    
    @name.setter
    def name(self, value: str):
        self._data.name = value
    
    @property
    def event_type(self) -> EventType:
        return self._event_type
    
    @property
    def action(self) -> str:
        return self._action
    
    @action.setter
    def action(self, value: str):
        self._action = value
    
    @property
    def params(self) -> Dict[str, Any]:
        return self._params.copy()
    
    def update_params(self, params: Dict[str, Any]):
        """更新参数。"""
        self._params.update(params)
    
    def execute(self, context: Dict[str, Any]) -> Any:
        """执行事件。
        
        子类应重写此方法。
        
        Args:
            context: 执行上下文
            
        Returns:
            执行结果
        """
        if not self._enabled:
            logger.warning(f"事件 {self.id} 已禁用，跳过执行")
            return None
        
        logger.info(f"执行事件: {self.name} ({self._action})")
        # 子类实现具体逻辑
        return self._execute_impl(context)
    
    def _execute_impl(self, context: Dict[str, Any]) -> Any:
        """子类实现的具体执行逻辑。"""
        return {"action": self._action, "params": self._params}
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            "id": self.id,
            "name": self.name,
            "event_type": self._event_type.name,
            "action": self._action,
            "params": self._params,
            "enabled": self._enabled,
            "created_at": self._data.created_at,
            "metadata": self._data.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """从字典反序列化。"""
        event = cls(
            name=data.get("name", ""),
            event_type=EventType[data.get("event_type", "CUSTOM")],
            action=data.get("action", ""),
            params=data.get("params", {}),
        )
        event._data.id = data.get("id", event._data.id)
        event._enabled = data.get("enabled", True)
        event._data.created_at = data.get("created_at", event._data.created_at)
        event._data.metadata = data.get("metadata", {})
        return event
    
    def __repr__(self) -> str:
        return f"Event(id={self.id}, name={self.name}, type={self._event_type.name})"
    
    def __del__(self):
        """析构时记录日志（调试用）。"""
        logger.debug(f"销毁事件: {self.id}")

class Signal(ISignal, QObject):
    """信号实现。
    
    【内存管理】
    - 使用弱引用存储事件，避免循环引用
    - 父对象销毁时自动清理
    - 支持上下文管理器
    
    【扩展性】
    - 通过 SignalFactory 可创建不同类型的信号
    - 支持自定义触发逻辑
    """
    
    # Qt 信号
    triggered = QtSignal(str, dict)  # 信号ID, 触发参数
    event_attached = QtSignal(str, str)  # 信号ID, 事件ID
    event_detached = QtSignal(str)  # 信号ID
    
    def __init__(self, 
                 name: str,
                 signal_type: SignalType = SignalType.CUSTOM,
                 parent: Optional[QObject] = None):
        """初始化信号。
        
        Args:
            name: 信号名称
            signal_type: 信号类型
            parent: 父对象
        """
        QObject.__init__(self, parent)
        self._id = str(uuid.uuid4())
        self._name = name
        self._signal_type = signal_type
        # 使用弱引用避免循环引用
        self._event_ref: Optional[weakref.ref] = None
        self._enabled = True
        self._metadata: Dict[str, Any] = {}
        
        logger.debug(f"创建信号: {self._id} ({name})")
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value
    
    @property
    def signal_type(self) -> SignalType:
        return self._signal_type
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
    
    def attach_event(self, event: IEvent) -> None:
        """附加事件（弱引用）。
        
        Args:
            event: 要附加的事件
        """
        self._event_ref = weakref.ref(event)
        self.event_attached.emit(self._id, event.id)
        logger.debug(f"事件 {event.id} 已附加到信号 {self._id}")
    
    def detach_event(self) -> None:
        """分离事件。"""
        self._event_ref = None
        self.event_detached.emit(self._id)
        logger.debug(f"信号 {self._id} 的事件已分离")
    
    def get_event(self) -> Optional[IEvent]:
        """获取关联的事件。
        
        Returns:
            事件对象，如果不存在则返回 None
        """
        if self._event_ref is None:
            return None
        event = self._event_ref()
        if event is None:
            # 事件已被垃圾回收
            self._event_ref = None
            logger.warning(f"信号 {self._id} 关联的事件已被回收")
        return event
    
    def trigger(self, **kwargs) -> None:
        """触发信号。
        
        Args:
            **kwargs: 触发参数
        """
        if not self._enabled:
            logger.debug(f"信号 {self._id} 已禁用，跳过触发")
            return
        
        logger.info(f"触发信号: {self._name} ({self._id})")
        self.triggered.emit(self._id, kwargs)
        
        # 执行关联的事件
        event = self.get_event()
        if event:
            context = {"signal_id": self._id, "signal_name": self._name, **kwargs}
            event.execute(context)
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        event = self.get_event()
        return {
            "id": self._id,
            "name": self._name,
            "signal_type": self._signal_type.name,
            "enabled": self._enabled,
            "metadata": self._metadata,
            "event_id": event.id if event else None,
        }
    
    def __enter__(self):
        """上下文管理器入口。"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动清理。"""
        self.detach_event()
    
    def __repr__(self) -> str:
        return f"Signal(id={self._id}, name={self._name}, type={self._signal_type.name})"
    
    def __del__(self):
        """析构时记录日志。"""
        logger.debug(f"销毁信号: {self._id}")

# ============================================================================
# 工厂模式 - 支持扩展
# ============================================================================

class EventFactory:
    """事件工厂。
    
    【扩展性】
    - 注册新的事件类型
    - 动态创建事件实例
    """
    
    _registry: Dict[str, Type[IEvent]] = {}
    
    @classmethod
    def register(cls, event_type: str, event_class: Type[IEvent]):
        """注册事件类型。
        
        Args:
            event_type: 事件类型标识
            event_class: 事件类
        """
        cls._registry[event_type] = event_class
        logger.info(f"注册事件类型: {event_type}")
    
    @classmethod
    def create(cls, event_type: str, **kwargs) -> IEvent:
        """创建事件实例。
        
        Args:
            event_type: 事件类型
            **kwargs: 构造函数参数
            
        Returns:
            事件实例
            
        Raises:
            ValueError: 未知的事件类型
        """
        if event_type not in cls._registry:
            raise ValueError(f"未知的事件类型: {event_type}")
        
        event_class = cls._registry[event_type]
        return event_class(**kwargs)
    
    @classmethod
    def get_registered_types(cls) -> List[str]:
        """获取所有已注册的类型。"""
        return list(cls._registry.keys())

class SignalFactory:
    """信号工厂。
    
    【扩展性】
    - 支持自定义信号类型
    - 统一创建接口
    """
    
    _registry: Dict[str, Type[Signal]] = {}
    
    @classmethod
    def register(cls, signal_type: str, signal_class: Type[Signal]):
        """注册信号类型。
        
        Args:
            signal_type: 信号类型标识
            signal_class: 信号类
        """
        cls._registry[signal_type] = signal_class
        logger.info(f"注册信号类型: {signal_type}")
    
    @classmethod
    def create(cls, 
               name: str,
               signal_type: SignalType = SignalType.CUSTOM,
               parent: Optional[QObject] = None) -> Signal:
        """创建信号实例。
        
        Args:
            name: 信号名称
            signal_type: 信号类型
            parent: 父对象
            
        Returns:
            信号实例
        """
        type_name = signal_type.name.lower()
        signal_class = cls._registry.get(type_name, Signal)
        return signal_class(name, signal_type, parent)

# ============================================================================
# 注册表模式 - 统一管理
# ============================================================================

class SignalManager(QObject):
    """信号管理器。
    
    【职责】
    - 管理所有信号的生命周期
    - 提供信号查找和查询
    - 序列化/反序列化
    
    【内存管理】
    - 使用弱引用避免内存泄漏
    - 自动清理已销毁的信号
    """
    
    signal_added = QtSignal(str)      # 信号ID
    signal_removed = QtSignal(str)    # 信号ID
    signal_triggered = QtSignal(str, dict)  # 信号ID, 参数
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        # 使用弱引用字典，当信号被销毁时自动移除
        self._signals: Dict[str, weakref.ref] = {}
        self._signal_names: Dict[str, str] = {}  # id -> name 映射
    
    def add_signal(self, signal: Signal) -> bool:
        """添加信号。
        
        Args:
            signal: 信号实例
            
        Returns:
            是否成功添加
        """
        if signal.id in self._signals:
            logger.warning(f"信号 {signal.id} 已存在")
            return False
        
        # 使用弱引用
        self._signals[signal.id] = weakref.ref(signal)
        self._signal_names[signal.id] = signal.name
        
        # 连接信号
        signal.triggered.connect(self._on_signal_triggered)
        
        self.signal_added.emit(signal.id)
        logger.info(f"添加信号: {signal.name} ({signal.id})")
        return True
    
    def remove_signal(self, signal_id: str) -> bool:
        """移除信号。
        
        Args:
            signal_id: 信号ID
            
        Returns:
            是否成功移除
        """
        if signal_id not in self._signals:
            return False
        
        signal_ref = self._signals.pop(signal_id)
        self._signal_names.pop(signal_id, None)
        
        signal = signal_ref()
        if signal:
            signal.triggered.disconnect(self._on_signal_triggered)
        
        self.signal_removed.emit(signal_id)
        logger.info(f"移除信号: {signal_id}")
        return True
    
    def get_signal(self, signal_id: str) -> Optional[Signal]:
        """获取信号。
        
        Args:
            signal_id: 信号ID
            
        Returns:
            信号实例，如果不存在则返回 None
        """
        if signal_id not in self._signals:
            return None
        
        signal = self._signals[signal_id]()
        if signal is None:
            # 信号已被垃圾回收，清理引用
            self._cleanup_signal(signal_id)
        return signal
    
    def get_signal_by_name(self, name: str) -> Optional[Signal]:
        """根据名称获取信号。
        
        Args:
            name: 信号名称
            
        Returns:
            信号实例
        """
        for signal_id, signal_name in self._signal_names.items():
            if signal_name == name:
                return self.get_signal(signal_id)
        return None
    
    def get_all_signals(self) -> List[Signal]:
        """获取所有有效的信号。"""
        valid_signals = []
        expired_ids = []
        
        for signal_id, signal_ref in self._signals.items():
            signal = signal_ref()
            if signal:
                valid_signals.append(signal)
            else:
                expired_ids.append(signal_id)
        
        # 清理已失效的引用
        for signal_id in expired_ids:
            self._cleanup_signal(signal_id)
        
        return valid_signals
    
    def _cleanup_signal(self, signal_id: str):
        """清理已失效的信号引用。"""
        self._signals.pop(signal_id, None)
        self._signal_names.pop(signal_id, None)
        logger.debug(f"清理失效信号引用: {signal_id}")
    
    def _on_signal_triggered(self, signal_id: str, params: dict):
        """信号触发回调。"""
        self.signal_triggered.emit(signal_id, params)
    
    def create_signal(self, name: str, signal_type: SignalType = SignalType.CUSTOM) -> Signal:
        """创建并添加信号。
        
        Args:
            name: 信号名称
            signal_type: 信号类型
            
        Returns:
            新创建的信号
        """
        signal = SignalFactory.create(name, signal_type, self)
        self.add_signal(signal)
        return signal
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        signals_data = []
        for signal in self.get_all_signals():
            signals_data.append(signal.to_dict())
        
        return {
            "signals": signals_data,
            "count": len(signals_data)
        }
    
    def clear(self):
        """清空所有信号。"""
        self._signals.clear()
        self._signal_names.clear()
        logger.info("信号管理器已清空")

# ============================================================================
# 便捷函数
# ============================================================================

def create_signal_event_pair(
    signal_name: str,
    event_name: str,
    action: str,
    params: Optional[Dict[str, Any]] = None,
    parent: Optional[QObject] = None
) -> tuple[Signal, Event]:
    """创建信号-事件对。
    
    【便捷函数】快速创建关联的信号和事件。
    
    Args:
        signal_name: 信号名称
        event_name: 事件名称
        action: 事件动作
        params: 事件参数
        parent: 父对象
        
    Returns:
        (信号, 事件) 元组
    """
    signal = Signal(signal_name, SignalType.CUSTOM, parent)
    event = Event(event_name, EventType.CUSTOM, action, params or {})
    signal.attach_event(event)
    return signal, event

# 注册默认类型
EventFactory.register("base", Event)
SignalFactory.register("custom", Signal)
