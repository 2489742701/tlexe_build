"""渲染器模块。

本模块包含组件渲染器，负责绘制不同类型的组件。
通过策略模式将绘制逻辑从 ComponentGraphicsItem 中分离。

## 修复说明 (2026-04-02)
【问题】canvas.py 中的 ComponentGraphicsItem 包含多个绘制方法
（_paint_combobox, _paint_checkbox, _paint_progressbar 等），
违反单一职责原则，且新增组件类型需要修改此类。

【解决方案】使用策略模式，为每种组件类型创建独立的渲染器，
ComponentGraphicsItem 只需调用对应渲染器的 render 方法。

【收益】
1. 绘制逻辑分离，每个渲染器只负责一种组件类型
2. 新增组件类型只需添加新的渲染器，无需修改现有代码（开闭原则）
3. 便于单元测试，可以单独测试每个渲染器的绘制逻辑
"""

from .component_renderer import ComponentRenderer
from .button_renderer import ButtonRenderer
from .label_renderer import LabelRenderer
from .input_renderer import InputRenderer
from .container_renderer import ContainerRenderer
from .checkbox_renderer import CheckBoxRenderer
from .combobox_renderer import ComboBoxRenderer
from .progressbar_renderer import ProgressBarRenderer
from .hidden_button_renderer import HiddenButtonRenderer
from .image_button_renderer import ImageButtonRenderer
from .image_carousel_renderer import ImageCarouselRenderer
from .renderer_factory import RendererFactory
from .renderer_factory_v2 import RendererFactoryV2

__all__ = [
    'ComponentRenderer',
    'ButtonRenderer',
    'LabelRenderer',
    'InputRenderer',
    'ContainerRenderer',
    'CheckBoxRenderer',
    'ComboBoxRenderer',
    'ProgressBarRenderer',
    'HiddenButtonRenderer',
    'ImageButtonRenderer',
    'ImageCarouselRenderer',
    'RendererFactory',
    'RendererFactoryV2',
]
