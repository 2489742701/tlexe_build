"""布局引擎主类。"""

import logging
from typing import Dict, List, Tuple, Optional

from .data import LayoutResult, OverlapInfo
from .layout_strategy import STRATEGY_MAP
from .overlap_detector import OverlapDetector
from .overlap_avoider import OverlapAvoider
from .commands import RelayoutCommand

logger = logging.getLogger(__name__)


class LayoutEngine:
    def __init__(self, project_model=None, undo_manager=None):
        self._project_model = project_model
        self._undo_manager = undo_manager
        self._overlap_detector = OverlapDetector()
        self._overlap_avoider = OverlapAvoider()
    
    def set_project_model(self, project_model):
        self._project_model = project_model
    
    def relayout(self, container) -> LayoutResult:
        layout = getattr(container, 'layout', 'none')
        if layout not in STRATEGY_MAP:
            logger.warning(f"非法布局模式 '{layout}'，回退为 'none'")
            layout = 'none'
        
        strategy = STRATEGY_MAP[layout]
        content_area = self._calc_content_area(container)
        children = self._get_children_models(container)
        
        if not children:
            return LayoutResult(positions={}, overlaps=[], overflow=False, content_area=content_area)
        
        new_positions = strategy.calculate(children, content_area,
                                          getattr(container, 'spacing', 5))
        
        overflow = self._check_overflow(children, new_positions, content_area)
        old_positions = {child.id: (child.x, child.y) for child in children}
        
        self._apply_positions(container, children, new_positions, old_positions)
        
        all_overlaps = OverlapDetector.detect_all(children)
        overlap_infos = []
        for src_id, tgt_id in all_overlaps:
            overlap_infos.append(OverlapInfo(
                source_id=src_id,
                target_id=tgt_id,
                intersection_rect=None
            ))
        
        return LayoutResult(
            positions=new_positions,
            overlaps=overlap_infos,
            overflow=overflow,
            content_area=content_area
        )
    
    def _calc_content_area(self, container) -> Tuple[int, int, int, int]:
        padding = getattr(container, 'padding', 10)
        return (
            container.x + padding,
            container.y + padding,
            container.width - 2 * padding,
            container.height - 2 * padding
        )
    
    def _get_children_models(self, container) -> list:
        children_ids = getattr(container, 'children', [])
        if not children_ids or not self._project_model:
            return []
        
        children = []
        get_comp = getattr(self._project_model, 'get_component', None)
        if not get_comp:
            get_comp = getattr(self._project_model, 'get_component_by_id', None)
        if not get_comp:
            return []
        
        for child_id in children_ids:
            comp = get_comp(child_id)
            if comp:
                children.append(comp)
        return children
    
    def _apply_positions(self, container, children, new_positions, old_positions):
        children_map = {child.id: child for child in children}
        
        for child in children:
            pos = new_positions.get(child.id)
            if pos:
                child.blockSignals(True)
                child._x = pos[0]
                child._y = pos[1]
        
        for child in children:
            child.blockSignals(False)
            child.data_changed.emit()
        
        if self._undo_manager and hasattr(self._undo_manager, 'push'):
            cmd = RelayoutCommand(old_positions, new_positions, children_map)
            self._undo_manager.push(cmd)
    
    def _check_overflow(self, children, new_positions, content_area) -> bool:
        if not content_area:
            return False
        cx, cy, cw, ch = content_area
        for child in children:
            pos = new_positions.get(child.id)
            if not pos:
                continue
            x, y = pos
            if x + child.width > cx + cw or y + child.height > cy + ch:
                return True
        return False
    
    def move_children_with_parent(self, container_id: str, dx: int, dy: int):
        if not self._project_model:
            return
        
        get_comp = getattr(self._project_model, 'get_component', None)
        if not get_comp:
            get_comp = getattr(self._project_model, 'get_component_by_id', None)
        if not get_comp:
            return
        
        container = get_comp(container_id)
        if not container:
            return
        
        children_ids = getattr(container, 'children', [])
        for child_id in children_ids:
            child = get_comp(child_id)
            if child and not getattr(child, 'locked', False):
                child._x = child.x + dx
                child._y = child.y + dy
                child.data_changed.emit()
