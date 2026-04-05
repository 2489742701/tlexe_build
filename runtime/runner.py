"""窗口运行器模块。

本模块负责将项目数据转换为实际运行的窗口。
使用统一的组件工厂创建控件，确保与画布预览一致。

主要功能：
- 解析项目数据并创建窗口
- 创建组件并设置正确的位置和大小
- 处理容器和子组件的层级关系
- 执行组件动作和事件处理
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


class Runner:
    """窗口运行器。
    
    负责将项目数据转换为实际运行的窗口。
    使用统一的组件工厂创建控件，确保与画布预览一致。
    """
    
    TITLE_BAR_HEIGHT = 28
    
    def __init__(self):
        self._windows: Dict[str, QMainWindow] = {}
        self._components: Dict[str, Any] = {}
        self._containers: Dict[str, QWidget] = {}
        self._container_positions: Dict[str, tuple] = {}
        self._container_original_positions: Dict[str, tuple] = {}
        self._container_parents: Dict[str, str] = {}
        self._executor: Optional[ActionExecutor] = None
        self._project_data: Dict[str, Any] = {}
    
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
            
            window = self._create_window(main_window_data)
            if window:
                self._windows[main_window_id] = window
                self._executor = ActionExecutor(self._components, self._windows, self._project_data)
                self._setup_actions(window, main_window_data)
                
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
            
            from PySide6.QtWidgets import QMessageBox
            try:
                QMessageBox.critical(
                    None,
                    "运行错误",
                    f"运行项目时发生错误:\n\n{str(e)}\n\n错误日志已保存到:\n{crash_file or '未知'}"
                )
            except:
                pass
    
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
                    container_width = comp_data.get('width', 800)
                    container_height = comp_data.get('height', 600)
                    window_width = container_width
                    window_height = container_height
                    container_data = comp_data
                    debug_log('component', f"找到容器: {comp_data.get('name')} 位置=({comp_data.get('x')}, {comp_data.get('y')}) 大小=({container_width}, {container_height})")
                    break
        
        debug_log('component', f"窗口大小: {window_width} x {window_height}")
        window.resize(window_width, window_height)
        
        from PySide6.QtGui import QScreen
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        window.move(x, y)
        
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        container_comps = []
        other_comps = []
        
        for comp_data in components_data:
            if comp_data.get('id') in comp_ids:
                comp_type = comp_data.get('type') or comp_data.get('comp_type', '')
                if comp_type == 'container':
                    container_comps.append(comp_data)
                else:
                    other_comps.append(comp_data)
        
        sorted_containers = self._build_container_hierarchy(container_comps)
        
        print(f"\n--- 创建容器组件 ({len(sorted_containers)}个) ---")
        for comp_data in sorted_containers:
            comp = self._create_component_from_dict(comp_data)
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
                    comp.setGeometry(0, 0, container_width, container_height)
                
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
            comp = self._create_component_from_dict(comp_data)
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
                    comp.setParent(central_widget)
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
        
        Args:
            comp_data: 组件数据
            parent_id: 直接父容器ID
            
        Returns:
            (relative_x, relative_y) 相对位置元组
        """
        comp_x = comp_data.get('x', 0)
        comp_y = comp_data.get('y', 0)
        
        if parent_id in self._container_original_positions:
            parent_orig_x, parent_orig_y = self._container_original_positions[parent_id]
            relative_x = comp_x - parent_orig_x
            relative_y = comp_y - parent_orig_y
        else:
            relative_x = comp_x
            relative_y = comp_y
        
        return relative_x, relative_y
    
    def _create_component_from_dict(self, comp_data: Dict[str, Any]) -> Optional[QWidget]:
        """从字典数据创建组件。
        
        使用统一的组件工厂创建控件。
        
        Args:
            comp_data: 组件数据字典
            
        Returns:
            创建的组件对象
        """
        from models.components import COMPONENT_TYPE_MAP
        
        comp_type = comp_data.get('comp_type') or comp_data.get('type', 'label')
        
        comp_class = COMPONENT_TYPE_MAP.get(comp_type)
        if comp_class:
            model = comp_class.from_dict(comp_data)
            widget = create_component_widget(model)
            
            if comp_type == 'progressbar':
                auto_progress = comp_data.get('auto_progress', False)
                duration = comp_data.get('duration', 3)
                if auto_progress and widget:
                    self._setup_auto_progress(widget, comp_data, duration)
            
            return widget
        
        return None
    
    def _setup_auto_progress(self, progressbar, comp_data: Dict[str, Any], duration: int):
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
                    # 修复：只关闭当前窗口，而不是所有窗口
                    if window:
                        window.close()
        
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
                        
                        if target_window_id:
                            button.clicked.connect(lambda checked, twid=target_window_id: self._open_event_window(twid))
                        elif action.get('action_type') == 'close_program':
                            button.clicked.connect(self._close_all_windows)
                        elif action.get('action_type') == 'close_window':
                            # 修复：确保正确关闭当前窗口
                            button.clicked.connect(window.close)
    
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
        
        # 如果窗口已经存在，直接显示
        if window_id in self._windows:
            self._windows[window_id].show()
            self._windows[window_id].raise_()
            self._windows[window_id].activateWindow()
            return
        
        # 创建新窗口
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
                window.show()
                window.activateWindow()
    
    def _safe_close_window(self, window_id: str, window):
        """安全关闭窗口，防止内存泄漏（基于MCP建议）。"""
        try:
            # 断开所有信号连接
            window.disconnect()
        except:
            pass
        
        # 设置删除标记，确保C++对象被释放
        window.setAttribute(Qt.WA_DeleteOnClose, True)
        window.close()
        window.deleteLater()
        
        # 从字典中移除已关闭的窗口
        self._windows.pop(window_id, None)
    
    def _close_all_windows(self):
        """关闭所有窗口。"""
        for window in self._windows.values():
            window.close()
        QApplication.quit()


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
