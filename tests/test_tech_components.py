"""测试技术类控件功能。

测试技术类控件的创建和管理功能。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TechComponentManager, create_component, GroupNodeModel


def test_tech_component_manager():
    """测试技术类控件管理器。"""
    print("=" * 60)
    print("测试技术类控件管理器")
    print("=" * 60)
    print()
    
    print("1. 获取所有可用模板:")
    templates = TechComponentManager.get_available_templates()
    for template_id in templates:
        info = TechComponentManager.get_template_info(template_id)
        print(f"  - {info['display_name']} ({template_id}): {info['description']}")
        print(f"    组件数量: {info['component_count']}")
    print()
    
    print("2. 创建抽奖系统组件:")
    try:
        components = TechComponentManager.create_tech_component("lottery", parent_id="test_parent")
        print(f"  成功创建 {len(components)} 个组件:")
        for comp in components:
            print(f"    - {comp.name} ({comp.type}): {comp.width}x{comp.height}")
    except Exception as e:
        print(f"  创建失败: {e}")
    print()
    
    print("3. 创建登录表单组件:")
    try:
        components = TechComponentManager.create_tech_component("login", offset_x=100, offset_y=100)
        print(f"  成功创建 {len(components)} 个组件:")
        for comp in components:
            print(f"    - {comp.name} ({comp.type}): 位置({comp.x}, {comp.y})")
    except Exception as e:
        print(f"  创建失败: {e}")
    print()


def test_group_node():
    """测试组节点功能。"""
    print("=" * 60)
    print("测试组节点功能")
    print("=" * 60)
    print()
    
    print("1. 创建组节点:")
    group = GroupNodeModel(name="测试组", x=10, y=10, width=400, height=300)
    print(f"  组节点ID: {group.id}")
    print(f"  组节点名称: {group.name}")
    print(f"  组节点类型: {group.type}")
    print(f"  组节点大小: {group.width}x{group.height}")
    print()
    
    print("2. 添加子组件:")
    comp1 = create_component("button", name="按钮1")
    comp2 = create_component("label", name="标签1")
    comp3 = create_component("input", name="输入框1")
    
    group.add_child(comp1.id)
    group.add_child(comp2.id)
    group.add_child(comp3.id)
    
    print(f"  子组件数量: {len(group.children)}")
    print(f"  子组件ID列表: {group.children}")
    print()
    
    print("3. 测试布局模式:")
    group.layout_mode = "vertical"
    print(f"  布局模式: {group.layout_mode}")
    group.spacing = 15
    print(f"  组件间距: {group.spacing}")
    group.padding = 20
    print(f"  内边距: {group.padding}")
    print()
    
    print("4. 测试边框样式:")
    group.border_style = "dashed"
    print(f"  边框样式: {group.border_style}")
    group.show_border = True
    print(f"  显示边框: {group.show_border}")
    print()
    
    print("5. 序列化和反序列化:")
    group_dict = group.to_dict()
    print(f"  序列化成功，包含 {len(group_dict)} 个字段")
    
    restored_group = GroupNodeModel.from_dict(group_dict)
    print(f"  反序列化成功，子组件数量: {len(restored_group.children)}")
    print(f"  布局模式: {restored_group.layout_mode}")
    print()


def test_component_creation():
    """测试组件创建功能。"""
    print("=" * 60)
    print("测试组件创建功能")
    print("=" * 60)
    print()
    
    print("1. 测试创建组节点组件:")
    try:
        group_comp = create_component("group_node", name="我的组节点")
        print(f"  成功创建: {group_comp.name} (类型: {group_comp.type})")
        print(f"  是否为GroupNodeModel: {isinstance(group_comp, GroupNodeModel)}")
    except Exception as e:
        print(f"  创建失败: {e}")
    print()
    
    print("2. 测试创建普通组件:")
    comp_types = ["button", "label", "input", "container"]
    for comp_type in comp_types:
        try:
            comp = create_component(comp_type)
            print(f"  成功创建 {comp_type}: {comp.name}")
        except Exception as e:
            print(f"  创建 {comp_type} 失败: {e}")
    print()


def main():
    """主函数。"""
    print()
    print("=" * 60)
    print("技术类控件和组节点功能测试")
    print("=" * 60)
    print()
    
    test_tech_component_manager()
    test_group_node()
    test_component_creation()
    
    print("=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
