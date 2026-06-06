import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

from models import ProjectModel
from runtime.action_executor import ActionExecutor
from runtime.linkage_manager import LinkageManager
from utils.component_factory import ComponentFactory


def test_lottery_sample():
    """测试交替变换演示示例的联动系统和组件工厂。"""
    
    sample_path = os.path.join(os.path.dirname(__file__), '..', 'samples', '交替变换演示.py')
    
    with open(sample_path, 'r', encoding='utf-8') as f:
        content = f.read()
    from utils.py_project_format import python_code_to_dict
    data = python_code_to_dict(content)
    
    print('=' * 50)
    print('交替变换演示 - 完整验证')
    print('=' * 50)
    
    project_model = ProjectModel()
    project_model.from_dict(data)
    
    print(f'项目名称: {project_model.name}')
    print(f'窗口数量: {len(project_model._windows)}')
    print(f'组件数量: {len(project_model.get_all_components())}')
    print(f'联动配置数量: {len(project_model.linkages)}')
    
    print('\n--- 组件列表 ---')
    for comp in project_model.get_all_components():
        print(f'  - {comp.id} ({comp.type}): {comp.name}')
    
    print('\n--- 联动配置 ---')
    for i, linkage in enumerate(project_model.linkages):
        src = linkage['source_component']
        evt = linkage['source_event']
        tgt = linkage['target_component']
        act = linkage['target_action']
        params = linkage.get('params', {})
        tmpl = params.get('text_template', '')
        print(f'  [{i+1}] {src}.{evt} -> {tgt}.{act}')
        if tmpl:
            print(f'      模板: {tmpl}')
    
    carousel = project_model.get_component('carousel_1')
    if carousel:
        print(f'\n轮播组件 ({carousel.name}):')
        print(f'  图片列表: {carousel.images}')
        print(f'  标签列表: {carousel.image_labels}')
        print(f'  数据一致性: {len(carousel.images) == len(carousel.image_labels)}')
    
    executor = ActionExecutor(project_model)
    linkage_manager = LinkageManager(project_model, executor)
    linkage_manager.setup_linkages()
    
    print('\n--- 模板替换测试 ---')
    
    test_cases = [
        ('中奖者: {winner}', (2,), '王五'),
        ('第 {index} 位 / 共 {count} 人', (3,), '3'),
        ('中奖者: {winner}', (0,), '张三'),
        ('中奖者: {winner} (第{index}名)', (4,), '钱七'),
    ]
    
    all_passed = True
    for i, (template, args, expected_name) in enumerate(test_cases):
        result = linkage_manager._replace_templates(template, args, {}, carousel)
        status = 'PASS' if expected_name in result else 'FAIL'
        if expected_name not in result:
            all_passed = False
        print(f'  [{status}] 模板{i+1}: {result}')
    
    print('\n--- 组件工厂测试 ---')
    from models.components import ImageCarouselModel, HiddenButtonModel, ImageButtonModel
    
    factory_tests = [
        ('image_carousel', lambda: ImageCarouselModel('test', 0, 0, 300, 200)),
        ('hidden_button', lambda: HiddenButtonModel('test', 0, 0, 100, 100)),
        ('image_button', lambda: ImageButtonModel('test', 0, 0, 120, 40)),
    ]
    
    for name, create_fn in factory_tests:
        model = create_fn()
        widget = ComponentFactory.create_widget(model)
        status = 'PASS' if widget else 'FAIL'
        wtype = type(widget).__name__ if widget else 'None'
        print(f'  [{status}] {name}: {wtype}')
        if not widget:
            all_passed = False
    
    print('\n' + '=' * 50)
    if all_passed:
        print('所有验证通过!')
    else:
        print('部分验证失败!')
    print('=' * 50)
    
    return all_passed


if __name__ == '__main__':
    success = test_lottery_sample()
    sys.exit(0 if success else 1)