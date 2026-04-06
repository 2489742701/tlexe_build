"""控制器模块。

本模块包含应用程序的控制器，负责处理业务逻辑和协调模型与视图。

## 修复说明 (2026-04-02)
新增 CanvasController，将画布交互逻辑从视图中分离，
实现真正的 MVC 架构。

控制器职责划分：
- ProjectController: 负责项目级别的操作（保存、加载、导出等）
- CanvasController: 负责画布上的交互（选择、拖拽、调整大小、对齐等）
"""

from .project_controller import ProjectController
from .canvas_controller import CanvasController
from .canvas_controller_v2 import CanvasControllerV2

__all__ = ['ProjectController', 'CanvasController', 'CanvasControllerV2']
