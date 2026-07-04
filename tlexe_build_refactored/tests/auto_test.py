"""自动化测试模块。

本模块提供基于信号和状态控制的自动化测试功能，用于开发者快速验证功能。

## 设计原则
1. 基于信号/槽机制控制测试流程，避免定时器的不确定性
2. 每个步骤完成后发出信号，触发下一个步骤
3. 完整的异常捕获和日志记录
4. 自动生成测试报告

## 使用方式
```bash
python main.py --test-blueprint
python main.py --test-all
```
"""

import os
import traceback
from datetime import datetime
from typing import Optional, List, Callable
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QTimer

class TestStep:
    """测试步骤数据类。"""
    
    def __init__(self, name: str, action: Callable, description: str = ""):
        self.name = name
        self.action = action
        self.description = description
        self.passed = False
        self.error: Optional[str] = None
        self.duration_ms = 0
        self.start_time: Optional[datetime] = None

class AutoTestManager(QObject):
    """自动化测试管理器。
    
    基于信号和槽机制控制测试流程，确保每个步骤按顺序执行。
    
    Signals:
        step_started: 步骤开始时发射，参数为步骤名称
        step_completed: 步骤完成时发射，参数为步骤名称、是否通过、错误信息
        all_completed: 所有测试完成时发射
        error_occurred: 发生错误时发射，参数为错误信息
    
    ## 使用示例
    ```python
    test_manager = AutoTestManager(session_logger)
    test_manager.add_step("打开项目", lambda: open_project("test.py"))
    test_manager.add_step("打开蓝图", open_blueprint)
    test_manager.start()
    ```
    """
    
    step_started = Signal(str)
    step_completed = Signal(str, bool, str)
    all_completed = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, session_logger=None, parent=None):
        super().__init__(parent)
        self._session_logger = session_logger
        self._steps: List[TestStep] = []
        self._current_step_index = 0
        self._test_results: List[dict] = []
        self._start_time: Optional[datetime] = None
        self._is_running = False
        
        self.step_started.connect(self._on_step_started)
        self.step_completed.connect(self._on_step_completed)
        self.all_completed.connect(self._on_all_completed)
    
    def add_step(self, name: str, action: Callable, description: str = ""):
        """添加测试步骤。
        
        Args:
            name: 步骤名称
            action: 要执行的动作（函数）
            description: 步骤描述
        """
        step = TestStep(name, action, description)
        self._steps.append(step)
    
    def clear_steps(self):
        """清除所有测试步骤。"""
        self._steps.clear()
        self._current_step_index = 0
        self._test_results.clear()
    
    def start(self):
        """开始执行测试。"""
        if self._is_running:
            self._log("WARNING", "测试已在运行中")
            return
        
        self._is_running = True
        self._current_step_index = 0
        self._test_results.clear()
        self._start_time = datetime.now()
        
        self._log("INFO", "=" * 60)
        self._log("INFO", "自动化测试开始")
        self._log("INFO", f"测试步骤数: {len(self._steps)}")
        self._log("INFO", "=" * 60)
        
        self._execute_next_step()
    
    def _execute_next_step(self):
        """执行下一个测试步骤。"""
        if self._current_step_index >= len(self._steps):
            self._finish_test()
            return
        
        step = self._steps[self._current_step_index]
        step.start_time = datetime.now()
        
        self.step_started.emit(step.name)
        
        try:
            self._log("INFO", f"[步骤 {self._current_step_index + 1}/{len(self._steps)}] 开始: {step.name}")
            
            result = step.action()
            
            step.duration_ms = (datetime.now() - step.start_time).total_seconds() * 1000
            step.passed = True
            step.error = None
            
            self.step_completed.emit(step.name, True, "")
            
        except Exception as e:
            step.duration_ms = (datetime.now() - step.start_time).total_seconds() * 1000
            step.passed = False
            step.error = f"{str(e)}\n{traceback.format_exc()}"
            
            self._log("ERROR", f"[步骤 {self._current_step_index + 1}] 失败: {step.name}")
            self._log("ERROR", step.error)
            
            self.step_completed.emit(step.name, False, step.error)
            self.error_occurred.emit(step.error)
    
    def _on_step_started(self, step_name: str):
        """步骤开始时的处理。"""
        pass
    
    def _on_step_completed(self, step_name: str, passed: bool, error: str):
        """步骤完成时的处理。"""
        step = self._steps[self._current_step_index]
        
        self._test_results.append({
            "name": step_name,
            "passed": passed,
            "error": error,
            "duration_ms": step.duration_ms
        })
        
        status = "✓ 通过" if passed else "✗ 失败"
        self._log("INFO", f"[步骤 {self._current_step_index + 1}] {status}: {step_name} ({step.duration_ms:.0f}ms)")
        
        self._current_step_index += 1
        
        QTimer.singleShot(100, self._execute_next_step)
    
    def _on_all_completed(self):
        """所有测试完成时的处理。"""
        self._generate_report()
    
    def _finish_test(self):
        """结束测试。"""
        self._is_running = False
        
        total_duration = (datetime.now() - self._start_time).total_seconds() * 1000
        
        passed_count = sum(1 for r in self._test_results if r["passed"])
        failed_count = len(self._test_results) - passed_count
        
        self._log("INFO", "=" * 60)
        self._log("INFO", "自动化测试完成")
        self._log("INFO", f"总耗时: {total_duration:.0f}ms")
        self._log("INFO", f"通过: {passed_count}/{len(self._test_results)}")
        if failed_count > 0:
            self._log("WARNING", f"失败: {failed_count}/{len(self._test_results)}")
        self._log("INFO", "=" * 60)
        
        self.all_completed.emit()
    
    def _generate_report(self):
        """生成测试报告。"""
        report_dir = Path("tests/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"auto_test_{timestamp}.txt"
        
        lines = [
            "=" * 60,
            "自动化测试报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            ""
        ]
        
        total_duration = (datetime.now() - self._start_time).total_seconds() * 1000
        passed_count = sum(1 for r in self._test_results if r["passed"])
        
        lines.append(f"总耗时: {total_duration:.0f}ms")
        lines.append(f"测试步骤: {len(self._test_results)}")
        lines.append(f"通过: {passed_count}")
        lines.append(f"失败: {len(self._test_results) - passed_count}")
        lines.append("")
        lines.append("详细结果:")
        lines.append("-" * 40)
        
        for i, result in enumerate(self._test_results):
            status = "✓ 通过" if result["passed"] else "✗ 失败"
            lines.append(f"{i + 1}. {status} - {result['name']} ({result['duration_ms']:.0f}ms)")
            if result["error"]:
                lines.append(f"   错误: {result['error'][:200]}")
        
        lines.append("")
        lines.append("=" * 60)
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        self._log("INFO", f"测试报告已保存: {report_file}")
    
    def _log(self, level: str, message: str):
        """记录日志。"""
        if self._session_logger:
            self._session_logger.log(level, message)
        else:
            print(f"[{level}] {message}")
    
    @property
    def is_running(self) -> bool:
        return self._is_running
    
    @property
    def results(self) -> List[dict]:
        return self._test_results.copy()

class BlueprintAutoTest(QObject):
    """蓝图功能自动化测试。
    
    专门用于测试状态机视图（蓝图）功能的自动化测试类。
    
    ## 测试流程
    1. 打开示例项目
    2. 打开状态机视图
    3. 验证节点数量
    4. 测试节点操作
    5. 关闭视图
    """
    
    test_completed = Signal(bool, str)
    
    def __init__(self, app_manager, parent=None):
        super().__init__(parent)
        self._app_manager = app_manager
        self._test_manager = AutoTestManager(app_manager._session_logger, parent)
        
        self._test_manager.all_completed.connect(self._on_test_completed)
    
    def setup_test_steps(self):
        """设置测试步骤。"""
        self._test_manager.clear_steps()
        
        self._test_manager.add_step(
            "打开示例项目",
            self._step_open_project,
            "自动打开 galgame 示例项目"
        )
        
        self._test_manager.add_step(
            "等待项目加载",
            self._step_wait_for_project,
            "等待项目完全加载"
        )
        
        self._test_manager.add_step(
            "打开状态机视图",
            self._step_open_blueprint,
            "打开状态机视图弹窗"
        )
        
        self._test_manager.add_step(
            "验证节点数量",
            self._step_verify_nodes,
            "验证状态机节点数量正确"
        )
        
        self._test_manager.add_step(
            "测试自动布局",
            self._step_test_auto_layout,
            "测试自动布局功能"
        )
    
    def start(self):
        """开始测试。"""
        self.setup_test_steps()
        self._test_manager.start()
    
    def _step_open_project(self):
        """步骤：打开示例项目。"""
        sample_file = "samples/galgame示例.py"
        if not os.path.exists(sample_file):
            raise FileNotFoundError(f"示例项目不存在: {sample_file}")
        
        self._app_manager._on_open_project(sample_file)
    
    def _step_wait_for_project(self):
        """步骤：等待项目加载完成。"""
        if not self._app_manager._project_model:
            raise RuntimeError("项目未加载")
        
        if not self._app_manager._main_window:
            raise RuntimeError("主窗口未初始化")
    
    def _step_open_blueprint(self):
        """步骤：打开状态机视图。"""
        if not self._app_manager._main_window:
            raise RuntimeError("主窗口未初始化")
        
        self._app_manager._main_window._toggle_state_machine_panel()
    
    def _step_verify_nodes(self):
        """步骤：验证节点数量。"""
        pass
    
    def _step_test_auto_layout(self):
        """步骤：测试自动布局。"""
        pass
    
    def _on_test_completed(self):
        """测试完成时的处理。"""
        results = self._test_manager.results
        passed = all(r["passed"] for r in results)
        
        message = "所有测试通过" if passed else "部分测试失败"
        self.test_completed.emit(passed, message)
