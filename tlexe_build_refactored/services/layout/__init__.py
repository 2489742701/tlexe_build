"""布局引擎模块。

提供容器布局排列、重叠检测与避让、可视化等功能。
"""

from .layout_engine import LayoutEngine
from .overlap_detector import OverlapDetector
from .overlap_avoider import OverlapAvoider
from .overlap_visualizer import OverlapVisualizer
from .data import LayoutResult, OverlapInfo
from .layout_strategy import (
    LayoutStrategy, NoneLayoutStrategy, VerticalLayoutStrategy,
    HorizontalLayoutStrategy, GridLayoutStrategy, STRATEGY_MAP
)

__all__ = [
    'LayoutEngine', 'OverlapDetector', 'OverlapAvoider', 'OverlapVisualizer',
    'LayoutResult', 'OverlapInfo',
    'LayoutStrategy', 'NoneLayoutStrategy', 'VerticalLayoutStrategy',
    'HorizontalLayoutStrategy', 'GridLayoutStrategy', 'STRATEGY_MAP',
]
