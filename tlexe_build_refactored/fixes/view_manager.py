"""视图管理器 - 解决容器切换问题。

提供统一的视图管理和容器切换功能。
"""

import logging
from typing import Dict, Optional, Callable, Any
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

logger = logging.getLogger(__name__)

class ViewManager(QObject):
    """视图管理器。
    
    解决主菜单容器切换问题：
    - 点击游戏主菜单时自动切换到主菜单容器
    - 统一管理所有视图/容器的切换
    - 支持视图历史记录（可选）
    
    【使用示例】
    >>> view_manager = ViewManager(stacked_widget)
    >>> view_manager.register_view("main_menu", main_menu_widget)
    >>> view_manager.register_view("game", game_widget)
    >>> view_manager.switch_to("main_menu")  # 切换到主菜单
    """
    
    # Qt 信号
    view_changed = Signal(str, str)  # 从视图ID, 到视图ID
    view_registered = Signal(str)     # 视图ID
    view_unregistered = Signal(str)   # 视图ID
    
    def __init__(self, stacked_widget: QStackedWidget, parent=None):
        """初始化视图管理器。
        
        Args:
            stacked_widget: 堆叠部件，用于切换视图
            parent: 父对象
        """
        super().__init__(parent)
        self._stacked = stacked_widget
        self._views: Dict[str, QWidget] = {}
        self._current_view_id: Optional[str] = None
        self._default_view_id: Optional[str] = None
    
    def register_view(self, view_id: str, widget: QWidget, 
                     make_default: bool = False) -> bool:
        """注册视图。
        
        Args:
            view_id: 视图唯一标识
            widget: 视图部件
            make_default: 是否设为默认视图
            
        Returns:
            是否注册成功
        """
        if view_id in self._views:
            logger.warning(f"视图已存在: {view_id}")
            return False
        
        self._views[view_id] = widget
        self._stacked.addWidget(widget)
        
        if make_default or self._default_view_id is None:
            self._default_view_id = view_id
        
        self.view_registered.emit(view_id)
        logger.info(f"视图已注册: {view_id}")
        return True
    
    def unregister_view(self, view_id: str) -> bool:
        """注销视图。
        
        Args:
            view_id: 视图唯一标识
            
        Returns:
            是否注销成功
        """
        if view_id not in self._views:
            logger.warning(f"视图不存在: {view_id}")
            return False
        
        widget = self._views.pop(view_id)
        self._stacked.removeWidget(widget)
        
        if self._current_view_id == view_id:
            self._current_view_id = None
        
        if self._default_view_id == view_id:
            self._default_view_id = next(iter(self._views.keys()), None)
        
        self.view_unregistered.emit(view_id)
        logger.info(f"视图已注销: {view_id}")
        return True
    
    def switch_to(self, view_id: str) -> bool:
        """切换到指定视图。
        
        Args:
            view_id: 目标视图ID
            
        Returns:
            是否切换成功
        """
        if view_id not in self._views:
            logger.error(f"视图不存在: {view_id}")
            return False
        
        if self._current_view_id == view_id:
            logger.debug(f"已经在视图: {view_id}")
            return True
        
        previous_id = self._current_view_id
        widget = self._views[view_id]
        
        self._stacked.setCurrentWidget(widget)
        self._current_view_id = view_id
        
        self.view_changed.emit(previous_id or "", view_id)
        logger.info(f"视图切换: {previous_id} -> {view_id}")
        return True
    
    def switch_to_default(self) -> bool:
        """切换到默认视图。
        
        Returns:
            是否切换成功
        """
        if self._default_view_id:
            return self.switch_to(self._default_view_id)
        logger.warning("没有设置默认视图")
        return False
    
    def get_current_view_id(self) -> Optional[str]:
        """获取当前视图ID。"""
        return self._current_view_id
    
    def get_view(self, view_id: str) -> Optional[QWidget]:
        """获取视图部件。"""
        return self._views.get(view_id)
    
    def get_all_view_ids(self) -> list:
        """获取所有视图ID。"""
        return list(self._views.keys())
    
    def set_default_view(self, view_id: str) -> bool:
        """设置默认视图。
        
        Args:
            view_id: 视图ID
            
        Returns:
            是否设置成功
        """
        if view_id not in self._views:
            logger.warning(f"视图不存在: {view_id}")
            return False
        
        self._default_view_id = view_id
        logger.info(f"默认视图已设置: {view_id}")
        return True

# ============================================================================
# 便捷函数
# ============================================================================

def create_view_manager(stacked_widget: QStackedWidget) -> ViewManager:
    """创建视图管理器的便捷函数。
    
    Args:
        stacked_widget: 堆叠部件
        
    Returns:
        视图管理器实例
    """
    return ViewManager(stacked_widget)
