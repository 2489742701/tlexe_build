"""开发者控制台模块。

本模块提供开发者控制台界面，用于调试和测试。
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QSplitter, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QTextCharFormat

from .debug_logger import DebugLogger, LogLevel
from .test_runner import TestCase, TestRunner

class DevConsole(QWidget):
    """开发者控制台。
    
    提供日志查看、测试运行等开发调试功能。
    
    Signals:
        command_executed: 命令执行时发射 (command)
    """
    
    command_executed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = DebugLogger.get_instance()
        self._test_runner = TestRunner()
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        tab_widget = QTabWidget()
        
        log_tab = self._create_log_tab()
        tab_widget.addTab(log_tab, "日志")
        
        test_tab = self._create_test_tab()
        tab_widget.addTab(test_tab, "测试")
        
        layout.addWidget(tab_widget)
    
    def _create_log_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        toolbar = QHBoxLayout()
        
        level_label = QLabel("日志级别:")
        toolbar.addWidget(level_label)
        
        self._level_combo = QComboBox()
        self._level_combo.addItems(["全部", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self._level_combo.currentTextChanged.connect(self._on_level_changed)
        toolbar.addWidget(self._level_combo)
        
        toolbar.addStretch()
        
        clear_btn = QPushButton("清除日志")
        clear_btn.clicked.connect(self._on_clear_logs)
        toolbar.addWidget(clear_btn)
        
        layout.addLayout(toolbar)
        
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFont(QFont("Consolas", 10))
        self._log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self._log_text)
        
        return widget
    
    def _create_test_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        toolbar = QHBoxLayout()
        
        run_all_btn = QPushButton("运行所有测试")
        run_all_btn.clicked.connect(self._on_run_all_tests)
        toolbar.addWidget(run_all_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self._test_tree = QTreeWidget()
        self._test_tree.setHeaderLabels(["测试用例", "状态"])
        self._test_tree.itemDoubleClicked.connect(self._on_test_double_clicked)
        splitter.addWidget(self._test_tree)
        
        self._test_result_text = QTextEdit()
        self._test_result_text.setReadOnly(True)
        self._test_result_text.setFont(QFont("Consolas", 10))
        splitter.addWidget(self._test_result_text)
        
        splitter.setSizes([300, 300])
        layout.addWidget(splitter)
        
        self._refresh_test_tree()
        
        return widget
    
    def _connect_signals(self):
        self._logger.log_added.connect(self._on_log_added)
        self._test_runner.test_started.connect(self._on_test_started)
        self._test_runner.test_finished.connect(self._on_test_finished)
        self._test_runner.all_tests_finished.connect(self._on_all_tests_finished)
    
    def _on_log_added(self, level: str, message: str, source: str):
        current_level = self._level_combo.currentText()
        if current_level != "全部" and level.upper() != current_level:
            return
        
        cursor = self._log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        color_map = {
            'debug': '#888888',
            'info': '#d4d4d4',
            'warning': '#ffcc00',
            'error': '#ff4444',
            'critical': '#ff0000',
        }
        
        color = color_map.get(level.lower(), '#d4d4d4')
        
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        
        cursor.insertText(f"[{level.upper()}] {message}\n", format)
        
        self._log_text.setTextCursor(cursor)
        self._log_text.ensureCursorVisible()
    
    def _on_level_changed(self, level: str):
        self._log_text.clear()
        
        log_level = None if level == "全部" else LogLevel(level)
        logs = self._logger.get_logs(log_level)
        
        for log in logs:
            self._on_log_added(log['level'], log['message'], log.get('source', ''))
    
    def _on_clear_logs(self):
        self._logger.clear_logs()
        self._log_text.clear()
    
    def _refresh_test_tree(self):
        self._test_tree.clear()
        
        all_tests = TestCase.get_all_tests()
        
        for category, tests in all_tests.items():
            category_item = QTreeWidgetItem([category, ""])
            category_item.setData(0, Qt.ItemDataRole.UserRole, "category")
            self._test_tree.addTopLevelItem(category_item)
            
            for test_id, test_info in tests.items():
                test_item = QTreeWidgetItem([test_info['name'], "未运行"])
                test_item.setData(0, Qt.ItemDataRole.UserRole, test_id)
                category_item.addChild(test_item)
            
            category_item.setExpanded(True)
    
    def _on_run_all_tests(self):
        self._test_result_text.clear()
        self._test_result_text.append("开始运行所有测试...\n")
        
        for i in range(self._test_tree.topLevelItemCount()):
            category_item = self._test_tree.topLevelItem(i)
            for j in range(category_item.childCount()):
                test_item = category_item.child(j)
                test_item.setText(1, "运行中...")
        
        self._test_runner.run_all_tests()
    
    def _on_test_double_clicked(self, item: QTreeWidgetItem, column: int):
        test_id = item.data(0, Qt.ItemDataRole.UserRole)
        if test_id and test_id != "category":
            item.setText(1, "运行中...")
            result = self._test_runner.run_single_test(test_id)
            self._update_test_result(item, result)
    
    def _on_test_started(self, test_id: str, test_name: str):
        self._test_result_text.append(f"运行: {test_name}...")
    
    def _on_test_finished(self, test_id: str, test_name: str, passed: bool, message: str):
        status = "✓ 通过" if passed else "✗ 失败"
        self._test_result_text.append(f"  {status}: {message}\n")
    
    def _on_all_tests_finished(self, passed: int, failed: int, errors: int):
        self._test_result_text.append(f"\n测试完成: {passed} 通过, {failed} 失败, {errors} 错误")
        
        results = self._test_runner.get_results()
        
        for i in range(self._test_tree.topLevelItemCount()):
            category_item = self._test_tree.topLevelItem(i)
            for j in range(category_item.childCount()):
                test_item = category_item.child(j)
                test_id = test_item.data(0, Qt.ItemDataRole.UserRole)
                
                for result in results:
                    if result['id'] == test_id:
                        self._update_test_result(test_item, result)
                        break
    
    def _update_test_result(self, item: QTreeWidgetItem, result: dict):
        status_map = {
            'passed': ('✓ 通过', '#00aa00'),
            'failed': ('✗ 失败', '#ff4444'),
            'error': ('✗ 错误', '#ff0000'),
        }
        
        status_text, color = status_map.get(result['status'], ('未知', '#888888'))
        item.setText(1, status_text)
        item.setForeground(1, QColor(color))
