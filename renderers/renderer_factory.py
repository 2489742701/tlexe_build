"""渲染器工厂模块。

负责根据组件类型创建对应的渲染器实例。
渲染器类查询委托给 ComponentRegistry，本类仅负责实例管理和缓存。
"""

from typing import Dict, Type, Optional

from models import ComponentModel
from .component_renderer import ComponentRenderer
from .label_renderer import LabelRenderer


class RendererFactory:
    """渲染器工厂。
    
    负责根据组件类型创建对应的渲染器实例。
    渲染器类查询已委托给 ComponentRegistry，本类仅负责实例管理和缓存。
    
    Attributes:
        _instances: 渲染器实例缓存
        _default_renderer_class: 默认渲染器类
    """
    
    _instances: Dict[str, ComponentRenderer] = {}
    
    _default_renderer_class: Type[ComponentRenderer] = LabelRenderer
    
    @classmethod
    def get_renderer(cls, component_type: str) -> ComponentRenderer:
        """获取渲染器实例。
        
        通过 ComponentRegistry 查询渲染器类，使用缓存避免重复创建。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            对应类型的渲染器实例
            
        Raises:
            ValueError: 如果组件类型未注册且没有设置默认渲染器
        """
        if component_type in cls._instances:
            return cls._instances[component_type]
        
        from models.component_registry import ComponentRegistry
        renderer_class = ComponentRegistry.get_renderer_class(component_type)
        
        if renderer_class:
            instance = renderer_class()
            cls._instances[component_type] = instance
            return instance
        
        raise ValueError(f"未知的组件类型: {component_type}. "
                        f"支持的类型: {ComponentRegistry.get_all_types()}")
    
    @classmethod
    def get_renderer_or_default(cls, component_type: str) -> ComponentRenderer:
        """获取渲染器实例，如果未找到则返回默认渲染器。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            对应类型的渲染器实例，如果未找到则返回默认渲染器
        """
        try:
            return cls.get_renderer(component_type)
        except ValueError:
            default_type = f"__default_{cls._default_renderer_class.__name__}__"
            if default_type not in cls._instances:
                cls._instances[default_type] = cls._default_renderer_class()
            return cls._instances[default_type]
    
    @classmethod
    def register_renderer(cls, component_type: str, renderer_class: Type[ComponentRenderer]):
        """注册新的渲染器到 ComponentRegistry。
        
        Args:
            component_type: 组件类型字符串
            renderer_class: 渲染器类
        """
        from models.component_registry import ComponentRegistry
        if ComponentRegistry.is_registered(component_type):
            ComponentRegistry.update_renderer(component_type, renderer_class)
        cls._instances.pop(component_type, None)
    
    @classmethod
    def set_default_renderer(cls, renderer_class: Type[ComponentRenderer]):
        """设置默认渲染器。
        
        Args:
            renderer_class: 默认渲染器类
        """
        cls._default_renderer_class = renderer_class
        default_type = f"__default_{renderer_class.__name__}__"
        cls._instances.pop(default_type, None)
    
    @classmethod
    def clear_cache(cls):
        """清除渲染器实例缓存。"""
        cls._instances.clear()
    
    @classmethod
    def get_supported_types(cls) -> list:
        """获取支持的组件类型列表。
        
        Returns:
            支持的组件类型字符串列表
        """
        from models.component_registry import ComponentRegistry
        return ComponentRegistry.get_all_types()
    
    @classmethod
    def is_cached(cls, component_type: str) -> bool:
        """检查指定类型的渲染器是否已缓存。"""
        return component_type in cls._instances
    
    @classmethod
    def preload_all(cls) -> None:
        """预加载所有注册的渲染器实例。
        
        遍历 ComponentRegistry 中所有已注册的渲染器类型，主动创建实例并填充缓存。
        应在 QApplication 创建后、主窗口显示前调用。
        """
        from models.component_registry import ComponentRegistry
        for component_type in ComponentRegistry.get_all_types():
            if component_type not in cls._instances:
                try:
                    cls.get_renderer(component_type)
                except ValueError:
                    pass
        
        default_type = f"__default_{cls._default_renderer_class.__name__}__"
        if default_type not in cls._instances:
            cls._instances[default_type] = cls._default_renderer_class()
    
    @classmethod
    def get_preload_status(cls) -> Dict[str, bool]:
        """获取预加载状态。"""
        from models.component_registry import ComponentRegistry
        return {
            component_type: component_type in cls._instances
            for component_type in ComponentRegistry.get_all_types()
        }
