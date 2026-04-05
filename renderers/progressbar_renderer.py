"""进度条渲染器。

本模块包含进度条组件的渲染逻辑。

## 修复说明 (2026-04-02)
【问题】canvas.py 中的 ComponentGraphicsItem._paint_progressbar 方法包含进度条绘制逻辑。

【解决方案】将进度条绘制逻辑抽取到 ProgressBarRenderer 类中。
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel
from .component_renderer import ComponentRenderer


class ProgressBarRenderer(ComponentRenderer):
    """进度条渲染器。
    
    负责绘制进度条组件的外观。
    
    ## 修复说明 (2026-04-02)
    从 ComponentGraphicsItem 中抽取进度条绘制逻辑。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染进度条组件。
        
        Args:
            painter: Qt 绘制器
            model: 进度条数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 绘制背景
        painter.setPen(Qt.PenStyle.NoPen)
        bg_color = style.background_color if style.background_color != "transparent" else "#e0e0e0"
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 获取进度值
        value = getattr(model, 'value', 0)
        progress_width = rect.width() * value / 100
        progress_rect = QRectF(0, 0, progress_width, rect.height())
        
        # 绘制进度
        painter.setBrush(QBrush(QColor("#0078d7")))
        painter.setClipRect(rect)
        painter.drawRoundedRect(progress_rect, style.border_radius, style.border_radius)
        painter.setClipping(False)
        
        # 绘制边框
        border_pen = QPen(QColor(style.border_color), style.border_width)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 绘制文字
        show_text = getattr(model, 'show_text', True)
        if show_text:
            text_position = getattr(model, 'text_position', 'center')
            font = QFont(style.font_family, style.font_size)
            font.setBold(True)
            painter.setFont(font)
            text = f"{value}%"
            
            if text_position == 'left':
                painter.setPen(QColor("#333333"))
                text_rect = QRectF(5, 0, rect.width() - 10, rect.height())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            elif text_position == 'right':
                painter.setPen(QColor("#333333"))
                text_rect = QRectF(5, 0, rect.width() - 10, rect.height())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, text)
            elif text_position == 'follow':
                if value > 10:
                    text_x = max(5, progress_width - 40)
                    text_rect = QRectF(text_x, 0, 60, rect.height())
                    painter.setPen(QColor("#ffffff"))
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
                else:
                    painter.setPen(QColor("#333333"))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            else:
                painter.setPen(QColor("#ffffff") if value > 50 else QColor("#333333"))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
