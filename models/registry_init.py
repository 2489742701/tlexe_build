"""统一注册初始化模块。

本模块是组件注册的唯一入口，在应用启动时由 AppInitializer 调用。
将所有组件类型集中注册到 ComponentRegistry，替代分散在多处的映射表。

使用延迟导入策略（函数内 import）避免模块级循环依赖。

调用方式：
    from models.registry_init import register_all_components
    register_all_components()
"""

import logging

logger = logging.getLogger(__name__)


_registry_initialized = False

def register_all_components():
    """注册所有组件类型到 ComponentRegistry。
    
    此函数是组件注册的唯一入口，确保：
    1. 所有基础组件类型均已注册
    2. 每个组件的 model_class、renderer_class、editor_class 均已关联
    3. 注册顺序与现有 COMPONENT_TYPE_MAP 和 RendererFactory 一致
    
    应在应用启动时、RendererFactory.preload_all() 之前调用。
    """
    global _registry_initialized
    if _registry_initialized:
        return
    _registry_initialized = True
    
    from models.component_registry import ComponentRegistry
    from models.components import (
        ButtonModel, LabelModel, InputModel, ContainerModel,
        CheckBoxModel, ComboBoxModel, ImageModel, VideoModel,
        ProgressBarModel, HiddenButtonModel, ImageButtonModel,
        ImageCarouselModel, LotteryModel, GroupNodeModel,
        TextAlternatingModel, ImageAlternatingModel, ConfirmButtonModel
    )
    
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
    from renderers.lottery_renderer import LotteryRenderer
    from renderers.alternating_renderer import AlternatingRenderer
    from renderers.image_renderer import ImageRenderer
    from renderers.video_renderer import VideoRenderer
    
    _register_basic_components(ComponentRegistry, {
        'ButtonModel': ButtonModel, 'LabelModel': LabelModel,
        'InputModel': InputModel, 'ContainerModel': ContainerModel,
        'CheckBoxModel': CheckBoxModel, 'ComboBoxModel': ComboBoxModel,
        'ImageModel': ImageModel, 'VideoModel': VideoModel,
        'ProgressBarModel': ProgressBarModel, 'HiddenButtonModel': HiddenButtonModel,
        'ImageButtonModel': ImageButtonModel, 'ImageCarouselModel': ImageCarouselModel,
        'LotteryModel': LotteryModel, 'GroupNodeModel': GroupNodeModel,
        'TextAlternatingModel': TextAlternatingModel, 'ImageAlternatingModel': ImageAlternatingModel,
        'ConfirmButtonModel': ConfirmButtonModel,
    }, {
        'ButtonRenderer': ButtonRenderer, 'LabelRenderer': LabelRenderer,
        'InputRenderer': InputRenderer, 'ContainerRenderer': ContainerRenderer,
        'CheckBoxRenderer': CheckBoxRenderer, 'ComboBoxRenderer': ComboBoxRenderer,
        'ProgressBarRenderer': ProgressBarRenderer, 'HiddenButtonRenderer': HiddenButtonRenderer,
        'ImageButtonRenderer': ImageButtonRenderer, 'ImageCarouselRenderer': ImageCarouselRenderer,
        'LotteryRenderer': LotteryRenderer, 'AlternatingRenderer': AlternatingRenderer,
        'ImageRenderer': ImageRenderer, 'VideoRenderer': VideoRenderer,
    })
    
    _register_editors(ComponentRegistry)
    
    logger.info(
        f"统一注册完成: 共注册 {len(ComponentRegistry.get_all_types())} 个组件类型"
    )


