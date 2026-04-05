"""标签渲染器。

本模块包含标签组件的渲染逻辑。

## 修复说明 (2026-04-02)
【问题】canvas.py 中的 ComponentGraphicsItem._paint_label 方法包含标签绘制逻辑。

【解决方案】将标签绘制逻辑抽取到 LabelRenderer 类中。

## 修复说明 (2026-04-02)
【问题】Label 不支持自动换行和自动调整大小。

【解决方案】
1. 添加 word_wrap 支持：使用文本绘制标志
2. 添加 auto_size 支持：计算文本大小并更新模型
"""

from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont, QTextOption, QFontMetrics
from PySide6.QtCore import QRectF, Qt

from models import ComponentModel, LabelModel
from .component_renderer import ComponentRenderer


class LabelRenderer(ComponentRenderer):
    """标签渲染器。
    
    负责绘制标签组件的外观。
    
    ## 修复说明 (2026-04-02)
    从 ComponentGraphicsItem 中抽取标签绘制逻辑。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染标签组件。
        
        Args:
            painter: Qt 绘制器
            model: 标签数据模型
            rect: 绘制区域
            is_selected: 是否被选中
        """
        style = self.get_style(model)
        if not style:
            return
        
        # 绘制背景（仅当不是透明时）
        if style.background_color != "transparent":
            brush = QBrush(QColor(style.background_color))
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 绘制边框（如果设置了边框宽度）
        if style.border_width > 0:
            if is_selected:
                pen = QPen(QColor("#87CEEB"), style.border_width + 1, Qt.PenStyle.DashLine)
            else:
                pen = QPen(QColor(style.border_color), style.border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
        
        # 绘制文字
        painter.setPen(QColor(style.text_color))
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        painter.setFont(font)
        
        text = model.text if hasattr(model, 'text') else "标签"
        
        # 获取对齐方式
        alignment = Qt.AlignmentFlag.AlignCenter
        if hasattr(model, 'alignment'):
            align_map = {
                'left': Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                'center': Qt.AlignmentFlag.AlignCenter,
                'right': Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            }
            alignment = align_map.get(model.alignment, Qt.AlignmentFlag.AlignCenter)
        
        # 处理自动调整大小
        if hasattr(model, 'auto_size') and model.auto_size:
            fm = QFontMetrics(font)
            text_rect = fm.boundingRect(0, 0, 10000, 10000, 
                                        Qt.TextFlag.TextWordWrap if (hasattr(model, 'word_wrap') and model.word_wrap) else 0,
                                        text)
            # 更新模型大小
            model.width = text_rect.width() + 10  # 加一点边距
            model.height = text_rect.height() + 6
        
        # 处理自动换行
        text_flags = alignment
        if hasattr(model, 'word_wrap') and model.word_wrap:
            text_flags |= Qt.TextFlag.TextWordWrap
        
        painter.drawText(rect, text_flags, text)
