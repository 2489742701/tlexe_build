"""自定义标题栏组件。

支持多种模式：
1. 完整模式：包含图标、标题、最小化、最大化、关闭
2. 无顶栏：完全隐藏标题栏（无边框窗口）
3. 只有最小化和关闭
4. 只有关闭
"""

import logging
from enum import Enum, auto
from typing import Optional, Callable

from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QApplication
)
from PySide6.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QFont

logger = logging.getLogger(__name__)


class TitleBarMode(Enum):
    """标题栏模式枚举。"""
    FULL = auto()           # 完整模式（图标+标题+最小化+最大化+关闭）
    NONE = auto()           # 无顶栏（无边框）
    MIN_CLOSE = auto()      # 只有最小化和关闭
    CLOSE_ONLY = auto()     # 只有关闭
    CUSTOM = auto()         # 自定义模式


class TitleBarButton(QPushButton):
    """标题栏按钮基类。"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(30, 30)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #333;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)


class CloseButton(TitleBarButton):
    """关闭按钮。"""
    
    def __init__(self, parent=None):
        super().__init__("×", parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #333;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
            QPushButton:pressed {
                background-color: #f1707a;
            }
        """)


class MinimizeButton(TitleBarButton):
    """最小化按钮。"""
    
    def __init__(self, parent=None):
        super().__init__("−", parent)


class MaximizeButton(TitleBarButton):
    """最大化/还原按钮。"""
    
    def __init__(self, parent=None):
        super().__init__("□", parent)
        self._is_maximized = False
    
    def set_maximized(self, maximized: bool):
        """设置最大化状态。"""
        self._is_maximized = maximized
        self.setText("❐" if maximized else "□")


