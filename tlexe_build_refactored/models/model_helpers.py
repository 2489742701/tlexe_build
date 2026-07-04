"""模型辅助工具模块。

本模块提供用于简化模型类开发的辅助工具和描述符。

【设计模式】描述符模式（Descriptor Pattern）
"""

from typing import Optional, Callable, Any, TypeVar, Generic

T = TypeVar('T')

class ObservableProperty(Generic[T]):
    """可观察属性描述符。
    
    自动处理属性变更通知，替代手动在 setter 中 emit 信号。
    
        class MyModel(ComponentModel):
            x = ObservableProperty[int]('x', default=0)
            y = ObservableProperty[int]('y', default=0)
            
        model = MyModel()
        model.x = 100  # 自动触发 data_changed 信号
    
    Attributes:
        name: 属性名称
        default: 默认值
        signal_name: 触发信号名称（可选）
    """
    
    def __init__(
        self,
        name: str,
        default: Optional[T] = None,
        signal_name: Optional[str] = None,
        validator: Optional[Callable[[T], bool]] = None
    ):
        """初始化可观察属性。
        
        Args:
            name: 属性名称
            default: 默认值
            signal_name: 触发信号名称，None 表示使用 data_changed
            validator: 值验证函数
        """
        self.name = name
        self.default = default
        self.signal_name = signal_name
        self.validator = validator
        self.private_name = f"_{name}"
    
    def __get__(self, instance, owner) -> T:
        """获取属性值。"""
        if instance is None:
            return self
        return getattr(instance, self.private_name, self.default)
    
    def __set__(self, instance, value: T):
        """设置属性值，自动触发信号。"""
        # 验证值
        if self.validator and not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}: {value}")
        
        # 获取旧值
        old_value = getattr(instance, self.private_name, self.default)
        
        # 如果值未改变，不触发信号
        if old_value == value:
            return
        
        # 设置新值
        setattr(instance, self.private_name, value)
        
        # 触发信号
        if hasattr(instance, 'data_changed'):
            if self.signal_name:
                # 触发特定信号
                signal = getattr(instance, self.signal_name, None)
                if signal:
                    signal.emit()
            else:
                # 触发通用 data_changed 信号
                instance.data_changed.emit()

class PositionProperty(ObservableProperty[int]):
    """位置属性描述符。
    
    专门用于 x, y 坐标属性，同时触发 position_changed 信号。
    
    """
    
    def __set__(self, instance, value: int):
        """设置位置值，触发位置和通用信号。"""
        old_value = getattr(instance, self.private_name, self.default)
        
        if old_value == value:
            return
        
        setattr(instance, self.private_name, value)
        
        # 触发 position_changed 信号
        if hasattr(instance, 'position_changed'):
            x = getattr(instance, '_x', 0)
            y = getattr(instance, '_y', 0)
            instance.position_changed.emit(x, y)
        
        # 触发 data_changed 信号
        if hasattr(instance, 'data_changed'):
            instance.data_changed.emit()

class SizeProperty(ObservableProperty[int]):
    """大小属性描述符。
    
    专门用于 width, height 属性，同时触发 size_changed 信号。
    
    """
    
    def __set__(self, instance, value: int):
        """设置大小值，触发大小和通用信号。"""
        old_value = getattr(instance, self.private_name, self.default)
        
        if old_value == value:
            return
        
        setattr(instance, self.private_name, value)
        
        # 触发 size_changed 信号
        if hasattr(instance, 'size_changed'):
            width = getattr(instance, '_width', 0)
            height = getattr(instance, '_height', 0)
            instance.size_changed.emit(width, height)
        
        # 触发 data_changed 信号
        if hasattr(instance, 'data_changed'):
            instance.data_changed.emit()

def validated_property(
    name: str,
    default: Any = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    choices: Optional[list] = None
):
    """创建带验证的可观察属性。
    
    Args:
        name: 属性名称
        default: 默认值
        min_value: 最小值（数值属性）
        max_value: 最大值（数值属性）
        choices: 可选值列表
        
    Returns:
        ObservableProperty 实例
        
    使用示例:
        class MyModel(ComponentModel):
            value = validated_property('value', default=0, min_value=0, max_value=100)
            status = validated_property('status', default='pending', choices=['pending', 'done'])
    """
    def validator(value):
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        if choices is not None and value not in choices:
            return False
        return True
    
    return ObservableProperty(name, default=default, validator=validator)

class SignalBlocker:
    """信号阻塞上下文管理器。
    
    临时阻塞模型信号，用于批量更新。
    
    """
    
    def __init__(self, model, emit_on_exit: bool = True):
        """初始化信号阻塞器。
        
        Args:
            model: 模型实例
            emit_on_exit: 退出时是否触发信号
        """
        self.model = model
        self.emit_on_exit = emit_on_exit
        self._was_blocked = False
        self._changed = False
    
    def __enter__(self):
        """进入上下文，阻塞信号。"""
        if hasattr(self.model, 'blockSignals'):
            self._was_blocked = self.model.signalsBlocked()
            self.model.blockSignals(True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，恢复信号。"""
        if hasattr(self.model, 'blockSignals'):
            self.model.blockSignals(self._was_blocked)
        
        if self.emit_on_exit and not self._was_blocked:
            if hasattr(self.model, 'data_changed'):
                self.model.data_changed.emit()
        
        return False
    
    def mark_changed(self):
        """标记有变更。"""
        self._changed = True
