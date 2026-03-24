"""开发者工具命令行入口。

提供命令行界面来测试、调试和管理项目。

使用方法:
    python devtools.py test              # 运行所有测试
    python devtools.py test component    # 运行组件测试
    python devtools.py test test_0001    # 运行单个测试
    python devtools.py check             # 项目健康检查
    python devtools.py log               # 查看日志
    python devtools.py demo button       # 启动按钮示例
    python devtools.py open project.uix  # 打开项目文件
    python devtools.py debug             # 进入交互调试模式
"""

import sys
import os
import argparse
import cmd
import platform
from typing import Optional


def setup_dev_mode():
    """初始化开发者模式环境。"""
    from PySide6.QtWidgets import QApplication
    from dev_mode import DevModeManager
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dev_manager = DevModeManager.get_instance()
    dev_manager.enable()
    
    return app, dev_manager


def test_command(args):
    """测试命令处理器。"""
    setup_dev_mode()
    from dev_mode import TestRunner, TestCase
    
    runner = TestRunner()
    
    if not args or args[0] == 'all':
        print("\n" + "=" * 60)
        print("开发者工具 - 测试执行器")
        print("=" * 60)
        
        all_tests = TestCase.get_all_tests()
        total_count = sum(len(tests) for tests in all_tests.values())
        print(f"\n运行所有测试 ({total_count} 个)...")
        print("-" * 60)
        
        result = runner.run_all_tests()
        
        print("\n" + "=" * 60)
        for category, tests in all_tests.items():
            for test_id, test_info in tests.items():
                status = "✅ [通过]" if any(
                    r['id'] == test_id and r['status'] == 'passed' 
                    for r in result['results']
                ) else "❌ [失败]"
                print(f"{status} [{category}] {test_info['name']}")
                if test_info.get('description'):
                    print(f"   描述: {test_info['description']}")
        
        print("\n" + "-" * 60)
        print(f"总计: {result['total']} 个测试")
        print(f"  通过: {result['passed']}")
        print(f"  失败: {result['failed']}")
        print(f"  错误: {result['errors']}")
        print("=" * 60)
        
    elif args[0] == 'list':
        print("\n可用测试列表:")
        print("-" * 40)
        all_tests = TestCase.get_all_tests()
        for category, tests in all_tests.items():
            print(f"\n[{category}]")
            for test_id, test_info in tests.items():
                print(f"  {test_id}: {test_info['name']}")
        
    elif args[0] in ['component', 'model', 'controller', 'view', 'integration']:
        category = args[0]
        print(f"\n运行 [{category}] 类别测试...")
        print("-" * 40)
        result = runner.run_tests_by_category(category)
        
        for r in result['results']:
            status = "✅" if r['status'] == 'passed' else "❌"
            print(f"{status} {r['name']}: {r['message']}")
        
        print(f"\n结果: 通过 {result['passed']}, 失败 {result['failed']}, 错误 {result['errors']}")
        
    else:
        test_id = args[0]
        print(f"\n运行测试: {test_id}")
        print("-" * 40)
        result = runner.run_single_test(test_id)
        
        status = "✅ 通过" if result['status'] == 'passed' else "❌ 失败"
        print(f"{status}: {result['message']}")


def check_command(args):
    """项目健康检查。"""
    print("\n" + "=" * 60)
    print("开发者工具 - 项目健康检查")
    print("=" * 60)
    
    checks = []
    
    print("\n检查 Python 版本...")
    python_version = platform.python_version()
    print(f"  Python {python_version}")
    
    try:
        from PySide6.QtCore import PYQT_VERSION_STR
        print(f"  PyQt6 版本 {PYQT_VERSION_STR}")
        checks.append(("Python版本", f"{python_version}", True))
        checks.append(("PyQt6", f"版本 {PYQT_VERSION_STR}", True))
    except ImportError as e:
        checks.append(("PyQt6", str(e), False))
    
    print("\n检查项目模块...")
    modules = ['models', 'views', 'controllers', 'utils', 'templates', 'runtime', 'dev_mode']
    for module in modules:
        try:
            __import__(module)
            print(f"  {module}")
            checks.append(("模块", f"{module}: 已导入", True))
        except ImportError as e:
            print(f"  {module} - 错误: {e}")
            checks.append(("模块", f"{module}: {e}", False))
    
    print("\n检查测试用例...")
    from dev_mode import TestCase
    all_tests = TestCase.get_all_tests()
    test_count = sum(len(tests) for tests in all_tests.values())
    print(f"  找到 {test_count} 个测试用例")
    checks.append(("测试用例", f"{test_count} 个测试", True))
    
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)
    
    passed = sum(1 for c in checks if c[2])
    total = len(checks)
    
    for name, detail, ok in checks:
        status = "通过" if ok else "失败"
        print(f"{status} {name}: {detail}")
    
    print(f"\n结果: {passed}/{total} 项通过")
    if passed == total:
        print("所有检查通过！项目状态良好。")
    else:
        print("部分检查未通过，请检查上述问题。")


