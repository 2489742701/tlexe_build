"""图片轮播渲染器。

本模块包含图片轮播组件的渲染逻辑。

图片轮播组件显示多张图片，支持自动轮播和手动切换。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPixmap, QFont, QPainterPath
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer


class ImageCarouselRenderer(ComponentRenderer):
    """图片轮播渲染器。
    
    负责绘制图片轮播组件的外观。
    显示当前图片和指示器。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染图片轮播组件。
        
        Args:
            painter: Qt 绘制器
            model: 图片轮播数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 获取图片列表和当前索引
        images = getattr(model, 'images', [])
        current_index = getattr(model, 'current_index', 0)
        
        if images and 0 <= current_index < len(images):
            # 显示当前图片
            image_path = images[current_index]
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # 缩放图片以适应区域
                    scaled_pixmap = pixmap.scaled(
                        int(rect.width()), int(rect.height()),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    painter.drawPixmap(rect.topLeft(), scaled_pixmap)
                else:
                    self._draw_placeholder(painter, model, rect, f"图片 {current_index + 1}/{len(images)}")
            except Exception:
                self._draw_placeholder(painter, model, rect, "图片加载错误")
        else:
            # 没有图片，显示占位符
            self._draw_placeholder(painter, model, rect, "图片轮播")
        
        # 绘制指示器
        if images:
            self._draw_indicators(painter, rect, len(images), current_index)
        
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
        painter.setBrush(QBrush(QColor("#f5f5f5")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
        
        # 绘制图标
        painter.setPen(QColor("#999999"))
        font = QFont("Arial", 24)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "🎞")
        
        # 绘制文本
        painter.setPen(QColor("#666666"))
        font = QFont("Arial", 10)
        painter.setFont(font)
        text_rect = QRectF(rect.x(), rect.y() + rect.height() - 30, rect.width(), 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def _draw_indicators(self, painter: QPainter, rect: QRectF, total: int, current: int):
        """绘制指示器。
        
        Args:
            painter: Qt 绘制器
            rect: 绘制区域
            total: 总图片数
            current: 当前索引
        """
        if total <= 1:
            return
        
        # 指示器参数
        indicator_size = 8
        spacing = 12
        total_width = total * indicator_size + (total - 1) * (spacing - indicator_size)
        start_x = rect.x() + (rect.width() - total_width) / 2
        y = rect.y() + rect.height() - 20
        
        for i in range(total):
            x = start_x + i * spacing
            
            if i == current:
                # 当前指示器
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.setPen(QPen(QColor("#333333"), 1))
            else:
                # 其他指示器
                painter.setBrush(QBrush(QColor("#333333")))
                painter.setPen(QPen(QColor("#FFFFFF"), 1))
            
            painter.drawEllipse(QRectF(x, y, indicator_size, indicator_size))
