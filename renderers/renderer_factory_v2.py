"""渲染器工厂 V2 - 改进版。

本模块是 RendererFactory 的改进版本，解决了以下问题：
1. 重复创建实例的性能问题
2. 默认降级策略不明确

## 修复说明 (2026-04-02 三轮审查)
【问题1】每次调用 get_renderer 都创建新实例，有性能问题
【解决】缓存无状态渲染器实例

【问题2】对于未知类型返回 LabelRenderer 作为默认，可能不符合预期
【解决】提供明确的降级策略，支持配置默认渲染器

【审查建议来源】MCP 三轮深度审查
"""

from typing import Dict, Type, Optional

from models import ComponentModel
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


class RendererFactoryV2:
    """渲染器工厂 V2 - 改进版。
    
    负责根据组件类型创建对应的渲染器实例。
    
    ## 修复说明 (2026-04-02 三轮审查)
    主要改进：
    1. 缓存无状态渲染器实例，避免重复创建
    2. 提供明确的降级策略
    3. 支持配置默认渲染器
    
    Attributes:
        _registry: 渲染器类注册表
        _instances: 渲染器实例缓存
        _default_renderer_class: 默认渲染器类
    """
    
    # 渲染器类注册表
    _registry: Dict[str, Type[ComponentRenderer]] = {
        'button': ButtonRenderer,
        'label': LabelRenderer,
        'input': InputRenderer,
        'container': ContainerRenderer,
        'checkbox': CheckBoxRenderer,
        'combobox': ComboBoxRenderer,
        'progressbar': ProgressBarRenderer,
        'hidden_button': HiddenButtonRenderer,
        'image_button': ImageButtonRenderer,
        'image_carousel': ImageCarouselRenderer,
    }
    
    # 渲染器实例缓存（修复：缓存实例避免重复创建）
    _instances: Dict[str, ComponentRenderer] = {}
    
    # 默认渲染器类
    _default_renderer_class: Type[ComponentRenderer] = LabelRenderer
    
    @classmethod
    def get_renderer(cls, component_type: str) -> ComponentRenderer:
        """获取渲染器实例。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            对应类型的渲染器实例
            
        Raises:
            ValueError: 如果组件类型未注册且没有设置默认渲染器
            
        ## 修复说明 (2026-04-02 三轮审查)
        使用实例缓存，避免每次创建新实例。
        如果渲染器无状态，缓存是安全的且能提高性能。
        """
        # 检查缓存
        if component_type in cls._instances:
            return cls._instances[component_type]
        
        # 获取渲染器类
        renderer_class = cls._registry.get(component_type)
        
        if renderer_class:
            # 创建实例并缓存
            instance = renderer_class()
            cls._instances[component_type] = instance
            return instance
        
        # 修复：明确的降级策略
        # 如果类型未注册，抛出异常而不是静默返回默认渲染器
        raise ValueError(f"未知的组件类型: {component_type}. "
                        f"支持的类型: {list(cls._registry.keys())}")
    
    @classmethod
    def get_renderer_or_default(cls, component_type: str) -> ComponentRenderer:
        """获取渲染器实例，如果未找到则返回默认渲染器。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            对应类型的渲染器实例，如果未找到则返回默认渲染器
            
        ## 修复说明 (2026-04-02 三轮审查)
        提供明确的降级策略，调用方可以选择使用默认渲染器或抛出异常。
        """
        try:
            return cls.get_renderer(component_type)
        except ValueError:
            # 返回默认渲染器实例（也使用缓存）
            default_type = f"__default_{cls._default_renderer_class.__name__}__"
            if default_type not in cls._instances:
                cls._instances[default_type] = cls._default_renderer_class()
            return cls._instances[default_type]
    
    @classmethod
    def register_renderer(cls, component_type: str, renderer_class: Type[ComponentRenderer]):
        """注册新的渲染器。
        
        Args:
            component_type: 组件类型字符串
            renderer_class: 渲染器类
            
        ## 修复说明 (2026-04-02 三轮审查)
        注册新渲染器时清除对应的缓存实例（如果存在）。
        """
        cls._registry[component_type] = renderer_class
        # 清除缓存（如果存在）
        cls._instances.pop(component_type, None)
    
    @classmethod
    def set_default_renderer(cls, renderer_class: Type[ComponentRenderer]):
        """设置默认渲染器。
        
        Args:
            renderer_class: 默认渲染器类
            
        ## 修复说明 (2026-04-02 三轮审查)
        支持配置默认渲染器，而不是硬编码 LabelRenderer。
        """
        cls._default_renderer_class = renderer_class
        # 清除默认渲染器缓存
        default_type = f"__default_{renderer_class.__name__}__"
        cls._instances.pop(default_type, None)
    
    @classmethod
    def clear_cache(cls):
        """清除渲染器实例缓存。
        
        ## 修复说明 (2026-04-02 三轮审查)
        提供清除缓存的方法，用于内存管理或热更新场景。
        """
        cls._instances.clear()
    
    @classmethod
    def get_supported_types(cls) -> list:
        """获取支持的组件类型列表。
        
        Returns:
            支持的组件类型字符串列表
        """
        return list(cls._registry.keys())
    
    @classmethod
    def is_cached(cls, component_type: str) -> bool:
        """检查指定类型的渲染器是否已缓存。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            是否已缓存
            
        ## 修复说明 (2026-04-02 三轮审查)
        提供缓存状态查询，便于调试和性能监控。
        """
        return component_type in cls._instances
    
    @classmethod
    def preload_all(cls) -> None:
        """预加载所有注册的渲染器实例。
        
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        【问题】渲染器在首次使用时才创建实例，导致 UI 启动时可能显示不正确
        【解决】在应用启动时预加载所有渲染器，确保缓存已填充
        【调用时机】AppInitializer._preload_resources() 中调用
        
        此方法会遍历所有注册的渲染器类型，主动创建实例并填充缓存。
        应在 QApplication 创建后、主窗口显示前调用。
        """
        for component_type in cls._registry:
            if component_type not in cls._instances:
                cls.get_renderer(component_type)  # 触发创建实例并缓存
        
        # 同时预加载默认渲染器
        default_type = f"__default_{cls._default_renderer_class.__name__}__"
        if default_type not in cls._instances:
            cls._instances[default_type] = cls._default_renderer_class()
    
    @classmethod
    def get_preload_status(cls) -> Dict[str, bool]:
        """获取预加载状态。
        
        Returns:
            字典，键为组件类型，值为是否已缓存
            
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        用于调试和监控，检查哪些渲染器已预加载。
        """
        return {
            component_type: component_type in cls._instances
            for component_type in cls._registry.keys()
        }
