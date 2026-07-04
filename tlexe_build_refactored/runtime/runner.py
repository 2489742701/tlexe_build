"""窗口运行器模块。

将项目数据转换为实际运行的窗口界面，使用统一的组件工厂创建控件，
确保与画布预览一致。

主要功能:
    - 解析项目数据并创建窗口
    - 创建组件并设置正确的位置和大小
    - 处理容器和子组件的层级关系
    - 执行组件动作和事件处理

命名约定:
    - 私有字典：_{名词}（_windows, _components, _containers）
    - 窗口操作：_{动词}_window（_create_window, _open_event_window, _safe_close_window）
    - 组件创建：_create_component_from_dict

注意:
    - 运行时调试输出应使用 debug_log()，不要使用 print()
    - _safe_close_window 不调用 QApplication.quit()，打包输出的 exe 由入口脚本自行退出
"""

import sys
import os
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication
from PySide6.QtCore import Qt, QTimer

from utils.component_factory import create_component_widget
from utils.settings import app_settings
from .action_executor import ActionExecutor

def _log_to_file(level: str, message: str):
    """将日志写入文件。"""
    try:
        appdata = os.environ.get('APPDATA', '')
        log_dir = os.path.join(appdata, 'UIDevTool', 'runtime_logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"runtime_{datetime.now().strftime('%Y%m%d')}.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    except Exception:
        pass

def _log_crash(error_msg: str):
    """记录崩溃日志。"""
    try:
        appdata = os.environ.get('APPDATA', '')
        crash_log_dir = os.path.join(appdata, 'UIDevTool', 'crash_logs')
        os.makedirs(crash_log_dir, exist_ok=True)
        
        crash_file = os.path.join(crash_log_dir, f"runtime_crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        with open(crash_file, 'w', encoding='utf-8') as f:
            f.write(f"UI快速开发工具 - 运行时崩溃日志\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            f.write(error_msg)
        
        print(f"运行时崩溃日志已保存到: {crash_file}")
        return crash_file
    except Exception as e:
        print(f"无法保存崩溃日志: {e}")
        return None

def debug_log(category: str, message: str, force: bool = False):
    """调试日志输出。
    
    Args:
        category: 日志类别 (position/component/general)
        message: 日志消息
        force: 是否强制输出（忽略开关设置）
    """
    if not app_settings.debug_verbose and not force:
        return
    
    if category == 'position' and not app_settings.debug_show_position and not force:
        return
    
    if category == 'component' and not app_settings.debug_show_component_details and not force:
        return
    
    print(message)
    _log_to_file("DEBUG", f"[{category}] {message}")
    
    try:
        from dev_mode.debug_logger import DebugLogger
        DebugLogger.debug(f"[{category}] {message}", "runner")
    except Exception:
        pass

class Runner:
    """窗口运行器。
    
    负责将项目数据转换为实际运行的窗口。
    使用统一的组件工厂创建控件，确保与画布预览一致。
    """
    
    TITLE_BAR_HEIGHT = 28
    
    def __init__(self):
        self._windows: Dict[str, QMainWindow] = {}
        self._components: Dict[str, Any] = {}
        self._component_models: Dict[str, Any] = {}
        self._containers: Dict[str, QWidget] = {}
        self._container_positions: Dict[str, tuple] = {}
        self._container_original_positions: Dict[str, tuple] = {}
        self._container_parents: Dict[str, str] = {}
        self._executor: Optional[ActionExecutor] = None
        self._linkage_manager: Optional[Any] = None
        self._project_data: Dict[str, Any] = {}
        self._runtime_console = None
        self._exception_interceptor = None
    
    def run(self, project_data: Dict[str, Any]):
        """运行项目。
        
        将项目数据转换为实际运行的窗口界面。
        创建主窗口、组件，并设置事件处理。
        
        Args:
            project_data: 项目数据字典，包含窗口和组件信息
        """
        try:
            print(f"\n{'='*50}")
            print(f"开始运行项目")
            print(f"{'='*50}")
            _log_to_file("INFO", f"开始运行项目")
            _log_to_file("INFO", f"项目数据键: {list(project_data.keys())}")
            debug_log('general', f"项目数据键: {list(project_data.keys())}")
            
            self._project_data = project_data
            
            from models.registry_init import register_all_components
            register_all_components()
            
            main_window_id = project_data.get('main_window_id')
            if not main_window_id:
                print("错误: 未找到主窗口ID")
                _log_to_file("ERROR", "未找到主窗口ID")
                return
            
            debug_log('general', f"主窗口ID: {main_window_id}")
            
            windows = project_data.get('windows', [])
            main_window_data = None
            for win in windows:
                if win.get('id') == main_window_id:
                    main_window_data = win
                    break
            
            if not main_window_data:
                print(f"错误: 未找到ID为 {main_window_id} 的窗口数据")
                _log_to_file("ERROR", f"未找到ID为 {main_window_id} 的窗口数据")
                return
            
            debug_log('general', f"主窗口名称: {main_window_data.get('name', '未命名')}")
            
            from models import ProjectModel
            self._project_model = ProjectModel()
            self._project_model.from_dict(project_data)
            
            window = self._create_window(main_window_data)
            if window:
                self._windows[main_window_id] = window
                
                self._executor = ActionExecutor(self._project_model)
                
                from .linkage_manager import LinkageManager
                self._linkage_manager = LinkageManager(self._project_model, self._executor)
                self._linkage_manager.setup_linkages()
                
                self._setup_actions(window, main_window_data)
                
                self._attach_runtime_console(window)
                self._install_exception_interceptor()

                print(f"\n窗口创建完成，组件数量: {len(self._components)}")
                _log_to_file("INFO", f"窗口创建完成，组件数量: {len(self._components)}")
                window.show()
                print("窗口已显示")
            else:
                print("错误: 窗口创建失败")
                _log_to_file("ERROR", "窗口创建失败")
            
            print(f"\n{'='*50}")
            print("项目运行完成")
            print(f"{'='*50}\n")
            _log_to_file("INFO", "项目运行完成")
        except Exception as e:
            error_msg = f"运行项目时发生错误:\n{traceback.format_exc()}"
            print(f"\n{'!'*60}\n{error_msg}\n{'!'*60}")
            _log_to_file("CRITICAL", error_msg)
            crash_file = _log_crash(error_msg)
            
            try:
                from dev_mode.debug_logger import DebugLogger
                DebugLogger.critical(error_msg, "runner")
            except Exception:
                pass
            
            if self._runtime_console:
                self._runtime_console.append_error(error_msg)
            
            from views.custom_dialogs import ErrorDialog
            try:
                ErrorDialog.show_error(
                    None,
                    "运行错误",
                    f"运行项目时发生错误:\n\n{str(e)}\n\n错误日志已保存到:\n{crash_file or '未知'}"
                )
            except Exception:
                pass
    
    def _attach_runtime_console(self, main_window: QMainWindow):
        """创建独立控制台弹窗，不破坏原有UI。"""
        try:
            from .runtime_console import RuntimeConsole
            
            self._runtime_console = RuntimeConsole()
            self._console_window = QMainWindow()
            self._console_window.setWindowTitle("运行时控制台")
            self._console_window.setCentralWidget(self._runtime_console)
            self._console_window.resize(600, 300)
            self._console_window.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
            
            screen = main_window.screen().availableGeometry()
            x = screen.x() + screen.width() - 620
            y = screen.y() + screen.height() - 340
            self._console_window.move(x, y)
            self._console_window.show()
            
            original_close = main_window.closeEvent
            def _close_event(event):
                self._close_console_window()
                original_close(event)
            main_window.closeEvent = _close_event
            
            from dev_mode.debug_logger import DebugLogger
            DebugLogger.info("运行时控制台已启动", "runtime")
        except Exception as e:
            debug_log('general', f"控制台创建失败: {e}", force=True)
    
    def _close_console_window(self):
        """关闭控制台弹窗。"""
        if hasattr(self, '_console_window') and self._console_window:
            self._console_window.close()
            self._console_window = None
    
    def _install_exception_interceptor(self):
        """安装全局异常拦截器，捕获未处理异常并显示到控制台。"""
        try:
            from .runtime_console import ExceptionInterceptor
            self._exception_interceptor = ExceptionInterceptor(self._runtime_console)
            self._exception_interceptor.install()
        except Exception as e:
            debug_log('general', f"异常拦截器安装失败: {e}", force=True)
    
    def _create_window(self, win_data: Dict[str, Any]) -> Optional[QMainWindow]:
        """创建窗口。
        
        Args:
            win_data: 窗口数据
            
        Returns:
            创建的窗口对象
        """
        print(f"\n{'='*50}")
        print(f"创建窗口: {win_data.get('name', '未命名')}")
        print(f"{'='*50}")
        
        window = QMainWindow()
        window.setWindowTitle(win_data.get('title', '窗口'))
        
        frameless = win_data.get('frameless', False)
        window_color = win_data.get('window_color', '')
        
        if frameless:
            window.setWindowFlags(Qt.FramelessWindowHint)
        
        if window_color:
            window.setStyleSheet(f"background-color: {window_color};")
        
        window_width = win_data.get('width', 800)
        window_height = win_data.get('height', 600)
        
        components_data = self._project_data.get('components', [])
        comp_ids = win_data.get('components', [])
        
        debug_log('component', f"窗口包含的组件ID: {comp_ids}")
        
        container_data = None
        for comp_data in components_data:
            if comp_data.get('id') in comp_ids:
                comp_type = comp_data.get('type') or comp_data.get('comp_type', '')
                if comp_type == 'container':
                    container_data = comp_data
                    debug_log('component', f"找到容器: {comp_data.get('name')} 位置=({comp_data.get('x')}, {comp_data.get('y')}) 大小=({comp_data.get('width', 800)}, {comp_data.get('height', 600)})")
                    break
        
        debug_log('component', f"窗口大小: {window_width} x {window_height}")
        
        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)
        window.setCentralWidget(central_widget)
        window.resize(window_width, window_height)
        window.setMaximumSize(window_width, window_height)
        
        container_comps = []
        other_comps = []
        
        for comp_data in components_data:
            if comp_data.get('id') in comp_ids:
                comp_type = comp_data.get('type') or comp_data.get('comp_type', '')
                if comp_type == 'container':
                    container_comps.append(comp_data)
                else:
                    other_comps.append(comp_data)
        
        # 没有容器的窗口：创建一个铺满窗口的隐式容器
        if not container_comps:
            from PySide6.QtWidgets import QFrame
            implicit_container = QFrame(central_widget)
            implicit_container.setStyleSheet("background-color: transparent;")
            implicit_container.resize(window_width, window_height)
            self._implicit_container = implicit_container
        else:
            self._implicit_container = None
        
        sorted_containers = self._build_container_hierarchy(container_comps)
        
        print(f"\n--- 创建容器组件 ({len(sorted_containers)}个) ---")
        for comp_data in sorted_containers:
            comp = self._create_component_from_dict(comp_data, current_window=window)
            if comp:
                container_width = comp_data.get('width', 400)
                container_height = comp_data.get('height', 300)
                orig_x = comp_data.get('x', 0)
                orig_y = comp_data.get('y', 0)
                parent_id = comp_data.get('parent_id', '')
                
                if parent_id and parent_id in self._containers:
                    parent_container = self._containers[parent_id]
                    comp.setParent(parent_container)
                    rel_x, rel_y = self._calculate_relative_position(comp_data, parent_id)
                    comp.setGeometry(rel_x, rel_y, container_width, container_height)
                    debug_log('position', f"  嵌套容器相对位置: ({rel_x}, {rel_y})")
                else:
                    comp.setParent(central_widget)
                    comp.setGeometry(orig_x, orig_y, container_width, container_height)
                
                self._components[comp_data['id']] = comp
                self._containers[comp_data['id']] = comp
                self._container_positions[comp_data['id']] = (0, 0)
                self._container_original_positions[comp_data['id']] = (orig_x, orig_y)
                
                print(f"\n[容器] {comp_data.get('name')}")
                debug_log('position', f"  ID: {comp_data.get('id')}")
                debug_log('position', f"  原始位置: ({orig_x}, {orig_y})")
                debug_log('position', f"  大小: ({container_width}, {container_height})")
        
        print(f"\n--- 创建其他组件 ({len(other_comps)}个) ---")
        for comp_data in other_comps:
            comp = self._create_component_from_dict(comp_data, current_window=window)
            if comp:
                parent_id = comp_data.get('parent_id', '')
                comp_name = comp_data.get('name', '未命名')
                comp_id = comp_data.get('id', '')
                comp_x = comp_data.get('x', 0)
                comp_y = comp_data.get('y', 0)
                comp_w = comp_data.get('width', 100)
                comp_h = comp_data.get('height', 30)
                comp_type = comp_data.get('type') or comp_data.get('comp_type', 'unknown')
                
                print(f"\n[{comp_type}] {comp_name}")
                debug_log('position', f"  ID: {comp_id}")
                debug_log('position', f"  原始位置: ({comp_x}, {comp_y})")
                debug_log('position', f"  大小: ({comp_w}, {comp_h})")
                debug_log('position', f"  父容器ID: {parent_id if parent_id else '无'}")
                
                if parent_id and parent_id in self._containers:
                    parent_container = self._containers[parent_id]
                    comp.setParent(parent_container)
                    
                    relative_x, relative_y = self._calculate_relative_position(comp_data, parent_id)
                    
                    debug_log('position', f"  计算相对位置: ({relative_x}, {relative_y})")
                    debug_log('position', f"  最终位置: ({relative_x}, {relative_y})")
                    
                    comp.setGeometry(relative_x, relative_y, comp_w, comp_h)
                else:
                    parent = self._implicit_container if self._implicit_container else central_widget
                    comp.setParent(parent)
                    debug_log('position', f"  无父容器，使用绝对位置: ({comp_x}, {comp_y})")
                    debug_log('position', f"  最终位置: ({comp_x}, {comp_y})")
                    comp.setGeometry(comp_x, comp_y, comp_w, comp_h)
                
                self._components[comp_data['id']] = comp
        
        print(f"\n{'='*50}")
        print(f"窗口创建完成")
        print(f"{'='*50}")
        return window
    
    def _build_container_hierarchy(self, container_comps: list):
        """构建容器层级关系并排序。
        
        确保父容器在子容器之前创建。
        
        Args:
            container_comps: 容器组件数据列表
            
        Returns:
            排序后的容器列表（父容器在前）
        """
        self._container_parents: Dict[str, str] = {}
        comp_by_id: Dict[str, Dict] = {}
        
        for comp_data in container_comps:
            comp_id = comp_data.get('id', '')
            parent_id = comp_data.get('parent_id', '')
            comp_by_id[comp_id] = comp_data
            if parent_id:
                self._container_parents[comp_id] = parent_id
        
        sorted_containers = []
        visited = set()
        
        def visit(comp_id: str):
            if comp_id in visited:
                return
            visited.add(comp_id)
            
            if comp_id in self._container_parents:
                parent_id = self._container_parents[comp_id]
                if parent_id in comp_by_id:
                    visit(parent_id)
            
            sorted_containers.append(comp_by_id[comp_id])
        
        for comp_id in comp_by_id:
            visit(comp_id)
        
        return sorted_containers
    
    def _calculate_relative_position(self, comp_data: Dict[str, Any], parent_id: str) -> tuple:
        """计算组件相对于父容器的位置。
        
        注意：设计器（Designer）在组件被放入容器时，保存到模型的 x 和 y
        已经是相对于父容器的局部坐标了。所以这里直接返回即可，不需要再减去父容器坐标。
        
        Args:
            comp_data: 组件数据
            parent_id: 直接父容器ID
            
        Returns:
            (relative_x, relative_y) 相对位置元组
        """
        comp_x = comp_data.get('x', 0)
        comp_y = comp_data.get('y', 0)
        
        # 设计器保存的已经是相对坐标，直接返回
        return comp_x, comp_y
    
    def _create_component_from_dict(self, comp_data: Dict[str, Any], current_window=None) -> Optional[QWidget]:
        """从字典数据创建组件。
        
        使用统一的组件工厂创建控件。
        优先使用 project_model 中已有的 model 实例（保证信号一致性）。
        
        Args:
            comp_data: 组件数据字典
            
        Returns:
            创建的组件对象
        """
        from models.component_registry import ComponentRegistry
        
        comp_type = comp_data.get('comp_type') or comp_data.get('type', 'label')
        comp_id = comp_data.get('id', '')
        
        comp_class = ComponentRegistry.get_model_class(comp_type)
        if comp_class:
            if hasattr(self, '_project_model') and self._project_model:
                model = self._project_model.get_component(comp_id)
            if not model:
                model = comp_class.from_dict(comp_data)
            self._component_models[comp_id] = model
            widget = create_component_widget(model)
            
            if comp_type == 'progressbar':
                auto_progress = comp_data.get('auto_progress', False)
                duration = comp_data.get('duration', 3)
                if auto_progress and widget:
                    self._setup_auto_progress(widget, comp_data, duration, current_window=current_window)
            
            return widget
        
        return None
    
    def _setup_auto_progress(self, progressbar, comp_data: Dict[str, Any], duration: int, current_window=None):
        """设置自动进度条。
        
        进度条完成后，与按钮逻辑一致：
        1. 如果有 target_window_id，打开目标窗口
        2. 如果有 action.action_type，执行对应动作
        """
        steps = 100
        interval = int(duration * 1000 / steps)
        current_step = [0]
        
        def update_progress():
            current_step[0] += 1
            progressbar.setValue(current_step[0])
            
            if current_step[0] >= 100:
                timer = progressbar._auto_timer
                if timer:
                    timer.stop()
                    timer.deleteLater()
                    progressbar._auto_timer = None
                
                target_window_id = comp_data.get('target_window_id')
                action = comp_data.get('action', {})
                action_type = action.get('action_type', 'none')
                
                if target_window_id:
                    self._open_event_window(target_window_id)
                elif action_type == 'close_program':
                    self._close_all_windows()
                elif action_type == 'close_window':
                    if current_window:
                        current_window.close()
        
        timer = QTimer(progressbar)
        timer.timeout.connect(update_progress)
        timer.start(interval)
        progressbar._auto_timer = timer
    
    def _setup_actions(self, window: QMainWindow, win_data: Dict[str, Any]):
        """设置窗口动作。"""
        components_data = self._project_data.get('components', [])
        comp_ids = win_data.get('components', [])
        
        for comp_data in components_data:
            if comp_data.get('id') in comp_ids:
                comp_id = comp_data['id']
                comp_type = comp_data.get('comp_type') or comp_data.get('type')
                
                if comp_type == 'button':
                    button = self._components.get(comp_id)
                    if button:
                        target_window_id = comp_data.get('target_window_id')
                        action = comp_data.get('action', {})
                        action_type = action.get('action_type', 'none')
                        
                        if action_type == 'close_program':
                            button.clicked.connect(self._close_all_windows)
                        elif action_type == 'close_window':
                            wid = win_data.get('id', '')
                            button.clicked.connect(lambda checked, w=window, wid=wid: self._safe_close_window(wid, w))
                        elif action_type == 'lottery_animation' and target_window_id:
                            self._setup_lottery_button(button, comp_data, target_window_id)
                        elif action_type == 'start_alternating':
                            self._setup_alternating_toggle(button, comp_data)
                        elif comp_type == 'confirm_button':
                            self._setup_confirm_button(button, comp_data, win_data)
                        else:
                            if target_window_id:
                                button.clicked.connect(lambda checked, twid=target_window_id: self._open_event_window(twid))
                            
                            if action_type != 'none':
                                button.clicked.connect(lambda checked, cid=comp_id: self._execute_button_action(cid))
    
    def _setup_confirm_button(self, button, comp_data: Dict[str, Any], win_data: Dict[str, Any]):
        """设置确认按钮：同窗口内全部按下才触发动作。
        
        同一窗口中的所有 confirm_button 自动归为一组，
        全部确认后执行按钮配置的 action（跳转窗口等）。
        """
        comp_id = comp_data.get('id', '')
        win_id = win_data.get('id', '') if win_data else 'default'
        model = self._project_model.get_component(comp_id)
        if not model:
            return
        
        if not hasattr(self, '_confirm_groups'):
            self._confirm_groups = {}
        if win_id not in self._confirm_groups:
            self._confirm_groups[win_id] = {}
        self._confirm_groups[win_id][comp_id] = model
        
        original_style = button.styleSheet()
        
        def on_click():
            model.toggle()
            if model.is_confirmed:
                button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px;")
            else:
                button.setStyleSheet(original_style)
            
            all_confirmed = all(
                getattr(m, 'is_confirmed', False)
                for m in self._confirm_groups[win_id].values()
            )
            
            if all_confirmed:
                action = comp_data.get('action', {})
                action_type = action.get('action_type', 'none')
                target_window_id = comp_data.get('target_window_id', '')
                
                if target_window_id:
                    self._open_event_window(target_window_id)
                elif action_type != 'none':
                    self._execute_button_action(comp_id)
                
                from dev_mode.debug_logger import DebugLogger
                DebugLogger.info(f"窗口 '{win_id}' 确认按钮全部确认，动作已触发", "runtime")
        
        button.clicked.connect(on_click)
    
    def _setup_alternating_toggle(self, button, comp_data: Dict[str, Any]):
        """设置交替变换的开始/暂停切换按钮。
        
        点击"开始"→启动动画，按钮变"暂停"
        点击"暂停"→停止动画，按钮变"开始"，发射 stopped 信号
        """
        action = comp_data.get('action', {})
        params = action.get('params', {})
        target_component_id = params.get('target_component_id', '')
        
        if not target_component_id:
            return
        
        original_text = comp_data.get('text', '开始')
        stop_text = '暂停' if original_text == '开始' else original_text.replace('开始', '暂停')
        start_text = original_text
        
        state = {'running': False}
        
        def on_toggle():
            comp_model = self._project_model.get_component(target_component_id)
            if not comp_model:
                return
            
            if state['running']:
                comp_model.stop_alternating()
                button.setText(start_text)
                button.setStyleSheet(button.styleSheet().replace('#f44336', '#4CAF50').replace('#d32f2f', '#388E3C'))
                state['running'] = False
            else:
                action_params = params.get('action_params', {})
                duration_ms = action_params.get('duration_ms', 3000)
                comp_model.start_alternating(duration_ms=duration_ms)
                button.setText(stop_text)
                button.setStyleSheet(button.styleSheet().replace('#4CAF50', '#f44336').replace('#388E3C', '#d32f2f'))
                state['running'] = True
        
        def on_stopped(*args):
            button.setText(start_text)
            button.setStyleSheet(button.styleSheet().replace('#f44336', '#4CAF50').replace('#d32f2f', '#388E3C'))
            state['running'] = False
        
        button.clicked.connect(on_toggle)
        
        target_model = self._project_model.get_component(target_component_id)
        if target_model and hasattr(target_model, 'stopped'):
            target_model.stopped.connect(on_stopped)
    
    def _setup_lottery_button(self, button, comp_data: Dict[str, Any], target_window_id: str):
        """设置抽奖按钮，在动画完成后打开目标窗口。
        
        Args:
            button: 按钮控件
            comp_data: 组件数据
            target_window_id: 目标窗口ID
        """
        action = comp_data.get('action', {})
        params = action.get('params', {})
        target_component_id = params.get('target_component_id', '')
        
        if not target_component_id:
            return
        
        target_component = self._project_model.get_component(target_component_id)
        if not target_component:
            return
        
        def on_lottery_finished(*args):
            self._open_event_window(target_window_id)
        
        if hasattr(target_component, 'lottery_finished'):
            target_component.lottery_finished.connect(on_lottery_finished)
        
        button.clicked.connect(lambda checked, cid=comp_data['id']: self._execute_button_action(cid))
    
    def _execute_button_action(self, comp_id: str):
        """执行按钮动作。"""
        comp_model = self._project_model.get_component(comp_id)
        if comp_model and hasattr(comp_model, 'action'):
            action = comp_model.action
            debug_log('general', f"执行动作: comp_id={comp_id}, action_type={action.action_type}, target={action.get_target_component_id()}, params={action.get_action_params()}", force=True)
            result = self._executor.execute(action)
            debug_log('general', f"动作执行结果: {result}", force=True)
        else:
            debug_log('general', f"按钮动作执行失败: comp_id={comp_id}, model={comp_model}", force=True)
    
    def _open_event_window(self, window_id: str):
        """打开事件窗口（基于MCP建议的优化版）。
        
        修复说明：
        - 打开新窗口时安全关闭其他窗口，避免窗口堆积
        - 保持主程序窗口的特殊处理（如果存在）
        - 添加内存安全机制，防止内存泄漏
        """
        # 先安全关闭所有其他窗口（除了主程序窗口）
        main_window_id = self._project_data.get('main_window_id')
        for existing_window_id, existing_window in list(self._windows.items()):
            # 保留主程序窗口，关闭其他窗口
            if existing_window_id != main_window_id and existing_window_id != window_id:
                self._safe_close_window(existing_window_id, existing_window)
        
        # 如果窗口已存在，先安全关闭再重建（确保组件状态与数据一致）
        if window_id in self._windows:
            self._safe_close_window(window_id, self._windows[window_id])
        
        # 查找窗口数据并创建新窗口
        windows = self._project_data.get('windows', [])
        win_data = None
        for win in windows:
            if win.get('id') == window_id:
                win_data = win
                break
        
        if win_data:
            window = self._create_window(win_data)
            if window:
                self._windows[window_id] = window
                self._setup_actions(window, win_data)
                window.setWindowFlags(window.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
                window.show()
                window.activateWindow()
    
    def _safe_close_window(self, window_id: str, window):
        """安全关闭窗口，清理该窗口相关组件，防止内存泄漏。
        
        注意：不主动调用 QApplication.quit()。
        打包输出的 exe 中，由入口脚本在 app.exec() 返回后自行退出。
        预览时只关窗口不影响编辑器。
        """
        try:
            window.disconnect()
        except:
            pass
        
        win_data = None
        for win in self._project_data.get('windows', []):
            if win.get('id') == window_id:
                win_data = win
                break
        if win_data:
            for comp_id in win_data.get('components', []):
                self._components.pop(comp_id, None)
                self._containers.pop(comp_id, None)
                self._container_positions.pop(comp_id, None)
                self._container_original_positions.pop(comp_id, None)
        
        window.setAttribute(Qt.WA_DeleteOnClose, True)
        window.close()
        window.deleteLater()
        
        self._windows.pop(window_id, None)
    
    def _close_all_windows(self):
        """关闭所有运行时窗口（不退出 QApplication，打包输出的 exe 由入口脚本自行退出）。"""
        for window_id, window in list(self._windows.items()):
            self._safe_close_window(window_id, window)

def main():
    """运行器主函数。"""
    app = QApplication(sys.argv)
    
    from templates import get_test_template
    project_data = get_test_template()
    
    runner = Runner()
    runner.run(project_data)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
