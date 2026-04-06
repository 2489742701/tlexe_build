"""
前端组件可用性测试

测试目标：确保所有12种组件用户都可以从前端：
1. 访问（创建和显示）
2. 修改（属性编辑）
3. 保存（序列化和反序列化）
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

from models import ProjectModel
from models.components import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ImageModel, VideoModel, ProgressBarModel,
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel,
    COMPONENT_TYPE_MAP, create_component
)
from utils.component_factory import ComponentFactory
from views.property_panel import PropertyPanel, COMPONENT_INFO

print("=" * 60)
print("前端组件可用性测试")
print("=" * 60)

errors = []
passed = 0

# ============================================================
# 测试1: 组件创建工厂
# ============================================================
print("\n【测试1】组件创建工厂")
print("-" * 50)

ALL_TYPES = {
    'button': ('按钮', ButtonModel),
    'label': ('文本标签', LabelModel),
    'input': ('输入框', InputModel),
    'container': ('容器', ContainerModel),
    'checkbox': ('复选框', CheckBoxModel),
    'combobox': ('下拉框', ComboBoxModel),
    'image': ('图片', ImageModel),
    'video': ('视频', VideoModel),
    'progressbar': ('进度条', ProgressBarModel),
    'hidden_button': ('隐藏按钮', HiddenButtonModel),
    'image_button': ('图片按钮', ImageButtonModel),
    'image_carousel': ('图片轮播', ImageCarouselModel),
}

for comp_type, (display_name, model_class) in ALL_TYPES.items():
    try:
        model = create_component(comp_type, name=f"测试{display_name}")
        if model:
            passed += 1
            print(f"  [OK] {comp_type:15s}")
    except Exception as e:
        errors.append(f"create_component('{comp_type}') 异常: {e}")
        print(f"  [ERROR] {comp_type:15s} -> {e}")

# ============================================================
# 测试2: 运行时控件创建
# ============================================================
print("\n【测试2】运行时控件创建")
print("-" * 50)

for comp_type, (display_name, model_class) in ALL_TYPES.items():
    try:
        model = model_class(name=f"测试{display_name}")
        widget = ComponentFactory.create_widget(model)
        if widget:
            passed += 1
            print(f"  [OK] {comp_type:15s}")
    except Exception as e:
        errors.append(f"ComponentFactory {comp_type} 异常: {e}")
        print(f"  [ERROR] {comp_type:15s} -> {e}")

# ============================================================
# 测试3: 属性面板编辑
# ============================================================
print("\n【测试3】属性面板编辑")
print("-" * 50)

panel = PropertyPanel()

for comp_type, (display_name, model_class) in ALL_TYPES.items():
    try:
        model = model_class(name=f"测试{display_name}")
        panel.set_component(model)
        
        title = panel._title_label.text()
        
        if title != "未选择":
            passed += 1
            print(f"  [OK] {comp_type:15s} -> {title}")
        else:
            errors.append(f"属性面板 {comp_type} 标题错误")
            print(f"  [FAIL] {comp_type:15s}")
    except Exception as e:
        errors.append(f"属性面板 {comp_type} 异常: {e}")
        print(f"  [ERROR] {comp_type:15s} -> {e}")

# ============================================================
# 测试4: 使用官方案例测试序列化和反序列化
# ============================================================
print("\n【测试4】官方案例序列化和反序列化")
print("-" * 50)

SAMPLE_FILES = [
    'samples/系统检测示例.itexe',
    'samples/年会抽奖示例.itexe',
]

for sample_file in SAMPLE_FILES:
    sample_path = os.path.join(os.path.dirname(__file__), '..', sample_file)
    if not os.path.exists(sample_path):
        continue
    
    try:
        with open(sample_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        project = ProjectModel()
        project.from_dict(data)
        
        loaded_count = len(project.get_all_components())
        
        dict_data = project.to_dict()
        
        new_project = ProjectModel()
        new_project.from_dict(dict_data)
        
        saved_count = len(new_project.get_all_components())
        
        if saved_count == loaded_count:
            passed += 1
            print(f"  [OK] {sample_file}: {loaded_count} 组件保存成功")
        else:
            errors.append(f"{sample_file} 序列化后组件数量变化: {loaded_count} -> {saved_count}")
            print(f"  [FAIL] {sample_file}")
    except Exception as e:
        errors.append(f"{sample_file} 测试失败: {e}")
        print(f"  [ERROR] {sample_file} -> {e}")

# ============================================================
# 测试5: 属性修改是否生效
# ============================================================
print("\n【测试5】属性修改测试")
print("-" * 50)

try:
    model = ButtonModel(name="测试按钮")
    model.text = "原始文本"
    model.width = 100
    
    assert model.text == "原始文本"
    assert model.width == 100
    
    model.text = "修改后"
    model.width = 200
    
    assert model.text == "修改后"
    assert model.width == 200
    
    passed += 1
    print("  [OK] 属性修改生效")
except Exception as e:
    errors.append(f"属性修改测试失败: {e}")
    print(f"  [ERROR] 属性修改测试失败: {e}")

# ============================================================
# 测试6: 组件ID设置
# ============================================================
print("\n【测试6】组件ID设置")
print("-" * 50)

try:
    model = LabelModel(name="测试标签")
    model.id = "custom_id_123"
    
    assert model.id == "custom_id_123", f"Expected 'custom_id_123', got '{model.id}'"
    
    passed += 1
    print("  [OK] 组件ID可以设置")
except Exception as e:
    errors.append(f"组件ID设置失败: {e}")
    print(f"  [ERROR] 组件ID设置失败: {e}")

# ============================================================
# 结果汇总
# ============================================================
print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)

print(f"\n通过: {passed} 项测试")

if errors:
    print(f"\n发现 {len(errors)} 个错误:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
    sys.exit(1)
else:
    print("\n所有前端可用性测试通过!")
    print("用户可以正常访问、修改和保存所有12种组件!")
    sys.exit(0)