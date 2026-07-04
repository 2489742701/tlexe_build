"""Presenter模块初始化。

本模块统一导出各Presenter类，提供统一的访问入口。

## 可用Presenter
- CanvasPresenter: 画布交互管理
"""

from .canvas_presenter import CanvasPresenter

__all__ = [
    "CanvasPresenter",
]
