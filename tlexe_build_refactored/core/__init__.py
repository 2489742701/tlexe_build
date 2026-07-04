"""核心架构模块。

提供可扩展、防内存泄漏的数据模型和架构组件。
"""

from .signal_event_system import (
    # 接口
    ISignal, IEvent,
    # 枚举
    SignalType, EventType,
    # 数据类
    EventData,
    # 实现类
    Signal, Event,
    # 工厂
    SignalFactory, EventFactory,
    # 管理器
    SignalManager,
    # 便捷函数
    create_signal_event_pair
)

__all__ = [
    # 接口
    'ISignal', 'IEvent',
    # 枚举
    'SignalType', 'EventType',
    # 数据类
    'EventData',
    # 实现类
    'Signal', 'Event',
    # 工厂
    'SignalFactory', 'EventFactory',
    # 管理器
    'SignalManager',
    # 便捷函数
    'create_signal_event_pair',
]
