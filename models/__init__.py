"""模型层模块，包含所有数据模型定义。"""

from .base import ComponentModel, ProjectModel, ActionConfig, StyleConfig
from .components import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ProgressBarModel,
    create_component, COMPONENT_TYPE_MAP
)
from .window import WindowModel, WindowType, ActionType, ActionDefinition, DEFAULT_ACTIONS
from .variable_system import (
    VariableManager, Variable, VariableType,
    get_variable_manager
)
from .communication_system import (
    CommunicationManager, SignalConnection, CommunicationChannel,
    SignalType, ActionType as CommActionType,
    get_communication_manager
)

__all__ = [
    'ComponentModel',
    'ProjectModel',
    'ActionConfig',
    'StyleConfig',
    'ButtonModel',
    'LabelModel',
    'InputModel',
    'ContainerModel',
    'CheckBoxModel',
    'ComboBoxModel',
    'ProgressBarModel',
    'create_component',
    'COMPONENT_TYPE_MAP',
    'WindowModel',
    'WindowType',
    'ActionType',
    'ActionDefinition',
    'DEFAULT_ACTIONS',
    'VariableManager',
    'Variable',
    'VariableType',
    'get_variable_manager',
    'CommunicationManager',
    'SignalConnection',
    'CommunicationChannel',
    'SignalType',
    'CommActionType',
    'get_communication_manager',
]
