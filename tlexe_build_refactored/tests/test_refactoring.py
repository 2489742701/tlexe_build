"""重构代码自动化测试脚本。

本脚本用于验证重构后的代码是否能正常导入和运行。

"""

import sys
import os
import traceback
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestResult:
    """测试结果类。"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        """添加通过测试。"""
        self.passed += 1
        print(f"  ✓ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        """添加失败测试。"""
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ✗ {test_name}")
        print(f"    错误: {error}")
    
    def print_summary(self):
        """打印测试摘要。"""
        total = self.passed + self.failed
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        print(f"总测试数: {total}")
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        
        if self.errors:
            print("\n失败的测试:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        print("="*60)
        
        if self.failed == 0:
            print("✓ 所有测试通过！")
        else:
            print(f"✗ {self.failed} 个测试失败")
        
        return self.failed == 0

def run_test(test_name: str, result: TestResult):
    """装饰器：运行单个测试。"""
    def decorator(func):
        try:
            func()
            result.add_pass(test_name)
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            result.add_fail(test_name, error_msg)
        return func
    return decorator

def test_services_module(result: TestResult):
    """测试服务层模块。"""
    print("\n【测试】服务层模块")
    
    @run_test("AppInitializer 导入", result)
    def test_app_initializer():
        from services import AppInitializer
        assert AppInitializer is not None
    
    @run_test("AutoSaveService 导入", result)
    def test_auto_save_service():
        from services import AutoSaveService
        assert AutoSaveService is not None
    
    @run_test("AppInitializer 实例化", result)
    def test_app_initializer_instance():
        from services import AppInitializer
        initializer = AppInitializer(dev_mode=False, skip_welcome=False)
        assert initializer is not None
        assert hasattr(initializer, 'run')
    
    @run_test("AutoSaveService 实例化", result)
    def test_auto_save_service_instance():
        from services import AutoSaveService
        service = AutoSaveService()
        assert service is not None
        assert hasattr(service, 'auto_save_project')
    
    test_app_initializer()
    test_auto_save_service()
    test_app_initializer_instance()
    test_auto_save_service_instance()

def test_utils_module(result: TestResult):
    """测试工具模块。"""
    print("\n【测试】工具模块")
    
    @run_test("TempFileManager 导入", result)
    def test_temp_file_manager():
        from utils.temp_file_manager import TempFileManager
        assert TempFileManager is not None
    
    @run_test("TempFileManager 单例模式", result)
    def test_temp_file_manager_singleton():
        from utils.temp_file_manager import TempFileManager
        manager1 = TempFileManager()
        manager2 = TempFileManager()
        assert manager1 is manager2
    
    @run_test("TempFileManager 生成临时路径", result)
    def test_temp_file_manager_path():
        from utils.temp_file_manager import TempFileManager
        manager = TempFileManager()
        path = manager.generate_temp_save_path()
        assert path is not None
        assert path.endswith('.py')
    
    test_temp_file_manager()
    test_temp_file_manager_singleton()
    test_temp_file_manager_path()

def test_controllers_module(result: TestResult):
    """测试控制器模块。"""
    print("\n【测试】控制器模块")
    
    @run_test("ProjectController 导入", result)
    def test_project_controller():
        from controllers import ProjectController
        assert ProjectController is not None
    
    @run_test("CanvasController 导入", result)
    def test_canvas_controller():
        from controllers import CanvasController
        assert CanvasController is not None
    
    @run_test("CanvasController 信号定义", result)
    def test_canvas_controller_signals():
        from controllers import CanvasController
        assert hasattr(CanvasController, 'component_selected')
        assert hasattr(CanvasController, 'components_moved')
        assert hasattr(CanvasController, 'component_resized')
    
    test_project_controller()
    test_canvas_controller()
    test_canvas_controller_signals()

def test_renderers_module(result: TestResult):
    """测试渲染器模块。"""
    print("\n【测试】渲染器模块")
    
    @run_test("渲染器模块导入", result)
    def test_renderers_import():
        from renderers import ComponentRenderer
        from renderers import ButtonRenderer, LabelRenderer, InputRenderer
        from renderers import ContainerRenderer, CheckBoxRenderer
        from renderers import ComboBoxRenderer, ProgressBarRenderer
        from renderers import RendererFactory
    
    @run_test("RendererFactory 获取渲染器", result)
    def test_renderer_factory():
        from renderers import RendererFactory, ButtonRenderer, LabelRenderer
        
        button_renderer = RendererFactory.get_renderer('button')
        assert button_renderer is not None
        assert isinstance(button_renderer, ButtonRenderer)
        
        label_renderer = RendererFactory.get_renderer('label')
        assert label_renderer is not None
        assert isinstance(label_renderer, LabelRenderer)
    
    @run_test("RendererFactory 获取支持的类型", result)
    def test_renderer_factory_types():
        from renderers import RendererFactory
        
        types = RendererFactory.get_supported_types()
        assert 'button' in types
        assert 'label' in types
        assert 'input' in types
        assert 'container' in types
    
    @run_test("RendererFactory 注册新渲染器", result)
    def test_renderer_factory_register():
        from renderers import RendererFactory, LabelRenderer
        
        # 注册一个测试类型
        RendererFactory.register_renderer('test_type', LabelRenderer)
        
        # 验证是否注册成功
        renderer = RendererFactory.get_renderer('test_type')
        assert renderer is not None
        assert isinstance(renderer, LabelRenderer)
    
    test_renderers_import()
    test_renderer_factory()
    test_renderer_factory_types()
    test_renderer_factory_register()

def test_property_panel_module(result: TestResult):
    """测试属性面板模块。"""
    print("\n【测试】属性面板模块")
    
    @run_test("PropertyEditorRegistry 导入", result)
    def test_registry_import():
        from views.property_editors import PropertyEditorRegistry
        from views.property_editors import BasePropertyEditor
    
    @run_test("PropertyEditorRegistry 注册和获取", result)
    def test_registry_register():
        from views.property_editors import PropertyEditorRegistry, BasePropertyEditor
        
        # 创建一个测试编辑器类
        class TestEditor(BasePropertyEditor):
            def _setup_ui(self):
                pass
            def _update_ui_from_model(self):
                pass
        
        # 注册
        PropertyEditorRegistry.register('test_component', TestEditor)
        
        # 获取
        editor_class = PropertyEditorRegistry.get_editor('test_component')
        assert editor_class is not None
        assert editor_class == TestEditor
    
    @run_test("PropertyEditorRegistry 创建编辑器类", result)
    def test_registry_create():
        from views.property_editors import PropertyEditorRegistry, BasePropertyEditor
        
        # 创建一个测试编辑器类
        class TestEditor2(BasePropertyEditor):
            def _setup_ui(self):
                pass
            def _update_ui_from_model(self):
                pass
        
        # 注册
        PropertyEditorRegistry.register('test_component2', TestEditor2)
        
        # 获取编辑器类（不创建实例，因为需要 QApplication）
        editor_class = PropertyEditorRegistry.get_editor('test_component2')
        assert editor_class is not None
        assert editor_class == TestEditor2
    
    test_registry_import()
    test_registry_register()
    test_registry_create()

def test_main_module(result: TestResult):
    """测试主程序模块。"""
    print("\n【测试】主程序模块")
    
    @run_test("main.py 导入", result)
    def test_main_import():
        import main
        assert hasattr(main, 'AppManager')
        assert hasattr(main, 'main')
    
    @run_test("AppManager 使用新的服务", result)
    def test_app_manager_services():
        import main
        
        # 检查 AppManager 的 __init__ 是否使用了新的服务
        import inspect
        source = inspect.getsource(main.AppManager.__init__)
        
        # 验证使用了新的服务类
        assert 'AppInitializer' in source
        assert 'AutoSaveService' in source
        assert 'TempFileManager' in source
    
    test_main_import()
    test_app_manager_services()

def main():
    """主函数。"""
    print("="*60)
    print("重构代码自动化测试")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    result = TestResult()
    
    try:
        # 运行所有测试
        test_services_module(result)
        test_utils_module(result)
        test_controllers_module(result)
        test_renderers_module(result)
        test_property_panel_module(result)
        test_main_module(result)
        
    except Exception as e:
        print(f"\n测试执行过程中发生错误: {e}")
        traceback.print_exc()
        result.add_fail("测试执行", str(e))
    
    # 打印摘要
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    success = result.print_summary()
    
    # 返回退出码
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
