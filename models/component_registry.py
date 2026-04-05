"""组件注册中心模块。

本模块提供统一的组件注册机制，将组件类型、模型类、渲染器类、
属性编辑器类集中管理，解决分散注册导致的维护问题。

## 修复说明 (2026-04-02 MCP架构审查)
【问题】新增组件需要修改多处注册表（模型映射、渲染器工厂、属性编辑器），
      违反开闭原则，维护成本高。
      
【解决方案】创建统一的 ComponentRegistry，通过装饰器一次性注册组件的所有元数据。

【设计模式】注册表模式（Registry Pattern）+ 元数据模式（Metadata Pattern）

【使用示例】
    @register_component('button')
    class ButtonModel(ComponentModel):
        pass
        
    # 或在组件定义后注册
    ComponentRegistry.register(
        type_name='custom_button',
        model_class=CustomButtonModel,
        renderer_class=CustomButtonRenderer,
        editor_class=CustomButtonEditor
    )
"""

from typing import Dict, Type, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class ComponentMeta:
    """组件元数据。
    
    存储组件类型的所有相关类和信息。
    
    Attributes:
        type_name: 组件类型标识符（如 'button', 'label'）
        model_class: 组件模型类
        renderer_class: 组件渲染器类（可选）
        editor_class: 属性编辑器类（可选）
        display_name: 显示名称（用于UI）
        icon: 图标路径或名称（可选）
        category: 组件分类（如 'basic', 'input', 'container'）
        default_props: 默认属性字典
    """
    type_name: str
    model_class: Type
    renderer_class: Optional[Type] = None
    editor_class: Optional[Type] = None
    display_name: str = ""
    icon: str = ""
    category: str = "basic"
    default_props: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.default_props is None:
            self.default_props = {}
        if not self.display_name:
            self.display_name = self.type_name.capitalize()


