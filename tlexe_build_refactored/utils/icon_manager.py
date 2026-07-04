"""图标管理模块。

本模块提供黑白UI图标的生成和管理功能。
支持SVG图标和Unicode符号图标。

## 图标类型
- 功能类：按钮、复选框、下拉框、进度条等
- 媒体类：图片、视频、轮播等
- 容器类：容器
- 输入类：输入框
- 显示类：文本标签

## 使用方法
```python
from utils.icon_manager import IconManager

# 获取图标
icon = IconManager.get_icon("button")
pixmap = IconManager.get_pixmap("button", size=32)

# 在按钮上使用
button.setIcon(icon)
```
"""

import os
from typing import Dict, Optional
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QFontMetrics
from PySide6.QtCore import Qt, QSize, QRect, QByteArray
from PySide6.QtSvg import QSvgRenderer

SVG_ICONS: Dict[str, str] = {
    "button": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="8" width="18" height="8" rx="2"/>
    </svg>''',
    
    "checkbox": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="4" y="4" width="16" height="16" rx="2"/>
        <path d="M8 12l3 3 5-6" stroke-width="2.5"/>
    </svg>''',
    
    "checkbox_unchecked": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="4" y="4" width="16" height="16" rx="2"/>
    </svg>''',
    
    "combobox": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="6" width="18" height="12" rx="2"/>
        <path d="M15 10l2 2 2-2"/>
    </svg>''',
    
    "progressbar": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="2" y="9" width="20" height="6" rx="1"/>
        <rect x="3" y="10" width="12" height="4" rx="0.5" fill="#333333"/>
    </svg>''',
    
    "hidden_button": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="8" width="18" height="8" rx="2" stroke-dasharray="3 2"/>
    </svg>''',
    
    "image_button": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="5" width="18" height="14" rx="2"/>
        <circle cx="8" cy="10" r="2" fill="#333333"/>
        <path d="M5 17l4-4 3 3 4-4 3 3"/>
    </svg>''',
    
    "image": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="5" width="18" height="14" rx="2"/>
        <circle cx="8" cy="10" r="2" fill="#333333"/>
        <path d="M5 17l4-4 3 3 4-4 3 3"/>
    </svg>''',
    
    "video": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="2" y="6" width="20" height="12" rx="2"/>
        <polygon points="10,9 10,15 16,12" fill="#333333"/>
    </svg>''',
    
    "image_carousel": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="4" y="6" width="16" height="12" rx="2"/>
        <circle cx="12" cy="19" r="1" fill="#333333"/>
        <path d="M7 19l-1 1M17 19l1 1"/>
    </svg>''',
    
    "container": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="2" y="4" width="20" height="16" rx="2"/>
        <line x1="2" y1="8" x2="22" y2="8"/>
    </svg>''',
    
    "group_node": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="2" y="4" width="20" height="16" rx="2" stroke-dasharray="4 2"/>
        <rect x="5" y="7" width="6" height="4" rx="1"/>
        <rect x="13" y="7" width="6" height="4" rx="1"/>
        <rect x="5" y="13" width="14" height="4" rx="1"/>
    </svg>''',
    
    "input": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="2" y="8" width="20" height="8" rx="2"/>
        <line x1="6" y1="12" x2="6" y2="12" stroke-width="2" stroke-linecap="round"/>
    </svg>''',
    
    "label": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <path d="M4 7h16M4 12h12M4 17h8"/>
    </svg>''',
    
    "lottery": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="5" width="18" height="14" rx="2"/>
        <circle cx="12" cy="12" r="4"/>
        <path d="M12 8v8M8 12h8"/>
    </svg>''',
    
    "login": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <circle cx="12" cy="8" r="3"/>
        <path d="M6 21v-2a4 4 0 014-4h4a4 4 0 014 4v2"/>
    </svg>''',
    
    "form": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="7" y1="8" x2="10" y2="8"/>
        <rect x="11" y="6" width="8" height="4" rx="1"/>
        <line x1="7" y1="14" x2="10" y2="14"/>
        <rect x="11" y="12" width="8" height="4" rx="1"/>
    </svg>''',
    
    "progress": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#333333" stroke-width="2">
        <rect x="2" y="6" width="20" height="12" rx="2"/>
        <rect x="3" y="7" width="14" height="10" rx="1" fill="#333333"/>
        <text x="12" y="14" text-anchor="middle" font-size="6" fill="#ffffff">%</text>
    </svg>''',
}

UNICODE_ICONS: Dict[str, str] = {
    "button": "⬚",
    "checkbox": "☑",
    "checkbox_unchecked": "☐",
    "combobox": "▼",
    "progressbar": "▰",
    "hidden_button": "⬚",
    "image_button": "🖼",
    "image": "🖼",
    "video": "▶",
    "image_carousel": "⧉",
    "container": "▢",
    "group_node": "⊞",
    "input": "▏",
    "label": "T",
    "lottery": "🎰",
    "login": "🔐",
    "form": "📝",
    "progress": "📊",
}

