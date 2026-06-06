"""属性编辑器注册表模块。

本模块包含属性编辑器注册表和自动注册装饰器，
查询逻辑已委托给 ComponentRegistry，本模块仅负责实例管理和注册顺序记录。
"""

from typing import Dict, Type, Optional, Callable
from functools import wraps

from models import ComponentModel
from .base_editor import BasePropertyEditor


class PropertyEditorRegistry:
    """属性编辑器注册表。
    
    负责管理组件类型到属性编辑器的映射。
    编辑器类查询已委托给 ComponentRegistry，本类仅负责实例创建和注册顺序记录。
    
    Attributes:
        _registration_order: 注册顺序列表，用于调试
    """
    
    _registration_order: list = []
    
    @classmethod
    def register(cls, component_type: str, editor_class: Type[BasePropertyEditor]):
        """注册属性编辑器到 ComponentRegistry。"""
        from models.component_registry import ComponentRegistry
        if ComponentRegistry.is_registered(component_type):
            ComponentRegistry.update_editor(component_type, editor_class)
        if component_type not in cls._registration_order:
            cls._registration_order.append(component_type)
    
    @classmethod
    def get_editor(cls, component_type: str) -> Optional[Type[BasePropertyEditor]]:
        """获取属性编辑器类。"""
        from models.component_registry import ComponentRegistry
        return ComponentRegistry.get_editor_class(component_type)
    
    @classmethod
    def create_editor(cls, component_type: str, parent=None) -> Optional[BasePropertyEditor]:
        """创建属性编辑器实例。"""
        from models.component_registry import ComponentRegistry
        editor_class = ComponentRegistry.get_editor_class(component_type)
        if editor_class:
            return editor_class(parent)
        return None
    
    @classmethod
    def unregister(cls, component_type: str):
        """注销属性编辑器。"""
        if component_type in cls._registration_order:
            cls._registration_order.remove(component_type)
    
    @classmethod
    def get_registered_types(cls) -> list:
        """获取已注册的组件类型列表。"""
        from models.component_registry import ComponentRegistry
        return ComponentRegistry.get_all_types()
    
    @classmethod
    def is_registered(cls, component_type: str) -> bool:
        """检查组件类型是否已注册。"""
        from models.component_registry import ComponentRegistry
        return ComponentRegistry.is_registered(component_type)
    
    @classmethod
    def get_registration_status(cls) -> Dict[str, bool]:
        """获取注册状态。"""
        from models.component_registry import ComponentRegistry
        return {
            comp_type: ComponentRegistry.get_editor_class(comp_type) is not None
            for comp_type in ComponentRegistry.get_all_types()
        }
    
    @classmethod
    def get_registered_count(cls) -> int:
        """获取已注册的编辑器数量。"""
        from models.component_registry import ComponentRegistry
        count = 0
        for comp_type in ComponentRegistry.get_all_types():
            if ComponentRegistry.get_editor_class(comp_type) is not None:
                count += 1
        return count
    
    @classmethod
    def clear(cls):
        """清空注册顺序记录。"""
        cls._registration_order.clear()


def register_property_editor(component_type: str) -> Callable:
    """装饰器：自动注册属性编辑器到 ComponentRegistry。"""
    def decorator(editor_class: Type[BasePropertyEditor]) -> Type[BasePropertyEditor]:
        PropertyEditorRegistry.register(component_type, editor_class)
        return editor_class
    return decorator
