"""属性编辑器注册表。

本模块包含属性编辑器注册表，用于根据组件类型获取对应的属性编辑器。

## 修复说明 (2026-04-02)
【问题】PropertyPanel 直接依赖所有具体模型类，新增组件类型需要修改导入。

【解决方案】使用注册表模式（Registry Pattern），创建 PropertyEditorRegistry
动态管理属性编辑器的注册和获取。

【设计模式】注册表模式（Registry Pattern）
- 为服务提供一个全局访问点，同时保持松耦合
- 避免直接依赖具体类，通过字符串键值获取对应的服务
"""

from typing import Dict, Type, Optional

from models import ComponentModel
from .base_editor import BasePropertyEditor


class PropertyEditorRegistry:
    """属性编辑器注册表。
    
    负责管理组件类型到属性编辑器的映射。
    
    ## 修复说明 (2026-04-02)
    此类是新创建的，用于解耦 PropertyPanel 与具体模型类的依赖。
    使用类级别的注册表，无需实例化即可使用。
    """
    
    # 编辑器注册表: {component_type: editor_class}
    _editors: Dict[str, Type[BasePropertyEditor]] = {}
    
    @classmethod
    def register(cls, component_type: str, editor_class: Type[BasePropertyEditor]):
        """注册属性编辑器。
        
        Args:
            component_type: 组件类型字符串
            editor_class: 属性编辑器类
            
        ## 修复说明 (2026-04-02)
        提供注册方法，支持在运行时动态注册编辑器。
        新增组件类型时调用此方法注册对应的编辑器。
        
        示例：
            PropertyEditorRegistry.register('button', ButtonPropertyEditor)
        """
        cls._editors[component_type] = editor_class
    
    @classmethod
    def get_editor(cls, component_type: str) -> Optional[Type[BasePropertyEditor]]:
        """获取属性编辑器类。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            对应的属性编辑器类，如果未找到则返回 None
            
        ## 修复说明 (2026-04-02)
        PropertyPanel 通过此方法获取对应类型的编辑器，
        无需直接导入具体模型类。
        """
        return cls._editors.get(component_type)
    
    @classmethod
    def create_editor(cls, component_type: str, parent=None) -> Optional[BasePropertyEditor]:
        """创建属性编辑器实例。
        
        Args:
            component_type: 组件类型字符串
            parent: 父控件
            
        Returns:
            属性编辑器实例，如果未找到则返回 None
        """
        editor_class = cls._editors.get(component_type)
        if editor_class:
            return editor_class(parent)
        return None
    
    @classmethod
    def unregister(cls, component_type: str):
        """注销属性编辑器。
        
        Args:
            component_type: 组件类型字符串
        """
        cls._editors.pop(component_type, None)
    
    @classmethod
    def get_registered_types(cls) -> list:
        """获取已注册的组件类型列表。
        
        Returns:
            已注册的组件类型字符串列表
        """
        return list(cls._editors.keys())
    
    @classmethod
    def is_registered(cls, component_type: str) -> bool:
        """检查组件类型是否已注册。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            是否已注册
        """
        return component_type in cls._editors
    
    @classmethod
    def clear(cls):
        """清空注册表。"""
        cls._editors.clear()


# 便捷函数
def register_property_editor(component_type: str):
    """装饰器：注册属性编辑器。
    
    Args:
        component_type: 组件类型字符串
        
    Returns:
        装饰器函数
        
    ## 修复说明 (2026-04-02)
    提供装饰器方式注册编辑器，简化注册代码。
    
    示例：
        @register_property_editor('button')
        class ButtonPropertyEditor(BasePropertyEditor):
            pass
    """
    def decorator(editor_class: Type[BasePropertyEditor]):
        PropertyEditorRegistry.register(component_type, editor_class)
        return editor_class
    return decorator
