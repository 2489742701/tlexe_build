"""UI快速开发工具 - 主入口。

本模块是应用程序的入口点，负责初始化并启动应用程序。

命令行参数:
    python main.py                           # 正常启动，显示欢迎页
    python main.py project.itexe             # 直接打开项目文件
    python main.py --dev project.itexe       # 开发者模式打开项目
    python main.py --run project.itexe       # 直接运行项目（不打开编辑器）
    python main.py --skip-welcome            # 跳过欢迎页，直接显示空白编辑器
    python main.py -r -d samples/demo.itexe  # 开发者模式直接运行项目

## 修复说明 (2026-04-02)
【问题】AppManager 类承担了过多职责（初始化、日志、开发者模式、字体设置、
自动保存、临时文件管理等），违反了单一职责原则。

【解决方案】
1. 创建 services/initialization.py - AppInitializer 负责应用初始化
2. 创建 services/auto_save_service.py - AutoSaveService 负责自动保存
3. 创建 utils/temp_file_manager.py - TempFileManager 负责临时文件管理
4. 简化 AppManager，只保留窗口管理相关的逻辑

【收益】
- 职责分离清晰，每个类只负责单一职责
- 易于单元测试，可以单独测试各个服务
- 新增功能只需扩展对应的服务，无需修改主类
"""

import sys
import os
import argparse
import traceback
from datetime import datetime
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox

