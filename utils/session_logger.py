"""会话日志模块。

本模块提供会话日志记录功能，用于记录应用程序运行时的重要事件。
自动保存日志到文件，并管理日志文件数量（保留最近8个）。
"""

from datetime import datetime
from typing import Optional, List
import os


class SessionLogger:
    """会话日志记录器。
    
    用于记录应用程序运行时的重要事件，如启动、打开项目、保存项目等。
    自动保存日志到文件，并管理日志文件数量（保留最近8个）。
    """
    
    MAX_LOG_FILES = 8
    LOG_DIR_NAME = "session_logs"
    
    def __init__(self):
        """初始化会话日志记录器。"""
        self._logs: list = []
        self._log_dir = self._get_log_dir()
        self._log_file = self._create_log_file()
        self._cleanup_old_logs()
    
    def _get_log_dir(self) -> str:
        """获取日志目录路径。"""
        app_data = os.getenv('APPDATA') or os.path.expanduser('~')
        log_dir = os.path.join(app_data, 'UIDevTool', self.LOG_DIR_NAME)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def _create_log_file(self) -> str:
        """创建当前会话的日志文件。"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(self._log_dir, f"session_{timestamp}.log")
    
    def _cleanup_old_logs(self):
        """清理旧日志文件，只保留最近8个。"""
        log_files = []
        for f in os.listdir(self._log_dir):
            if f.startswith('session_') and f.endswith('.log'):
                log_files.append(os.path.join(self._log_dir, f))
        
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        for old_file in log_files[self.MAX_LOG_FILES:]:
            try:
                os.remove(old_file)
            except Exception:
                pass
    
    def log(self, level: str, message: str):
        """记录一条日志。
        
        Args:
            level: 日志级别（INFO, WARNING, ERROR, DEBUG）
            message: 日志消息
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self._logs.append(log_entry)
        
        try:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception:
            pass
    
    def info(self, message: str):
        """记录INFO级别日志。"""
        self.log("INFO", message)
    
    def warning(self, message: str):
        """记录WARNING级别日志。"""
        self.log("WARNING", message)
    
    def error(self, message: str):
        """记录ERROR级别日志。"""
        self.log("ERROR", message)
    
    def debug(self, message: str):
        """记录DEBUG级别日志。"""
        self.log("DEBUG", message)
    
    def get_logs(self) -> list:
        """获取所有日志记录。"""
        return self._logs.copy()
    
    def clear(self):
        """清空日志记录。"""
        self._logs.clear()
    
    def get_log_file_path(self) -> str:
        """获取当前日志文件路径。"""
        return self._log_file
    
    def get_all_log_files(self) -> List[str]:
        """获取所有日志文件列表。"""
        log_files = []
        for f in os.listdir(self._log_dir):
            if f.startswith('session_') and f.endswith('.log'):
                log_files.append(os.path.join(self._log_dir, f))
        return sorted(log_files, key=lambda x: os.path.getmtime(x), reverse=True)