class ComponentRegistry:
    """组件注册中心。
    
    统一管理所有组件类型的元数据，提供统一的注册和查询接口。
    
    ## 修复说明 (2026-04-02 MCP架构审查)
    此类是架构改进的核心，将分散在多个模块的注册表统一到这里。
    
    Attributes:
        _components: 组件元数据字典 {type_name: ComponentMeta}
        _categories: 组件分类字典 {category: [type_name, ...]}
    """
    
    _components: Dict[str, ComponentMeta] = {}
    _categories: Dict[str, list] = {}
    
    @classmethod
    def register(
        cls,
        type_name: str,
        model_class: Type,
        renderer_class: Optional[Type] = None,
        editor_class: Optional[Type] = None,
        display_name: str = "",
        icon: str = "",
        category: str = "basic",
        default_props: Optional[Dict[str, Any]] = None
    ):
        """注册组件类型。
        
        Args:
            type_name: 组件类型标识符
            model_class: 组件模型类
            renderer_class: 渲染器类（可选）
            editor_class: 属性编辑器类（可选）
            display_name: 显示名称
            icon: 图标
            category: 分类
            default_props: 默认属性
            
        ## 修复说明 (2026-04-02 MCP架构审查)
        统一的注册入口，替代原来分散在多个模块的注册逻辑。
        """
        meta = ComponentMeta(
            type_name=type_name,
            model_class=model_class,
            renderer_class=renderer_class,
            editor_class=editor_class,
            display_name=display_name or type_name.capitalize(),
            icon=icon,
            category=category,
            default_props=default_props or {}
        )
        
        cls._components[type_name] = meta
        
        # 更新分类索引
        if category not in cls._categories:
            cls._categories[category] = []
        if type_name not in cls._categories[category]:
            cls._categories[category].append(type_name)
    
    @classmethod
    def unregister(cls, type_name: str):
        """注销组件类型。
        
        Args:
            type_name: 组件类型标识符
        """
        if type_name in cls._components:
            meta = cls._components.pop(type_name)
            # 从分类中移除
            if meta.category in cls._categories:
                if type_name in cls._categories[meta.category]:
                    cls._categories[meta.category].remove(type_name)
    
    @classmethod
    def get_meta(cls, type_name: str) -> Optional[ComponentMeta]:
        """获取组件元数据。
        
        Args:
            type_name: 组件类型标识符
            
        Returns:
            组件元数据，未找到返回 None
        """
        return cls._components.get(type_name)
    
    @classmethod
    def get_model_class(cls, type_name: str) -> Optional[Type]:
        """获取组件模型类。
        
        Args:
            type_name: 组件类型标识符
            
        Returns:
            模型类，未找到返回 None
        """
        meta = cls._components.get(type_name)
        return meta.model_class if meta else None
    
    @classmethod
    def get_renderer_class(cls, type_name: str) -> Optional[Type]:
        """获取渲染器类。
        
        Args:
            type_name: 组件类型标识符
            
        Returns:
            渲染器类，未找到返回 None
        """
        meta = cls._components.get(type_name)
        return meta.renderer_class if meta else None
    
    @classmethod
    def get_editor_class(cls, type_name: str) -> Optional[Type]:
        """获取属性编辑器类。
        
        Args:
            type_name: 组件类型标识符
            
        Returns:
            编辑器类，未找到返回 None
        """
        meta = cls._components.get(type_name)
        return meta.editor_class if meta else None
    
    @classmethod
    def create_model(cls, type_name: str, **kwargs) -> Any:
        """创建组件模型实例。
        
        Args:
            type_name: 组件类型标识符
            **kwargs: 传递给模型构造函数的参数
            
        Returns:
            模型实例
            
        Raises:
            ValueError: 组件类型未注册
        """
        model_class = cls.get_model_class(type_name)
        if model_class is None:
            raise ValueError(f"未注册的组件类型: {type_name}")
        
        # 合并默认属性
        meta = cls._components.get(type_name)
        if meta and meta.default_props:
            defaults = meta.default_props.copy()
            defaults.update(kwargs)
            kwargs = defaults
        
        return model_class(**kwargs)
    
    @classmethod
    def get_all_types(cls) -> list:
        """获取所有注册的组件类型。
        
        Returns:
            组件类型标识符列表
        """
        return list(cls._components.keys())
    
    @classmethod
    def get_types_by_category(cls, category: str) -> list:
        """获取指定分类的所有组件类型。
        
        Args:
            category: 组件分类
            
        Returns:
            组件类型标识符列表
        """
        return cls._categories.get(category, []).copy()
    
    @classmethod
    def get_all_categories(cls) -> list:
        """获取所有组件分类。
        
        Returns:
            分类名称列表
        """
        return list(cls._categories.keys())
    
    @classmethod
    def is_registered(cls, type_name: str) -> bool:
        """检查组件类型是否已注册。
        
        Args:
            type_name: 组件类型标识符
            
        Returns:
            是否已注册
        """
        return type_name in cls._components
    
    @classmethod
    def clear(cls):
        """清空所有注册信息。"""
        cls._components.clear()
        cls._categories.clear()
    
    @classmethod
    def get_display_name(cls, type_name: str) -> str:
        """获取组件显示名称。
        
        Args:
            type_name: 组件类型标识符
            
        Returns:
            显示名称，未找到返回类型名
        """
        meta = cls._components.get(type_name)
        return meta.display_name if meta else type_name
    
    @classmethod
    def update_renderer(cls, type_name: str, renderer_class: Type):
        """更新组件的渲染器类。
        
        Args:
            type_name: 组件类型标识符
            renderer_class: 新的渲染器类
        """
        if type_name in cls._components:
            cls._components[type_name].renderer_class = renderer_class
    
    @classmethod
    def update_editor(cls, type_name: str, editor_class: Type):
        """更新组件的属性编辑器类。
        
        Args:
            type_name: 组件类型标识符
            editor_class: 新的编辑器类
        """
        if type_name in cls._components:
            cls._components[type_name].editor_class = editor_class


def register_component(
    type_name: str,
    renderer_class: Optional[Type] = None,
    editor_class: Optional[Type] = None,
    display_name: str = "",
    icon: str = "",
    category: str = "basic",
    default_props: Optional[Dict[str, Any]] = None
):
    """组件注册装饰器。
    
    用于简化组件注册，在模型类定义时自动注册。
    
    Args:
        type_name: 组件类型标识符
        renderer_class: 渲染器类（可选）
        editor_class: 属性编辑器类（可选）
        display_name: 显示名称
        icon: 图标
        category: 分类
        default_props: 默认属性
        
    Returns:
        装饰器函数
        
    ## 修复说明 (2026-04-02 MCP架构审查)
    提供装饰器方式注册，简化组件开发。
    
    使用示例:
        @register_component('button', category='basic')
        class ButtonModel(ComponentModel):
            pass
    """
    def decorator(model_class: Type) -> Type:
        ComponentRegistry.register(
            type_name=type_name,
            model_class=model_class,
            renderer_class=renderer_class,
            editor_class=editor_class,
            display_name=display_name,
            icon=icon,
            category=category,
            default_props=default_props
        )
        return model_class
    return decorator


def auto_register_from_module(module_name: str):
    """自动从模块中注册组件。
    
    扫描指定模块，自动注册带有 @register_component 装饰器的类。
    
    Args:
        module_name: 模块名称
        
    ## 修复说明 (2026-04-02 MCP架构审查)
    支持插件系统，自动发现和注册组件。
    """
    import importlib
    
    try:
        module = importlib.import_module(module_name)
        # 装饰器会自动注册，这里只需要导入模块即可
    except ImportError as e:
        raise ImportError(f"无法导入模块 {module_name}: {e}")
