"""UI快速开发工具 - 主入口。

本模块是应用程序的入口点，负责初始化并启动应用程序。

命令行参数:
    python main.py                    # 正常启动
    python main.py project.itexe      # 直接打开项目文件
    python main.py --dev project.itexe # 开发者模式打开项目
"""

import sys
import os
import argparse
import traceback
from datetime import datetime
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtGui import QFont

from models import ProjectModel
from views import MainWindow
from views.welcome_page import WelcomePage
from views.register_dialog import RegisterDialog
from controllers import ProjectController
from utils.settings import app_settings
from utils.session_logger import SessionLogger


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
    
    from PySide6.QtWidgets import QMessageBox
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
        description='UI快速开发工具 - 桌面应用程序可视化开发工具'
    )
    parser.add_argument(
        'project', 
        nargs='?', 
        help='要打开的项目文件路径 (.itexe)'
    )
    parser.add_argument(
        '--dev', 
        action='store_true', 
        help='启用开发者模式'
    )
    return parser.parse_args()


class AppManager:
    """应用程序管理器。
    
    管理欢迎页和编辑器窗口之间的切换。
    """
    
    def __init__(self, dev_mode: bool = False):
        global _session_logger
        
        self._app = QApplication(sys.argv)
        
        self._session_logger = SessionLogger()
        _session_logger = self._session_logger
        self._session_logger.log("INFO", "应用程序启动")
        self._session_logger.log("INFO", f"Python版本: {sys.version}")
        self._session_logger.log("INFO", f"工作目录: {os.getcwd()}")
        self._session_logger.log("INFO", f"命令行参数: {sys.argv}")
        
        if dev_mode:
            from dev_mode import DevModeManager
            DevModeManager.get_instance().enable()
            self._session_logger.log("INFO", "开发者模式已启用")
        
        font_family = app_settings.font_family
        font_size = app_settings.font_size
        
        font = QFont(font_family, font_size)
        self._app.setFont(font)
        
        self._stacked_widget = QStackedWidget()
        self._stacked_widget.setWindowTitle("UI快速开发工具")
        self._stacked_widget.resize(1200, 800)
        
        self._welcome_page = WelcomePage()
        
        self._welcome_page.new_project_requested.connect(self._on_new_project)
        self._welcome_page.open_project_requested.connect(self._on_open_project)
        self._welcome_page.open_template_requested.connect(self._on_open_template)
        self._welcome_page.logout_requested.connect(self._on_logout)
        self._stacked_widget.addWidget(self._welcome_page)
        
        self._main_window = None
        self._project_model = None
        self._controller = None
        
        self._setup_close_event()
    
    def _setup_close_event(self):
        """设置关闭事件处理。"""
        original_close_event = self._stacked_widget.closeEvent
        
        def wrapped_close_event(event):
            if self._check_unsaved_before_exit():
                original_close_event(event)
            else:
                event.ignore()
        
        self._stacked_widget.closeEvent = wrapped_close_event
    
    def _check_unsaved_before_exit(self) -> bool:
        """退出前自动保存未保存项目。
        
        Returns:
            bool: True 表示可以退出
        """
        if not self._project_model or not self._project_model.is_dirty:
            return True
        
        self._auto_save_unsaved_project()
        return True
    
    def _auto_save_unsaved_project(self):
        """自动保存未保存项目。"""
        import tempfile
        import random
        import string
        import json
        from datetime import datetime
        
        temp_path = self._get_temp_save_path()
        if self._project_model.save_to_file(temp_path):
            self._session_logger.log("INFO", f"自动保存未保存项目: {temp_path}")
            
            unsaved_projects = self._get_unsaved_projects()
            unsaved_projects.insert(0, {
                'path': temp_path,
                'name': self._project_model.name or "未保存项目",
                'saved_at': datetime.now().isoformat()
            })
            
            if len(unsaved_projects) > 5:
                for old_project in unsaved_projects[5:]:
                    try:
                        if os.path.exists(old_project.get('path')):
                            os.remove(old_project.get('path'))
                    except:
                        pass
                unsaved_projects = unsaved_projects[:5]
            
            self._save_unsaved_projects(unsaved_projects)
    
    def _get_unsaved_projects(self) -> list:
        """获取未保存项目列表。
        
        Returns:
            list: 未保存项目列表
        """
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'UIDevTool')
        os.makedirs(config_dir, exist_ok=True)
        unsaved_file = os.path.join(config_dir, 'unsaved_projects.json')
        
        try:
            if os.path.exists(unsaved_file):
                with open(unsaved_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _save_unsaved_projects(self, projects: list):
        """保存未保存项目列表。
        
        Args:
            projects: 未保存项目列表
        """
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'UIDevTool')
        os.makedirs(config_dir, exist_ok=True)
        unsaved_file = os.path.join(config_dir, 'unsaved_projects.json')
        
        try:
            with open(unsaved_file, 'w', encoding='utf-8') as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _get_temp_save_path(self) -> str:
        """生成临时保存路径。
        
        Returns:
            str: 临时文件路径
        """
        import tempfile
        import random
        import string
        
        random_str = ''.join(random.choices(string.digits, k=8))
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, f"unsaved_project_{random_str}.itexe")
    
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
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                None,
                "文件不存在",
                f"项目文件不存在: {file_path}"
            )
            self._stacked_widget.show()
    
    def _check_unsaved_changes(self) -> bool:
        """检查是否有未保存的修改，如果有则提示用户。
        
        Returns:
            bool: True 表示可以继续操作，False 表示用户取消了操作
        """
        if not self._project_model or not self._project_model.is_dirty:
            return True
        
        from PySide6.QtWidgets import QMessageBox
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
        """打开项目。"""
        if not self._check_unsaved_changes():
            return
        
        self._session_logger.log("INFO", f"打开项目文件: {file_path}")
        self._project_model = ProjectModel()
        if self._project_model.load_from_file(file_path):
            self._welcome_page.add_recent_project(
                self._project_model.name,
                file_path
            )
            self._remove_from_unsaved_projects(file_path)
            self._show_editor()
        else:
            self._session_logger.log("ERROR", f"无法打开项目: {file_path}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self._stacked_widget,
                "打开失败",
                f"无法打开项目文件: {file_path}"
            )
    
    def _remove_from_unsaved_projects(self, file_path: str):
        """从未保存项目列表中删除项目。
        
        Args:
            file_path: 项目文件路径
        """
        import json
        
        normalized_path = os.path.normpath(os.path.abspath(file_path))
        unsaved_projects = self._get_unsaved_projects()
        
        updated_projects = []
        for project in unsaved_projects:
            project_path = os.path.normpath(os.path.abspath(project.get('path', '')))
            if project_path != normalized_path:
                updated_projects.append(project)
            else:
                try:
                    if os.path.exists(project.get('path')):
                        os.remove(project.get('path'))
                except:
                    pass
        
        self._save_unsaved_projects(updated_projects)
    
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
        from PySide6.QtWidgets import QMessageBox
        
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
        
        self._stacked_widget.show()
        return self._app.exec()


def main():
    """应用程序主函数。"""
    sys.excepthook = exception_hook
    
    args = parse_args()
    
    manager = AppManager(dev_mode=args.dev)
    
    if args.project:
        manager.open_project_file(args.project)
    
    sys.exit(manager.run())


if __name__ == "__main__":
    main()
