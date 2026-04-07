"""测试图标显示效果。

创建一个简单的窗口来展示所有生成的图标。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QGridLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QSize

from utils.icon_manager import IconManager


class IconTestWindow(QMainWindow):
    """图标测试窗口。"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("黑白图标测试 - UI快速开发工具")
        self.setMinimumSize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        """初始化UI。"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        title = QLabel("黑白UI图标展示")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        icons = IconManager.get_available_icons()
        icons.sort()
        
        row = 0
        col = 0
        max_cols = 4
        
        for icon_name in icons:
            icon_widget = self._create_icon_widget(icon_name)
            grid_layout.addWidget(icon_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        info_label = QLabel(
            "提示：这些图标已替换组件面板中的文本图标\n"
            "图标格式：SVG矢量图标（可缩放，黑白风格）"
        )
        info_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 10px;
                background-color: #f5f5f5;
                border-radius: 5px;
            }
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
    
    def _create_icon_widget(self, icon_name: str) -> QWidget:
        """创建单个图标展示组件。
        
        Args:
            icon_name: 图标名称
            
        Returns:
            包含图标和标签的组件
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #f0f4ff;
                border-color: #4a90d9;
            }
        """)
        
        icon = IconManager.get_icon(icon_name, use_svg=True)
        btn = QPushButton()
        btn.setIcon(icon)
        btn.setIconSize(QSize(48, 48))
        btn.setFixedSize(80, 80)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(74, 144, 217, 0.1);
                border-radius: 5px;
            }
        """)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(icon_name)
        label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #555;
                background-color: transparent;
            }
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return widget


def main():
    """主函数。"""
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    window = IconTestWindow()
    window.show()
    
    print("=" * 60)
    print("图标测试窗口已启动")
    print("=" * 60)
    print()
    print("可用图标列表:")
    for icon_name in sorted(IconManager.get_available_icons()):
        print(f"  - {icon_name}")
    print()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
