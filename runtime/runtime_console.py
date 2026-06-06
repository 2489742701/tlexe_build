"""运行时控制台模块。

提供运行时的日志查看面板，嵌入到运行窗口底部，
实时显示 DebugLogger 的日志输出和 Python 异常信息。
"""

import sys
import traceback
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QSplitter
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QColor, QTextCharFormat

from dev_mode.debug_logger import DebugLogger, LogLevel


class RuntimeConsole(QWidget):
    """运行时控制台面板。
    
    嵌入运行窗口底部，显示日志输出和异常信息。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = DebugLogger.get_instance()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setMaximumHeight(250)
        self.setMinimumHeight(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 2, 4, 2)

        self._level_combo = QComboBox()
        self._level_combo.addItems(["全部", "ERROR", "WARNING", "INFO", "DEBUG", "CRITICAL"])
        self._level_combo.setCurrentText("全部")
        self._level_combo.currentTextChanged.connect(self._on_level_changed)
        toolbar.addWidget(self._level_combo)

        toolbar.addStretch()

        clear_btn = QPushButton("清除")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(self._on_clear_logs)
        toolbar.addWidget(clear_btn)

        toggle_btn = QPushButton("收起")
        toggle_btn.setFixedWidth(60)
        toggle_btn.clicked.connect(self._toggle_collapse)
        toolbar.addWidget(toggle_btn)
        self._toggle_btn = toggle_btn

        layout.addLayout(toolbar)

        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFont(QFont("Consolas", 9))
        self._log_text.setStyleSheet(
            "QTextEdit { background-color: #1a1a2e; color: #d4d4d4; border: 1px solid #333; }"
        )
        layout.addWidget(self._log_text)

        self._collapsed = False

    def _connect_signals(self):
        self._logger.log_added.connect(self._on_log_added)

    @Slot(str, str, str)
    def _on_log_added(self, level: str, message: str, source: str):
        current_filter = self._level_combo.currentText()
        if current_filter != "全部" and level.upper() != current_filter:
            return

        self._append_log(level, message, source)

    def _append_log(self, level: str, message: str, source: str):
        cursor = self._log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        color_map = {
            'debug': '#666666',
            'info': '#a0a0a0',
            'warning': '#ffcc00',
            'error': '#ff5555',
            'critical': '#ff2222',
        }

        color = color_map.get(level.lower(), '#d4d4d4')

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))

        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        source_tag = f"[{source}]" if source else ""
        line = f"[{ts}] [{level.upper()}] {source_tag} {message}\n"

        cursor.insertText(line, fmt)
        self._log_text.setTextCursor(cursor)
        self._log_text.ensureCursorVisible()

    def _on_level_changed(self, level: str):
        self._log_text.clear()
        log_level = None if level == "全部" else LogLevel(level.lower())
        logs = self._logger.get_logs(log_level)
        for log in logs:
            self._append_log(log['level'], log['message'], log.get('source', ''))

    def _on_clear_logs(self):
        self._logger.clear_logs()
        self._log_text.clear()

    def _toggle_collapse(self):
        if self._collapsed:
            self._log_text.show()
            self._level_combo.show()
            self._toggle_btn.setText("收起")
            self._collapsed = False
        else:
            self._log_text.hide()
            self._level_combo.hide()
            self._toggle_btn.setText("展开")
            self._collapsed = True

    def append_error(self, error_msg: str):
        self._append_log("error", error_msg, "runtime")

    def append_exception(self, exc_type, exc_value, exc_tb):
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        self._append_log("critical", tb_str, "exception")


class ExceptionInterceptor:
    """全局异常拦截器。
    
    安装后捕获所有未处理异常，转发到 RuntimeConsole 和 DebugLogger。
    """

    def __init__(self, console: RuntimeConsole = None):
        self._console = console
        self._original_excepthook = sys.excepthook

    def install(self):
        sys.excepthook = self._excepthook

    def uninstall(self):
        sys.excepthook = self._original_excepthook

    def set_console(self, console: RuntimeConsole):
        self._console = console

    def _excepthook(self, exc_type, exc_value, exc_tb):
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

        DebugLogger.critical(tb_str, "exception")

        if self._console:
            try:
                self._console.append_exception(exc_type, exc_value, exc_tb)
            except RuntimeError:
                self._console = None

        self._original_excepthook(exc_type, exc_value, exc_tb)
