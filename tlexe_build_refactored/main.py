"""UI快速开发工具 - 主入口。

本模块是应用程序的入口点，负责初始化并启动应用程序。

命令行参数:
    python main.py                           # 正常启动，显示欢迎页
    python main.py project.py                # 直接打开项目文件
    python main.py --dev project.py          # 开发者模式打开项目
    python main.py --run project.py          # 直接运行项目（不打开编辑器）
    python main.py --skip-welcome            # 跳过欢迎页，直接显示空白编辑器
    python main.py -r -d samples/demo.py     # 开发者模式直接运行项目

"""

import sys
import os

if getattr(sys, "frozen", False) or globals().get("__compiled__") is not None:
    try:
        _frozen_log = open(os.path.join(os.path.dirname(sys.executable), "frozen_debug.log"), "w", encoding="utf-8")
        sys.stdout = _frozen_log
        sys.stderr = _frozen_log
    except Exception:
        pass
    try:
        if hasattr(sys, "_MEIPASS"):
            ext_dir = sys._MEIPASS
        elif globals().get("__compiled__") is not None:
            ext_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            ext_dir = os.path.dirname(sys.executable)
        plugin_path = os.path.join(ext_dir, "lib", "PySide6", "plugins")
        if os.path.isdir(plugin_path):
            os.environ["QT_PLUGIN_PATH"] = plugin_path
            os.environ["PATH"] = plugin_path + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass

import argparse
import traceback
from datetime import datetime

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from models import ProjectModel
from views import MainWindow
from views.welcome_page import WelcomePage
from views.register_dialog import RegisterDialog
from controllers import ProjectController
from utils.settings import app_settings
from utils.session_logger import SessionLogger
from utils.temp_file_manager import TempFileManager
from services import AppInitializer, AutoSaveService, NavigationManager

_session_logger: SessionLogger = None

