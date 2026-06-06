"""属性编辑器模块。

本模块包含属性面板相关的类和注册表，用于解耦属性面板与具体模型类的依赖。
使用注册表模式（Registry Pattern）动态管理属性编辑器的注册和获取。
"""

from .registry import PropertyEditorRegistry, register_property_editor
from .base_editor import BasePropertyEditor

__all__ = [
    'PropertyEditorRegistry',
    'BasePropertyEditor',
    'register_property_editor',
]
