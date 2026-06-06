"""布局引擎数据模型。"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from PySide6.QtCore import QRectF


@dataclass
class OverlapInfo:
    source_id: str
    target_id: str
    intersection_rect: QRectF
    avoidance_position: Optional[Tuple[int, int]] = None


@dataclass
class LayoutResult:
    positions: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    overlaps: List[OverlapInfo] = field(default_factory=list)
    overflow: bool = False
    content_area: Optional[Tuple[int, int, int, int]] = None
