"""统一注册初始化模块。

本模块是组件注册的唯一入口，在应用启动时由 AppInitializer 调用。
将所有组件类型集中注册到 ComponentRegistry，替代分散在多处的映射表。

使用延迟导入策略（函数内 import）避免模块级循环依赖。

调用方式：
    from models.registry_init import register_all_components
    register_all_components()

## 插件支持
在应用目录下创建 plugins/ 文件夹，放入带有 @register_component 装饰器的 .py 文件，
应用启动时会自动扫描并注册。无需修改此文件。
"""

import logging
import os

logger = logging.getLogger(__name__)

_registry_initialized = False

def register_all_components():
    """注册所有组件类型到 ComponentRegistry。
    
    此函数是组件注册的唯一入口，确保：
    1. 所有基础组件类型均已注册
    2. 每个组件的 model_class、renderer_class、factory_func、update_func 均已关联
    3. 注册顺序与现有 COMPONENT_TYPE_MAP 和 RendererFactory 一致
    
    应在应用启动时、RendererFactory.preload_all() 之前调用。
    """
    global _registry_initialized
    if _registry_initialized:
        return
    _registry_initialized = True
    
    from models.component_registry import ComponentRegistry
    
    # ── 模型类 ──────────────────────────────────────────────────────────────
    from models.components import (
        ButtonModel, LabelModel, InputModel, ContainerModel,
        CheckBoxModel, ComboBoxModel, ImageModel, VideoModel,
        ProgressBarModel, HiddenButtonModel, ImageButtonModel,
        ImageCarouselModel, GroupNodeModel,
        AlternatingModel, ConfirmButtonModel,
        # 新增独立 Model 类（修复旧版别名注册的问题）
        TextAreaModel, ListWidgetModel, GroupBoxModel,
    )
    
    # ── 渲染器类 ────────────────────────────────────────────────────────────
    from renderers.button_renderer import ButtonRenderer
    from renderers.label_renderer import LabelRenderer
    from renderers.input_renderer import InputRenderer
    from renderers.container_renderer import ContainerRenderer
    from renderers.checkbox_renderer import CheckBoxRenderer
    from renderers.combobox_renderer import ComboBoxRenderer
    from renderers.progressbar_renderer import ProgressBarRenderer
    from renderers.hidden_button_renderer import HiddenButtonRenderer
    from renderers.image_button_renderer import ImageButtonRenderer
    from renderers.image_carousel_renderer import ImageCarouselRenderer
    from renderers.alternating_renderer import AlternatingRenderer
    from renderers.image_renderer import ImageRenderer
    from renderers.video_renderer import VideoRenderer
    from renderers.group_node_renderer import GroupNodeRenderer
    
    # ── 工厂函数 ────────────────────────────────────────────────────────────
    # 从 ComponentFactory 拉取各类型的创建/更新函数，注册进 Registry。
    # 这样 ComponentFactory.create_widget 只需查询 Registry，不再需要维护
    # 硬编码的 creators 字典，新增组件只需在此处注册一次即可。
    from utils.component_factory import ComponentFactory
    
    _register_all(ComponentRegistry, {
        'ButtonModel': ButtonModel, 'LabelModel': LabelModel,
        'InputModel': InputModel, 'ContainerModel': ContainerModel,
        'CheckBoxModel': CheckBoxModel, 'ComboBoxModel': ComboBoxModel,
        'ImageModel': ImageModel, 'VideoModel': VideoModel,
        'ProgressBarModel': ProgressBarModel, 'HiddenButtonModel': HiddenButtonModel,
        'ImageButtonModel': ImageButtonModel, 'ImageCarouselModel': ImageCarouselModel,
        'GroupNodeModel': GroupNodeModel,
        'AlternatingModel': AlternatingModel,
        'ConfirmButtonModel': ConfirmButtonModel,
        # 新增独立 Model 类
        'TextAreaModel': TextAreaModel,
        'ListWidgetModel': ListWidgetModel,
        'GroupBoxModel': GroupBoxModel,
    }, {
        'ButtonRenderer': ButtonRenderer, 'LabelRenderer': LabelRenderer,
        'InputRenderer': InputRenderer, 'ContainerRenderer': ContainerRenderer,
        'CheckBoxRenderer': CheckBoxRenderer, 'ComboBoxRenderer': ComboBoxRenderer,
        'ProgressBarRenderer': ProgressBarRenderer, 'HiddenButtonRenderer': HiddenButtonRenderer,
        'ImageButtonRenderer': ImageButtonRenderer,
        'ImageCarouselRenderer': ImageCarouselRenderer,
        'AlternatingRenderer': AlternatingRenderer,
        'ImageRenderer': ImageRenderer, 'VideoRenderer': VideoRenderer,
        'GroupNodeRenderer': GroupNodeRenderer,
    }, ComponentFactory)
    
    _register_editors(ComponentRegistry)
    
    # ── 插件目录扫描 ────────────────────────────────────────────────────────
    # 扫描 plugins/ 目录，自动加载第三方组件插件。
    # 插件只需用 @register_component 装饰模型类，无需修改此文件。
    _scan_plugins(ComponentRegistry)
    
    logger.info(
        f"统一注册完成: 共注册 {len(ComponentRegistry.get_all_types())} 个组件类型"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 私有辅助函数
# ─────────────────────────────────────────────────────────────────────────────

def _register_all(CR, models: dict, renderers: dict, factory_cls):
    """注册所有内置组件，包括模型、渲染器、工厂函数和图标。"""
    
    # 图标映射（使用 emoji 作为轻量级默认图标，UI 层可根据 icon 字段替换为正式图片）
    ICONS = {
        'button':            '🔲',
        'label':             '🏷️',
        'input':             '📝',
        'textarea':          '📄',
        'checkbox':          '☑️',
        'combobox':          '📋',
        'listwidget':        '📃',
        'groupbox':          '📦',
        'container':         '🗂️',
        'progressbar':       '📊',
        'image':             '🖼️',
        'video':             '🎬',
        'image_carousel':    '🎠',
        'lottery':           '🎰',
        'hidden_button':     '👻',
        'image_button':      '🖼️',
        'group_node':        '🗃️',
        'text_alternating':  '🔄',
        'image_alternating': '🔀',
        'confirm_button':    '✅',
    }

    # 默认属性映射（这些值在 ComponentRegistry.create_model 时会自动合并为 kwargs 默认值）
    DEFAULT_PROPS = {
        'button':         {'width': 120, 'height': 40, 'text': '按钮'},
        'label':          {'width': 120, 'height': 30, 'text': '文本'},
        'input':          {'width': 200, 'height': 30},
        'textarea':       {'width': 200, 'height': 80},
        'checkbox':       {'width': 120, 'height': 24, 'text': '复选框'},
        'combobox':       {'width': 150, 'height': 28},
        'listwidget':     {'width': 200, 'height': 150},
        'groupbox':       {'width': 200, 'height': 150, 'text': '分组'},
        'container':      {'width': 400, 'height': 300},
        'progressbar':    {'width': 200, 'height': 24},
        'image':          {'width': 200, 'height': 150},
        'video':          {'width': 400, 'height': 300},
        'image_carousel': {'width': 300, 'height': 200},
        'hidden_button':  {'width': 100, 'height': 100},
        'image_button':   {'width': 120, 'height': 40},
    }
    
    # 工厂函数映射（从 ComponentFactory 的静态方法注册进 Registry）
    # 这消除了 ComponentFactory.create_widget 内部 creators 字典的维护负担
    FACTORY_FUNCS = {
        'button':            factory_cls._create_button,
        'label':             factory_cls._create_label,
        'input':             factory_cls._create_input,
        'textarea':          factory_cls._create_textarea,
        'checkbox':          factory_cls._create_checkbox,
        'combobox':          factory_cls._create_combobox,
        'listwidget':        factory_cls._create_listwidget,
        'groupbox':          factory_cls._create_groupbox,
        'container':         factory_cls._create_container,
        'progressbar':       factory_cls._create_progressbar,
        'image':             factory_cls._create_image,
        'video':             factory_cls._create_video,
        'image_carousel':    factory_cls._create_image_carousel,
        'hidden_button':     factory_cls._create_hidden_button,
        'image_button':      factory_cls._create_image_button,
        'group_node':        factory_cls._create_group_node,
        'text_alternating':  factory_cls._create_alternating,
        'image_alternating': factory_cls._create_alternating,
        'confirm_button':    factory_cls._create_confirm_button,
    }

    _do_register(CR, models, renderers, ICONS, DEFAULT_PROPS, FACTORY_FUNCS)

def _do_register(CR, models, renderers, icons, default_props, factory_funcs):
    """执行实际注册。"""

    def _r(type_name, model_key, renderer_key=None, display_name='', category='basic', description=''):
        CR.register(
            type_name=type_name,
            model_class=models[model_key],
            renderer_class=renderers.get(renderer_key) if renderer_key else None,
            factory_func=factory_funcs.get(type_name),
            display_name=display_name,
            icon=icons.get(type_name, ''),
            category=category,
            default_props=default_props.get(type_name, {}),
            description=description,
        )

    # ── 基础控件 ──
    _r('button',         'ButtonModel',        'ButtonRenderer',        '按钮',       'basic',     '可点击的按钮组件，支持文本、样式和动作配置')
    _r('label',          'LabelModel',         'LabelRenderer',         '标签',       'basic',     '文本标签组件，支持文字抽奖动画')
    _r('progressbar',    'ProgressBarModel',   'ProgressBarRenderer',   '进度条',     'basic',     '进度指示条组件')
    _r('image',          'ImageModel',         'ImageRenderer',         '图片',       'basic',     '图片显示组件')
    _r('video',          'VideoModel',         'VideoRenderer',         '视频',       'basic',     '视频播放组件')
    _r('image_carousel', 'ImageCarouselModel', 'ImageCarouselRenderer', '图片轮播',   'basic',     '图片轮播组件，支持图片抽奖动画')
    _r('hidden_button',  'HiddenButtonModel',  'HiddenButtonRenderer',  '隐藏按钮',   'basic',     '不可见的触发按钮，用于事件联动')
    _r('image_button',   'ImageButtonModel',   'ImageButtonRenderer',   '图片按钮',   'basic',     '用图片作为外观的按钮组件')
    _r('confirm_button', 'ConfirmButtonModel', 'ButtonRenderer',        '确认按钮',   'basic',     '同组按钮全部按下后才触发的确认按钮')
    _r('alternating', 'AlternatingModel', 'AlternatingRenderer', '交替变换', 'basic', '交替变换组件，支持文字或图片轮播，支持开始/停止信号控制')
    # 向后兼容
    _r('text_alternating',  'AlternatingModel',  'AlternatingRenderer', '文字交替', 'basic',  '文字组交替变换组件')
    _r('image_alternating', 'AlternatingModel', 'AlternatingRenderer', '图片交替', 'basic', '图片组交替变换组件')

    # ── 输入控件 ──
    _r('input',       'InputModel',    'InputRenderer',    '输入框',   'input',  '单行文本输入框')
    _r('textarea',    'TextAreaModel', 'InputRenderer',    '多行文本', 'input',  '多行文本输入框，支持自动滚动和换行')
    _r('checkbox',    'CheckBoxModel', 'CheckBoxRenderer', '复选框',   'input',  '可勾选的复选框组件')
    _r('combobox',    'ComboBoxModel', 'ComboBoxRenderer', '下拉框',   'input',  '下拉选择框组件')
    _r('listwidget',  'ListWidgetModel', 'ComboBoxRenderer', '列表',   'input',  '列表选择控件，支持单选/多选模式')

    # ── 容器控件 ──
    _r('container',  'ContainerModel', 'ContainerRenderer', '容器',   'container', '布局容器，支持子组件嵌套和多种布局模式')
    _r('groupbox',   'GroupBoxModel',  'ContainerRenderer', '分组框', 'container', '带标题的视觉分组框，可设为可勾选模式')
    _r('group_node', 'GroupNodeModel', 'GroupNodeRenderer', '组节点', 'container', '逻辑分组节点，用于组织组件层级')

def _register_editors(CR):
    """注册属性编辑器到 ComponentRegistry。
    
    使用延迟导入，仅在编辑器已注册到 PropertyEditorRegistry 后关联。
    如果编辑器尚未注册，则跳过（将在后续被装饰器自动关联）。
    """
    try:
        from views.property_editors.registry import PropertyEditorRegistry
        
        editor_types = PropertyEditorRegistry.get_registered_types()
        for comp_type in editor_types:
            editor_class = PropertyEditorRegistry.get_editor(comp_type)
            if editor_class and CR.is_registered(comp_type):
                CR.update_editor(comp_type, editor_class)
    except ImportError:
        logger.debug("PropertyEditorRegistry 尚未导入，编辑器关联将延迟执行")

def _scan_plugins(CR):
    """扫描 plugins/ 目录加载第三方组件插件。
    
    此函数无需修改即可自动发现新插件：
    只需在 plugins/ 目录下放置带 @register_component 装饰器的 .py 文件即可。
    """
    try:
        from models.component_registry import scan_plugin_directory
        
        # 查找 plugins 目录（相对于项目根目录）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plugins_dir = os.path.join(project_root, 'plugins')
        
        loaded = scan_plugin_directory(plugins_dir)
        if loaded:
            logger.info(f"插件目录扫描完成，加载了 {len(loaded)} 个插件: {loaded}")
        else:
            logger.debug(f"插件目录无可用插件: {plugins_dir}")
    except Exception as e:
        logger.warning(f"插件扫描失败（不影响主程序启动）: {e}")
