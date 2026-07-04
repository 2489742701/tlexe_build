"""自动避让器。"""

from typing import Dict, Tuple, List
import logging

from .data import OverlapInfo

logger = logging.getLogger(__name__)
MAX_CASCADE_DEPTH = 20

class OverlapAvoider:
    @staticmethod
    def avoid(source, overlaps: List[OverlapInfo], layout: str,
              spacing: int = 5, container=None) -> Dict[str, Tuple[int, int]]:
        if layout == "none" or not overlaps:
            return {}
        
        adjustments = {}
        cascade_depth = 0
        
        for overlap in overlaps:
            if overlap.target_id in adjustments:
                continue
            
            if layout == "vertical":
                new_y = source.y + source.height + spacing
                adjustments[overlap.target_id] = (source.x, new_y)
            elif layout == "horizontal":
                new_x = source.x + source.width + spacing
                adjustments[overlap.target_id] = (new_x, source.y)
            elif layout == "grid":
                new_x = source.x + source.width + spacing
                if container and new_x + 120 > container.x + container.width:
                    new_y = source.y + source.height + spacing
                    adjustments[overlap.target_id] = (container.x + (container._padding if hasattr(container, '_padding') else 10), new_y)
                else:
                    adjustments[overlap.target_id] = (new_x, source.y)
            else:
                continue
            
            cascade_depth += 1
            if cascade_depth > MAX_CASCADE_DEPTH:
                logger.warning(f"级联避让深度超过 {MAX_CASCADE_DEPTH}，停止避让")
                break
        
        return adjustments
