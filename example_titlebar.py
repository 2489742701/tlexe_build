"""自定义标题栏演示示例。

展示如何使用自定义标题栏组件。
"""

import sys
import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QComboBox,
    QMainWindow, QDockWidget
)

# 导入自定义标题栏组件
from ui.custom_titlebar import (
    TitleBarMode, CustomTitleBar, FramelessWindow,
    TitleBarPreview, TitleBarConfigDialog,
    create_frameless_window, show_titlebar_config
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoContent(QWidget):
    """演示内容部件。"""
    
    def __init__(self, title: str = "内容区域", parent=None):
        super().__init__(parent)
        self._setup_ui(title)
    
    def _setup_ui(self, title: str):
        """设置UI。"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 说明文本
        desc = QTextEdit()
        desc.setPlainText("这是一个无边框窗口的演示。\n\n"
                         "功能特点：\n"
                         "1. 支持拖动标题栏移动窗口\n"
                         "2. 双击标题栏最大化/还原\n"
                         "3. 可自定义标题栏显示模式\n"
                         "4. 带有阴影效果\n\n"
                         "试试拖动标题栏或双击它！")
        desc.setReadOnly(True)
        layout.addWidget(desc)


class MainDemoWindow(QMainWindow):
    """主演示窗口。"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自定义标题栏演示")
        self.setGeometry(100, 100, 800, 600)
        
        self._setup_ui()
        self._demo_windows = []  # 保持引用
    
    def _setup_ui(self):
        """设置UI。"""
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # 标题
        title = QLabel("自定义标题栏演示")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("点击下方按钮创建不同模式的窗口")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 完整模式
        full_btn = QPushButton("完整模式")
        full_btn.clicked.connect(lambda: self._create_window(TitleBarMode.FULL, "完整模式"))
        btn_layout.addWidget(full_btn)
        
        # 无顶栏
        none_btn = QPushButton("无顶栏")
        none_btn.clicked.connect(lambda: self._create_window(TitleBarMode.NONE, "无顶栏模式"))
        btn_layout.addWidget(none_btn)
        
        # 最小化+关闭
        min_close_btn = QPushButton("最小化+关闭")
        min_close_btn.clicked.connect(lambda: self._create_window(TitleBarMode.MIN_CLOSE, "最小化+关闭"))
        btn_layout.addWidget(min_close_btn)
        
        # 仅关闭
        close_only_btn = QPushButton("仅关闭")
        close_only_btn.clicked.connect(lambda: self._create_window(TitleBarMode.CLOSE_ONLY, "仅关闭"))
        btn_layout.addWidget(close_only_btn)
        
        layout.addLayout(btn_layout)
        
        # 第二行按钮
        btn_layout2 = QHBoxLayout()
        
        # 配置对话框
        config_btn = QPushButton("打开配置对话框（带预览）")
        config_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        config_btn.clicked.connect(self._show_config_dialog)
        btn_layout2.addWidget(config_btn)
        
        # 画布预览
        preview_btn = QPushButton("显示画布预览")
        preview_btn.clicked.connect(self._show_preview)
        btn_layout2.addWidget(preview_btn)
        
        layout.addLayout(btn_layout2)
        
        # 画布预览区域
        self._preview_dock = QDockWidget("画布预览", self)
        self._preview_widget = TitleBarPreview()
        self._preview_dock.setWidget(self._preview_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self._preview_dock)
        
        # 模式选择（控制预览）
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("预览模式:"))
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("完整模式", TitleBarMode.FULL)
        self._mode_combo.addItem("无顶栏", TitleBarMode.NONE)
        self._mode_combo.addItem("最小化+关闭", TitleBarMode.MIN_CLOSE)
        self._mode_combo.addItem("仅关闭", TitleBarMode.CLOSE_ONLY)
        self._mode_combo.currentIndexChanged.connect(self._on_preview_mode_changed)
        mode_layout.addWidget(self._mode_combo)
        
        layout.addLayout(mode_layout)
        layout.addStretch()
    
    def _create_window(self, mode: TitleBarMode, title: str):
        """创建演示窗口。"""
        content = DemoContent(f"模式: {title}")
        window = create_frameless_window(mode, title, content)
        window.setGeometry(200, 200, 500, 400)
        window.show()
        
        self._demo_windows.append(window)
        logger.info(f"创建窗口: {title} ({mode.name})")
    
    def _show_config_dialog(self):
        """显示配置对话框。"""
        dialog = show_titlebar_config(self)
        dialog.config_applied.connect(self._on_config_applied)
        self._demo_windows.append(dialog)
    
    def _on_config_applied(self, mode: TitleBarMode):
        """配置应用回调。"""
        logger.info(f"从对话框应用配置: {mode.name}")
        # 可以在这里应用到主窗口或其他窗口
    
    def _show_preview(self):
        """显示画布预览。"""
        self._preview_dock.show()
        self._preview_dock.raise_()
    
    def _on_preview_mode_changed(self, index: int):
        """预览模式改变。"""
        mode = self._mode_combo.currentData()
        self._preview_widget.set_mode(mode)


def main():
    """主函数。"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainDemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
