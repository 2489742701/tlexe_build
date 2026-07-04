"""模型层模块，包含所有数据模型定义。"""

from .schemas import (
    ActionType, WindowType, VariableType, SignalType, CommActionType,
    StyleConfig, ActionConfig, ActionDefinition, VariableSchema,
    BindingConfig, ConditionalActionConfig,
    SignalConnectionSchema, CommunicationChannelSchema,
    DEFAULT_ACTIONS,
)
from .base import ComponentModel, ProjectModel, SignalProperty
from .components import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ImageModel, VideoModel, ProgressBarModel,
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel,
    AlternatingModel, GroupNodeModel, ConfirmButtonModel,
    # 新增独立 Model 类（以前错误地复用其他类型）
    TextAreaModel, ListWidgetModel, GroupBoxModel,
    create_component,
)
from .window import WindowModel
from .variable_system import VariableManager, get_variable_manager
from .variable_binding import VariableBinding, BindingManager
from .communication_system import CommunicationManager, get_communication_manager
from .component_registry import (
    ComponentRegistry, ComponentMeta,
    RegistrationConsistencyReport,
    register_component, auto_register_from_module, scan_plugin_directory,
)
from .registry_init import register_all_components
from .model_helpers import SignalBlocker
from .tech_components import TechComponentManager, TechComponentTemplate, TECH_TEMPLATES

__all__ = [
    'ActionType', 'WindowType', 'VariableType', 'SignalType', 'CommActionType',
    'StyleConfig', 'ActionConfig', 'ActionDefinition', 'VariableSchema',
    'BindingConfig', 'ConditionalActionConfig',
    'SignalConnectionSchema', 'CommunicationChannelSchema',
    'DEFAULT_ACTIONS',
    'ComponentModel', 'ProjectModel', 'SignalProperty',
    'ButtonModel', 'LabelModel', 'InputModel', 'ContainerModel',
    'CheckBoxModel', 'ComboBoxModel', 'ImageModel', 'VideoModel', 'ProgressBarModel',
    'HiddenButtonModel', 'ImageButtonModel', 'ImageCarouselModel',
    'AlternatingModel',
    'ConfirmButtonModel', 'GroupNodeModel',
    # 新增独立 Model 类
    'TextAreaModel', 'ListWidgetModel', 'GroupBoxModel',
    'create_component',
    'WindowModel',
    'VariableManager', 'get_variable_manager',
    'VariableBinding', 'BindingManager',
    'CommunicationManager', 'get_communication_manager',
    'ComponentRegistry', 'ComponentMeta', 'RegistrationConsistencyReport',
    'register_component', 'auto_register_from_module', 'scan_plugin_directory',
    'register_all_components',
    'SignalBlocker',
    'TechComponentManager', 'TechComponentTemplate', 'TECH_TEMPLATES',
]
