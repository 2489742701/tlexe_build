"""视频渲染器。

本模块包含视频组件的渲染逻辑。

## 修复说明 (2026-04-02)
【问题】渲染器工厂中缺少 Video 渲染器。

【解决方案】创建 VideoRenderer 类，处理视频组件的渲染。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPixmap, QFont
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel, VideoModel
from .component_renderer import ComponentRenderer


class VideoRenderer(ComponentRenderer):
    """视频渲染器。
    
    负责绘制视频组件的外观。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染视频组件。
        
        Args:
            painter: Qt 绘制器
            model: 视频数据模型
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
        
        # 尝试加载视频封面或显示占位符
        video_path = getattr(model, 'video_path', '')
        poster_image = getattr(model, 'poster_image', '')
        
        if poster_image:
            try:
                pixmap = QPixmap(poster_image)
                if not pixmap.isNull():
                    # 绘制封面图片
                    aspect_ratio = getattr(model, 'aspect_ratio', True)
                    if aspect_ratio:
                        scaled_pixmap = pixmap.scaled(
                            int(rect.width()), int(rect.height()),
                            Qt.AspectRatioMode.KeepAspectRatio
                        )
                        x = rect.x() + (rect.width() - scaled_pixmap.width()) / 2
                        y = rect.y() + (rect.height() - scaled_pixmap.height()) / 2
                        painter.drawPixmap(x, y, scaled_pixmap)
                    else:
                        scaled_pixmap = pixmap.scaled(
                            int(rect.width()), int(rect.height()),
                            Qt.AspectRatioMode.IgnoreAspectRatio
                        )
                        painter.drawPixmap(rect.topLeft(), scaled_pixmap)
                else:
                    self._draw_video_placeholder(painter, model, rect)
            except Exception:
                self._draw_video_placeholder(painter, model, rect)
        else:
            self._draw_video_placeholder(painter, model, rect)
        
        # 绘制边框
        if style.border_width > 0 or is_selected:
            if is_selected:
                pen = QPen(QColor("#87CEEB"), 2, Qt.PenStyle.DashLine)
            else:
                pen = QPen(QColor(style.border_color), style.border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 绘制播放按钮（如果有视频）
        if video_path:
            self._draw_play_button(painter, rect)
    
    def _draw_video_placeholder(self, painter: QPainter, model: ComponentModel, rect: QRectF):
        """绘制视频占位符。"""
        placeholder_text = getattr(model, 'placeholder_text', '点击选择视频')
        
        # 绘制占位符背景
        painter.setBrush(QBrush(QColor("#1a1a1a")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
        
        # 绘制视频图标
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 32)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "🎬")
        
        # 绘制占位符文本
        painter.setPen(QColor("#cccccc"))
        font = QFont("Arial", 10)
        painter.setFont(font)
        text_rect = QRectF(rect.x(), rect.y() + rect.height() - 30, rect.width(), 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, placeholder_text)
    
    def _draw_play_button(self, painter: QPainter, rect: QRectF):
        """绘制播放按钮。"""
        # 计算播放按钮位置（居中）
        button_size = min(rect.width(), rect.height()) * 0.2
        center_x = rect.x() + rect.width() / 2
        center_y = rect.y() + rect.height() / 2
        
        # 绘制半透明背景圆
        painter.setBrush(QBrush(QColor(0, 0, 0, 128)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            center_x - button_size / 2,
            center_y - button_size / 2,
            button_size,
            button_size
        )
        
        # 绘制播放三角形
        painter.setBrush(QBrush(QColor("#ffffff")))
        triangle_size = button_size * 0.4
        points = [
            (center_x - triangle_size / 3, center_y - triangle_size / 2),
            (center_x - triangle_size / 3, center_y + triangle_size / 2),
            (center_x + triangle_size * 2 / 3, center_y),
        ]
        from PySide6.QtGui import QPolygonF
        from PySide6.QtCore import QPointF
        
        polygon = QPolygonF([QPointF(p[0], p[1]) for p in points])
        painter.drawPolygon(polygon)
