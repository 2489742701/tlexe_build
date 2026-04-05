"""属性编辑器模块。

本模块包含属性面板相关的类和注册表，用于解耦属性面板与具体模型类的依赖。

## 修复说明 (2026-04-02)
【问题】PropertyPanel 直接依赖所有具体模型类，新增组件类型需要修改导入。

【解决方案】使用注册表模式（Registry Pattern），创建 PropertyEditorRegistry
动态管理属性编辑器的注册和获取。

## 修复说明 (2026-04-02 MCP 启动缓存审查)
【新增】提供 register_property_editor 装饰器，支持自动注册。
【新增】提供 PropertyEditorRegistry 注册表类，支持状态查询。
"""

from .property_registry import PropertyEditorRegistry
from .base_editor import BasePropertyEditor
from .registry import register_property_editor

__all__ = [
    'PropertyEditorRegistry',
    'BasePropertyEditor',
    'register_property_editor',
]
