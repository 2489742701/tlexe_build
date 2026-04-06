"""图片按钮渲染器。

本模块包含图片按钮组件的渲染逻辑。

图片按钮使用图片作为按钮外观，支持不同状态显示不同图片。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPixmap
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer


class ImageButtonRenderer(ComponentRenderer):
    """图片按钮渲染器。
    
    负责绘制图片按钮组件的外观。
    支持默认、悬停、按下三种状态的图片显示。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染图片按钮组件。
        
        Args:
            painter: Qt 绘制器
            model: 图片按钮数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 获取图片路径
        image_path = getattr(model, 'image_path', '')
        
        if image_path:
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # 缩放图片以适应按钮区域
                    scaled_pixmap = pixmap.scaled(
                        int(rect.width()), int(rect.height()),
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    painter.drawPixmap(rect.topLeft(), scaled_pixmap)
                else:
                    self._draw_placeholder(painter, model, rect, "图片加载失败")
            except Exception:
                self._draw_placeholder(painter, model, rect, "图片加载错误")
        else:
            # 没有图片路径，显示占位符
            self._draw_placeholder(painter, model, rect, "图片按钮")
        
        # 绘制选中边框
        if is_selected:
            pen = QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)
    
    def _draw_placeholder(self, painter: QPainter, model: ComponentModel, rect: QRectF, text: str):
        """绘制占位符。
        
        Args:
            painter: Qt 绘制器
            model: 组件模型
            rect: 绘制区域
            text: 占位符文本
        """
        # 绘制背景
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
        
        # 绘制边框
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)
        
        # 绘制图标
        painter.setPen(QColor("#999999"))
        from PySide6.QtGui import QFont
        font = QFont("Arial", 16)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "[IB]")
        
        # 绘制文本
        painter.setPen(QColor("#666666"))
        font = QFont("Arial", 9)
        painter.setFont(font)
        text_rect = QRectF(rect.x(), rect.y() + rect.height() - 20, rect.width(), 15)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
