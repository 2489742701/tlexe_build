"""调试日志模块。

本模块提供统一的日志记录功能，支持多种日志级别和输出方式。
"""

import sys
import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from PySide6.QtCore import QObject, Signal

class LogLevel(Enum):
    """日志级别枚举。"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DebugLogger(QObject):
    """调试日志记录器。
    
    提供统一的日志记录功能，支持控制台输出和文件输出。
    
    Signals:
        log_added: 新日志添加时发射 (level, message, source)
    """
    
    _instance: Optional['DebugLogger'] = None
    
    log_added = Signal(str, str, str)
    
    def __init__(self):
        super().__init__()
        self._logs: List[Dict[str, Any]] = []
        self._console_output: bool = True
        self._file_output: bool = False
        self._log_file: str = ""
        self._min_level: LogLevel = LogLevel.DEBUG
    
    @classmethod
    def get_instance(cls) -> 'DebugLogger':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def debug(cls, message: str, source: str = ""):
        cls.log_internal(message, LogLevel.DEBUG, source)
    
    @classmethod
    def info(cls, message: str, source: str = ""):
        cls.log_internal(message, LogLevel.INFO, source)
    
    @classmethod
    def warning(cls, message: str, source: str = ""):
        cls.log_internal(message, LogLevel.WARNING, source)
    
    @classmethod
    def error(cls, message: str, source: str = ""):
        cls.log_internal(message, LogLevel.ERROR, source)
    
    @classmethod
    def critical(cls, message: str, source: str = ""):
        cls.log_internal(message, LogLevel.CRITICAL, source)
    
    @classmethod
    def log_internal(cls, message: str, level: LogLevel, source: str = ""):
        instance = cls.get_instance()
        
        log_entry = {
            'level': level.value,
            'message': message,
            'source': source,
            'timestamp': datetime.datetime.now().isoformat()
        }
        instance._logs.append(log_entry)
        
        if instance._console_output:
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f")[:-3] + "]"
            level_str = f"[{level.value.upper()}]"
            source_str = f"[{source}]" if source else "[内部]"
            print(f"{timestamp} {level_str} {source_str} {message}")
        
        if instance._file_output and instance._log_file:
            try:
                with open(instance._log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f")[:-3] + "]"
                    f.write(f"{timestamp} [{level.value}] [{source}] {message}\n")
            except Exception:
                pass
        
        instance.log_added.emit(level.value, message, source)
    
    def get_logs(self, level: LogLevel = None) -> List[Dict[str, Any]]:
        if level:
            return [log for log in self._logs if log['level'] == level.value]
        return self._logs.copy()
    
    def clear_logs(self):
        self._logs.clear()
    
    def set_console_output(self, enabled: bool):
        self._console_output = enabled
    
    def set_file_output(self, enabled: bool, file_path: str = ""):
        self._file_output = enabled
        if file_path:
            self._log_file = file_path
    
    def set_min_level(self, level: LogLevel):
        self._min_level = level

def get_logger() -> DebugLogger:
    return DebugLogger.get_instance()
