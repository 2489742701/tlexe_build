"""组件注册中心模块。

本模块提供统一的组件注册机制，将组件类型、模型类、渲染器类、
属性编辑器类集中管理，解决分散注册导致的维护问题。

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

from typing import Dict, Type, Optional, Callable, Any, List
from dataclasses import dataclass, field
import logging
import inspect
import re

logger = logging.getLogger(__name__)

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
    description: str = ""
    _registered_at: str = ""
    _registered_from: str = ""
    
    def __post_init__(self):
        if self.default_props is None:
            self.default_props = {}
        if not self.display_name:
            self.display_name = self.type_name.capitalize()

@dataclass
class RegistrationConsistencyReport:
    """注册一致性检测报告。
    
    Attributes:
        type_name: 组件类型标识符
        missing_items: 缺失项列表（取值 "model_class" | "renderer_class" | "editor_class"）
        severity: 严重级别（"WARNING" | "ERROR"）
        suggestion: 修复建议
    """
    type_name: str
    missing_items: List[str]
    severity: str
    suggestion: str

class ComponentRegistry:
    """组件注册中心。
    
    统一管理所有组件类型的元数据，提供统一的注册和查询接口。
    
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
        default_props: Optional[Dict[str, Any]] = None,
        description: str = ""
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
            description: 组件描述（供使用指引使用）
        """
        cls.validate_type_name(type_name)
        
        if type_name in cls._components:
            logger.warning(f"组件类型 {type_name} 被重复注册，原有记录已被覆盖")
        
        from datetime import datetime
        registered_at = datetime.now().isoformat()
        try:
            frame = inspect.currentframe().f_back
            registered_from = frame.f_globals.get('__name__', 'unknown') if frame else 'unknown'
        except Exception:
            registered_from = 'unknown'
        
        meta = ComponentMeta(
            type_name=type_name,
            model_class=model_class,
            renderer_class=renderer_class,
            editor_class=editor_class,
            display_name=display_name or type_name.capitalize(),
            icon=icon,
            category=category,
            default_props=default_props or {},
            description=description,
            _registered_at=registered_at,
            _registered_from=registered_from
        )
        
        cls._components[type_name] = meta
        
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
            
        Raises:
            ValueError: 渲染器类为空或组件类型未注册
        """
        if not renderer_class:
            raise ValueError(f"渲染器类不能为空")
        if type_name not in cls._components:
            raise ValueError(f"组件类型 {type_name} 未注册，无法更新渲染器")
        cls._components[type_name].renderer_class = renderer_class
    
    @classmethod
    def update_editor(cls, type_name: str, editor_class: Type):
        """更新组件的属性编辑器类。
        
        Args:
            type_name: 组件类型标识符
            editor_class: 新的编辑器类
            
        Raises:
            ValueError: 编辑器类为空或组件类型未注册
        """
        if not editor_class:
            raise ValueError(f"编辑器类不能为空")
        if type_name not in cls._components:
            raise ValueError(f"组件类型 {type_name} 未注册，无法更新编辑器")
        cls._components[type_name].editor_class = editor_class
    
    @classmethod
    def get_all_meta(cls) -> Dict[str, 'ComponentMeta']:
        """获取所有组件元数据的浅拷贝。
        
        Returns:
            组件元数据字典副本
        """
        return dict(cls._components)
    
    @classmethod
    def validate_type_name(cls, type_name: str):
        """验证组件类型标识符合法性。
        
        Args:
            type_name: 组件类型标识符
            
        Raises:
            ValueError: 标识符不合法
        """
        if not re.match(r'^[a-z0-9_]{1,50}$', type_name):
            raise ValueError(
                f"组件类型标识符 '{type_name}' 不合法，"
                f"仅允许小写字母、数字、下划线，长度1-50"
            )
    
    @classmethod
    def check_registration_consistency(cls) -> List['RegistrationConsistencyReport']:
        """检查注册一致性。
        
        遍历所有已注册组件，检查 model_class/renderer_class/editor_class 是否完整。
        
        Returns:
            一致性检测报告列表，空列表表示全部一致
        """
        reports = []
        for type_name, meta in cls._components.items():
            missing_items = []
            if meta.model_class is None:
                missing_items.append("model_class")
            if meta.renderer_class is None:
                missing_items.append("renderer_class")
            if meta.editor_class is None:
                missing_items.append("editor_class")
            
            if not missing_items:
                continue
            
            if meta.model_class is None:
                severity = "ERROR"
            else:
                severity = "WARNING"
            
            suggestion = f"请在 ComponentRegistry 中为 {type_name} 注册 {', '.join(missing_items)}"
            
            reports.append(RegistrationConsistencyReport(
                type_name=type_name,
                missing_items=missing_items,
                severity=severity,
                suggestion=suggestion
            ))
        
        return reports

def register_component(
    type_name: str,
    renderer_class: Optional[Type] = None,
    editor_class: Optional[Type] = None,
    display_name: str = "",
    icon: str = "",
    category: str = "basic",
    default_props: Optional[Dict[str, Any]] = None,
    description: str = ""
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
        description: 组件描述
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
            default_props=default_props,
            description=description
        )
        return model_class
    return decorator

def auto_register_from_module(module_name: str):
    """自动从模块中注册组件。
    
    扫描指定模块，自动注册带有 @register_component 装饰器的类。
    
    Args:
        module_name: 模块名称
        
    """
    import importlib
    
    try:
        module = importlib.import_module(module_name)
        # 装饰器会自动注册，这里只需要导入模块即可
    except ImportError as e:
        raise ImportError(f"无法导入模块 {module_name}: {e}")


def scan_plugin_directory(plugin_dir: str):
    from pathlib import Path
    import sys
    import pkgutil
    import importlib.util
    import logging
    
    logger = logging.getLogger(__name__)
    plugin_path = Path(plugin_dir)
    if not plugin_path.exists() or not plugin_path.is_dir():
        logger.debug(f"目录不存在或非目录: {plugin_dir}")
        return []
        
    loaded = []
    
    plugin_dir_str = str(plugin_path.resolve())
    if plugin_dir_str not in sys.path:
        sys.path.insert(0, plugin_dir_str)
        
    for finder, module_name, is_pkg in pkgutil.iter_modules([plugin_dir_str]):
        full_name = f"plugin_{module_name}"
        try:
            spec = importlib.util.spec_from_file_location(full_name, plugin_path / f"{module_name}.py")
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                loaded.append(module_name)
                logger.info(f"加载成功: {module_name}")
        except Exception as e:
            logger.warning(f"加载失败: {module_name} -> {e}")
            
    return loaded
