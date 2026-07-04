"""UI 问题修复 - 实际使用问题修复。

修复内容：
1. 文本居中加载问题
2. 程序逻辑树默认显示问题
3. 信号注册功能逻辑
4. 主菜单容器切换问题
"""

import logging
from typing import Optional, Dict, Any, List
from PySide6.QtCore import QObject, Signal, QTimer, Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout,
    QStackedWidget, QLabel, QPushButton, QMessageBox
)

logger = logging.getLogger(__name__)

# ============================================================================
# 修复 1: 布局刷新管理器
# ============================================================================

class LayoutRefreshManager(QObject):
    """布局刷新管理器。
    
    解决文本居中加载问题：确保组件在显示时正确刷新布局。
    """
    
    refresh_needed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._widgets_to_refresh = []
    
    def schedule_refresh(self, widget: QWidget, delay_ms: int = 100):
        """计划刷新组件。
        
        Args:
            widget: 需要刷新的组件
            delay_ms: 延迟时间（毫秒）
        """
        self._widgets_to_refresh.append(widget)
        QTimer.singleShot(delay_ms, lambda: self._do_refresh(widget))
    
    def _do_refresh(self, widget: QWidget):
        """执行刷新。"""
        if widget and widget.isVisible():
            widget.updateGeometry()
            if widget.layout():
                widget.layout().activate()
            
            # 递归刷新子组件
            for child in widget.findChildren(QWidget):
                child.updateGeometry()
            
            logger.debug(f"刷新组件布局: {widget.objectName()}")
    
    def refresh_all(self, parent_widget: QWidget):
        """刷新所有子组件。"""
        for widget in parent_widget.findChildren(QWidget):
            widget.updateGeometry()
        
        if parent_widget.layout():
            parent_widget.layout().activate()
        
        self.refresh_needed.emit()
        logger.info("刷新所有布局完成")

# ============================================================================
# 修复 2: 左侧布局管理器
# ============================================================================

