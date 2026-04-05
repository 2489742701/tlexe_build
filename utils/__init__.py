"""工具模块。

本模块包含各种工具类和函数。
"""

from .undo_manager import UndoManager
from .settings import app_settings
from .crash_log import setup_crash_handler, get_crash_log_dir, get_recent_crash_logs
from .font_utils import get_available_fonts, get_default_font, is_font_available
from .converter import ProjectConverter, convert_itexe_to_py, convert_py_to_itexe
from .safe_code_generator import (
    SafeCodeGenerator,
    safe_format_template,
    safe_repr,
    generate_safe_button_code,
    CODE_TEMPLATES
)
from .signal_manager import (
    SignalConnection,
    SignalConnectionGroup,
    QObjectTracker,
    SafeSlot,
    SignalThrottler,
    safe_connect,
    safe_disconnect_all,
    GlobalSignalRegistry
)

__all__ = [
    'UndoManager',
    'app_settings',
    'setup_crash_handler',
    'get_crash_log_dir',
    'get_recent_crash_logs',
    'get_available_fonts',
    'get_default_font',
    'is_font_available',
    'ProjectConverter',
    'convert_itexe_to_py',
    'convert_py_to_itexe',
    # 新增：安全代码生成
    'SafeCodeGenerator',
    'safe_format_template',
    'safe_repr',
    'generate_safe_button_code',
    'CODE_TEMPLATES',
    # 新增：信号生命周期管理
    'SignalConnection',
    'SignalConnectionGroup',
    'QObjectTracker',
    'SafeSlot',
    'SignalThrottler',
    'safe_connect',
    'safe_disconnect_all',
    'GlobalSignalRegistry',
]