def _register_basic_components(CR, models, renderers):
    """注册基础组件类型。"""
    CR.register(
        type_name='button',
        model_class=models['ButtonModel'],
        renderer_class=renderers['ButtonRenderer'],
        display_name='按钮',
        category='basic',
        description='可点击的按钮组件，支持文本、样式和动作配置'
    )
    CR.register(
        type_name='label',
        model_class=models['LabelModel'],
        renderer_class=renderers['LabelRenderer'],
        display_name='标签',
        category='basic',
        description='文本标签组件，支持文字抽奖动画'
    )
    CR.register(
        type_name='input',
        model_class=models['InputModel'],
        renderer_class=renderers['InputRenderer'],
        display_name='输入框',
        category='input',
        description='单行文本输入框'
    )
    CR.register(
        type_name='container',
        model_class=models['ContainerModel'],
        renderer_class=renderers['ContainerRenderer'],
        display_name='容器',
        category='container',
        description='布局容器，支持子组件嵌套和多种布局模式'
    )
    CR.register(
        type_name='checkbox',
        model_class=models['CheckBoxModel'],
        renderer_class=renderers['CheckBoxRenderer'],
        display_name='复选框',
        category='input',
        description='可勾选的复选框组件'
    )
    CR.register(
        type_name='combobox',
        model_class=models['ComboBoxModel'],
        renderer_class=renderers['ComboBoxRenderer'],
        display_name='下拉框',
        category='input',
        description='下拉选择框组件'
    )
    CR.register(
        type_name='progressbar',
        model_class=models['ProgressBarModel'],
        renderer_class=renderers['ProgressBarRenderer'],
        display_name='进度条',
        category='basic',
        description='进度指示条组件'
    )
    CR.register(
        type_name='image',
        model_class=models['ImageModel'],
        renderer_class=renderers['ImageRenderer'],
        display_name='图片',
        category='basic',
        description='图片显示组件'
    )
    CR.register(
        type_name='video',
        model_class=models['VideoModel'],
        renderer_class=renderers['VideoRenderer'],
        display_name='视频',
        category='basic',
        description='视频播放组件'
    )
    CR.register(
        type_name='image_carousel',
        model_class=models['ImageCarouselModel'],
        renderer_class=renderers['ImageCarouselRenderer'],
        display_name='图片轮播',
        category='basic',
        description='图片轮播组件，支持图片抽奖动画'
    )
    CR.register(
        type_name='lottery',
        model_class=models['LotteryModel'],
        renderer_class=renderers['LotteryRenderer'],
        display_name='抽奖',
        category='basic',
        description='独立抽奖组件，支持图片/文字双模式抽奖动画'
    )
    CR.register(
        type_name='hidden_button',
        model_class=models['HiddenButtonModel'],
        renderer_class=renderers['HiddenButtonRenderer'],
        display_name='隐藏按钮',
        category='basic',
        description='不可见的触发按钮，用于事件联动'
    )
    CR.register(
        type_name='image_button',
        model_class=models['ImageButtonModel'],
        renderer_class=renderers['ImageButtonRenderer'],
        display_name='图片按钮',
        category='basic',
        description='用图片作为外观的按钮组件'
    )
    CR.register(
        type_name='group_node',
        model_class=models['GroupNodeModel'],
        display_name='组节点',
        category='container',
        description='逻辑分组节点，用于组织组件层级'
    )
    CR.register(
        type_name='text_alternating',
        model_class=models['TextAlternatingModel'],
        renderer_class=renderers['AlternatingRenderer'],
        display_name='文字交替变换',
        category='basic',
        description='文字组交替变换组件，支持开始/停止信号控制'
    )
    CR.register(
        type_name='image_alternating',
        model_class=models['ImageAlternatingModel'],
        renderer_class=renderers['AlternatingRenderer'],
        display_name='图片交替变换',
        category='basic',
        description='图片组交替变换组件，支持开始/停止信号控制'
    )
    CR.register(
        type_name='textarea',
        model_class=models['InputModel'],
        renderer_class=renderers['InputRenderer'],
        display_name='多行文本框',
        category='input',
        description='多行文本输入框'
    )
    CR.register(
        type_name='listwidget',
        model_class=models['ComboBoxModel'],
        renderer_class=renderers['ComboBoxRenderer'],
        display_name='列表控件',
        category='input',
        description='列表选择控件'
    )
    CR.register(
        type_name='groupbox',
        model_class=models['ContainerModel'],
        renderer_class=renderers['ContainerRenderer'],
        display_name='分组框',
        category='container',
        description='带标题的分组容器'
    )
    CR.register(
        type_name='confirm_button',
        model_class=models['ConfirmButtonModel'],
        renderer_class=renderers['ButtonRenderer'],
        display_name='确认按钮',
        category='basic',
        description='同组按钮全部按下后才触发的确认按钮'
    )


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