from models import ProjectModel
from views import MainWindow
from views.welcome_page import WelcomePage
from views.register_dialog import RegisterDialog
from controllers import ProjectController
from utils.settings import app_settings
from utils.session_logger import SessionLogger
from utils.temp_file_manager import TempFileManager
from services import AppInitializer, AutoSaveService


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
  python main.py project.itexe             # 直接打开项目文件
  python main.py --run project.itexe       # 直接运行项目
  python main.py -r -d samples/demo.itexe  # 开发者模式运行项目
  python main.py --skip-welcome            # 跳过欢迎页
        '''
    )
    parser.add_argument(
        'project', 
        nargs='?', 
        help='要打开的项目文件路径 (.itexe)'
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
        'project', 
        nargs='?', 
        help='要打开的项目文件路径 (.itexe)'
    )
    return parser.parse_args()


class AppManager:
    """应用程序管理器。
    
    管理欢迎页和编辑器窗口之间的切换。
    
    ## 修复说明 (2026-04-02)
    【重构前】此类承担了过多职责：
    - 应用初始化（QApplication 创建、日志初始化、开发者模式、字体设置）
    - 自动保存逻辑（_auto_save_unsaved_project, _check_unsaved_before_exit）
    - 临时文件管理（_get_unsaved_projects, _save_unsaved_projects, _get_temp_save_path）
    - 窗口管理（欢迎页、编辑器切换）
    
    【重构后】职责分离：
    - AppInitializer: 负责应用初始化
    - AutoSaveService: 负责自动保存
    - TempFileManager: 负责临时文件管理
    - AppManager: 只负责窗口管理和用户交互流程
    
    这样每个类都有单一的、明确的职责，符合单一职责原则。
    """
    
    def __init__(self, dev_mode: bool = False, skip_welcome: bool = False):
        """初始化应用程序管理器。
        
        Args:
            dev_mode: 是否启用开发者模式
            skip_welcome: 是否跳过欢迎页
            
        ## 修复说明 (2026-04-02)
        使用 AppInitializer 进行初始化，移除了原本散落在 __init__ 中的
        各种初始化代码，使此方法更加简洁清晰。
        """
        global _session_logger
        
        # 使用 AppInitializer 进行应用初始化
        # 修复：将初始化逻辑抽取到独立的服务类
        initializer = AppInitializer(dev_mode=dev_mode, skip_welcome=skip_welcome)
        self._app = initializer.run()
        
        # 获取会话日志记录器，用于全局异常处理
        _session_logger = initializer._session_logger
        self._session_logger = initializer._session_logger
        
        # 初始化自动保存服务
        # 修复：将自动保存逻辑抽取到 AutoSaveService
        self._auto_save_service = AutoSaveService(session_logger=self._session_logger)
        
        # 初始化临时文件管理器
        # 修复：将临时文件管理抽取到 TempFileManager
        self._temp_file_manager = TempFileManager()
        
        self._skip_welcome = skip_welcome
        
        # 设置主窗口
        self._stacked_widget = QStackedWidget()
        self._stacked_widget.setWindowTitle("UI快速开发工具")
        self._stacked_widget.resize(1200, 800)
        
        # 创建欢迎页
        self._welcome_page = WelcomePage()
        self._welcome_page.new_project_requested.connect(self._on_new_project)
        self._welcome_page.open_project_requested.connect(self._on_open_project)
        self._welcome_page.open_template_requested.connect(self._on_open_template)
        self._welcome_page.logout_requested.connect(self._on_logout)
        self._stacked_widget.addWidget(self._welcome_page)
        
        # 初始化其他成员
        self._main_window = None
        self._project_model = None
        self._controller = None
        
        # 设置关闭事件处理
        self._setup_close_event()
    
    def _setup_close_event(self):
        """设置关闭事件处理。
        
        ## 修复说明 (2026-04-02)
        使用 AutoSaveService 处理退出前的自动保存逻辑。
        """
        original_close_event = self._stacked_widget.closeEvent
        
        def wrapped_close_event(event):
            # 修复：使用 AutoSaveService 处理自动保存
            if self._auto_save_service.on_application_exit(self._project_model):
                original_close_event(event)
            else:
                event.ignore()
        
        self._stacked_widget.closeEvent = wrapped_close_event
    
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
            self._stacked_widget.show()
    
    def test_blueprint_auto(self):
        """自动测试蓝图功能。
        
        使用基于信号的自动化测试框架，自动打开示例项目并测试状态机视图。
        """
        from PySide6.QtCore import QTimer
        from tests.auto_test import BlueprintAutoTest
        
        self._auto_test = BlueprintAutoTest(self)
        self._auto_test.test_completed.connect(self._on_auto_test_completed)
        
        QTimer.singleShot(500, self._auto_test.start)
    
    def _on_auto_test_completed(self, passed: bool, message: str):
        """自动化测试完成时的回调。"""
        status = "成功" if passed else "失败"
        self._session_logger.log("INFO", f"自动化测试{status}: {message}")
    
    def _check_unsaved_changes(self) -> bool:
        """检查是否有未保存的修改，如果有则提示用户。
        
        Returns:
            bool: True 表示可以继续操作，False 表示用户取消了操作
        """
        if not self._project_model or not self._project_model.is_dirty:
            return True
        
        reply = QMessageBox.question(
            self._stacked_widget,
            "未保存的修改",
            "当前项目有未保存的修改，是否保存？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self._controller:
                self._controller._on_save_project()
            return True
        elif reply == QMessageBox.StandardButton.No:
            return True
        else:
            return False
    
    def _on_new_project(self):
        """新建项目。"""
        if not self._check_unsaved_changes():
            return
        
        self._session_logger.log("INFO", "新建项目")
        self._project_model = ProjectModel()
        self._show_editor()
    
    def _on_open_project(self, file_path: str):
        """打开项目。
        
        ## 修复说明 (2026-04-02)
        使用 TempFileManager 处理未保存项目列表的更新。
        """
        if not self._check_unsaved_changes():
            return
        
        self._session_logger.log("INFO", f"打开项目文件: {file_path}")
        self._project_model = ProjectModel()
        if self._project_model.load_from_file(file_path):
            self._welcome_page.add_recent_project(
                self._project_model.name,
                file_path
            )
            # 修复：使用 TempFileManager 移除已保存的项目
            self._temp_file_manager.remove_from_unsaved(file_path)
            self._show_editor()
        else:
            self._session_logger.log("ERROR", f"无法打开项目: {file_path}")
            QMessageBox.warning(
                self._stacked_widget,
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
        """注销账户。"""
        reply = QMessageBox.question(
            self._stacked_widget,
            "注销账户",
            "确定要注销账户吗？\n\n注销后需要重新注册才能使用。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            app_settings.user_name = ""
            app_settings.is_registered = False
            self._session_logger.log("INFO", "用户注销账户")
            
            register_dialog = RegisterDialog(self._stacked_widget)
            if register_dialog.exec() == RegisterDialog.DialogCode.Accepted:
                self._welcome_page._update_greeting()
            else:
                self._stacked_widget.close()
    
    def _show_editor(self):
        """显示编辑器窗口。"""
        if self._main_window is None:
            self._main_window = MainWindow()
            self._stacked_widget.addWidget(self._main_window)
        
        if self._controller is None:
            self._controller = ProjectController(self._main_window, self._project_model)
        else:
            self._controller.project_model = self._project_model
        
        self._stacked_widget.setCurrentWidget(self._main_window)
        self._stacked_widget.setWindowTitle(f"{self._project_model.name} - UI快速开发工具")
    
    def run(self):
        """运行应用程序。"""
        if not app_settings.is_registered:
            register_dialog = RegisterDialog(self._stacked_widget)
            if register_dialog.exec() != RegisterDialog.DialogCode.Accepted:
                return 0
        
        if self._skip_welcome:
            self._on_new_project()
        
        self._stacked_widget.show()
        return self._app.exec()
    
    def run_project_directly(self, project_path: str):
        """直接运行项目，不打开编辑器。
        
        Args:
            project_path: 项目文件路径
        """
        import json
        from runtime.runner import Runner
        
        self._session_logger.log("INFO", f"直接运行项目: {project_path}")
        
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
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
    sys.excepthook = exception_hook
    
    args = parse_args()
    
    if args.run and args.project:
        manager = AppManager(dev_mode=args.dev)
        sys.exit(manager.run_project_directly(args.project))
    
    manager = AppManager(dev_mode=args.dev, skip_welcome=args.skip_welcome)
    
    if args.project:
        manager.open_project_file(args.project)
    
    if args.test_blueprint:
        manager.test_blueprint_auto()
    
    sys.exit(manager.run())


if __name__ == "__main__":
    main()
