"""属性编辑器注册表模块。

本模块包含属性编辑器注册表和自动注册装饰器，
用于在应用启动时自动注册所有属性编辑器。

## 修复说明 (2026-04-02 MCP 启动缓存审查)
【问题】PropertyEditorRegistry 的 _editors 初始为空，编辑器在运行时动态注册，
       如果启动时就需要显示属性面板，可能编辑器还未注册。

【解决方案】
1. 提供 register_property_editor 装饰器，在类定义时自动注册
2. 在 AppInitializer._import_all_property_editors() 中导入所有模块触发注册
3. 提供注册状态查询方法

【使用示例】
    from views.property_editors.registry import register_property_editor
    from views.property_editors.base_editor import BasePropertyEditor
    
    @register_property_editor('button')
    class ButtonPropertyEditor(BasePropertyEditor):
        pass
"""

from typing import Dict, Type, Optional, Callable
from functools import wraps

from models import ComponentModel
from .base_editor import BasePropertyEditor


class PropertyEditorRegistry:
    """属性编辑器注册表。
    
    负责管理组件类型到属性编辑器的映射。
    
    ## 修复说明 (2026-04-02 MCP 启动缓存审查)
    新增功能：
    1. 提供 get_registration_status() 查询注册状态
    2. 提供 get_registered_count() 获取已注册数量
    3. 优化注册流程，支持装饰器自动注册
    
    Attributes:
        _editors: 编辑器注册表 {component_type: editor_class}
        _registration_order: 注册顺序列表，用于调试
    """
    
    # 编辑器注册表: {component_type: editor_class}
    _editors: Dict[str, Type[BasePropertyEditor]] = {}
    
    # 注册顺序记录（用于调试）
    _registration_order: list = []
    
    @classmethod
    def register(cls, component_type: str, editor_class: Type[BasePropertyEditor]):
        """注册属性编辑器。
        
        Args:
            component_type: 组件类型字符串
            editor_class: 属性编辑器类
            
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        新增注册顺序记录，便于调试和监控。
        """
        cls._editors[component_type] = editor_class
        cls._registration_order.append(component_type)
    
    @classmethod
    def get_editor(cls, component_type: str) -> Optional[Type[BasePropertyEditor]]:
        """获取属性编辑器类。
        
        Args:
            component_type: 组件类型字符串
            
        Returns:
            对应的属性编辑器类，如果未找到则返回 None
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
        if component_type in cls._registration_order:
            cls._registration_order.remove(component_type)
    
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
    def get_registration_status(cls) -> Dict[str, bool]:
        """获取注册状态。
        
        Returns:
            字典，键为常见组件类型，值为是否已注册
            
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        用于调试和监控，检查哪些属性编辑器已注册。
        """
        common_types = ['button', 'label', 'input', 'container', 
                       'checkbox', 'combobox', 'progressbar', 'image', 'video']
        return {
            comp_type: comp_type in cls._editors
            for comp_type in common_types
        }
    
    @classmethod
    def get_registered_count(cls) -> int:
        """获取已注册的编辑器数量。
        
        Returns:
            已注册的编辑器数量
            
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        用于监控注册状态。
        """
        return len(cls._editors)
    
    @classmethod
    def clear(cls):
        """清空注册表。"""
        cls._editors.clear()
        cls._registration_order.clear()


def register_property_editor(component_type: str) -> Callable:
    """装饰器：自动注册属性编辑器。
    
    Args:
        component_type: 组件类型字符串
        
    Returns:
        装饰器函数
        
    ## 修复说明 (2026-04-02 MCP 启动缓存审查)
    新增装饰器，在类定义时自动将编辑器注册到 PropertyEditorRegistry。
    避免手动维护注册表，减少遗漏风险。
    
    使用示例：
        @register_property_editor('button')
        class ButtonPropertyEditor(BasePropertyEditor):
            def _setup_ui(self):
                # 设置按钮属性编辑界面
                pass
    """
    def decorator(editor_class: Type[BasePropertyEditor]) -> Type[BasePropertyEditor]:
        PropertyEditorRegistry.register(component_type, editor_class)
        return editor_class
    return decorator