class IconManager:
    """图标管理类。
    
    提供图标的生成、缓存和获取功能。
    支持SVG图标和Unicode符号图标。
    """
    
    _icon_cache: Dict[str, QIcon] = {}
    _pixmap_cache: Dict[tuple, QPixmap] = {}
    
    @classmethod
    def get_icon(cls, icon_name: str, use_svg: bool = True) -> QIcon:
        """获取图标。
        
        Args:
            icon_name: 图标名称
            use_svg: 是否使用SVG图标，False则使用Unicode符号
            
        Returns:
            QIcon对象
        """
        cache_key = f"{icon_name}_{'svg' if use_svg else 'unicode'}"
        
        if cache_key in cls._icon_cache:
            return cls._icon_cache[cache_key]
        
        if use_svg and icon_name in SVG_ICONS:
            icon = cls._create_svg_icon(icon_name)
        else:
            icon = cls._create_unicode_icon(icon_name)
        
        cls._icon_cache[cache_key] = icon
        return icon
    
    @classmethod
    def get_pixmap(cls, icon_name: str, size: int = 32, use_svg: bool = True) -> QPixmap:
        """获取像素图。
        
        Args:
            icon_name: 图标名称
            size: 图标大小
            use_svg: 是否使用SVG图标
            
        Returns:
            QPixmap对象
        """
        cache_key = (icon_name, size, use_svg)
        
        if cache_key in cls._pixmap_cache:
            return cls._pixmap_cache[cache_key]
        
        if use_svg and icon_name in SVG_ICONS:
            pixmap = cls._create_svg_pixmap(icon_name, size)
        else:
            pixmap = cls._create_unicode_pixmap(icon_name, size)
        
        cls._pixmap_cache[cache_key] = pixmap
        return pixmap
    
    @classmethod
    def _create_svg_icon(cls, icon_name: str) -> QIcon:
        """从SVG创建图标。
        
        Args:
            icon_name: 图标名称
            
        Returns:
            QIcon对象
        """
        svg_data = SVG_ICONS.get(icon_name, "")
        if not svg_data:
            return QIcon()
        
        renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
        if not renderer.isValid():
            return QIcon()
        
        sizes = [16, 24, 32, 48, 64]
        icon = QIcon()
        
        for size in sizes:
            pixmap = QPixmap(QSize(size, size))
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            icon.addPixmap(pixmap)
        
        return icon
    
    @classmethod
    def _create_svg_pixmap(cls, icon_name: str, size: int) -> QPixmap:
        """从SVG创建像素图。
        
        Args:
            icon_name: 图标名称
            size: 图标大小
            
        Returns:
            QPixmap对象
        """
        svg_data = SVG_ICONS.get(icon_name, "")
        if not svg_data:
            return QPixmap()
        
        renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
        if not renderer.isValid():
            return QPixmap()
        
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    
    @classmethod
    def _create_unicode_icon(cls, icon_name: str) -> QIcon:
        """从Unicode符号创建图标。
        
        Args:
            icon_name: 图标名称
            
        Returns:
            QIcon对象
        """
        pixmap = cls._create_unicode_pixmap(icon_name, 32)
        return QIcon(pixmap)
    
    @classmethod
    def _create_unicode_pixmap(cls, icon_name: str, size: int) -> QPixmap:
        """从Unicode符号创建像素图。
        
        Args:
            icon_name: 图标名称
            size: 图标大小
            
        Returns:
            QPixmap对象
        """
        unicode_char = UNICODE_ICONS.get(icon_name, "?")
        
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        font = QFont("Segoe UI Symbol", int(size * 0.6))
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        painter.setFont(font)
        
        painter.setPen(QColor("#333333"))
        
        fm = QFontMetrics(font)
        text_rect = fm.boundingRect(unicode_char)
        x = (size - text_rect.width()) / 2
        y = (size + text_rect.height()) / 2 - fm.descent()
        
        painter.drawText(int(x), int(y), unicode_char)
        painter.end()
        
        return pixmap
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除图标缓存。"""
        cls._icon_cache.clear()
        cls._pixmap_cache.clear()
    
    @classmethod
    def get_available_icons(cls) -> list:
        """获取所有可用的图标名称。
        
        Returns:
            图标名称列表
        """
        return list(set(SVG_ICONS.keys()) | set(UNICODE_ICONS.keys()))
    
    @classmethod
    def save_icons_to_files(cls, output_dir: str) -> None:
        """将SVG图标保存到文件。
        
        Args:
            output_dir: 输出目录路径
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for icon_name, svg_data in SVG_ICONS.items():
            file_path = os.path.join(output_dir, f"{icon_name}.svg")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_data)
        
        print(f"已保存 {len(SVG_ICONS)} 个SVG图标到: {output_dir}")
