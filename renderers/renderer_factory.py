"""渲染器工厂。

本模块包含渲染器工厂，用于根据组件类型创建对应的渲染器。

## 修复说明 (2026-04-02)
【问题】ComponentGraphicsItem 需要根据不同的组件类型选择不同的绘制逻辑，
如果直接在类中判断类型，会导致耦合严重。

【解决方案】使用工厂模式，创建 RendererFactory 根据组件类型返回对应的渲染器实例。

【设计模式】工厂模式（Factory Pattern）
- 定义一个创建对象的接口，让子类决定实例化哪一个类
- 使一个类的实例化延迟到其子类
"""

from typing import Dict, Type

from models import ComponentModel
from .component_renderer import ComponentRenderer
from .button_renderer import ButtonRenderer
from .label_renderer import LabelRenderer
from .input_renderer import InputRenderer
from .container_renderer import ContainerRenderer
from .checkbox_renderer import CheckBoxRenderer
from .combobox_renderer import ComboBoxRenderer
from .progressbar_renderer import ProgressBarRenderer
from .image_renderer import ImageRenderer
from .video_renderer import VideoRenderer


class RendererFactory:
    """渲染器工厂。
    
    负责根据组件类型创建对应的渲染器实例。
    
    ## 修复说明 (2026-04-02)
    此类是新创建的，使用工厂模式解耦组件类型和渲染器的创建逻辑。
    新增组件类型时，只需在此工厂中注册新的渲染器即可。
    """
    
    # 渲染器注册表
    _renderers: Dict[str, Type[ComponentRenderer]] = {
        'button': ButtonRenderer,
        'label': LabelRenderer,
        'input': InputRenderer,
        'container': ContainerRenderer,
        'checkbox': CheckBoxRenderer,
        'combobox': ComboBoxRenderer,
        'progressbar': ProgressBarRenderer,
        'image': ImageRenderer,
        'video': VideoRenderer,
    }
    
    @classmethod
    def get_renderer(cls, component_type: str) -> ComponentRenderer:
        """获取渲染器实例。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            对应类型的渲染器实例，如果未找到则返回默认渲染器
            
        ## 修复说明 (2026-04-02)
        使用类方法，无需实例化工厂即可获取渲染器。
        """
        renderer_class = cls._renderers.get(component_type)
        if renderer_class:
            return renderer_class()
        
        # 返回默认渲染器（标签渲染器作为默认）
        return LabelRenderer()
    
    @classmethod
    def register_renderer(cls, component_type: str, renderer_class: Type[ComponentRenderer]):
        """注册新的渲染器。
        
        Args:
            component_type: 组件类型字符串
            renderer_class: 渲染器类
            
        ## 修复说明 (2026-04-02)
        提供注册方法，支持在运行时动态注册新的渲染器，
        便于插件系统扩展。
        """
        cls._renderers[component_type] = renderer_class
    
    @classmethod
    def get_supported_types(cls) -> list:
        """获取支持的组件类型列表。
        
        Returns:
            支持的组件类型字符串列表
        """
        return list(cls._renderers.keys())
