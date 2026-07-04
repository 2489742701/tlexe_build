"""字体工具模块。

本模块提供字体相关的工具函数，包括字体检测和获取可用字体列表。
"""

import os
import platform
from typing import List, Optional

_cached_fonts: Optional[List[str]] = None

def get_available_fonts() -> List[str]:
    """获取系统可用字体列表。
    
    Returns:
        字体名称列表
    """
    global _cached_fonts
    
    if _cached_fonts is not None:
        return _cached_fonts
    
    fonts = []
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QFontDatabase
        
        if QApplication.instance() is None:
            QApplication([])
        
        font_db = QFontDatabase()
        font_families = font_db.families()
        fonts = list(font_families)
        
    except Exception:
        if platform.system() == 'Windows':
            fonts = [
                'Microsoft YaHei',
                'SimSun',
                'SimHei',
                'KaiTi',
                'FangSong',
                'Arial',
                'Times New Roman',
                'Courier New',
            ]
        elif platform.system() == 'Darwin':
            fonts = [
                'PingFang SC',
                'Heiti SC',
                'STHeiti',
                'Helvetica',
                'Times',
                'Courier',
            ]
        else:
            fonts = [
                'Noto Sans CJK SC',
                'WenQuanYi Micro Hei',
                'DejaVu Sans',
                'Liberation Sans',
            ]
    
    _cached_fonts = sorted(set(fonts))
    return _cached_fonts

def get_default_font() -> str:
    """获取默认字体。
    
    Returns:
        默认字体名称
    """
    fonts = get_available_fonts()
    
    preferred_fonts = [
        'Microsoft YaHei',
        'PingFang SC',
        'Noto Sans CJK SC',
        'WenQuanYi Micro Hei',
        'SimHei',
    ]
    
    for font in preferred_fonts:
        if font in fonts:
            return font
    
    if fonts:
        return fonts[0]
    
    return 'Arial'

def is_font_available(font_name: str) -> bool:
    """检查字体是否可用。
    
    Args:
        font_name: 字体名称
        
    Returns:
        字体是否可用
    """
    fonts = get_available_fonts()
    return font_name in fonts

def clear_font_cache():
    """清除字体缓存。"""
    global _cached_fonts
    _cached_fonts = None
