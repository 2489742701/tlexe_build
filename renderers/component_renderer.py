"""组件渲染器基类。

本模块定义组件渲染器的抽象基类，所有具体渲染器都需要继承此类。

## 修复说明 (2026-04-02)
【问题】canvas.py 中的 ComponentGraphicsItem 直接包含所有组件类型的绘制逻辑，
导致类过于庞大且难以维护。

【解决方案】定义 ComponentRenderer 抽象基类，使用策略模式将绘制逻辑分离。

【设计模式】策略模式（Strategy Pattern）
- 定义算法族（渲染算法），分别封装起来，让它们可以互相替换
- 让算法的变化独立于使用算法的客户

## 修复说明 (2026-04-02 MCP架构审查)
【问题】ComponentGraphicsItem 仍包含绘制逻辑，与 RendererFactory 分工不清晰。
【解决方案】扩展 ComponentRenderer 接口，支持完整的绘制流程。
"""

from abc import ABC, abstractmethod
from typing import Optional
from PySide6.QtGui import QPainter, QFont, QFontMetrics, QBrush, QColor, QPen
from PySide6.QtCore import QRectF, Qt, QPointF

from models import ComponentModel


class ComponentRenderer(ABC):
    """组件渲染器抽象基类。
    
    所有组件渲染器都需要继承此类并实现 render 方法。
    
    ## 修复说明 (2026-04-02 MCP架构审查)
    扩展接口，支持完整的绘制流程，包括：
    - 背景绘制
    - 内容绘制
    - 边框绘制
    - 选中状态绘制
    
    【设计模式】策略模式（Strategy Pattern）
    - 将绘制逻辑完全从 ComponentGraphicsItem 中分离
    - 每个组件类型有自己的渲染策略
    """
    
    @abstractmethod
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染组件。
        
        Args:
            painter: Qt 绘制器
            model: 组件数据模型
            rect: 绘制区域
            is_selected: 是否被选中
            
        ## 修复说明 (2026-04-02)
        从 ComponentGraphicsItem.paint 方法中抽取，
        将绘制逻辑封装到独立的渲染器类中。
        """
        pass
    
    def render_background(self, painter: QPainter, model: ComponentModel, rect: QRectF):
        """渲染背景。
        
        Args:
            painter: Qt 绘制器
            model: 组件数据模型
            rect: 绘制区域
            
        ## 修复说明 (2026-04-02 MCP架构审查)
        提供默认背景绘制，子类可重写。
        """
        style = self._get_style(model)
        if style and style.background_color and style.background_color != "transparent":
            painter.setBrush(QBrush(QColor(style.background_color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
    
    def render_border(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染边框。
        
        Args:
            painter: Qt 绘制器
            model: 组件数据模型
            rect: 绘制区域
            is_selected: 是否被选中
            
        ## 修复说明 (2026-04-02 MCP架构审查)
        提供默认边框绘制，支持选中状态高亮。
        """
        style = self._get_style(model)
        if not style:
            return
        
        if is_selected:
            pen = QPen(QColor("#87CEEB"), style.border_width + 1, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(style.border_color), style.border_width)
        
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, style.border_radius, style.border_radius)
    
    def render_text(self, painter: QPainter, model: ComponentModel, rect: QRectF, 
                   text: Optional[str] = None, alignment: str = "center"):
        """渲染文本。
        
        Args:
            painter: Qt 绘制器
            model: 组件数据模型
            rect: 绘制区域
            text: 要渲染的文本，None 使用 model.text
            alignment: 对齐方式 ('left', 'center', 'right')
            
        ## 修复说明 (2026-04-02 MCP架构审查)
        提供通用文本渲染，支持样式设置。
        """
        display_text = text if text is not None else getattr(model, 'text', '')
        if not display_text:
            return
        
        style = self._get_style(model)
        if not style:
            return
        
        # 设置文本颜色
        painter.setPen(QColor(style.text_color))
        
        # 设置字体
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        painter.setFont(font)
        
        # 计算文本区域
        margin = 5
        text_rect = rect.adjusted(margin, margin, -margin, -margin)
        
        # 设置对齐方式
        if alignment == 'left':
            text_flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif alignment == 'right':
            text_flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        else:
            text_flags = Qt.AlignmentFlag.AlignCenter
        
        painter.drawText(text_rect, text_flags, display_text)
    
    def _get_style(self, model: ComponentModel):
        """获取组件样式。
        
        Args:
            model: 组件数据模型
            
        Returns:
            样式对象
        """
        return model.style if hasattr(model, 'style') else None
    
    def _apply_native_style(self, style) -> tuple:
        """应用原生样式。
        
        Args:
            style: 样式对象
            
        Returns:
            (bg_color, text_color, border_color, border_width, border_radius)
        """
        if style and getattr(style, 'use_native_style', False):
            return ("#f0f0f0", "#333333", "#999999", 1, 4)
        
        if style:
            return (
                style.background_color,
                style.text_color,
                style.border_color,
                style.border_width,
                style.border_radius
            )
        
        return ("#f0f0f0", "#333333", "#999999", 1, 5)


class DefaultRenderer(ComponentRenderer):
    """默认渲染器。
    
    用于未找到特定渲染器时的降级处理。
    
    ## 修复说明 (2026-04-02 MCP架构审查)
    提供默认渲染实现，避免渲染失败。
    """
    
    def render(self, painter: QPainter, model: ComponentModel, rect: QRectF, is_selected: bool = False):
        """渲染默认组件。"""
        self.render_background(painter, model, rect)
        self.render_text(painter, model, rect)
        self.render_border(painter, model, rect, is_selected)
