"""信号定义模块。

本模块定义了项目中使用的各种信号。
"""

from PySide6.QtCore import QObject, Signal


class GlobalSignals(QObject):
    """全局信号对象。
    
    提供跨模块通信的信号。
    """
    
    # ==================== 信号定义（出口） ====================
    project_saved = Signal(str)      # 【信号出口】项目保存完成，参数：file_path 项目文件路径
    project_loaded = Signal(str)     # 【信号出口】项目加载完成，参数：file_path 项目文件路径
    component_created = Signal(str)  # 【信号出口】组件创建完成，参数：comp_id 组件ID
    component_deleted = Signal(str)  # 【信号出口】组件删除完成，参数：comp_id 组件ID
    window_created = Signal(str)     # 【信号出口】窗口创建完成，参数：window_id 窗口ID
    window_deleted = Signal(str)     # 【信号出口】窗口删除完成，参数：window_id 窗口ID


global_signals = GlobalSignals()
