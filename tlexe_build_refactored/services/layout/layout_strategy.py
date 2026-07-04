"""布局策略接口与实现。

策略模式解耦四种布局模式：none/vertical/horizontal/grid。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

MIN_COLUMN_WIDTH = 120

class LayoutStrategy(ABC):
    @abstractmethod
    def calculate(self, children: list, content_area: Tuple[int, int, int, int],
                  spacing: int = 5) -> Dict[str, Tuple[int, int]]:
        pass

class NoneLayoutStrategy(LayoutStrategy):
    def calculate(self, children: list, content_area: Tuple[int, int, int, int],
                  spacing: int = 5) -> Dict[str, Tuple[int, int]]:
        return {child.id: (child.x, child.y) for child in children}

class VerticalLayoutStrategy(LayoutStrategy):
    def calculate(self, children: list, content_area: Tuple[int, int, int, int],
                  spacing: int = 5) -> Dict[str, Tuple[int, int]]:
        if not children:
            return {}
        
        cx, cy, cw, ch = content_area
        positions = {}
        current_y = cy
        
        for child in children:
            if child.width <= 0 or child.height <= 0:
                continue
            positions[child.id] = (cx, current_y)
            current_y += child.height + spacing
        
        return positions

class HorizontalLayoutStrategy(LayoutStrategy):
    def calculate(self, children: list, content_area: Tuple[int, int, int, int],
                  spacing: int = 5) -> Dict[str, Tuple[int, int]]:
        if not children:
            return {}
        
        cx, cy, cw, ch = content_area
        positions = {}
        current_x = cx
        
        for child in children:
            if child.width <= 0 or child.height <= 0:
                continue
            positions[child.id] = (current_x, cy)
            current_x += child.width + spacing
        
        return positions

class GridLayoutStrategy(LayoutStrategy):
    def calculate(self, children: list, content_area: Tuple[int, int, int, int],
                  spacing: int = 5) -> Dict[str, Tuple[int, int]]:
        if not children:
            return {}
        
        cx, cy, cw, ch = content_area
        
        if cw + spacing <= 0:
            return VerticalLayoutStrategy().calculate(children, content_area, spacing)
        
        num_cols = max(1, (cw + spacing) // (MIN_COLUMN_WIDTH + spacing))
        
        positions = {}
        col_x = [cx + i * (MIN_COLUMN_WIDTH + spacing) for i in range(num_cols)]
        col_y = [cy] * num_cols
        
        for child in children:
            if child.width <= 0 or child.height <= 0:
                continue
            
            min_col = 0
            min_y = col_y[0]
            for i in range(1, num_cols):
                if col_y[i] < min_y:
                    min_y = col_y[i]
                    min_col = i
            
            positions[child.id] = (col_x[min_col], col_y[min_col])
            col_y[min_col] += child.height + spacing
        
        return positions

STRATEGY_MAP = {
    "none": NoneLayoutStrategy(),
    "vertical": VerticalLayoutStrategy(),
    "horizontal": HorizontalLayoutStrategy(),
    "grid": GridLayoutStrategy(),
}
