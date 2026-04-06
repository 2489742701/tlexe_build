"""启动画面（Splash Screen）模块。

本模块提供应用程序启动时的加载界面，显示初始化进度和状态信息。

特性：
- 无边框窗口，居中显示
- 支持加载状态文字更新
- 支持进度条显示
- 优雅的淡入淡出动画效果
- 可选的加载动画（旋转圆圈）
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup,
    Property, QParallelAnimationGroup
)
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath


class SpinnerWidget(QWidget):
    """旋转加载动画组件。
    
    显示一个旋转的圆圈动画，表示正在加载中。
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._color = QColor("#1a56db")
        self.setFixedSize(40, 40)
        
        # 创建旋转动画
        self._animation = QPropertyAnimation(self, b"angle")
        self._animation.setDuration(1000)
        self._animation.setStartValue(0)
        self._animation.setEndValue(360)
        self._animation.setLoopCount(-1)  # 无限循环
        self._animation.setEasingCurve(QEasingCurve.Type.Linear)
        
    def start(self):
        """开始动画。"""
        self._animation.start()
        
    def stop(self):
        """停止动画。"""
        self._animation.stop()
        self._angle = 0
        self.update()
        
    def get_angle(self):
        """获取当前角度。"""
        return self._angle
        
    def set_angle(self, angle):
        """设置当前角度。"""
        self._angle = angle
        self.update()
        
    angle = Property(int, get_angle, set_angle)
        
    def paintEvent(self, event):
        """绘制旋转圆圈。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景圆
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 4
        
        # 绘制灰色背景圆
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(230, 230, 230)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 绘制旋转的弧线
        pen = QPen(self._color, 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # 绘制 270 度的弧线
        rect = center_x - radius + 4, center_y - radius + 4, (radius - 4) * 2, (radius - 4) * 2
        start_angle = self._angle * 16  # Qt 使用 1/16 度为单位
        span_angle = 270 * 16
        painter.drawArc(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]), start_angle, span_angle)


class SplashWindow(QWidget):
    """启动画面窗口。
    
    显示应用程序加载进度和状态信息。
    
    Signals:
        无信号，通过方法调用更新状态
        
    使用方式:
        splash = SplashWindow()
        splash.show()
        splash.update_status("正在初始化...", 0)
        # ... 执行初始化步骤
        splash.update_status("正在加载组件...", 50)
        # ... 完成初始化
        splash.finish()  # 淡出并关闭
    """
    
    def __init__(self, parent=None):
        """初始化启动画面。
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 窗口属性设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 280)
        
        # 初始化 UI
        self._init_ui()
        
        # 居中显示
        self._center_on_screen()
        
        # 动画相关
        self._fade_animation = None
        self._opacity = 1.0
        
    def _init_ui(self):
        """初始化用户界面。"""
        # 主容器（带圆角和阴影效果）
        main_container = QFrame()
        main_container.setObjectName("splashContainer")
        main_container.setStyleSheet("""
            #splashContainer {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # 主布局
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(main_container)
        
        # 容器内部布局
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 顶部：应用名称和版本
        header_layout = QHBoxLayout()
        
        # 应用图标/Logo区域
        logo_label = QLabel()
        logo_label.setFixedSize(48, 48)
        logo_label.setStyleSheet("""
            background-color: #1a56db;
            border-radius: 10px;
        """)
        header_layout.addWidget(logo_label)
        
        # 应用名称
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        app_name = QLabel("UI快速开发工具")
        app_name.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        app_name.setStyleSheet("color: #333333; background: transparent;")
        title_layout.addWidget(app_name)
        
        version_label = QLabel("v1.0.0")
        version_label.setFont(QFont("Microsoft YaHei", 10))
        version_label.setStyleSheet("color: #999999; background: transparent;")
        title_layout.addWidget(version_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # 旋转动画
        self._spinner = SpinnerWidget()
        self._spinner.start()
        header_layout.addWidget(self._spinner)
        
        layout.addLayout(header_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e0e0e0; border: none; max-height: 1px;")
        layout.addWidget(separator)
        
        # 状态文字
        self._status_label = QLabel("正在初始化...")
        self._status_label.setFont(QFont("Microsoft YaHei", 11))
        self._status_label.setStyleSheet("color: #666666; background: transparent;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)
        
        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #1a56db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self._progress_bar)
        
        # 底部提示
        footer_label = QLabel("首次启动可能需要较长时间")
        footer_label.setFont(QFont("Microsoft YaHei", 9))
        footer_label.setStyleSheet("color: #aaaaaa; background: transparent;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)
        
    def _center_on_screen(self):
        """将窗口居中显示在屏幕上。"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
            
    def update_status(self, text: str, progress: int = None):
        """更新加载状态。
        
        Args:
            text: 状态文字
            progress: 进度值（0-100），None 表示不更新进度条
        """
        self._status_label.setText(text)
        if progress is not None:
            self._progress_bar.setValue(progress)
        # 强制刷新界面
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
    def get_opacity(self):
        """获取窗口透明度。"""
        return self._opacity
        
    def set_opacity(self, opacity):
        """设置窗口透明度。"""
        self._opacity = opacity
        self.setWindowOpacity(opacity)
        
    opacity = Property(float, get_opacity, set_opacity)
        
    def show_with_fade(self):
        """显示窗口（带淡入效果）。"""
        self.setWindowOpacity(0)
        self.show()
        
        self._fade_animation = QPropertyAnimation(self, b"opacity")
        self._fade_animation.setDuration(300)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._fade_animation.start()
        
    def finish(self, callback=None):
        """完成加载，淡出并关闭窗口。
        
        Args:
            callback: 关闭后的回调函数
        """
        self._spinner.stop()
        
        self._fade_animation = QPropertyAnimation(self, b"opacity")
        self._fade_animation.setDuration(400)
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        if callback:
            self._fade_animation.finished.connect(callback)
        self._fade_animation.finished.connect(self.close)
        self._fade_animation.start()
        
    def showEvent(self, event):
        """窗口显示事件。"""
        super().showEvent(event)
        # 确保窗口在最前面
        self.raise_()
        self.activateWindow()