def log_command(args):
    """日志命令处理器。"""
    setup_dev_mode()
    from dev_mode import DevModeManager
    
    dev_manager = DevModeManager.get_instance()
    
    if args and args[0] == 'clear':
        dev_manager.clear_logs()
        print("日志已清空")
    elif args and args[0] == 'tail' and len(args) > 1:
        n = int(args[1])
        logs = dev_manager.get_logs()[-n:]
        for log in logs:
            print(f"[{log['level']}] [{log['source']}] {log['message']}")
    else:
        logs = dev_manager.get_logs()
        if not logs:
            print("暂无日志")
        else:
            for log in logs[-20:]:
                print(f"[{log['level']}] [{log['source']}] {log['message']}")


def demo_command(args):
    """演示命令处理器。"""
    app, dev_manager = setup_dev_mode()
    from dev_mode import DebugLogger
    
    if not args:
        print("用法: python devtools.py demo <类型>")
        print("可用类型: button, label, input, container, progressbar")
        return
    
    demo_type = args[0]
    
    from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
    from models import ButtonModel, LabelModel, InputModel, ContainerModel, ProgressBarModel
    
    window = QMainWindow()
    window.setWindowTitle(f"演示 - {demo_type}")
    window.resize(400, 300)
    
    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)
    
    if demo_type == 'button':
        model = ButtonModel(x=0, y=0, width=120, height=40, text="演示按钮")
        from PySide6.QtWidgets import QPushButton
        btn = QPushButton(model.text)
        btn.clicked.connect(lambda: DebugLogger.info("按钮被点击", "Demo"))
        layout.addWidget(btn)
        
    elif demo_type == 'label':
        model = LabelModel(x=0, y=0, width=200, height=30, text="演示标签")
        from PySide6.QtWidgets import QLabel
        label = QLabel(model.text)
        layout.addWidget(label)
        
    elif demo_type == 'input':
        model = InputModel(x=0, y=0, width=200, height=30)
        model.placeholder = "请输入..."
        from PySide6.QtWidgets import QLineEdit
        edit = QLineEdit()
        edit.setPlaceholderText(model.placeholder)
        layout.addWidget(edit)
        
    elif demo_type == 'container':
        model = ContainerModel(x=0, y=0, width=300, height=200)
        from PySide6.QtWidgets import QGroupBox
        group = QGroupBox("演示容器")
        layout.addWidget(group)
        
    elif demo_type == 'progressbar':
        model = ProgressBarModel(x=0, y=0, width=200, height=24, value=50)
        from PySide6.QtWidgets import QProgressBar
        bar = QProgressBar()
        bar.setValue(model.value)
        layout.addWidget(bar)
    
    else:
        print(f"未知演示类型: {demo_type}")
        return
    
    window.show()
    DebugLogger.info(f"启动 {demo_type} 演示", "Demo")
    sys.exit(app.exec())


def open_command(args):
    """打开项目命令处理器。"""
    if not args:
        print("用法: python devtools.py open <项目文件.uix>")
        print("示例: python devtools.py open my_project.uix")
        return
    
    file_path = args[0]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return
    
    if not file_path.endswith('.uix'):
        print(f"警告: 文件扩展名不是 .uix，尝试打开...")
    
    app, dev_manager = setup_dev_mode()
    from dev_mode import DebugLogger
    
    from PySide6.QtWidgets import QMainWindow, QMessageBox
    from models import ProjectModel
    from views import MainWindow
    from controllers import ProjectController
    
    project = ProjectModel()
    
    if project.load_from_file(file_path):
        print(f"成功加载项目: {project.name}")
        print(f"  文件: {file_path}")
        print(f"  组件数: {len(project.get_all_components())}")
        
        window = MainWindow()
        controller = ProjectController(window, project)
        
        window.setWindowTitle(f"{project.name} - UI快速开发工具")
        window.resize(1200, 800)
        window.show()
        
        DebugLogger.info(f"通过命令行打开项目: {project.name}", "DevTools")
        
        sys.exit(app.exec())
    else:
        print(f"错误: 无法加载项目文件: {file_path}")
        sys.exit(1)


