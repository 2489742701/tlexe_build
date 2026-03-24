"""测试运行器模块。

本模块提供测试用例的注册、管理和执行功能。
"""

import sys
import datetime
from typing import Optional, Dict, Any, List, Callable
from PySide6.QtCore import QObject, Signal


class TestCase:
    """测试用例装饰器和注册器。
    
    提供装饰器方式注册测试用例，支持分类管理。
    所有注册的测试用例会被自动收集，可以通过TestRunner执行。
    
    测试类别说明:
        - component: 组件测试，测试组件的创建、属性、方法
        - model: 模型测试，测试数据模型的CRUD操作
        - controller: 控制器测试，测试控制器的业务逻辑
        - view: 视图测试，测试视图的显示和交互
        - integration: 集成测试，测试多个模块的协作
    
    使用示例:
        # 注册测试用例
        @TestCase.register("component", "按钮创建测试")
        def test_button_creation():
            button = create_component("button")
            assert button is not None
            return button
        
        @TestCase.register("model", "项目保存测试")
        def test_project_save():
            model = ProjectModel()
            assert model.save_to_file("test.uix")
        
        # 获取所有测试用例
        tests = TestCase.get_all_tests()
        
        # 获取特定类别的测试用例
        component_tests = TestCase.get_tests_by_category("component")
    """
    
    _test_cases: Dict[str, Dict[str, Any]] = {}
    _test_counter: int = 0
    
    @classmethod
    def register(cls, category: str, name: str = "", description: str = "") -> Callable:
        """注册测试用例装饰器。
        
        将函数注册为测试用例，并指定类别和名称。
        
        Args:
            category: 测试类别（component/model/controller/view/integration）
            name: 测试名称（可选），为空则使用函数名
            description: 测试描述（可选）
        
        Returns:
            装饰器函数
        
        使用示例:
            @TestCase.register("component", "按钮创建测试")
            def test_button():
                pass
        """
        def decorator(func: Callable) -> Callable:
            cls._test_counter += 1
            test_id = f"test_{cls._test_counter:04d}"
            test_name = name or func.__name__
            
            if category not in cls._test_cases:
                cls._test_cases[category] = {}
            
            func._test_id = test_id
            func._test_name = test_name
            func._test_category = category
            
            cls._test_cases[category][test_id] = {
                'id': test_id,
                'name': test_name,
                'category': category,
                'function': func,
                'description': description or func.__doc__ or "",
            }
            
            return func
        
        return decorator
    
    @classmethod
    def get_all_tests(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有测试用例。
        
        Returns:
            所有测试用例的字典，按类别组织
        """
        return cls._test_cases.copy()
    
    @classmethod
    def get_tests_by_category(cls, category: str) -> Dict[str, Any]:
        """获取指定类别的测试用例。
        
        Args:
            category: 测试类别
        
        Returns:
            该类别的测试用例字典
        """
        return cls._test_cases.get(category, {})
    
    @classmethod
    def get_test_by_id(cls, test_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取测试用例。
        
        Args:
            test_id: 测试用例ID
        
        Returns:
            测试用例信息字典，如果不存在则返回None
        """
        for category_tests in cls._test_cases.values():
            if test_id in category_tests:
                return category_tests[test_id]
        return None
    
    @classmethod
    def clear_all_tests(cls):
        """清空所有测试用例。
        
        通常在重新加载测试模块时使用。
        """
        cls._test_cases.clear()
        cls._test_counter = 0


class TestRunner(QObject):
    """测试运行器。
    
    负责执行测试用例，收集测试结果，并生成测试报告。
    
    Signals:
        test_started: 测试开始时发射 (test_id, test_name)
        test_finished: 测试完成时发射 (test_id, test_name, passed, message)
        all_tests_finished: 所有测试完成时发射 (passed_count, failed_count, error_count)
    """
    
    test_started = Signal(str, str)
    test_finished = Signal(str, str, bool, str)
    all_tests_finished = Signal(int, int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._results: List[Dict[str, Any]] = []
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试用例。
        
        Returns:
            测试结果摘要
        """
        self._results.clear()
        all_tests = TestCase.get_all_tests()
        
        passed = 0
        failed = 0
        errors = 0
        
        for category, tests in all_tests.items():
            for test_id, test_info in tests.items():
                result = self._run_single_test(test_info)
                self._results.append(result)
                
                if result['status'] == 'passed':
                    passed += 1
                elif result['status'] == 'failed':
                    failed += 1
                else:
                    errors += 1
        
        self.all_tests_finished.emit(passed, failed, errors)
        
        return {
            'total': len(self._results),
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'results': self._results.copy()
        }
    
    def run_tests_by_category(self, category: str) -> Dict[str, Any]:
        """运行指定类别的测试用例。
        
        Args:
            category: 测试类别
        
        Returns:
            测试结果摘要
        """
        self._results.clear()
        tests = TestCase.get_tests_by_category(category)
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_id, test_info in tests.items():
            result = self._run_single_test(test_info)
            self._results.append(result)
            
            if result['status'] == 'passed':
                passed += 1
            elif result['status'] == 'failed':
                failed += 1
            else:
                errors += 1
        
        self.all_tests_finished.emit(passed, failed, errors)
        
        return {
            'total': len(self._results),
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'results': self._results.copy()
        }
    
    def run_single_test(self, test_id: str) -> Dict[str, Any]:
        """运行单个测试用例。
        
        Args:
            test_id: 测试用例ID
        
        Returns:
            测试结果
        """
        test_info = TestCase.get_test_by_id(test_id)
        if test_info is None:
            return {
                'id': test_id,
                'status': 'error',
                'message': f'测试用例不存在: {test_id}'
            }
        
        return self._run_single_test(test_info)
    
    def _run_single_test(self, test_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个测试用例。
        
        Args:
            test_info: 测试用例信息
        
        Returns:
            测试结果
        """
        test_id = test_info['id']
        test_name = test_info['name']
        test_func = test_info['function']
        
        self.test_started.emit(test_id, test_name)
        
        try:
            test_func()
            result = {
                'id': test_id,
                'name': test_name,
                'category': test_info['category'],
                'status': 'passed',
                'message': '测试通过',
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.test_finished.emit(test_id, test_name, True, '测试通过')
        except AssertionError as e:
            result = {
                'id': test_id,
                'name': test_name,
                'category': test_info['category'],
                'status': 'failed',
                'message': str(e) or '断言失败',
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.test_finished.emit(test_id, test_name, False, str(e) or '断言失败')
        except Exception as e:
            result = {
                'id': test_id,
                'name': test_name,
                'category': test_info['category'],
                'status': 'error',
                'message': f'错误: {str(e)}',
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.test_finished.emit(test_id, test_name, False, f'错误: {str(e)}')
        
        return result
    
    def get_results(self) -> List[Dict[str, Any]]:
        """获取测试结果列表。
        
        Returns:
            测试结果列表
        """
        return self._results.copy()
    
    def clear_results(self):
        """清空测试结果。"""
        self._results.clear()


def define_builtin_tests():
    """定义内置测试用例。
    
    注册一系列基础测试用例，用于验证核心功能。
    """
    
    @TestCase.register("component", "按钮组件创建测试", "测试按钮组件的创建功能")
    def test_button_creation():
        from models import ButtonModel
        button = ButtonModel(x=100, y=100, width=120, height=40, text="测试按钮")
        assert button is not None
        assert button.type == "button"
        assert button.text == "测试按钮"
    
    @TestCase.register("component", "标签组件创建测试", "测试标签组件的创建功能")
    def test_label_creation():
        from models import LabelModel
        label = LabelModel(x=50, y=50, width=200, height=30, text="测试标签")
        assert label is not None
        assert label.type == "label"
    
    @TestCase.register("component", "输入框组件创建测试", "测试输入框组件的创建功能")
    def test_input_creation():
        from models import InputModel
        input_box = InputModel(x=100, y=100, width=200, height=30)
        input_box.placeholder = "请输入"
        assert input_box is not None
        assert input_box.type == "input"
    
    @TestCase.register("component", "容器组件创建测试", "测试容器组件的创建功能")
    def test_container_creation():
        from models import ContainerModel
        container = ContainerModel(x=50, y=50, width=300, height=200)
        assert container is not None
        assert container.type == "container"
    
    @TestCase.register("model", "项目模型创建测试", "测试项目模型的创建功能")
    def test_project_model_creation():
        from models import ProjectModel
        project = ProjectModel()
        project.name = "测试项目"
        assert project is not None
        assert project.name == "测试项目"
    
    @TestCase.register("model", "项目组件添加测试", "测试向项目添加组件的功能")
    def test_project_add_component():
        from models import ProjectModel, ButtonModel
        project = ProjectModel()
        button = ButtonModel(x=100, y=100, width=120, height=40)
        comp_id = project.add_component(button)
        assert comp_id is not None
        assert project.get_component(comp_id) is not None
    
    @TestCase.register("model", "项目序列化测试", "测试项目的序列化和反序列化功能")
    def test_project_serialization():
        from models import ProjectModel, ButtonModel
        project = ProjectModel()
        project.name = "测试项目"
        button = ButtonModel(x=100, y=100, width=120, height=40, text="按钮")
        project.add_component(button)
        
        data = project.to_dict()
        assert data is not None
        assert 'name' in data
        assert 'components' in data
    
    @TestCase.register("controller", "撤销管理器测试", "测试撤销管理器的基本功能")
    def test_undo_manager():
        from utils.undo_manager import UndoManager
        manager = UndoManager()
        
        manager.push(
            action_type="test",
            description="测试操作",
            undo_data={},
            redo_data={},
            undo_callback=lambda: None,
            redo_callback=lambda: None
        )
        
        assert manager.can_undo() == True
        assert manager.undo_count == 1
    
    @TestCase.register("integration", "完整工作流测试", "测试从创建到保存的完整工作流")
    def test_full_workflow():
        from models import ProjectModel, ButtonModel, LabelModel
        project = ProjectModel()
        project.name = "完整测试项目"
        
        button = ButtonModel(x=100, y=100, width=120, height=40, text="确定")
        label = LabelModel(x=100, y=50, width=200, height=30, text="欢迎使用")
        
        project.add_component(button)
        project.add_component(label)
        
        data = project.to_dict()
        assert len(data.get('components', [])) == 2


define_builtin_tests()
