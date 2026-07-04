"""自动化测试框架。

本模块提供项目级别的自动化测试功能，支持：
- 自动打开项目
- 自动打开状态机视图
- 全流程测试
- 错误检测和日志记录
- 测试报告生成

## 使用方式

### 运行所有测试
```bash
python -m tests.run_tests
```

### 运行单个测试
```bash
python -m tests.test_flow
```

## 测试分类

| 测试类 | 说明 |
|--------|------|
| TestProject | 项目操作测试 |
| TestStateMachineView | 状态机视图测试 |
| TestFlow | 全流程测试 |
"""

import unittest
import sys
import os
import logging
import traceback
from datetime import datetime
from typing import Optional, List, Callable
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtTest import QTest

class TestSignals(QObject):
    """测试信号类。"""
    
    test_started = Signal(str)
    test_passed = Signal(str)
    test_failed = Signal(str, str)
    test_error = Signal(str, str)

class TestLogger:
    """测试日志记录器。
    
    用于记录测试过程中的日志信息，包括：
    - 测试开始/结束
    - 操作步骤
    - 错误信息
    - 截图保存
    """
    
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir) if log_dir else Path("tests/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"test_{timestamp}.log"
        
        self.logger = logging.getLogger("TestLogger")
        self.logger.setLevel(logging.DEBUG)
        
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.test_results: List[dict] = []
        self.current_test: Optional[str] = None
    
    def start_test(self, test_name: str):
        """记录测试开始。"""
        self.current_test = test_name
        self.logger.info(f"{'='*60}")
        self.logger.info(f"测试开始: {test_name}")
        self.logger.info(f"{'='*60}")
    
    def end_test(self, test_name: str, passed: bool, error: str = None):
        """记录测试结束。"""
        status = "通过" if passed else "失败"
        self.logger.info(f"测试结束: {test_name} - {status}")
        
        if error:
            self.logger.error(f"错误信息: {error}")
        
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        self.current_test = None
    
    def step(self, message: str):
        """记录测试步骤。"""
        self.logger.info(f"[步骤] {message}")
    
    def info(self, message: str):
        """记录信息。"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告。"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误。"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """记录调试信息。"""
        self.logger.debug(message)
    
    def exception(self, message: str):
        """记录异常。"""
        self.logger.exception(message)
    
    def generate_report(self) -> str:
        """生成测试报告。"""
        report_lines = [
            "=" * 60,
            "测试报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"日志文件: {self.log_file}",
            "=" * 60,
            ""
        ]
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed
        
        report_lines.append(f"总计: {total} 个测试")
        report_lines.append(f"通过: {passed} 个")
        report_lines.append(f"失败: {failed} 个")
        report_lines.append("")
        
        if failed > 0:
            report_lines.append("失败的测试:")
            for result in self.test_results:
                if not result["passed"]:
                    report_lines.append(f"  - {result['name']}")
                    if result["error"]:
                        report_lines.append(f"    错误: {result['error']}")
            report_lines.append("")
        
        report_lines.append("详细结果:")
        for result in self.test_results:
            status = "✓ 通过" if result["passed"] else "✗ 失败"
            report_lines.append(f"  {status} - {result['name']}")
        
        report = "\n".join(report_lines)
        
        report_file = self.log_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        self.logger.info(f"测试报告已保存: {report_file}")
        
        return report

class TestBase(unittest.TestCase):
    """测试基类。
    
    提供测试的基础功能：
    - QApplication 管理
    - 日志记录
    - 异常捕获
    - 截图功能
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化。"""
        cls.logger = TestLogger()
        cls.signals = TestSignals()
        
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理。"""
        report = cls.logger.generate_report()
        print("\n" + report)
    
    def setUp(self):
        """每个测试前执行。"""
        self._test_passed = False
        self._test_error = None
        self.logger.start_test(self._testMethodName)
    
    def tearDown(self):
        """每个测试后执行。"""
        self.logger.end_test(
            self._testMethodName,
            self._test_passed,
            self._test_error
        )
    
    def mark_passed(self):
        """标记测试通过。"""
        self._test_passed = True
    
    def mark_failed(self, error: str):
        """标记测试失败。"""
        self._test_passed = False
        self._test_error = error
    
    def safe_call(self, func: Callable, *args, **kwargs):
        """安全调用函数，捕获异常。"""
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_msg = f"{func.__name__} 执行失败: {str(e)}\n{traceback.format_exc()}"
            self.logger.exception(error_msg)
            self.mark_failed(error_msg)
            raise
    
    def wait(self, ms: int):
        """等待指定毫秒。"""
        QTest.qWait(ms)
    
    def process_events(self):
        """处理事件队列。"""
        self.app.processEvents()

class TestProject(TestBase):
    """项目操作测试类。
    
    测试项目的创建、打开、保存等操作。
    """
    
    def test_create_project(self):
        """测试创建项目。"""
        try:
            self.logger.step("创建新项目")
            
            from models import ProjectModel
            
            project = ProjectModel()
            project.name = "测试项目"
            
            self.assertIsNotNone(project)
            self.assertEqual(project.name, "测试项目")
            
            self.logger.info("项目创建成功")
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise
    
    def test_open_project(self):
        """测试打开项目。"""
        try:
            from models import ProjectModel
            
            test_file = Path("samples/galgame示例.py")
            if not test_file.exists():
                self.logger.warning(f"测试文件不存在: {test_file}")
                self.skipTest(f"测试文件不存在: {test_file}")
            
            self.logger.step(f"打开项目文件: {test_file}")
            
            project = ProjectModel.load_from_file(str(test_file))
            
            self.assertIsNotNone(project)
            self.logger.info(f"项目名称: {project.name}")
            self.logger.info(f"窗口数量: {len(project.get_all_windows())}")
            
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise
    
    def test_get_main_window(self):
        """测试获取主窗口。"""
        try:
            from models import ProjectModel
            
            project = ProjectModel()
            project.name = "测试项目"
            
            main_window = project.get_main_window()
            
            if main_window:
                self.logger.info(f"主窗口: {main_window.name}")
            else:
                self.logger.info("无主窗口")
            
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise

class TestStateMachineView(TestBase):
    """状态机视图测试类。
    
    测试状态机视图的打开、节点操作等。
    """
    
    def test_create_state_machine_dialog(self):
        """测试创建状态机视图弹窗。"""
        try:
            self.logger.step("创建状态机视图弹窗")
            
            from views.state_machine_view import StateMachineDialog
            
            dialog = StateMachineDialog()
            
            self.assertIsNotNone(dialog)
            self.assertEqual(dialog.windowTitle(), "📊 状态机视图")
            
            self.logger.info("状态机视图创建成功")
            
            dialog.close()
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise
    
    def test_add_node(self):
        """测试添加节点。"""
        try:
            from views.state_machine_view import (
                StateMachineDialog, StateNodeData, StateMachineModel
            )
            
            self.logger.step("创建状态机模型")
            
            model = StateMachineModel()
            node = StateNodeData(
                id="test_node_1",
                name="测试节点",
                x=100,
                y=100
            )
            model.nodes.append(node)
            
            self.logger.step("创建状态机视图并添加节点")
            
            dialog = StateMachineDialog()
            dialog._state_model = model
            dialog._scene.add_node(node)
            
            self.assertEqual(len(dialog._scene._nodes), 1)
            self.logger.info("节点添加成功")
            
            dialog.close()
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise
    
    def test_add_connection(self):
        """测试添加连线。"""
        try:
            from views.state_machine_view import (
                StateMachineDialog, StateNodeData, TransitionData, StateMachineModel
            )
            
            self.logger.step("创建两个节点")
            
            model = StateMachineModel()
            
            node1 = StateNodeData(id="node_1", name="节点1", x=100, y=100, is_main=True)
            node2 = StateNodeData(id="node_2", name="节点2", x=350, y=100)
            model.nodes.extend([node1, node2])
            
            self.logger.step("创建连线")
            
            conn = TransitionData(
                id="conn_1",
                source_node_id="node_1",
                target_node_id="node_2"
            )
            model.transitions.append(conn)
            
            self.logger.step("添加到视图")
            
            dialog = StateMachineDialog()
            dialog._state_model = model
            dialog._scene.add_node(node1)
            dialog._scene.add_node(node2)
            dialog._scene.add_connection(conn)
            
            self.assertEqual(len(dialog._scene._connections), 1)
            self.logger.info("连线添加成功")
            
            dialog.close()
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise

class TestFlow(TestBase):
    """全流程测试类。
    
    测试完整的工作流程。
    """
    
    def test_full_flow(self):
        """测试完整流程：打开项目 -> 打开状态机视图。"""
        try:
            self.logger.step("步骤1: 创建项目")
            
            from models import ProjectModel
            from views.state_machine_view import StateMachineDialog
            
            project = ProjectModel()
            project.name = "全流程测试项目"
            
            self.logger.step("步骤2: 创建主窗口")
            
            from models import WindowModel
            main_window = WindowModel(name="主窗口", is_main=True)
            project.add_window(main_window)
            
            self.logger.step("步骤3: 打开状态机视图")
            
            dialog = StateMachineDialog(project)
            
            self.logger.info(f"状态机节点数: {len(dialog._state_model.nodes)}")
            
            self.assertGreaterEqual(len(dialog._state_model.nodes), 1)
            
            self.logger.step("步骤4: 验证节点")
            
            main_node = dialog._state_model.get_node_by_window(main_window.id)
            self.assertIsNotNone(main_node)
            self.assertTrue(main_node.is_main)
            
            self.logger.info("全流程测试完成")
            
            dialog.close()
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise
    
    def test_open_sample_project(self):
        """测试打开示例项目。"""
        try:
            from models import ProjectModel
            from views.state_machine_view import StateMachineDialog
            
            test_file = Path("samples/galgame示例.py")
            if not test_file.exists():
                self.logger.warning(f"测试文件不存在: {test_file}")
                self.skipTest(f"测试文件不存在: {test_file}")
            
            self.logger.step(f"打开示例项目: {test_file}")
            
            project = ProjectModel.load_from_file(str(test_file))
            
            self.assertIsNotNone(project)
            self.logger.info(f"项目: {project.name}")
            
            self.logger.step("打开状态机视图")
            
            dialog = StateMachineDialog(project)
            
            node_count = len(dialog._state_model.nodes)
            conn_count = len(dialog._state_model.transitions)
            
            self.logger.info(f"节点数: {node_count}")
            self.logger.info(f"连线数: {conn_count}")
            
            self.assertGreater(node_count, 0)
            
            self.logger.step("测试自动布局")
            
            dialog._auto_layout()
            
            self.wait(100)
            
            self.logger.info("示例项目测试完成")
            
            dialog.close()
            self.mark_passed()
            
        except Exception as e:
            self.mark_failed(str(e))
            raise

def run_tests(test_names: List[str] = None):
    """运行测试。
    
    Args:
        test_names: 要运行的测试名称列表，为空则运行所有测试
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if test_names:
        for name in test_names:
            try:
                suite.addTest(loader.loadTestsFromName(name))
            except Exception as e:
                print(f"无法加载测试 {name}: {e}")
    else:
        suite.addTests(loader.loadTestsFromModule(sys.modules[__name__]))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    run_tests()
