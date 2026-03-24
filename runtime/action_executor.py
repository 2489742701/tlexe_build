"""动作执行器模块。

本模块负责执行各种动作，如显示消息、设置属性、运行命令等。

【统一说明】
本模块使用 models.window.ActionType 中定义的统一动作类型。
所有动作类型字符串与 ActionType 枚举值保持一致。
"""

import sys
import os
import platform
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, Any, Optional, List

from models.window import ActionType


class ActionExecutor:
    """动作执行器。
    
    负责执行各种动作，如显示消息、设置属性、运行命令等。
    
    【动作类型映射】
    基础动作：none, close_program, close_window
    导航动作：open_event, open_file, open_url
    脚本动作：run_script, run_command, run_cmd, run_powershell
    UI动作：show_message, set_property, delay
    系统动作：get_system_info, run_as_admin
    """
    
    def __init__(self, components: Dict[str, Any], windows: Dict[str, Any], 
                 project_data: Dict[str, Any], parent_window=None):
        """初始化动作执行器。
        
        Args:
            components: 组件字典
            windows: 窗口字典
            project_data: 项目数据
            parent_window: 父窗口对象（用于关闭窗口等操作）
        """
        self._components = components
        self._windows = windows
        self._project_data = project_data
        self._parent_window = parent_window
    
    def execute(self, action_type: str, params: Dict[str, Any]) -> Any:
        """执行动作。
        
        Args:
            action_type: 动作类型（使用 ActionType 枚举值）
            params: 动作参数
            
        Returns:
            执行结果
        """
        # 【动作类型映射表】使用 ActionType 枚举值
        executors = {
            # 基础动作
            ActionType.NONE.value: self._execute_none,
            ActionType.CLOSE_PROGRAM.value: self._execute_close_program,
            ActionType.CLOSE_WINDOW.value: self._execute_close_window,
            
            # 导航动作
            ActionType.OPEN_EVENT.value: self._execute_open_event,
            ActionType.OPEN_FILE.value: self._execute_open_file,
            ActionType.OPEN_URL.value: self._execute_open_url,
            
            # 脚本动作
            ActionType.RUN_SCRIPT.value: self._execute_run_script,
            ActionType.RUN_COMMAND.value: self._execute_run_command,
            ActionType.RUN_CMD.value: self._execute_run_cmd,
            ActionType.RUN_POWERSHELL.value: self._execute_run_powershell,
            
            # UI动作
            ActionType.SHOW_MESSAGE.value: self._execute_show_message,
            ActionType.SET_PROPERTY.value: self._execute_set_property,
            ActionType.DELAY.value: self._execute_delay,
            
            # 系统动作
            ActionType.GET_SYSTEM_INFO.value: self._execute_get_system_info,
            ActionType.RUN_AS_ADMIN.value: self._execute_run_as_admin,
            
            # 自定义动作
            ActionType.CUSTOM.value: self._execute_custom,
        }
        
        executor = executors.get(action_type)
        if executor:
            return executor(params)
        return None
    
    # ==================== 基础动作 ====================
    
    def _execute_none(self, params: Dict[str, Any]) -> None:
        """无动作。"""
        pass
    
    def _execute_close_program(self, params: Dict[str, Any]) -> None:
        """关闭程序。"""
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
    
    def _execute_close_window(self, params: Dict[str, Any]) -> None:
        """关闭当前窗口。"""
        if self._parent_window:
            self._parent_window.close()
    
    # ==================== 导航动作 ====================
    
    def _execute_open_event(self, params: Dict[str, Any]) -> None:
        """打开事件窗口。
        
        【说明】
        这个方法需要在 Runner 类中被重写，以实现窗口跳转功能。
        """
        target_event_id = params.get('target_event_id', '')
        # 这个方法会在 Runner 中被重写
        pass
    
    def _execute_open_file(self, params: Dict[str, Any]) -> None:
        """打开文件。"""
        file_path = params.get('file_path', '')
        
        if file_path and os.path.exists(file_path):
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
    
    def _execute_open_url(self, params: Dict[str, Any]) -> None:
        """打开网址。"""
        url = params.get('url', '')
        
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
    
    # ==================== 脚本动作 ====================
    
    def _execute_run_script(self, params: Dict[str, Any]) -> None:
        """运行脚本文件。"""
        script_path = params.get('script_path', '')
        wait = params.get('wait', False)
        
        if script_path and os.path.exists(script_path):
            if wait:
                subprocess.run(['python', script_path])
            else:
                subprocess.Popen(['python', script_path])
    
    def _execute_run_command(self, params: Dict[str, Any]) -> None:
        """运行命令。"""
        command = params.get('command', '')
        wait = params.get('wait', False)
        
        if command:
            if wait:
                subprocess.run(command, shell=True)
            else:
                subprocess.Popen(command, shell=True)
    
    def _execute_run_cmd(self, params: Dict[str, Any]) -> str:
        """执行CMD命令。"""
        command = params.get('command', '')
        
        if not command:
            return ''
        
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['cmd', '/c', command],
                    capture_output=True,
                    text=True,
                    encoding='gbk',
                    errors='ignore'
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
            
            return result.stdout + result.stderr
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _execute_run_powershell(self, params: Dict[str, Any]) -> str:
        """执行PowerShell命令。"""
        command = params.get('command', '')
        
        if not command:
            return ''
        
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['powershell', '-Command', command],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                return result.stdout + result.stderr
            else:
                return "PowerShell 仅在 Windows 上可用"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    # ==================== UI动作 ====================
    
    def _execute_show_message(self, params: Dict[str, Any]) -> None:
        """显示消息框。"""
        from PySide6.QtWidgets import QMessageBox
        
        title = params.get('title', '消息')
        message = params.get('message', '')
        msg_type = params.get('type', 'info')
        
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        
        if msg_type == 'warning':
            box.setIcon(QMessageBox.Icon.Warning)
        elif msg_type == 'error':
            box.setIcon(QMessageBox.Icon.Critical)
        else:
            box.setIcon(QMessageBox.Icon.Information)
        
        box.exec()
    
    def _execute_set_property(self, params: Dict[str, Any]) -> None:
        """设置组件属性。"""
        comp_id = params.get('component_id', '')
        prop_name = params.get('property_name', '')
        prop_value = params.get('value', None)
        
        comp = self._components.get(comp_id)
        if comp and prop_name:
            if hasattr(comp, prop_name):
                setattr(comp, prop_name, prop_value)
            elif hasattr(comp, 'setProperty'):
                comp.setProperty(prop_name, prop_value)
    
    def _execute_delay(self, params: Dict[str, Any]) -> None:
        """延时执行（非阻塞）。
        
        【重要】
        使用QTimer实现非阻塞延时，避免阻塞主线程导致UI卡顿。
        
        如果需要在延时后执行回调，可以传入callback参数。
        """
        from PySide6.QtCore import QTimer
        
        milliseconds = params.get('milliseconds', 1000)
        callback = params.get('callback', None)
        
        timer = QTimer()
        timer.setSingleShot(True)
        
        if callback:
            timer.timeout.connect(callback)
        
        timer.start(milliseconds)
        
        return timer
    
    # ==================== 系统动作 ====================
    
    def _execute_get_system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取系统信息。"""
        return {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'current_time': datetime.now().isoformat(),
        }
    
    def _execute_run_as_admin(self, params: Dict[str, Any]) -> bool:
        """以管理员权限运行。"""
        program_path = params.get('program_path', '')
        args = params.get('args', '')
        
        if not program_path:
            return False
        
        try:
            if platform.system() == 'Windows':
                import ctypes
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, 'runas', program_path, args, None, 1
                )
                return result > 32
            else:
                subprocess.run(['sudo', program_path] + (args.split() if args else []))
                return True
        except Exception as e:
            raise RuntimeError(f"以管理员权限运行失败: {e}")
    
    # ==================== 自定义动作 ====================
    
    def _execute_custom(self, params: Dict[str, Any]) -> Any:
        """执行自定义动作。"""
        python_code = params.get('python_code', '')
        if python_code:
            exec_globals = {
                'components': self._components,
                'windows': self._windows,
                'project_data': self._project_data,
                'parent_window': self._parent_window,
            }
            exec(python_code, exec_globals)