class LeftPanelManager(QObject):
    """左侧面板管理器。
    
    解决程序逻辑树默认显示问题：管理逻辑树和组件面板的布局。
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._splitter: Optional[QSplitter] = None
        self._logic_tree: Optional[QWidget] = None
        self._component_panel: Optional[QWidget] = None
    
    def setup_layout(self, logic_tree: QWidget, component_panel: QWidget) -> QSplitter:
        """设置左侧布局。
        
        Args:
            logic_tree: 程序逻辑树组件
            component_panel: 组件面板
            
        Returns:
            配置好的 QSplitter
        """
        self._logic_tree = logic_tree
        self._component_panel = component_panel
        
        # 创建垂直分割器
        self._splitter = QSplitter(Qt.Vertical)
        self._splitter.addWidget(logic_tree)
        self._splitter.addWidget(component_panel)
        
        # 设置初始大小（平分）
        # 假设总高度为 600，各分配 300
        self._splitter.setSizes([300, 300])
        
        # 设置拉伸因子（保持比例）
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)
        
        logger.info("左侧面板布局已设置")
        return self._splitter
    
    def set_equal_sizes(self):
        """设置两个面板大小相等。"""
        if self._splitter:
            total_height = sum(self._splitter.sizes())
            half_height = total_height // 2
            self._splitter.setSizes([half_height, half_height])

# ============================================================================
# 修复 3: 信号-事件系统（简化版）
# ============================================================================

class SignalEvent(QObject):
    """信号-事件关联类。
    
    解决信号注册功能逻辑问题：
    - 点击信号注册时创建信号和事件
    - 事件在信号内部管理
    - 不直接跳转，而是创建后可在信号列表中查看
    """
    
    # Qt 信号定义
    event_created = Signal(str)  # 参数：信号ID
    event_updated = Signal(str)  # 参数：信号ID
    
    def __init__(self, signal_id: str, signal_name: str, parent=None):
        super().__init__(parent)
        self._id = signal_id
        self._name = signal_name
        self._event_data: Dict[str, Any] = {
            "action": "",
            "params": {},
            "enabled": True
        }
        self._is_registered = False
    
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
    def is_registered(self) -> bool:
        return self._is_registered
    
    def register(self) -> bool:
        """注册信号并创建默认事件。
        
        Returns:
            是否成功注册
        """
        if self._is_registered:
            logger.warning(f"信号 {self._id} 已注册")
            return False
        
        # 创建默认事件
        self._event_data = {
            "action": "show_message",  # 默认动作
            "params": {"message": f"信号 {self._name} 触发"},
            "enabled": True
        }
        
        self._is_registered = True
        self.event_created.emit(self._id)
        
        logger.info(f"信号已注册: {self._name} ({self._id})")
        return True
    
    def update_event(self, action: str, params: Dict[str, Any]):
        """更新事件。
        
        Args:
            action: 动作类型
            params: 动作参数
        """
        self._event_data["action"] = action
        self._event_data["params"] = params
        self.event_updated.emit(self._id)
        
        logger.info(f"事件已更新: {self._name}")
    
    def get_event_data(self) -> Dict[str, Any]:
        """获取事件数据。"""
        return self._event_data.copy()
    
    def execute_event(self) -> Any:
        """执行关联的事件。
        
        Returns:
            执行结果
        """
        if not self._is_registered:
            logger.warning(f"信号 {self._id} 未注册")
            return None
        
        if not self._event_data["enabled"]:
            logger.info(f"事件已禁用: {self._name}")
            return None
        
        action = self._event_data["action"]
        params = self._event_data["params"]
        
        # 执行动作（简化示例）
        if action == "show_message":
            message = params.get("message", "")
            QMessageBox.information(None, "信号触发", message)
            return {"action": action, "result": "success"}
        
        return {"action": action, "result": "unknown_action"}

class SignalRegistry(QObject):
    """信号注册表。
    
    管理所有信号-事件关联。
    """
    
    signal_registered = Signal(str)  # 信号ID
    signal_removed = Signal(str)     # 信号ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals: Dict[str, SignalEvent] = {}
    
    def create_signal(self, name: str) -> SignalEvent:
        """创建新信号（不注册）。
        
        Args:
            name: 信号名称
            
        Returns:
            信号对象
        """
        import uuid
        signal_id = str(uuid.uuid4())
        signal = SignalEvent(signal_id, name, self)
        self._signals[signal_id] = signal
        return signal
    
    def register_signal(self, signal_id: str) -> bool:
        """注册信号（创建默认事件）。
        
        Args:
            signal_id: 信号ID
            
        Returns:
            是否成功
        """
        if signal_id not in self._signals:
            logger.warning(f"信号 {signal_id} 不存在")
            return False
        
        signal = self._signals[signal_id]
        if signal.register():
            self.signal_registered.emit(signal_id)
            return True
        return False
    
    def get_signal(self, signal_id: str) -> Optional[SignalEvent]:
        """获取信号。"""
        return self._signals.get(signal_id)
    
    def get_all_signals(self) -> List[SignalEvent]:
        """获取所有信号。"""
        return list(self._signals.values())
    
    def remove_signal(self, signal_id: str) -> bool:
        """移除信号。"""
        if signal_id in self._signals:
            del self._signals[signal_id]
            self.signal_removed.emit(signal_id)
            return True
        return False

# ============================================================================
# 修复 4: 视图切换帮助类
# ============================================================================

class NavigationHelper(QObject):
    """导航帮助类。
    
    解决主菜单容器切换问题：辅助菜单按钮切换视图。
    """
    
    def __init__(self, stacked_widget: QStackedWidget, parent=None):
        super().__init__(parent)
        self._stacked = stacked_widget
        self._button_to_view: Dict[QPushButton, str] = {}
        self._current_view_id: Optional[str] = None
    
    def register_button(self, button: QPushButton, view_id: str):
        """注册按钮和视图的映射。
        
        Args:
            button: 菜单按钮
            view_id: 视图ID
        """
        self._button_to_view[button] = view_id
        button.clicked.connect(lambda: self.switch_to(view_id))
    
    def switch_to(self, view_id: str) -> bool:
        """切换到指定视图。
        
        Args:
            view_id: 视图ID
            
        Returns:
            是否成功切换
        """
        for i in range(self._stacked.count()):
            widget = self._stacked.widget(i)
            if widget.objectName() == view_id:
                self._stacked.setCurrentWidget(widget)
                self._current_view_id = view_id
                logger.info(f"切换到视图: {view_id}")
                return True
        return False
    
    def get_current_view(self) -> Optional[str]:
        """获取当前视图ID。"""
        return self._current_view_id