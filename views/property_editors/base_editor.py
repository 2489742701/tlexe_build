"""属性编辑器基类。

本模块定义属性编辑器的抽象基类，所有具体属性编辑器都需要继承此类。

## 修复说明 (2026-04-02)
【问题】PropertyPanel 直接为每种组件类型创建不同的 UI 控件，
导致代码冗长且难以维护。

【解决方案】定义 BasePropertyEditor 抽象基类，每种组件类型实现
对应的属性编辑器，PropertyPanel 只需调用编辑器的通用接口。

【设计模式】模板方法模式（Template Method Pattern）
- 定义一个操作中的算法骨架，将一些步骤延迟到子类中
- 使得子类可以不改变一个算法的结构即可重定义该算法的某些特定步骤
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

from models import ComponentModel


class BasePropertyEditor(QWidget):
    """属性编辑器基类。
    
    所有组件类型的属性编辑器都需要继承此类。
    
    Signals:
        property_changed: 属性改变时发射 (property_name, old_value, new_value)
        action_config_requested: 请求配置行为时发射
        
    ## 修复说明 (2026-04-02)
    此类是新创建的，作为所有属性编辑器的基类。
    将 PropertyPanel 中的属性编辑逻辑抽取到独立的编辑器类中。
    """
    
    property_changed = Signal(str, object, object)  # property_name, old_value, new_value
    action_config_requested = Signal()
    
    def __init__(self, parent=None):
        """初始化属性编辑器。"""
        super().__init__(parent)
        self._model: Optional[ComponentModel] = None
        self._updating = False  # 防止循环更新
        self._setup_ui()
    
    @abstractmethod
    def _setup_ui(self):
        """设置 UI。
        
        子类需要实现此方法创建具体的属性编辑控件。
        
        ## 修复说明 (2026-04-02)
        从 PropertyPanel._setup_ui 中抽取，
        每种组件类型创建自己的 UI 布局。
        """
        pass
    
    def set_model(self, model: ComponentModel):
        """设置要编辑的模型。
        
        Args:
            model: 组件数据模型
        """
        self._model = model
        self._update_ui_from_model()
    
    @abstractmethod
    def _update_ui_from_model(self):
        """从模型更新 UI。
        
        子类需要实现此方法将模型数据同步到 UI 控件。
        
        ## 修复说明 (2026-04-02)
        从 PropertyPanel 的更新逻辑中抽取。
        """
        pass
    
    def _on_property_changed(self, property_name: str, new_value):
        """处理属性改变。
        
        Args:
            property_name: 属性名
            new_value: 新值
        """
        if self._updating or not self._model:
            return
        
        old_value = getattr(self._model, property_name, None)
        if old_value != new_value:
            setattr(self._model, property_name, new_value)
            self.property_changed.emit(property_name, old_value, new_value)
    
    def get_supported_properties(self) -> list:
        """获取支持的属性列表。
        
        Returns:
            支持的属性名字符串列表
        """
        return []