def exception_hook(exc_type, exc_value, exc_tb):
    """全局异常处理钩子。
    
    捕获所有未处理的异常并记录到日志文件。
    """
    global _session_logger
    
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    full_log = f"\n{'='*60}\n[{timestamp}] 未捕获的异常:\n{error_msg}{'='*60}\n"
    
    print(full_log, file=sys.stderr)
    
    if _session_logger:
        _session_logger.log("CRITICAL", f"未捕获的异常:\n{error_msg}")
    
    try:
        appdata = os.environ.get('APPDATA', '')
        crash_log_dir = os.path.join(appdata, 'UIDevTool', 'crash_logs')
        os.makedirs(crash_log_dir, exist_ok=True)
        
        crash_file = os.path.join(crash_log_dir, f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        with open(crash_file, 'w', encoding='utf-8') as f:
            f.write(f"UI快速开发工具 - 崩溃日志\n")
            f.write(f"时间: {timestamp}\n")
            f.write(f"{'='*60}\n\n")
            f.write(full_log)
            
            if _session_logger:
                f.write(f"\n\n{'='*60}\n")
                f.write("最近日志记录:\n")
                f.write(f"{'='*60}\n")
                for log in _session_logger.get_logs()[-50:]:
                    f.write(log + '\n')
        
        print(f"崩溃日志已保存到: {crash_file}")
    except Exception as e:
        print(f"无法保存崩溃日志: {e}")
    
    try:
        QMessageBox.critical(
            None,
            "程序发生错误",
            f"程序发生未预期的错误:\n\n{str(exc_value)}\n\n崩溃日志已保存到:\n{crash_file if 'crash_file' in dir() else '未知'}"
        )
    except:
        pass

def parse_args():
    """解析命令行参数。
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='UI快速开发工具 - 桌面应用程序可视化开发工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py                           # 正常启动，显示欢迎页
  python main.py project.py                # 直接打开项目文件
  python main.py --run project.py          # 直接运行项目
  python main.py -r -d samples/demo.py     # 开发者模式运行项目
  python main.py --skip-welcome            # 跳过欢迎页
        '''
    )
    parser.add_argument(
        'project', 
        nargs='?', 
        help='要打开的项目文件路径 (.py 或 .itexe)'
    )
    parser.add_argument(
        '-d', '--dev', 
        action='store_true', 
        help='启用开发者模式'
    )
    parser.add_argument(
        '-r', '--run', 
        action='store_true', 
        help='直接运行项目（不打开编辑器）'
    )
    parser.add_argument(
        '-s', '--skip-welcome', 
        action='store_true', 
        help='跳过欢迎页，直接显示空白编辑器'
    )
    parser.add_argument(
        '--test-blueprint', 
        action='store_true', 
        help='自动测试蓝图功能（打开项目后自动打开状态机视图）'
    )
    parser.add_argument(
        '--auto-test-editor', 
        action='store_true', 
        help='自动测试编辑器功能（自动遍历并选中所有组件）'
    )
    return parser.parse_args()

class AppManager:
    """应用程序管理器。
    
    管理欢迎页和编辑器窗口之间的切换。
    
    """
    
    def __init__(self, dev_mode: bool = False, skip_welcome: bool = False):
        global _session_logger
        
        self._initializer = AppInitializer(dev_mode=dev_mode, skip_welcome=skip_welcome)
        self._app = self._initializer.run()
        
        _session_logger = self._initializer._session_logger
        self._session_logger = self._initializer._session_logger
        if self._session_logger:
            self._session_logger.log("INFO", "AppInitializer.run() 完成")
        
        self._auto_save_service = AutoSaveService(session_logger=self._session_logger)
        
        self._temp_file_manager = TempFileManager()
        
        self._navigation = NavigationManager(session_logger=self._session_logger)
        if self._session_logger:
            self._session_logger.log("INFO", "NavigationManager 创建完成")
        
        self._skip_welcome = skip_welcome
        
        self._project_model = None
        self._controller = None
        
        self._setup_close_event()
    
    def _setup_close_event(self):
        original_close_event = self._navigation.stacked_widget.closeEvent
        
        def wrapped_close_event(event):
            if self._auto_save_service.on_application_exit(self._project_model):
                original_close_event(event)
            else:
                event.ignore()
        
        self._navigation.stacked_widget.closeEvent = wrapped_close_event
    
    def open_project_file(self, file_path: str):
        """直接打开项目文件。
        
        Args:
            file_path: 项目文件路径
        """
        if os.path.exists(file_path):
            self._session_logger.log("INFO", f"打开项目: {file_path}")
            self._on_open_project(file_path)
        else:
            self._session_logger.log("ERROR", f"项目文件不存在: {file_path}")
            QMessageBox.warning(
                None,
                "文件不存在",
                f"项目文件不存在: {file_path}"
            )
            self._navigation.stacked_widget.show()
    
    def test_blueprint_auto(self):
        """自动测试蓝图功能。
        
        使用基于信号的自动化测试框架，自动打开示例项目并测试状态机视图。
        """
        from PySide6.QtCore import QTimer
        from tests.auto_test import BlueprintAutoTest
        
        self._auto_test = BlueprintAutoTest(self)
        self._auto_test.test_completed.connect(self._on_auto_test_completed)
        
        QTimer.singleShot(500, self._auto_test.start)
        
    def test_editor_auto(self):
        """自动测试编辑器功能。"""
        from PySide6.QtCore import QTimer
        from tests.auto_test import ComponentEditorAutoTest
        
        self._auto_test = ComponentEditorAutoTest(self)
        self._auto_test.test_completed.connect(self._on_auto_test_completed)
        
        # Start the test after UI has initialized and project is loaded
        QTimer.singleShot(1000, self._auto_test.start)
    
    def _on_auto_test_completed(self, passed: bool, message: str):
        """自动化测试完成时的回调。"""
        status = "成功" if passed else "失败"
        self._session_logger.log("INFO", f"自动化测试{status}: {message}")
        print(f"\n自动化测试结束: {status} - {message}")
        # Close without prompt
        self._auto_save_service.on_application_exit = lambda _: True
        sys.exit(0 if passed else 1)
    
    def _check_unsaved_changes(self) -> bool:
        """检查是否有未保存的修改，如果有则提示用户。

        使用 Save/Discard/Cancel 三按钮对话框，
        保存失败时中止操作，确保数据不丢失。

        Returns:
            bool: True 表示可以继续操作，False 表示用户取消或保存失败
        """
        if not self._project_model or not self._project_model.is_dirty:
            return True

        # 构建三按钮对话框：保存 / 放弃 / 取消
        dialog = QMessageBox(self._navigation.stacked_widget)
        dialog.setWindowTitle("未保存的修改")
        dialog.setText("当前项目有未保存的修改。")
        dialog.setInformativeText("是否保存修改？")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Save)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        reply = dialog.exec()

        if reply == QMessageBox.StandardButton.Save:
            try:
                if self._controller:
                    self._controller._on_save_project()
                if self._project_model and self._project_model.is_dirty:
                    QMessageBox.warning(
                        self._navigation.stacked_widget,
                        "保存失败",
                        "项目保存失败，请检查文件路径和权限后重试。"
                    )
                    return False
                return True
            except Exception as e:
                self._session_logger.log("ERROR", f"保存项目时发生异常: {e}")
                QMessageBox.warning(
                    self._navigation.stacked_widget,
                    "保存失败",
                    f"保存项目时发生错误：\n{str(e)}"
                )
                return False
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
    
    def _on_close_project(self):
        if self._navigation.main_window is not None:
            if self._navigation.stacked_widget.indexOf(self._navigation.main_window) == -1:
                self._session_logger.log("WARNING", "关闭项目时 MainWindow 不在 QStackedWidget 中，忽略")
                return

        if not self._check_unsaved_changes():
            return

        self._cleanup_editor_state()

        self._navigation.show_welcome()

    def _cleanup_editor_state(self):
        if self._navigation.main_window is not None:
            try:
                self._navigation.main_window.close_project_requested.disconnect(self._on_close_project)
            except TypeError:
                pass

        if self._controller is not None:
            self._controller.project_model = None

        self._project_model = None

        self._session_logger.log("INFO", "编辑器状态已清理")

    def _on_new_project(self):
        if not self._check_unsaved_changes():
            return
        
        self._session_logger.log("INFO", "新建项目")
        self._project_model = ProjectModel()
        self._show_editor()
    
    def _on_open_project(self, file_path: str):
        if not self._check_unsaved_changes():
            return
        
        self._session_logger.log("INFO", f"打开项目文件: {file_path}")
        self._project_model = ProjectModel()
        if self._project_model.load_from_file(file_path):
            self._navigation.welcome_page.add_recent_project(
                self._project_model.name,
                file_path
            )
            self._temp_file_manager.remove_from_unsaved(file_path)
            self._show_editor()
        else:
            self._session_logger.log("ERROR", f"无法打开项目: {file_path}")
            QMessageBox.warning(
                self._navigation.stacked_widget,
                "打开失败",
                f"无法打开项目文件: {file_path}"
            )
    
    def _on_open_template(self, template_data: dict):
        """打开模板。"""
        if not self._check_unsaved_changes():
            return
        
        self._session_logger.log("INFO", "从模板创建项目")
        self._project_model = ProjectModel()
        self._project_model.from_dict(template_data)
        self._show_editor()
    
    def _on_logout(self):
        reply = QMessageBox.question(
            self._navigation.stacked_widget,
            "注销账户",
            "确定要注销账户吗？\n\n注销后需要重新注册才能使用。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            app_settings.user_name = ""
            app_settings.is_registered = False
            self._session_logger.log("INFO", "用户注销账户")
            
            register_dialog = RegisterDialog(self._navigation.stacked_widget)
            if register_dialog.exec() == RegisterDialog.DialogCode.Accepted:
                self._navigation.welcome_page._update_greeting()
            else:
                self._navigation.stacked_widget.close()
    
    def _show_editor(self):
        if self._navigation.main_window is None:
            self._navigation.main_window = MainWindow()
        
        try:
            self._navigation.main_window.close_project_requested.connect(self._on_close_project)
        except TypeError:
            pass
        
        if self._controller is None:
            self._controller = ProjectController(self._navigation.main_window, self._project_model)
        else:
            self._controller.project_model = self._project_model
        
        self._navigation.show_editor(self._project_model.name if self._project_model else "")
    
    def run(self):
        if self._session_logger:
            self._session_logger.log("INFO", "AppManager.run() 开始")
        
        try:
            from PySide6.QtGui import QGuiApplication
            platform_name = QGuiApplication.platformName()
            if self._session_logger:
                self._session_logger.log("INFO", f"Qt platform: {platform_name}")
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("WARNING", f"Failed to get platform name: {e}")

        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._deferred_init_ui)
        
        if self._session_logger:
            self._session_logger.log("INFO", "进入事件循环")
        ret = self._app.exec()
        if self._session_logger:
            self._session_logger.log("INFO", f"事件循环结束, ret={ret}")
        return ret
    
    def _deferred_init_ui(self):
        if self._session_logger:
            self._session_logger.log("INFO", "_deferred_init_ui 开始")
        
        self._navigation.show()
        self._app.setQuitOnLastWindowClosed(True)
        
        if not app_settings.is_registered:
            if self._session_logger:
                self._session_logger.log("INFO", "显示注册对话框")
            register_dialog = RegisterDialog(self._navigation.stacked_widget)
            if register_dialog.exec() != RegisterDialog.DialogCode.Accepted:
                self._app.quit()
                return
        
        try:
            if self._session_logger:
                self._session_logger.log("INFO", "开始创建 WelcomePage...")
            welcome_page = WelcomePage()
            welcome_page.new_project_requested.connect(self._on_new_project)
            welcome_page.open_project_requested.connect(self._on_open_project)
            welcome_page.open_template_requested.connect(self._on_open_template)
            welcome_page.logout_requested.connect(self._on_logout)
            self._navigation.welcome_page = welcome_page
            self._navigation.show_welcome()
            if self._session_logger:
                self._session_logger.log("INFO", "WelcomePage 创建完成")
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("ERROR", f"WelcomePage 创建失败: {e}\n{traceback.format_exc()}")
        
        if self._skip_welcome:
            self._on_new_project()

    def run_project_directly(self, project_path: str):
        """直接运行项目，不打开编辑器。
        
        Args:
            project_path: 项目文件路径
        """
        import json
        from runtime.runner import Runner
        
        self._session_logger.log("INFO", f"直接运行项目: {project_path}")
        
        try:
            from utils.py_project_format import python_code_to_dict
            with open(project_path, 'r', encoding='utf-8') as f:
                content = f.read()
            project_data = python_code_to_dict(content)
            
            runner = Runner()
            runner.run(project_data)
            
            return self._app.exec()
        except Exception as e:
            self._session_logger.log("ERROR", f"运行项目失败: {e}")
            QMessageBox.critical(
                None,
                "运行失败",
                f"无法运行项目:\n\n{str(e)}"
            )
            return 1

def main():
    """应用程序主函数。"""
    _setup_file_logging()
    sys.excepthook = exception_hook
    
    try:
        args = parse_args()
    except Exception as e:
        _write_fatal_log(f"parse_args failed: {e}")
        sys.exit(1)
    
    try:
        if args.run and args.project:
            manager = AppManager(dev_mode=args.dev)
            sys.exit(manager.run_project_directly(args.project))
        
        manager = AppManager(dev_mode=args.dev, skip_welcome=args.skip_welcome)
        
        if args.project:
            manager.open_project_file(args.project)
        
        if args.test_blueprint:
            manager.test_blueprint_auto()
            
        if getattr(args, 'auto_test_editor', False):
            manager.test_editor_auto()
        
        sys.exit(manager.run())
    except Exception as e:
        _write_fatal_log(f"Fatal error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "启动失败", f"程序启动失败:\n\n{type(e).__name__}: {e}\n\n详细日志已保存。")
        except:
            pass
        sys.exit(1)

def _setup_file_logging():
    """设置文件日志，将所有 logging 输出重定向到文件。"""
    import logging
    try:
        appdata = os.environ.get('APPDATA', '')
        log_dir = os.path.join(appdata, 'UIDevTool', 'session_logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'))
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        
        logging.getLogger().info(f"文件日志已启动: {log_file}")
    except Exception:
        pass

def _write_fatal_log(msg: str):
    try:
        from datetime import datetime
        appdata = os.environ.get('APPDATA', '')
        log_dir = os.path.join(appdata, 'UIDevTool', 'crash_logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"fatal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"UI快速开发工具 - 启动失败日志\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"cwd: {os.getcwd()}\n")
            f.write(f"{'='*60}\n\n")
            f.write(msg)
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc()
        msg = f"Python: {sys.version}\ncwd: {os.getcwd()}\nargv: {sys.argv}\n\n{tb}"
        try:
            fatal_path = os.path.join(os.getcwd(), "fatal_error.txt")
            with open(fatal_path, 'w', encoding='utf-8') as f:
                f.write(msg)
        except:
            pass
        print(msg, file=sys.stderr)
        try:
            input("程序崩溃，按回车键退出...")
        except:
            pass
        sys.exit(1)
