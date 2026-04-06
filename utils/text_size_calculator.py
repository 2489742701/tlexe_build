"""
文本尺寸自动计算器
用于检测和修复文本挤压问题
"""

from typing import Tuple, Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtCore import QRect


class TextSizeCalculator:
    """文本尺寸计算器，用于自动检测和修复文本挤压问题"""
    
    def __init__(self):
        self._app = QApplication.instance()
    
    def calculate_text_size(self, text: str, font_family: str = "Microsoft YaHei", 
                           font_size: int = 12, font_bold: bool = False,
                           container_width: int = 300, container_height: int = 100,
                           word_wrap: bool = True) -> Tuple[int, int]:
        """
        计算文本所需的合适尺寸
        
        Args:
            text: 文本内容
            font_family: 字体家族
            font_size: 字体大小
            font_bold: 是否粗体
            container_width: 容器宽度
            container_height: 容器高度
            word_wrap: 是否自动换行
            
        Returns:
            (width, height): 推荐的宽度和高度
        """
        # 创建字体对象
        font = QFont(font_family, font_size)
        font.setBold(font_bold)
        
        # 创建字体度量对象
        font_metrics = QFontMetrics(font)
        
        if word_wrap:
            # 如果启用自动换行，计算多行文本的高度
            # 使用容器宽度作为边界
            text_rect = font_metrics.boundingRect(
                0, 0, container_width, 0,
                QFontMetrics.TextFlag.TextWordWrap,
                text
            )
            
            # 计算推荐尺寸
            recommended_width = container_width
            recommended_height = max(text_rect.height() + 10, container_height)  # 增加10像素边距
        else:
            # 单行文本，计算文本宽度
            text_width = font_metrics.horizontalAdvance(text)
            
            # 计算推荐尺寸
            recommended_width = min(max(text_width + 20, container_width), 1000)  # 限制最大宽度
            recommended_height = max(font_metrics.height() + 10, container_height)
        
        return recommended_width, recommended_height
    
    def detect_text_squeeze(self, text: str, current_width: int, current_height: int,
                           font_family: str = "Microsoft YaHei", font_size: int = 12,
                           font_bold: bool = False, word_wrap: bool = True) -> bool:
        """
        检测文本是否被挤压
        
        Args:
            text: 文本内容
            current_width: 当前宽度
            current_height: 当前高度
            font_family: 字体家族
            font_size: 字体大小
            font_bold: 是否粗体
            word_wrap: 是否自动换行
            
        Returns:
            bool: True表示文本被挤压，需要修复
        """
        # 计算文本实际需要的尺寸
        required_width, required_height = self.calculate_text_size(
            text, font_family, font_size, font_bold, current_width, current_height, word_wrap
        )
        
        # 检测挤压条件
        width_squeeze = required_width > current_width * 1.1  # 宽度不足10%
        height_squeeze = required_height > current_height * 1.2  # 高度不足20%
        
        # 如果文本包含换行符，对高度要求更严格
        if '\n' in text:
            height_squeeze = required_height > current_height * 1.1
        
        return width_squeeze or height_squeeze
    
    def get_fix_recommendation(self, text: str, current_width: int, current_height: int,
                              font_family: str = "Microsoft YaHei", font_size: int = 12,
                              font_bold: bool = False, word_wrap: bool = True) -> dict:
        """
        获取修复建议
        
        Returns:
            dict: 包含修复建议的字典
        """
        # 计算推荐尺寸
        recommended_width, recommended_height = self.calculate_text_size(
            text, font_family, font_size, font_bold, current_width, current_height, word_wrap
        )
        
        # 检测是否挤压
        is_squeezed = self.detect_text_squeeze(
            text, current_width, current_height, font_family, font_size, font_bold, word_wrap
        )
        
        # 计算挤压程度
        width_ratio = recommended_width / current_width if current_width > 0 else float('inf')
        height_ratio = recommended_height / current_height if current_height > 0 else float('inf')
        
        # 生成修复建议
        recommendations = {
            'is_squeezed': is_squeezed,
            'current_size': (current_width, current_height),
            'recommended_size': (recommended_width, recommended_height),
            'width_ratio': width_ratio,
            'height_ratio': height_ratio,
            'squeeze_level': self._get_squeeze_level(width_ratio, height_ratio),
            'fix_actions': self._get_fix_actions(is_squeezed, width_ratio, height_ratio)
        }
        
        return recommendations
    
    def _get_squeeze_level(self, width_ratio: float, height_ratio: float) -> str:
        """获取挤压程度"""
        max_ratio = max(width_ratio, height_ratio)
        
        if max_ratio > 2.0:
            return "严重挤压"
        elif max_ratio > 1.5:
            return "中度挤压"
        elif max_ratio > 1.2:
            return "轻微挤压"
        else:
            return "正常"
    
    def _get_fix_actions(self, is_squeezed: bool, width_ratio: float, height_ratio: float) -> list:
        """获取修复操作建议"""
        if not is_squeezed:
            return []
        
        actions = []
        
        if width_ratio > 1.2:
            actions.append({
                'type': 'resize_width',
                'reason': '文本宽度超出容器',
                'priority': 'high' if width_ratio > 1.5 else 'medium'
            })
        
        if height_ratio > 1.2:
            actions.append({
                'type': 'resize_height',
                'reason': '文本高度超出容器',
                'priority': 'high' if height_ratio > 1.5 else 'medium'
            })
        
        return actions