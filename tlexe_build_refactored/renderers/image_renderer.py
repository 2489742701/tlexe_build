"""图片渲染器。

本模块包含图片组件的渲染逻辑。

"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPixmap, QFont
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel, ImageModel
from .component_renderer import ComponentRenderer

class ImageRenderer(ComponentRenderer):
    """图片渲染器。
    
    负责绘制图片组件的外观。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染图片组件。
        
        Args:
            painter: Qt 绘制器
            model: 图片数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 绘制背景
        if style.background_color != "transparent":
            brush = QBrush(QColor(style.background_color))
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 尝试加载图片
        image_path = getattr(model, 'image_path', '')
        if image_path:
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # 获取缩放模式
                    scale_mode = getattr(model, 'scale_mode', 'fit')
                    aspect_ratio = getattr(model, 'aspect_ratio', True)
                    
                    # 计算绘制区域
                    if scale_mode == 'stretch':
                        # 拉伸填充
                        target_rect = rect
                    elif scale_mode == 'center':
                        # 居中显示
                        scaled_pixmap = pixmap.scaled(
                            int(rect.width()), int(rect.height()),
                            Qt.AspectRatioMode.KeepAspectRatio
                        )
                        x = rect.x() + (rect.width() - scaled_pixmap.width()) / 2
                        y = rect.y() + (rect.height() - scaled_pixmap.height()) / 2
                        target_rect = QRectF(x, y, scaled_pixmap.width(), scaled_pixmap.height())
                        painter.drawPixmap(target_rect.topLeft(), scaled_pixmap)
                        return
                    else:  # fill, fit, tile
                        # 保持宽高比或填充
                        if aspect_ratio:
                            scaled_pixmap = pixmap.scaled(
                                int(rect.width()), int(rect.height()),
                                Qt.AspectRatioMode.KeepAspectRatio
                            )
                            x = rect.x() + (rect.width() - scaled_pixmap.width()) / 2
                            y = rect.y() + (rect.height() - scaled_pixmap.height()) / 2
                            target_rect = QRectF(x, y, scaled_pixmap.width(), scaled_pixmap.height())
                        else:
                            scaled_pixmap = pixmap.scaled(
                                int(rect.width()), int(rect.height()),
                                Qt.AspectRatioMode.IgnoreAspectRatio
                            )
                            target_rect = rect
                        
                        painter.drawPixmap(target_rect.topLeft(), scaled_pixmap)
            except Exception:
                self._draw_placeholder(painter, model, rect)
        else:
            # 没有图片路径，显示占位符
            self._draw_placeholder(painter, model, rect)
        
        # 绘制边框
        border_radius = getattr(model, 'border_radius', 0)
        if border_radius > 0 or is_selected:
            if is_selected:
                pen = QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine)
            else:
                pen = QPen(QColor(style.border_color), style.border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, border_radius or style.border_radius, border_radius or style.border_radius)
    
    def _draw_placeholder(self, painter: QPainter, model: ComponentModel, rect: QRectF):
        """绘制占位符。"""
        placeholder_text = getattr(model, 'placeholder_text', '[Click to select image]')
        
        painter.setBrush(QBrush(QColor("#f5f5f5")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
        
        painter.setPen(QColor("#999999"))
        font = QFont("Arial", 24)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "[IMG]")
        
        painter.setPen(QColor("#666666"))
        font = QFont("Arial", 10)
        painter.setFont(font)
        text_rect = QRectF(rect.x(), rect.y() + rect.height() - 30, rect.width(), 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, placeholder_text)
