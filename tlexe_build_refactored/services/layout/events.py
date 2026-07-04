"""布局引擎事件定义。"""

class LayoutUpdatedEvent:
    def __init__(self, container_id: str, result=None):
        self.container_id = container_id
        self.result = result

class OverlapDetectedEvent:
    def __init__(self, container_id: str, overlap_ids: list):
        self.container_id = container_id
        self.overlap_ids = overlap_ids
