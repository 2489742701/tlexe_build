"""自定义消息弹窗模块。

替代 QMessageBox 的原生弹窗，提供统一风格的消息提示。

ErrorDialog:
    - 红色顶栏警告条
    - 可编辑文本框（可选中复制错误详情）
    - 复制 / 上报 / 关闭 三个按钮

WarningDialog:
    - 橙色顶栏警告条
    - 可编辑文本框
    - 复制 / 关闭 两个按钮
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from styles.theme import Colors, Fonts

class ErrorDialog(QDialog):
    """自定义错误弹窗。

    特征:
        - 红色顶栏警告条
        - 可编辑文本框显示错误详情
        - 复制 / 上报 / 关闭 三个按钮

    用法::

        ErrorDialog.show_error(parent, "导出失败", "无法写入文件:\\nPermission denied")
    """

    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self._message = message
        self.setWindowTitle(title)
        self.setMinimumWidth(480)
        self.setMinimumHeight(260)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui(title, message)

    def _setup_ui(self, title: str, message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel(f"  ⚠  {title}")
        header.setFixedHeight(44)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.ERROR};
                color: white;
                font-size: {Fonts.SIZE_LG}px;
                font-weight: bold;
                font-family: {Fonts.FAMILY_PRIMARY};
                padding-left: 16px;
            }}
        """)
        layout.addWidget(header)

        body = QVBoxLayout()
        body.setContentsMargins(20, 16, 20, 16)
        body.setSpacing(12)

        detail_edit = QTextEdit()
        detail_edit.setPlainText(message)
        detail_edit.setReadOnly(False)
        detail_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.GRAY_100};
                border: 1px solid {Colors.GRAY_200};
                border-radius: 4px;
                padding: 8px;
                font-family: {Fonts.FAMILY_MONOSPACE};
                font-size: {Fonts.SIZE_MD}px;
                color: {Colors.BLACK};
            }}
        """)
        detail_edit.setMinimumHeight(100)
        body.addWidget(detail_edit)
        self._detail_edit = detail_edit

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        copy_btn = QPushButton("复制")
        copy_btn.setFixedSize(80, 32)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_200};
                color: {Colors.BLACK};
                border: none;
                border-radius: 4px;
                font-size: {Fonts.SIZE_MD}px;
                font-family: {Fonts.FAMILY_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_300};
            }}
        """)
        copy_btn.clicked.connect(self._on_copy)
        btn_layout.addWidget(copy_btn)

        report_btn = QPushButton("上报")
        report_btn.setFixedSize(80, 32)
        report_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {Fonts.SIZE_MD}px;
                font-family: {Fonts.FAMILY_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        report_btn.clicked.connect(self._on_report)
        btn_layout.addWidget(report_btn)

        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(80, 32)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ERROR};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {Fonts.SIZE_MD}px;
                font-family: {Fonts.FAMILY_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: #c62828;
            }}
        """)
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        body.addLayout(btn_layout)
        layout.addLayout(body)

    def _on_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self._detail_edit.toPlainText())
        self._detail_edit.setStyleSheet(self._detail_edit.styleSheet())

    def _on_report(self):
        try:
            import urllib.parse
            import webbrowser
            body = urllib.parse.quote(self._detail_edit.toPlainText())
            webbrowser.open(f"https://github.com/example/report/issues/new?body={body}")
        except Exception:
            pass

    @staticmethod
    def show_error(parent, title: str, message: str):
        dialog = ErrorDialog(title, message, parent)
        dialog.exec()

class WarningDialog(QDialog):
    """自定义警告弹窗。

    特征:
        - 橙色顶栏警告条
        - 可编辑文本框显示警告详情
        - 复制 / 关闭 两个按钮

    用法::

        WarningDialog.show_warning(parent, "提示", "请先添加组件")
    """

    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self._message = message
        self.setWindowTitle(title)
        self.setMinimumWidth(420)
        self.setMinimumHeight(200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui(title, message)

    def _setup_ui(self, title: str, message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel(f"  ⚠  {title}")
        header.setFixedHeight(44)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.WARNING};
                color: white;
                font-size: {Fonts.SIZE_LG}px;
                font-weight: bold;
                font-family: {Fonts.FAMILY_PRIMARY};
                padding-left: 16px;
            }}
        """)
        layout.addWidget(header)

        body = QVBoxLayout()
        body.setContentsMargins(20, 16, 20, 16)
        body.setSpacing(12)

        detail_edit = QTextEdit()
        detail_edit.setPlainText(message)
        detail_edit.setReadOnly(False)
        detail_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.GRAY_100};
                border: 1px solid {Colors.GRAY_200};
                border-radius: 4px;
                padding: 8px;
                font-family: {Fonts.FAMILY_PRIMARY};
                font-size: {Fonts.SIZE_MD}px;
                color: {Colors.BLACK};
            }}
        """)
        detail_edit.setMinimumHeight(60)
        body.addWidget(detail_edit)
        self._detail_edit = detail_edit

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        copy_btn = QPushButton("复制")
        copy_btn.setFixedSize(80, 32)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_200};
                color: {Colors.BLACK};
                border: none;
                border-radius: 4px;
                font-size: {Fonts.SIZE_MD}px;
                font-family: {Fonts.FAMILY_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_300};
            }}
        """)
        copy_btn.clicked.connect(self._on_copy)
        btn_layout.addWidget(copy_btn)

        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(80, 32)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WARNING};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {Fonts.SIZE_MD}px;
                font-family: {Fonts.FAMILY_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: #e65100;
            }}
        """)
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        body.addLayout(btn_layout)
        layout.addLayout(body)

    def _on_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self._detail_edit.toPlainText())

    @staticmethod
    def show_warning(parent, title: str, message: str):
        dialog = WarningDialog(title, message, parent)
        dialog.exec()