"""重叠检测器。"""

from typing import List, Tuple
from PySide6.QtCore import QRectF
from .data import OverlapInfo


class OverlapDetector:
    @staticmethod
    def detect(source, siblings: list) -> List[OverlapInfo]:
        source_rect = QRectF(source.x, source.y, source.width, source.height)
        if source.width <= 0 or source.height <= 0:
            return []
        
        overlaps = []
        for sibling in siblings:
            if sibling.id == source.id:
                continue
            if sibling.width <= 0 or sibling.height <= 0:
                continue
            
            sibling_rect = QRectF(sibling.x, sibling.y, sibling.width, sibling.height)
            intersection = source_rect.intersected(sibling_rect)
            
            if intersection.isValid() and intersection.width() > 0 and intersection.height() > 0:
                overlaps.append(OverlapInfo(
                    source_id=source.id,
                    target_id=sibling.id,
                    intersection_rect=intersection
                ))
        
        return overlaps
    
    @staticmethod
    def detect_all(children: list) -> List[Tuple[str, str]]:
        overlaps = []
        n = len(children)
        for i in range(n):
            if children[i].width <= 0 or children[i].height <= 0:
                continue
            rect_i = QRectF(children[i].x, children[i].y, children[i].width, children[i].height)
            for j in range(i + 1, n):
                if children[j].width <= 0 or children[j].height <= 0:
                    continue
                rect_j = QRectF(children[j].x, children[j].y, children[j].width, children[j].height)
                intersection = rect_i.intersected(rect_j)
                if intersection.isValid() and intersection.width() > 0 and intersection.height() > 0:
                    overlaps.append((children[i].id, children[j].id))
        return overlaps
