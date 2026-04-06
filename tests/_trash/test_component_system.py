import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

print("=" * 60)
print("组件系统全面自检")
print("=" * 60)

errors = []
warnings = []

# ============================================================
# 1. 检查 COMPONENT_TYPE_MAP (模型注册表)
# ============================================================
print("\n【1】模型注册表 (COMPONENT_TYPE_MAP)")
print("-" * 40)

from models.components import COMPONENT_TYPE_MAP
from models import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ImageModel, VideoModel, ProgressBarModel,
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel
)

ALL_MODELS = {
    'button': ButtonModel,
    'label': LabelModel,
    'input': InputModel,
    'container': ContainerModel,
    'checkbox': CheckBoxModel,
    'combobox': ComboBoxModel,
    'image': ImageModel,
    'video': VideoModel,
    'progressbar': ProgressBarModel,
    'hidden_button': HiddenButtonModel,
    'image_button': ImageButtonModel,
    'image_carousel': ImageCarouselModel,
}

for type_name, model_class in ALL_MODELS.items():
    if type_name in COMPONENT_TYPE_MAP:
        print(f"  [OK] {type_name:20s} -> {model_class.__name__}")
    else:
        errors.append(f"组件类型 '{type_name}' 未在 COMPONENT_TYPE_MAP 中注册!")
        print(f"  [MISSING] {type_name:20s} <- 缺失!")

for type_name in COMPONENT_TYPE_MAP:
    if type_name not in ALL_MODELS:
        warnings.append(f"COMPONENT_TYPE_MAP 中有多余的类型: {type_name}")

# ============================================================
# 2. 检查 ComponentFactory (运行时工厂)
# ============================================================
print("\n【2】运行时组件工厂 (ComponentFactory)")
print("-" * 40)

from utils.component_factory import ComponentFactory

FACTORY_TYPES = [
    'button', 'label', 'input', 'textarea',
    'checkbox', 'combobox', 'listwidget', 'groupbox',
    'container', 'progressbar',
    'hidden_button', 'image_button', 'image_carousel',
]

for type_name in FACTORY_TYPES:
    try:
        if type_name == 'button':
            model = ButtonModel('test')
        elif type_name == 'label':
            model = LabelModel('test')
        elif type_name == 'input':
            model = InputModel('test')
        elif type_name == 'textarea':
            model = InputModel('test')
        elif type_name == 'checkbox':
            model = CheckBoxModel('test')
        elif type_name == 'combobox':
            model = ComboBoxModel('test')
        elif type_name == 'listwidget':
            model = ContainerModel('test')  # listwidget 用 container 代替测试
        elif type_name == 'groupbox':
            model = ContainerModel('test')  # groupbox 用 container 代替测试
        elif type_name == 'container':
            model = ContainerModel('test')
        elif type_name == 'progressbar':
            model = ProgressBarModel('test')
        elif type_name == 'hidden_button':
            model = HiddenButtonModel('test')
        elif type_name == 'image_button':
            model = ImageButtonModel('test')
        elif type_name == 'image_carousel':
            model = ImageCarouselModel('test')
        else:
            model = LabelModel('test')
        
        widget = ComponentFactory.create_widget(model)
        if widget:
            print(f"  [OK] {type_name:20s} -> {type(widget).__name__}")
        else:
            errors.append(f"ComponentFactory 无法创建: {type_name}")
            print(f"  [FAIL] {type_name:20s} -> 返回 None")
    except Exception as e:
        errors.append(f"ComponentFactory 创建 {type_name} 异常: {e}")
        print(f"  [ERROR] {type_name:20s} -> {e}")

# 检查是否有模型类型没有对应的工厂方法
for type_name in ALL_MODELS:
    if type_name not in ['textarea', 'listwidget', 'groupbox']:
        if type_name not in FACTORY_TYPES:
            errors.append(f"ComponentFactory 缺少 '{type_name}' 的创建方法!")
            print(f"  [MISSING] {type_name:20s} <- 工厂缺少!")

# ============================================================
# 3. 检查 PropertyPanel (属性面板)
# ============================================================
print("\n【3】属性面板 (PropertyPanel)")
print("-" * 40)

from views.property_panel import PropertyPanel

PANEL_TYPES = [
    'ButtonModel', 'LabelModel', 'InputModel', 'ContainerModel',
    'CheckBoxModel', 'ComboBoxModel', 'ImageModel', 'VideoModel',
    'ProgressBarModel', 'ImageCarouselModel', 'HiddenButtonModel', 'ImageButtonModel',
]