def run_command(args):
    """运行项目命令处理器。"""
    if not args:
        print("用法: python devtools.py run <项目文件.uix>")
        print("示例: python devtools.py run my_project.uix")
        return
    
    file_path = args[0]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return
    
    app, dev_manager = setup_dev_mode()
    from dev_mode import DebugLogger
    
    from models import ProjectModel
    from runtime import ProjectRunner
    
    project = ProjectModel()
    
    if project.load_from_file(file_path):
        print(f"运行项目: {project.name}")
        
        runner = ProjectRunner(project)
        runner.run()
        
        DebugLogger.info(f"通过命令行运行项目: {project.name}", "DevTools")
        
        sys.exit(app.exec())
    else:
        print(f"错误: 无法加载项目文件: {file_path}")
        sys.exit(1)


class DebugShell(cmd.Cmd):
    """交互式调试命令行。"""
    
    intro = """
============================================================
开发者工具 - 交互调试模式
============================================================
可用命令:
  test [list|<category>|<test_id>]  - 运行测试
  log [clear|tail <n>]              - 查看日志
  check                             - 项目健康检查
  demo <type>                       - 启动演示
  open <file.uix>                   - 打开项目文件
  run <file.uix>                    - 运行项目
  exit / quit                       - 退出调试模式
  help                              - 显示帮助
============================================================
"""
    prompt = "(devtools) "
    
    def do_test(self, arg):
        """运行测试: test [list|<category>|<test_id>]"""
        args = arg.split() if arg else []
        test_command(args)
    
    def do_log(self, arg):
        """查看日志: log [clear|tail <n>]"""
        args = arg.split() if arg else []
        log_command(args)
    
    def do_check(self, arg):
        """项目健康检查: check"""
        check_command([])
    
    def do_demo(self, arg):
        """启动演示: demo <button|label|input|container|progressbar>"""
        args = arg.split() if arg else []
        demo_command(args)
    
    def do_open(self, arg):
        """打开项目: open <file.uix>"""
        args = arg.split() if arg else []
        open_command(args)
    
    def do_run(self, arg):
        """运行项目: run <file.uix>"""
        args = arg.split() if arg else []
        run_command(args)
    
    def do_exit(self, arg):
        """退出调试模式"""
        print("再见！")
        return True
    
    def do_quit(self, arg):
        """退出调试模式"""
        return self.do_exit(arg)
    
    def do_help(self, arg):
        """显示帮助"""
        print("\n可用命令:")
        print("  test [list|<category>|<test_id>]  - 运行测试")
        print("  log [clear|tail <n>]              - 查看日志")
        print("  check                             - 项目健康检查")
        print("  demo <type>                       - 启动演示")
        print("  open <file.uix>                   - 打开项目文件")
        print("  run <file.uix>                    - 运行项目")
        print("  exit / quit                       - 退出调试模式")


def debug_command(args):
    """进入交互调试模式。"""
    setup_dev_mode()
    shell = DebugShell()
    shell.cmdloop()


def main():
    """主入口函数。"""
    parser = argparse.ArgumentParser(
        description='开发者工具命令行',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python devtools.py test              # 运行所有测试
  python devtools.py test component    # 运行组件测试
  python devtools.py test test_0001    # 运行单个测试
  python devtools.py check             # 项目健康检查
  python devtools.py log               # 查看日志
  python devtools.py demo button       # 启动按钮演示
  python devtools.py open project.uix  # 打开项目文件
  python devtools.py run project.uix   # 运行项目
  python devtools.py debug             # 进入交互调试模式
        """
    )
    
    parser.add_argument('command', nargs='?', default='debug',
                       help='命令: test, check, log, demo, open, run, debug')
    parser.add_argument('args', nargs='*',
                       help='命令参数')
    
    args = parser.parse_args()
    
    commands = {
        'test': test_command,
        'check': check_command,
        'log': log_command,
        'demo': demo_command,
        'open': open_command,
        'run': run_command,
        'debug': debug_command,
    }
    
    if args.command in commands:
        commands[args.command](args.args)
    else:
        print(f"未知命令: {args.command}")
        print("可用命令: test, check, log, demo, open, run, debug")
        sys.exit(1)


if __name__ == "__main__":
    main()
