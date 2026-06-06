"""模型层模块，包含所有数据模型定义。"""

from .base import ComponentModel, ProjectModel, ActionConfig, StyleConfig
from .components import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ImageModel, VideoModel, ProgressBarModel,
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel,
    AlternatingModel, TextAlternatingModel, ImageAlternatingModel,
    GroupNodeModel,
    create_component
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
    RegistrationConsistencyReport,
    register_component,
    auto_register_from_module
)
from .registry_init import register_all_components
from .model_helpers import (
    ObservableProperty,
    PositionProperty,
    SizeProperty,
    validated_property,
    SignalBlocker
)
from .tech_components import (
    TechComponentManager,
    TechComponentTemplate,
    TECH_TEMPLATES
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
    'AlternatingModel',
    'TextAlternatingModel',
    'ImageAlternatingModel',
    'ConfirmButtonModel',
    'GroupNodeModel',
    'create_component',
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
    'RegistrationConsistencyReport',
    'register_component',
    'auto_register_from_module',
    'register_all_components',
    # 新增：模型辅助工具
    'ObservableProperty',
    'PositionProperty',
    'SizeProperty',
    'validated_property',
    'SignalBlocker',
    # 新增：技术类控件
    'TechComponentManager',
    'TechComponentTemplate',
    'TECH_TEMPLATES',
]