class CustomTitleBar(QFrame):
    """自定义标题栏。
    
    【功能】
    - 支持多种显示模式
    - 支持窗口拖动
    - 支持双击最大化/还原
    - 可自定义样式
    
    【信号】
    - minimize_clicked: 最小化按钮点击
    - maximize_clicked: 最大化按钮点击
    - close_clicked: 关闭按钮点击
    - double_clicked: 双击标题栏
    """
    
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    double_clicked = Signal()
    
    def __init__(self, 
                 mode: TitleBarMode = TitleBarMode.FULL,
                 title: str = "",
                 parent=None):
        super().__init__(parent)
        self._mode = mode
        self._title_text = title
        self._drag_pos: Optional[QPoint] = None
        self._is_maximized = False
        
        self._setup_ui()
        self._apply_mode()
    
    def _setup_ui(self):
        """设置UI。"""
        self.setFixedHeight(35)
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #f5f5f5;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        
        # 窗口图标（可选）
        self._icon_label = QLabel("◆")
        self._icon_label.setFixedSize(20, 20)
        self._icon_label.setStyleSheet("color: #2196F3; font-size: 12px;")
        layout.addWidget(self._icon_label)
        
        # 标题
        self._title_label = QLabel(self._title_text)
        self._title_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 13px;
                padding-left: 5px;
            }
        """)
        layout.addWidget(self._title_label)
        
        # 弹性空间
        layout.addStretch()
        
        # 按钮容器
        self._button_layout = QHBoxLayout()
        self._button_layout.setSpacing(0)
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 最小化按钮
        self._min_btn = MinimizeButton()
        self._min_btn.clicked.connect(self.minimize_clicked.emit)
        self._button_layout.addWidget(self._min_btn)
        
        # 最大化按钮
        self._max_btn = MaximizeButton()
        self._max_btn.clicked.connect(self.maximize_clicked.emit)
        self._button_layout.addWidget(self._max_btn)
        
        # 关闭按钮
        self._close_btn = CloseButton()
        self._close_btn.clicked.connect(self.close_clicked.emit)
        self._button_layout.addWidget(self._close_btn)
        
        layout.addLayout(self._button_layout)
    
    def _apply_mode(self):
        """应用当前模式。"""
        if self._mode == TitleBarMode.FULL:
            # 完整模式：显示所有
            self._icon_label.setVisible(True)
            self._title_label.setVisible(True)
            self._min_btn.setVisible(True)
            self._max_btn.setVisible(True)
            self._close_btn.setVisible(True)
            
        elif self._mode == TitleBarMode.NONE:
            # 无顶栏：隐藏整个标题栏
            self.setVisible(False)
            
        elif self._mode == TitleBarMode.MIN_CLOSE:
            # 只有最小化和关闭
            self._icon_label.setVisible(False)
            self._title_label.setVisible(False)
            self._min_btn.setVisible(True)
            self._max_btn.setVisible(False)
            self._close_btn.setVisible(True)
            
        elif self._mode == TitleBarMode.CLOSE_ONLY:
            # 只有关闭
            self._icon_label.setVisible(False)
            self._title_label.setVisible(False)
            self._min_btn.setVisible(False)
            self._max_btn.setVisible(False)
            self._close_btn.setVisible(True)
            
        elif self._mode == TitleBarMode.CUSTOM:
            # 自定义模式：默认显示所有，可通过方法控制
            pass
    
    def set_mode(self, mode: TitleBarMode):
        """设置标题栏模式。
        
        Args:
            mode: 新的模式
        """
        self._mode = mode
        self._apply_mode()
        logger.info(f"标题栏模式切换为: {mode.name}")
    
    def get_mode(self) -> TitleBarMode:
        """获取当前模式。"""
        return self._mode
    
    def set_title(self, title: str):
        """设置标题文本。"""
        self._title_text = title
        self._title_label.setText(title)
    
    def set_maximized(self, maximized: bool):
        """设置最大化状态。"""
        self._is_maximized = maximized
        self._max_btn.set_maximized(maximized)
    
    def show_button(self, button_name: str, show: bool = True):
        """显示/隐藏指定按钮（自定义模式用）。
        
        Args:
            button_name: 按钮名称 (min/max/close)
            show: 是否显示
        """
        if button_name == "min":
            self._min_btn.setVisible(show)
        elif button_name == "max":
            self._max_btn.setVisible(show)
        elif button_name == "close":
            self._close_btn.setVisible(show)
        elif button_name == "icon":
            self._icon_label.setVisible(show)
        elif button_name == "title":
            self._title_label.setVisible(show)
    
    # 鼠标事件处理（支持拖动）
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            if not self._is_maximized:
                self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        event.accept()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()
            event.accept()


class FramelessWindow(QWidget):
    """无边框窗口（使用自定义标题栏）。
    
    【使用方式】
    window = FramelessWindow(TitleBarMode.FULL, "窗口标题")
    window.set_content_widget(your_widget)
    window.show()
    """
    
    def __init__(self, 
                 mode: TitleBarMode = TitleBarMode.FULL,
                 title: str = "",
                 parent=None):
        super().__init__(parent)
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._setup_ui(mode, title)
        self._connect_signals()
    
    def _setup_ui(self, mode: TitleBarMode, title: str):
        """设置UI。"""
        # 主布局
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(10, 10, 10, 10)
        self._main_layout.setSpacing(0)
        
        # 容器（带阴影效果）
        self._container = QFrame()
        self._container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self._container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 标题栏
        self._title_bar = CustomTitleBar(mode, title, self._container)
        container_layout.addWidget(self._title_bar)
        
        # 内容区域
        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self._content_widget, 1)
        
        self._main_layout.addWidget(self._container)
    
    def _connect_signals(self):
        """连接信号。"""
        self._title_bar.minimize_clicked.connect(self.showMinimized)
        self._title_bar.maximize_clicked.connect(self._toggle_maximize)
        self._title_bar.close_clicked.connect(self.close)
        self._title_bar.double_clicked.connect(self._toggle_maximize)
    
    def _toggle_maximize(self):
        """切换最大化/还原。"""
        if self.isMaximized():
            self.showNormal()
            self._title_bar.set_maximized(False)
        else:
            self.showMaximized()
            self._title_bar.set_maximized(True)
    
    def set_content_widget(self, widget: QWidget):
        """设置内容部件。
        
        Args:
            widget: 要显示的内容部件
        """
        # 清除旧内容
        layout = self._content_widget.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新内容
        layout.addWidget(widget)
    
    def get_title_bar(self) -> CustomTitleBar:
        """获取标题栏（用于自定义）。"""
        return self._title_bar
    
    def set_title_bar_mode(self, mode: TitleBarMode):
        """设置标题栏模式。"""
        self._title_bar.set_mode(mode)
    
    def set_window_title(self, title: str):
        """设置窗口标题。"""
        self._title_bar.set_title(title)


# ============================================================================
# 画布预览组件
# ============================================================================

class TitleBarPreview(QWidget):
    """标题栏预览组件（用于画布显示）。
    
    在画布中显示标题栏的预览效果。
    """
    
    mode_changed = Signal(TitleBarMode)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mode = TitleBarMode.FULL
        self._preview_scale = 0.6  # 预览缩放比例
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI。"""
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #ccc;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 预览标签
        self._preview_label = QLabel("标题栏预览")
        self._preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._preview_label)
        
        # 创建预览标题栏
        self._preview_bar = CustomTitleBar(TitleBarMode.FULL, "预览窗口", self)
        self._preview_bar.setFixedSize(int(300 * self._preview_scale), int(35 * self._preview_scale))
        
        # 禁用按钮功能
        self._preview_bar._min_btn.setEnabled(False)
        self._preview_bar._max_btn.setEnabled(False)
        self._preview_bar._close_btn.setEnabled(False)
        
        layout.addWidget(self._preview_bar, alignment=Qt.AlignCenter)
        
        # 模拟窗口内容区域
        self._content_preview = QFrame()
        self._content_preview.setFixedSize(int(300 * self._preview_scale), int(150 * self._preview_scale))
        self._content_preview.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-top: none;
            }
        """)
        layout.addWidget(self._content_preview, alignment=Qt.AlignCenter)
        
        layout.addStretch()
    
    def set_mode(self, mode: TitleBarMode):
        """设置预览模式。
        
        Args:
            mode: 标题栏模式
        """
        self._current_mode = mode
        self._preview_bar.set_mode(mode)
        
        # 更新内容区域显示
        if mode == TitleBarMode.NONE:
            self._content_preview.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
            """)
        else:
            self._content_preview.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-top: none;
                }
            """)
        
        self.mode_changed.emit(mode)
        self.update()
    
    def get_mode(self) -> TitleBarMode:
        """获取当前模式。"""
        return self._current_mode
    
    def paintEvent(self, event: QPaintEvent):
        """绘制预览背景。"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制模式标签
        painter.setPen(QPen(QColor(100, 100, 100)))
        painter.setFont(QFont("Microsoft YaHei", 10))
        
        mode_text = f"模式: {self._current_mode.name}"
        painter.drawText(self.rect().adjusted(10, 10, -10, -10), 
                        Qt.AlignTop | Qt.AlignLeft, mode_text)


