"""模型层模块，包含所有数据模型定义。"""

from .base import ComponentModel, ProjectModel, ActionConfig, StyleConfig
from .components import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ImageModel, VideoModel, ProgressBarModel,
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel,
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
from .component_registry import (
    ComponentRegistry,
    ComponentMeta,
    register_component,
    auto_register_from_module
)
from .model_helpers import (
    ObservableProperty,
    PositionProperty,
    SizeProperty,
    validated_property,
    SignalBlocker
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
    'ImageModel',
    'VideoModel',
    'ProgressBarModel',
    'HiddenButtonModel',
    'ImageButtonModel',
    'ImageCarouselModel',
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
    # 新增：组件注册中心
    'ComponentRegistry',
    'ComponentMeta',
    'register_component',
    'auto_register_from_module',
    # 新增：模型辅助工具
    'ObservableProperty',
    'PositionProperty',
    'SizeProperty',
    'validated_property',
    'SignalBlocker',
]
