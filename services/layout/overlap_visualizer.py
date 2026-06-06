"""重叠可视化指示器。"""

from typing import Set, Dict
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt


class OverlapVisualizer:
    _indicators: Dict[str, object] = {}
    _pen = QPen(QColor("#FF0000"), 2, Qt.PenStyle.DashLine)
    
    @classmethod
    def show_overlaps(cls, overlap_ids: Set[str], canvas_view=None):
        if not canvas_view:
            return
        
        scene = canvas_view.scene() if hasattr(canvas_view, 'scene') else None
        if not scene:
            return
        
        current_ids = set(cls._indicators.keys())
        
        for comp_id in current_ids - overlap_ids:
            cls._remove_overlap_indicator(comp_id)
        
        for comp_id in overlap_ids - current_ids:
            cls._add_overlap_indicator(comp_id, scene)
    
    @classmethod
    def _add_overlap_indicator(cls, comp_id: str, scene):
        try:
            from PySide6.QtWidgets import QGraphicsRectItem
            items = scene.items()
            for item in items:
                if hasattr(item, 'model') and getattr(item.model, 'id', None) == comp_id:
                    rect = item.boundingRect()
                    indicator = QGraphicsRectItem(rect)
                    indicator.setPen(cls._pen)
                    indicator.setBrush(Qt.BrushStyle.NoBrush)
                    indicator.setZValue(100)
                    item.setParentItem(indicator) if False else None
                    scene.addItem(indicator)
                    indicator.setPos(item.pos())
                    cls._indicators[comp_id] = indicator
                    return
        except Exception:
            pass
    
    @classmethod
    def _remove_overlap_indicator(cls, comp_id: str):
        indicator = cls._indicators.pop(comp_id, None)
        if indicator:
            try:
                scene = indicator.scene()
                if scene:
                    scene.removeItem(indicator)
            except Exception:
                pass
    
    @classmethod
    def clear_overlaps(cls):
        for comp_id in list(cls._indicators.keys()):
            cls._remove_overlap_indicator(comp_id)
