"""Blockly行为编辑器模块。

本模块提供可视化编程功能，使用积木块方式编辑组件行为。
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class BlocklyEditor(QWidget):
    """Blockly可视化编程编辑器。
    
    提供积木块式的行为编辑界面。
    
    Signals:
        code_generated: 代码生成完成时发射 (code)
        saved: 保存时发射 (xml_data)
    """
    
    code_generated = Signal(str)
    saved = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_xml: str = ""
        self._current_code: str = ""
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("行为编辑器")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        self._placeholder = QLabel("Blockly 可视化编程功能开发中...\n\n当前可使用代码模式编辑行为。")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #666; font-size: 16px;")
        layout.addWidget(self._placeholder)
        
        self._code_edit = QTextEdit()
        self._code_edit.setPlaceholderText("# 在此输入 Python 代码\n# 例如:\n# print('Hello World')")
        self._code_edit.setFont(QFont("Consolas", 10))
        self._code_edit.setVisible(False)
        layout.addWidget(self._code_edit)
        
        btn_layout = QHBoxLayout()
        
        self._code_btn = QPushButton("代码模式")
        self._code_btn.clicked.connect(self._toggle_code_mode)
        btn_layout.addWidget(self._code_btn)
        
        btn_layout.addStretch()
        
        self._apply_btn = QPushButton("应用")
        self._apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(self._apply_btn)
        
        self._save_btn = QPushButton("保存")
        self._save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self._save_btn)
        
        layout.addLayout(btn_layout)
    
    def _toggle_code_mode(self):
        code_visible = self._code_edit.isVisible()
        self._placeholder.setVisible(code_visible)
        self._code_edit.setVisible(not code_visible)
        self._code_btn.setText("可视化模式" if not code_visible else "代码模式")
    
    def _on_apply(self):
        if self._code_edit.isVisible():
            self._current_code = self._code_edit.toPlainText()
            self.code_generated.emit(self._current_code)
    
    def _on_save(self):
        if self._code_edit.isVisible():
            self._current_code = self._code_edit.toPlainText()
        self.saved.emit(self._current_xml)
    
    def set_xml(self, xml_data: str):
        self._current_xml = xml_data
    
    def get_xml(self) -> str:
        return self._current_xml
    
    def set_code(self, code: str):
        self._current_code = code
        self._code_edit.setPlainText(code)
    
    def get_code(self) -> str:
        return self._current_code
    
    def generate_code(self) -> str:
        return "# Blockly代码生成开发中"
