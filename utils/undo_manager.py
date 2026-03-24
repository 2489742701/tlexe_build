"""撤销/重做管理器模块。

本模块提供撤销和重做功能，支持多步操作管理。
采用基于栈的数据结构来存储操作历史。
"""

from typing import List, Dict, Any, Optional, Callable
from PySide6.QtCore import QObject, Signal


class UndoManager(QObject):
    """撤销/重做管理器。
    
    管理项目的撤销和重做操作，支持多步撤销。
    采用双栈结构：撤销栈和重做栈。
    
    Attributes:
        _undo_stack: 撤销操作栈，存储可撤销的操作
        _redo_stack: 重做操作栈，存储可重做的操作
        _max_steps: 最大撤销步数限制
    
    Signals:
        can_undo_changed: 撤销状态改变时发射 (can_undo)
        can_redo_changed: 重做状态改变时发射 (can_redo)
    """
    
    can_undo_changed = Signal(bool)
    can_redo_changed = Signal(bool)
    
    def __init__(self, parent=None):
        """初始化撤销管理器。
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        
        from utils.settings import app_settings
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._max_steps: int = app_settings.undo_max_steps
        
        app_settings.add_change_callback(self._on_settings_changed)
    
    def push(self, action_type: str, description: str, 
             undo_data: Dict[str, Any], redo_data: Dict[str, Any],
             undo_callback: Callable, redo_callback: Callable):
        """推送一个操作到撤销栈。
        
        当执行新操作时调用此方法，将操作信息推入撤销栈。
        同时清空重做栈，因为新操作会覆盖重做历史。
        
        Args:
            action_type: 操作类型（如'move', 'add', 'delete'等）
            description: 操作描述（显示给用户的文本）
            undo_data: 撤销操作所需的数据
            redo_data: 重做操作所需的数据
            undo_callback: 撤销回调函数，接收undo_data参数
            redo_callback: 重做回调函数，接收redo_data参数
        """
        action = {
            'type': action_type,
            'description': description,
            'undo_data': undo_data,
            'redo_data': redo_data,
            'undo_callback': undo_callback,
            'redo_callback': redo_callback
        }
        
        self._undo_stack.append(action)
        
        if len(self._undo_stack) > self._max_steps:
            self._undo_stack.pop(0)
        
        self._redo_stack.clear()
        
        self._emit_state_changed()
    
    def can_undo(self) -> bool:
        """是否可以撤销。
        
        Returns:
            是否可以撤销
        """
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """是否可以重做。
        
        Returns:
            是否可以重做
        """
        return len(self._redo_stack) > 0
    
    def undo(self) -> bool:
        """执行撤销操作。
        
        从撤销栈弹出最新操作，执行撤销回调函数，
        然后将该操作推入重做栈以便后续重做。
        
        Returns:
            是否成功撤销
        """
        if not self.can_undo():
            print("撤销调试: 无可撤销操作")
            return False
        
        action = self._undo_stack.pop()
        
        try:
            print(f"撤销调试: 执行撤销操作 - {action.get('description', '未知操作')}")
            print(f"撤销调试: 撤销数据 - {action.get('undo_data', {})}")
            
            action['undo_callback'](action['undo_data'])
            
            self._redo_stack.append(action)
            
            self._emit_state_changed()
            
            print(f"撤销调试: 撤销成功，重做栈大小: {len(self._redo_stack)}")
            return True
        except Exception as e:
            print(f"撤销失败: {e}")
            self._undo_stack.append(action)
            return False
    
    def redo(self) -> bool:
        """执行重做操作。
        
        Returns:
            是否成功重做
        """
        if not self.can_redo():
            return False
        
        action = self._redo_stack.pop()
        
        try:
            action['redo_callback'](action['redo_data'])
            
            self._undo_stack.append(action)
            
            self._emit_state_changed()
            
            return True
        except Exception as e:
            print(f"重做失败: {e}")
            self._redo_stack.append(action)
            return False
    
    def clear(self):
        """清空撤销/重做栈。"""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._emit_state_changed()
    
    def get_undo_description(self) -> Optional[str]:
        """获取撤销操作的描述。
        
        Returns:
            撤销操作描述，如果没有可撤销的操作则返回None
        """
        if not self.can_undo():
            return None
        
        return self._undo_stack[-1].get('description', "撤销")
    
    def get_redo_description(self) -> Optional[str]:
        """获取重做操作的描述。
        
        Returns:
            重做操作描述，如果没有可重做的操作则返回None
        """
        if not self.can_redo():
            return None
        
        return self._redo_stack[-1].get('description', "重做")
    
    def _emit_state_changed(self):
        """发射状态改变信号。"""
        self.can_undo_changed.emit(self.can_undo())
        self.can_redo_changed.emit(self.can_redo())
    
    @property
    def undo_count(self) -> int:
        """获取撤销栈大小。"""
        return len(self._undo_stack)
    
    @property
    def redo_count(self) -> int:
        """获取重做栈大小。"""
        return len(self._redo_stack)
    
    def _on_settings_changed(self, key: str, value: Any):
        """设置变化回调。
        
        Args:
            key: 设置键
            value: 设置值
        """
        if key == "undo_max_steps":
            self._max_steps = value
            if len(self._undo_stack) > self._max_steps:
                self._undo_stack = self._undo_stack[-self._max_steps:]