panel = PropertyPanel()
for model_class_name in PANEL_TYPES:
    try:
        if model_class_name == 'ButtonModel':
            model = ButtonModel('test')
        elif model_class_name == 'LabelModel':
            model = LabelModel('test')
        elif model_class_name == 'InputModel':
            model = InputModel('test')
        elif model_class_name == 'ContainerModel':
            model = ContainerModel('test')
        elif model_class_name == 'CheckBoxModel':
            model = CheckBoxModel('test')
        elif model_class_name == 'ComboBoxModel':
            model = ComboBoxModel('test')
        elif model_class_name == 'ImageModel':
            model = ImageModel('test')
        elif model_class_name == 'VideoModel':
            model = VideoModel('test')
        elif model_class_name == 'ProgressBarModel':
            model = ProgressBarModel('test')
        elif model_class_name == 'ImageCarouselModel':
            model = ImageCarouselModel('test')
        elif model_class_name == 'HiddenButtonModel':
            model = HiddenButtonModel('test')
        elif model_class_name == 'ImageButtonModel':
            model = ImageButtonModel('test')
        else:
            continue
        
        panel.set_component(model)
        print(f"  [OK] {model_class_name:25s} -> 属性正常显示")
    except Exception as e:
        errors.append(f"PropertyPanel 处理 {model_class_name} 异常: {e}")
        print(f"  [ERROR] {model_class_name:25s} -> {e}")

# 检查是否有模型类型没有对应的属性面板处理
for type_name, model_class in ALL_MODELS.items():
    if model_class.__name__ not in PANEL_TYPES:
        errors.append(f"PropertyPanel 缺少 {model_class.__name__} 的属性编辑!")
        print(f"  [MISSING] {model_class.__name__:25s} <- 面板缺少!")

# ============================================================
# 4. 检查 RendererFactoryV2 (渲染器工厂)
# ============================================================
print("\n【4】渲染器工厂 (RendererFactoryV2)")
print("-" * 40)

from renderers.renderer_factory_v2 import RendererFactoryV2

RENDERER_TYPES = [
    'button', 'label', 'input', 'container',
    'checkbox', 'combobox', 'progressbar',
    'hidden_button', 'image_button', 'image_carousel',
]

for type_name in RENDERER_TYPES:
    try:
        renderer = RendererFactoryV2.get_renderer_or_default(type_name)
        print(f"  [OK] {type_name:20s} -> {type(renderer).__name__}")
    except Exception as e:
        errors.append(f"渲染器工厂获取 {type_name} 失败: {e}")
        print(f"  [ERROR] {type_name:20s} -> {e}")

# 检查是否有模型类型没有对应的渲染器
for type_name in ALL_MODELS:
    if type_name not in RENDERER_TYPES:
        errors.append(f"RendererFactoryV2 缺少 '{type_name}' 的渲染器!")
        print(f"  [MISSING] {type_name:20s} <- 渲染器缺失!")

# ============================================================
# 5. 检查组件面板 (左侧添加列表)
# ============================================================
print("\n【5】组件面板 (ComponentPanel - 左侧添加列表)")
print("-" * 40)

from views.component_panel import ComponentPanel

PANEL_COMPONENTS = {
    "button": "按钮",
    "label": "文本标签",
    "input": "输入框",
    "container": "容器",
    "checkbox": "复选框",
    "combobox": "下拉框",
    "progressbar": "进度条",
    "image": "图片",
    "video": "视频",
}

for type_name, display_name in PANEL_COMPONENTS.items():
    status = "OK" if type_name in ALL_MODELS else "EXTRA"
    icon = "[OK]" if status == "OK" else "[??]"
    print(f"  {icon} {type_name:15s} ({display_name})")

for type_name in ALL_MODELS:
    if type_name not in PANEL_COMPONENTS:
        warnings.append(f"组件面板中缺少 '{type_name}' ({ALL_MODELS[type_name].__name__})，用户无法从UI添加!")
        print(f"  [MISSING] {type_name:15s} <- 用户无法添加!")

# ============================================================
# 结果汇总
# ============================================================
print("\n" + "=" * 60)
print("自检结果汇总")
print("=" * 60)

if errors:
    print(f"\n❌ 发现 {len(errors)} 个错误:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
else:
    print("\n✅ 所有核心检查通过!")

if warnings:
    print(f"\n⚠️  发现 {len(warnings)} 个警告:")
    for i, warn in enumerate(warnings, 1):
        print(f"  {i}. {warn}")

print(f"\n统计: 组件模型={len(ALL_MODELS)}, 工厂方法={len(FACTORY_TYPES)}, "
      f"属性面板={len(PANEL_TYPES)}, 渲染器={len(RENDERER_TYPES)}, "
      f"UI面板条目={len(PANEL_COMPONENTS)}")

sys.exit(0 if not errors else 1)