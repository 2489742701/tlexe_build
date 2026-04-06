"""视图层模块，包含所有视图组件。

## 修复说明 (2026-04-02)
将 property_panel 目录重命名为 property_editors，
避免与 property_panel.py 文件产生命名冲突。

## 修复说明 (2026-04-06)
新增 SplashWindow 启动画面组件。
"""

from .main_window import MainWindow
from .canvas import DesignerView, DesignerScene, ComponentGraphicsItem
from .property_panel import PropertyPanel

# 从 property_editors 目录导入注册表相关类
from .property_editors import PropertyEditorRegistry, BasePropertyEditor

from .component_tree import ComponentTreeView
from .logic_tree import LogicTreeView
from .welcome_page import WelcomePage
from .component_panel import ComponentPanel
from .signal_manager import SignalManagerPanel, SignalEditDialog
from .state_machine_view import StateMachineView, StateMachineModel, StateNodeData, TransitionData
from .splash_window import SplashWindow

__all__ = [
    'MainWindow',
    'DesignerView',
    'DesignerScene',
    'ComponentGraphicsItem',
    'PropertyPanel',
    'PropertyEditorRegistry',
    'BasePropertyEditor',
    'ComponentTreeView',
    'LogicTreeView',
    'WelcomePage',
    'ComponentPanel',
    'SignalManagerPanel',
    'SignalEditDialog',
    'StateMachineView',
    'StateMachineModel',
    'StateNodeData',
    'TransitionData',
    'SplashWindow',
]
