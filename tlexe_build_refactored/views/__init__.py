"""视图层模块，包含所有视图组件。

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
from .variable_panel import VariablePanel, get_player_name, set_player_name, get_variable, set_variable

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
    'VariablePanel',
    'get_player_name',
    'set_player_name',
    'get_variable',
    'set_variable',
]