class TitleBarConfigDialog(QWidget):
    """标题栏配置对话框。
    
    提供UI来配置标题栏模式，并实时预览。
    """
    
    config_applied = Signal(TitleBarMode)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("标题栏配置")
        self.setMinimumSize(500, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI。"""
        from PySide6.QtWidgets import QRadioButton, QButtonGroup, QGroupBox
        
        layout = QHBoxLayout(self)
        
        # 左侧：配置选项
        left_panel = QGroupBox("标题栏模式")
        left_layout = QVBoxLayout(left_panel)
        
        self._button_group = QButtonGroup(self)
        
        modes = [
            (TitleBarMode.FULL, "完整模式", "图标 + 标题 + 最小化 + 最大化 + 关闭"),
            (TitleBarMode.NONE, "无顶栏", "完全隐藏标题栏"),
            (TitleBarMode.MIN_CLOSE, "最小化+关闭", "只有最小化和关闭按钮"),
            (TitleBarMode.CLOSE_ONLY, "仅关闭", "只有关闭按钮"),
        ]
        
        for mode, title, desc in modes:
            radio = QRadioButton(f"{title}\n  {desc}")
            radio.setProperty("mode", mode)
            self._button_group.addButton(radio)
            left_layout.addWidget(radio)
            
            if mode == TitleBarMode.FULL:
                radio.setChecked(True)
        
        left_layout.addStretch()
        
        # 应用按钮
        apply_btn = QPushButton("应用配置")
        apply_btn.clicked.connect(self._on_apply)
        left_layout.addWidget(apply_btn)
        
        layout.addWidget(left_panel)
        
        # 右侧：预览
        right_panel = QGroupBox("实时预览")
        right_layout = QVBoxLayout(right_panel)
        
        self._preview = TitleBarPreview()
        right_layout.addWidget(self._preview, alignment=Qt.AlignCenter)
        
        layout.addWidget(right_panel)
        
        # 连接信号
        self._button_group.buttonClicked.connect(self._on_mode_changed)
    
    def _on_mode_changed(self, button):
        """模式改变。"""
        mode = button.property("mode")
        self._preview.set_mode(mode)
    
    def _on_apply(self):
        """应用配置。"""
        mode = self._preview.get_mode()
        self.config_applied.emit(mode)
        logger.info(f"应用标题栏配置: {mode.name}")


# ============================================================================
# 便捷函数
# ============================================================================

def create_frameless_window(
    mode: TitleBarMode = TitleBarMode.FULL,
    title: str = "",
    content: Optional[QWidget] = None
) -> FramelessWindow:
    """创建无边框窗口。
    
    Args:
        mode: 标题栏模式
        title: 窗口标题
        content: 内容部件
        
    Returns:
        无边框窗口实例
    """
    window = FramelessWindow(mode, title)
    if content:
        window.set_content_widget(content)
    return window


def show_titlebar_config(parent=None) -> TitleBarConfigDialog:
    """显示标题栏配置对话框。
    
    Args:
        parent: 父窗口
        
    Returns:
        配置对话框实例
    """
    dialog = TitleBarConfigDialog(parent)
    dialog.show()
    return dialog
