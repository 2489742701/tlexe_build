"""开发者模式管理器模块。

本模块提供开发者模式的统一管理，包括调试日志、测试框架等功能。
"""

from typing import Optional, Dict, Any, List
from PySide6.QtCore import QObject, Signal
from enum import Enum


class LogLevel(Enum):
    """日志级别枚举。"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class _DevModeManagerSignals(QObject):
    """信号类，用于解决 QObject 单例模式的递归问题。
    
    将信号分离到独立的 QObject 子类中，避免 DevModeManager 本身的
    单例实现与 QObject 的初始化机制冲突。
    """
    mode_changed = Signal(bool)
    log_added = Signal(str, str, str)


class DevModeManager:
    """开发者模式管理器。
    
    单例模式实现，管理开发者模式的所有功能。
    
    注意：本类不继承 QObject，以避免单例模式与 QObject 初始化机制的冲突。
    信号功能通过内部的 _signals 对象实现。
    """
    
    _instance: Optional['DevModeManager'] = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现。
        
        确保全局只有一个 DevModeManager 实例。
        
        Returns:
            DevModeManager: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化开发者模式管理器。
        
        采用延迟初始化策略，通过 _initialized 标志确保只初始化一次。
        这是单例模式的关键部分，避免多次调用 __init__ 导致状态重置。
        """
        # 检查是否已初始化，避免单例重复初始化
        if DevModeManager._initialized:
            return
        
        # 创建信号对象，用于发出状态变化通知
        self._signals = _DevModeManagerSignals()
        
        # 开发者模式开启状态，默认关闭
        self._enabled: bool = False
        
        # 关联的项目模型引用
        self._project_model = None
        
        # 日志存储列表
        self._logs: List[Dict[str, Any]] = []
        
        # 标记初始化完成
        DevModeManager._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'DevModeManager':
        """获取单例实例。
        
        类方法，返回全局唯一的 DevModeManager 实例。
        如果实例不存在则创建。
        
        Returns:
            DevModeManager: 单例实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def mode_changed(self):
        """开发者模式状态改变信号。
        
        通过此属性可以连接信号处理函数。
        
        Returns:
            Signal: 状态改变信号
        
        示例:
            manager.mode_changed.connect(self._on_mode_changed)
        """
        return self._signals.mode_changed
    
    @property
    def log_added_signal(self):
        """日志添加信号。
        
        当新日志添加时发射此信号，可用于实时显示日志。
        
        Returns:
            Signal: 日志添加信号，参数为(level, message, source)
        
        示例:
            manager.log_added_signal.connect(self._on_log_added)
        """
        return self._signals.log_added
    
    @property
    def enabled(self) -> bool:
        """获取开发者模式是否开启。
        
        Returns:
            bool: True 表示已开启，False 表示已关闭
        """
        return self._enabled
    
    def enable(self, project_model=None):
        """开启开发者模式。
        
        设置开发者模式为开启状态，并可选地设置项目模型。
        
        Args:
            project_model: 项目模型实例（可选），用于项目级操作
        
        执行流程:
            1. 设置开启状态
            2. 保存项目模型（如果提供）
            3. 发出状态改变信号
        """
        self._enabled = True
        self._project_model = project_model
        self._signals.mode_changed.emit(True)
    
    def disable(self):
        """关闭开发者模式。
        
        设置开发者模式为关闭状态，并发出状态改变信号。
        """
        self._enabled = False
        self._signals.mode_changed.emit(False)
    
    def toggle(self):
        """切换开发者模式状态。
        
        便捷方法：如果已开启则关闭，如果已关闭则开启。
        适用于菜单项或快捷键绑定。
        """
        if self._enabled:
            self.disable()
        else:
            self.enable()
    
    def set_project_model(self, model):
        """设置项目模型。
        
        关联项目模型，用于项目级操作和日志上下文。
        
        Args:
            model: 项目模型实例
        """
        self._project_model = model
    
    def add_log(self, level: str, message: str, source: str = ""):
        """添加日志条目。
        
        创建一个带时间戳的日志条目并存储，同时发出日志添加信号。
        
        Args:
            level: 日志级别，如 "debug", "info", "warning", "error", "critical"
            message: 日志消息内容
            source: 日志来源标识（可选），如类名或方法名
        
        日志条目结构:
            {
                'level': 日志级别,
                'message': 日志消息,
                'source': 来源标识,
                'timestamp': ISO格式时间戳
            }
        
        示例:
            manager.add_log("info", "用户登录成功", "AuthManager")
        """
        import datetime
        
        # 创建日志条目
        log_entry = {
            'level': level,
            'message': message,
            'source': source,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # 存储日志
        self._logs.append(log_entry)
        
        # 发出日志添加信号，通知监听者
        self._signals.log_added.emit(level, message, source)
    
    def get_logs(self, level: str = None) -> List[Dict[str, Any]]:
        """获取日志列表。
        
        返回存储的日志条目，可按级别过滤。
        
        Args:
            level: 日志级别过滤（可选），如果提供则只返回该级别的日志
        
        Returns:
            List[Dict[str, Any]]: 日志条目列表
        
        示例:
            # 获取所有日志
            all_logs = manager.get_logs()
            
            # 只获取错误日志
            error_logs = manager.get_logs("error")
        """
        if level:
            # 过滤指定级别的日志
            return [log for log in self._logs if log['level'] == level]
        # 返回日志副本，避免外部修改影响内部数据
        return self._logs.copy()
    
    def clear_logs(self):
        """清除所有日志。
        
        清空内部日志存储列表。此操作不可撤销。
        """
        self._logs.clear()


def get_dev_manager() -> DevModeManager:
    """获取开发者模式管理器实例。
    
    便捷函数，返回全局唯一的 DevModeManager 单例实例。
    等同于 DevModeManager.get_instance() 或 DevModeManager()。
    
    Returns:
        DevModeManager: 开发者模式管理器单例实例
    
    示例:
        # 快速获取管理器实例
        dev_manager = get_dev_manager()
        
        # 开启开发者模式
        dev_manager.enable()
        
        # 添加日志
        dev_manager.add_log("info", "操作完成")
    """
    return DevModeManager.get_instance()
