"""崩溃日志模块。

本模块提供崩溃日志记录功能，捕获未处理的异常并记录到文件。
"""

import sys
import os
import traceback
import datetime
from typing import Optional

def setup_crash_handler(log_dir: str = None) -> str:
    """设置崩溃处理器。
    
    Args:
        log_dir: 日志目录，默认为用户数据目录
        
    Returns:
        日志文件路径
    """
    if log_dir is None:
        app_data = os.getenv('APPDATA') or os.path.expanduser('~')
        log_dir = os.path.join(app_data, 'UIDevTool', 'crash_logs')
    
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"crash_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    def exception_hook(exc_type, exc_value, exc_traceback):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"崩溃时间: {datetime.datetime.now().isoformat()}\n")
            f.write(f"异常类型: {exc_type.__name__}\n")
            f.write(f"异常信息: {str(exc_value)}\n\n")
            f.write("堆栈跟踪:\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_hook
    
    return log_file

def get_crash_log_dir() -> str:
    """获取崩溃日志目录。
    
    Returns:
        崩溃日志目录路径
    """
    app_data = os.getenv('APPDATA') or os.path.expanduser('~')
    return os.path.join(app_data, 'UIDevTool', 'crash_logs')

def get_recent_crash_logs(count: int = 5) -> list:
    """获取最近的崩溃日志文件。
    
    Args:
        count: 返回的日志数量
        
    Returns:
        日志文件路径列表
    """
    log_dir = get_crash_log_dir()
    if not os.path.exists(log_dir):
        return []
    
    files = []
    for f in os.listdir(log_dir):
        if f.startswith('crash_') and f.endswith('.log'):
            files.append(os.path.join(log_dir, f))
    
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[:count]
