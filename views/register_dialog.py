"""注册对话框模块。

本模块包含首次启动时的用户注册对话框实现。
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QWidget, QSpacerItem, QSizePolicy, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.settings import app_settings


class RegisterDialog(QDialog):
    """注册对话框。
    
    首次启动时显示，要求用户输入名字进行注册。
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("欢迎使用")
        self.setMinimumWidth(420)
        self.setMinimumHeight(350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)
        
        title_label = QLabel("你好！")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        welcome_label = QLabel("欢迎使用傻瓜桌面开发工具")
        welcome_label.setFont(QFont("Microsoft YaHei", 12))
        welcome_label.setStyleSheet("color: #666666;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        layout.addSpacing(10)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        input_style = """
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0078d7;
            }
        """
        
        name_label = QLabel("你的名字：")
        name_label.setFont(QFont("Microsoft YaHei", 11))
        name_label.setStyleSheet("color: #333333;")
        
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("请输入你的名字")
        self._name_edit.setMinimumHeight(36)
        self._name_edit.setStyleSheet(input_style)
        form_layout.addRow(name_label, self._name_edit)
        
        invite_label = QLabel("邀请码：")
        invite_label.setFont(QFont("Microsoft YaHei", 11))
        invite_label.setStyleSheet("color: #333333;")
        
        self._invite_edit = QLineEdit()
        self._invite_edit.setPlaceholderText("可选，可留空")
        self._invite_edit.setMinimumHeight(36)
        self._invite_edit.setStyleSheet(input_style)
        form_layout.addRow(invite_label, self._invite_edit)
        
        test_label = QLabel("测试码：")
        test_label.setFont(QFont("Microsoft YaHei", 11))
        test_label.setStyleSheet("color: #333333;")
        
        self._test_edit = QLineEdit()
        self._test_edit.setPlaceholderText("可选，可留空")
        self._test_edit.setMinimumHeight(36)
        self._test_edit.setStyleSheet(input_style)
        form_layout.addRow(test_label, self._test_edit)
        
        layout.addLayout(form_layout)
        
        layout.addSpacing(10)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self._confirm_btn = QPushButton("确定")
        self._confirm_btn.setFixedSize(120, 40)
        self._confirm_btn.setFont(QFont("Microsoft YaHei", 11))
        self._confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self._confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(self._confirm_btn)
        
        layout.addLayout(btn_layout)
        
        self._name_edit.textChanged.connect(self._on_text_changed)
        self._confirm_btn.setEnabled(False)
    
    def _on_text_changed(self, text: str):
        """文本改变时的回调。"""
        self._confirm_btn.setEnabled(len(text.strip()) > 0)
    
    def _on_confirm(self):
        """确认按钮点击。"""
        name = self._name_edit.text().strip()
        if name:
            app_settings.user_name = name
            app_settings.is_registered = True
            invite_code = self._invite_edit.text().strip()
            test_code = self._test_edit.text().strip()
            if invite_code:
                app_settings.set("invite_code", invite_code)
            if test_code:
                app_settings.set("test_code", test_code)
            self.accept()
    
    def get_user_name(self) -> str:
        """获取用户输入的名字。"""
        return self._name_edit.text().strip()
    
    def get_invite_code(self) -> str:
        """获取邀请码。"""
        return self._invite_edit.text().strip()
    
    def get_test_code(self) -> str:
        """获取测试码。"""
        return self._test_edit.text().strip()
