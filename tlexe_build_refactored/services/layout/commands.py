"""布局引擎撤销命令。"""

from typing import Dict, Tuple

class RelayoutCommand:
    def __init__(self, old_positions: Dict[str, Tuple[int, int]],
                 new_positions: Dict[str, Tuple[int, int]],
                 children_map: dict = None):
        self.old_positions = old_positions
        self.new_positions = new_positions
        self._children_map = children_map

    def execute(self):
        if not self._children_map:
            return
        for comp_id, (x, y) in self.new_positions.items():
            comp = self._children_map.get(comp_id)
            if comp:
                comp._x = x
                comp._y = y
                comp.data_changed.emit()

    def undo(self):
        if not self._children_map:
            return
        for comp_id, (x, y) in self.old_positions.items():
            comp = self._children_map.get(comp_id)
            if comp:
                comp._x = x
                comp._y = y
                comp.data_changed.emit()
