"""项目转换工具模块。

本模块提供项目文件与Python脚本之间的相互转换功能。
支持将.itexe项目文件转换为可独立运行的Python脚本，
也支持将符合格式的Python脚本转换回项目文件。
"""

import json
import os
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

class ProjectConverter:
    """项目转换器。
    
    提供项目文件与Python脚本之间的相互转换功能。
    """
    
    @staticmethod
    def itexe_to_python(project_data: Dict[str, Any]) -> str:
        """将项目数据转换为Python脚本。
        
        Args:
            project_data: 项目数据字典
            
        Returns:
            生成的Python脚本代码
        """
        project_name = project_data.get('name', '未命名项目')
        windows = project_data.get('windows', [])
        components = project_data.get('components', [])
        main_window_id = project_data.get('main_window_id', '')
        
        code_lines = [
            '"""',
            f'{project_name} - 自动生成的窗口程序',
            f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            '本文件由傻瓜桌面开发工具自动生成。',
            '可以直接运行，也可以导入到工具中编辑。',
            '"""',
            '',
            'import sys',
            'import json',
            'from typing import Optional, Dict, Any',
            'from PySide6.QtWidgets import (',
            '    QApplication, QMainWindow, QWidget, QPushButton, QLabel,',
            '    QLineEdit, QCheckBox, QComboBox, QProgressBar, QFrame,',
            '    QVBoxLayout, QHBoxLayout, QMessageBox',
            ')',
            'from PySide6.QtCore import Qt, QTimer',
            'from PySide6.QtGui import QFont, QColor, QPalette',
            '',
            '',
        ]
        
        component_classes = ProjectConverter._generate_component_classes(components)
        code_lines.extend(component_classes)
        
        code_lines.extend([
            'class WindowManager:',
            '    """窗口管理器。"""',
            '    ',
            '    def __init__(self):',
            '        self._windows: Dict[str, QMainWindow] = {}',
            '        self._main_window_id = ""',
            '    ',
            '    def register_window(self, window_id: str, window: QMainWindow):',
            '        self._windows[window_id] = window',
            '    ',
            '    def get_window(self, window_id: str) -> Optional[QMainWindow]:',
            '        return self._windows.get(window_id)',
            '    ',
            '    def close_all(self):',
            '        for window in self._windows.values():',
            '            window.close()',
            '    ',
            '    def show_window(self, window_id: str):',
            '        window = self.get_window(window_id)',
            '        if window:',
            '            window.show()',
            '            window.raise_()',
            '            window.activateWindow()',
            '',
            '',
        ])
        
        for window in windows:
            window_class = ProjectConverter._generate_window_class(window, components)
            code_lines.extend(window_class)
            code_lines.append('')
            code_lines.append('')
        
        code_lines.extend([
            'def get_project_data() -> Dict[str, Any]:',
            '    """获取项目数据（用于导入回编辑器）。"""',
            '    return {',
        ])
        
        for key, value in project_data.items():
            if isinstance(value, str):
                code_lines.append(f'        "{key}": "{value}",')
            elif isinstance(value, (int, float, bool)):
                code_lines.append(f'        "{key}": {value},')
            elif isinstance(value, list):
                code_lines.append(f'        "{key}": {json.dumps(value, ensure_ascii=False)},')
            else:
                code_lines.append(f'        "{key}": {json.dumps(value, ensure_ascii=False)},')
        
        code_lines.extend([
            '    }',
            '',
            '',
            'def main():',
            '    """主函数。"""',
            '    app = QApplication(sys.argv)',
            '    ',
            '    window_manager = WindowManager()',
            '    ',
        ])
        
        for window in windows:
            window_id = window.get('id', '')
            window_name = window.get('name', '')
            class_name = ProjectConverter._to_class_name(window_id, window_name)
            code_lines.extend([
                f'    {window_id}_window = {class_name}(window_manager)',
                f'    window_manager.register_window("{window_id}", {window_id}_window)',
            ])
        
        code_lines.extend([
            '    ',
            f'    window_manager._main_window_id = "{main_window_id}"',
            '    window_manager.show_window("{main_window_id}")',
            '    ',
            '    sys.exit(app.exec())',
            '',
            '',
            'if __name__ == "__main__":',
            '    main()',
        ])
        
        return '\n'.join(code_lines)
    
    @staticmethod
    def python_to_itexe(code: str) -> Optional[Dict[str, Any]]:
        """将Python脚本转换回项目数据。
        
        Args:
            code: Python脚本代码
            
        Returns:
            项目数据字典，如果转换失败返回None
        """
        try:
            match = re.search(r'def get_project_data\(\)\s*->\s*Dict\[str,\s*Any\]:\s*""".*?"""\s*return\s*(\{.*?\n\s*\})', code, re.DOTALL)
            
            if match:
                dict_str = match.group(1)
                try:
                    import ast
                    return ast.literal_eval(dict_str)
                except Exception:
                    # 如果 ast.literal_eval 失败（例如包含了 json.dumps 产生的 true/false/null），
                    # 则回退到安全的 eval 解析
                    safe_globals = {'true': True, 'false': False, 'null': None}
                    return eval(dict_str, {"__builtins__": {}}, safe_globals)
            
            json_match = re.search(r'\{[\s\S]*"name"[\s\S]*"windows"[\s\S]*"components"[\s\S]*\}', code)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            print(f"转换失败: {e}")
            return None
    
    @staticmethod
    def _generate_component_classes(components: List[Dict]) -> List[str]:
        """生成组件创建辅助类。"""
        lines = [
            'class ComponentFactory:',
            '    """组件工厂。"""',
            '    ',
            '    @staticmethod',
            '    def create_button(data: Dict[str, Any], parent: QWidget, window_manager: WindowManager) -> QPushButton:',
            '        btn = QPushButton(data.get("text", ""), parent)',
            '        btn.setGeometry(data["x"], data["y"], data["width"], data["height"])',
            '        ',
            '        style = data.get("style", {})',
            '        btn.setStyleSheet(f"""',
            '            QPushButton {{',
            '                background-color: {style.get("background_color", "#f0f0f0")};',
            '                color: {style.get("text_color", "#333333")};',
            '                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#999999")};',
            '                border-radius: {style.get("border_radius", 4)}px;',
            '                font-size: {style.get("font_size", 12)}px;',
            '                font-weight: {"bold" if style.get("font_bold") else "normal"};',
            '            }}',
            '            QPushButton:hover {{',
            '                opacity: 0.8;',
            '            }}',
            '        """)',
            '        ',
            '        target_window = data.get("target_window_id", "")',
            '        if target_window:',
            '            btn.clicked.connect(lambda: window_manager.show_window(target_window))',
            '        else:',
            '            action = data.get("action", {})',
            '            action_type = action.get("action_type", "none")',
            '            if action_type == "close_window":',
            '                btn.clicked.connect(lambda: btn.window().close())',
            '            elif action_type == "show_message":',
            '                msg = action.get("params", {}).get("param", "")',
            '                btn.clicked.connect(lambda: QMessageBox.information(btn.window(), "提示", msg))',
            '        ',
            '        return btn',
            '    ',
            '    @staticmethod',
            '    def create_label(data: Dict[str, Any], parent: QWidget) -> QLabel:',
            '        lbl = QLabel(data.get("text", ""), parent)',
            '        lbl.setGeometry(data["x"], data["y"], data["width"], data["height"])',
            '        ',
            '        style = data.get("style", {})',
            '        alignment = data.get("alignment", "left")',
            '        align_map = {"left": Qt.AlignmentFlag.AlignLeft, "center": Qt.AlignmentFlag.AlignCenter, "right": Qt.AlignmentFlag.AlignRight}',
            '        lbl.setAlignment(align_map.get(alignment, Qt.AlignmentFlag.AlignLeft) | Qt.AlignmentFlag.AlignVCenter)',
            '        ',
            '        lbl.setStyleSheet(f"""',
            '            QLabel {{',
            '                background-color: {style.get("background_color", "transparent")};',
            '                color: {style.get("text_color", "#333333")};',
            '                font-size: {style.get("font_size", 12)}px;',
            '                font-weight: {"bold" if style.get("font_bold") else "normal"};',
            '            }}',
            '        """)',
            '        lbl.setWordWrap(data.get("word_wrap", False))',
            '        ',
            '        return lbl',
            '    ',
            '    @staticmethod',
            '    def create_input(data: Dict[str, Any], parent: QWidget) -> QLineEdit:',
            '        inp = QLineEdit(parent)',
            '        inp.setGeometry(data["x"], data["y"], data["width"], data["height"])',
            '        inp.setPlaceholderText(data.get("placeholder", ""))',
            '        inp.setMaxLength(data.get("max_length", 32767))',
            '        ',
            '        if data.get("is_password", False):',
            '            inp.setEchoMode(QLineEdit.EchoMode.Password)',
            '        ',
            '        style = data.get("style", {})',
            '        inp.setStyleSheet(f"""',
            '            QLineEdit {{',
            '                background-color: {style.get("background_color", "#ffffff")};',
            '                color: {style.get("text_color", "#333333")};',
            '                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#cccccc")};',
            '                border-radius: {style.get("border_radius", 4)}px;',
            '                padding: 4px;',
            '                font-size: {style.get("font_size", 12)}px;',
            '            }}',
            '        """)',
            '        ',
            '        return inp',
            '    ',
            '    @staticmethod',
            '    def create_checkbox(data: Dict[str, Any], parent: QWidget) -> QCheckBox:',
            '        chk = QCheckBox(data.get("text", ""), parent)',
            '        chk.setGeometry(data["x"], data["y"], data["width"], data["height"])',
            '        chk.setChecked(data.get("checked", False))',
            '        ',
            '        style = data.get("style", {})',
            '        chk.setStyleSheet(f"""',
            '            QCheckBox {{',
            '                color: {style.get("text_color", "#333333")};',
            '                font-size: {style.get("font_size", 12)}px;',
            '            }}',
            '        """)',
            '        ',
            '        return chk',
            '    ',
            '    @staticmethod',
            '    def create_combobox(data: Dict[str, Any], parent: QWidget) -> QComboBox:',
            '        cbo = QComboBox(parent)',
            '        cbo.setGeometry(data["x"], data["y"], data["width"], data["height"])',
            '        cbo.addItems(data.get("items", []))',
            '        cbo.setCurrentIndex(data.get("current_index", 0))',
            '        ',
            '        style = data.get("style", {})',
            '        cbo.setStyleSheet(f"""',
            '            QComboBox {{',
            '                background-color: {style.get("background_color", "#ffffff")};',
            '                color: {style.get("text_color", "#333333")};',
            '                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#cccccc")};',
            '                border-radius: {style.get("border_radius", 4)}px;',
            '                padding: 4px;',
            '                font-size: {style.get("font_size", 12)}px;',
            '            }}',
            '        """)',
            '        ',
            '        return cbo',
            '    ',
            '    @staticmethod',
            '    def create_progressbar(data: Dict[str, Any], parent: QWidget) -> QProgressBar:',
            '        pbar = QProgressBar(parent)',
            '        pbar.setGeometry(data["x"], data["y"], data["width"], data["height"])',
            '        pbar.setValue(data.get("value", 0))',
            '        pbar.setTextVisible(data.get("show_text", True))',
            '        ',
            '        style = data.get("style", {})',
            '        pbar.setStyleSheet(f"""',
            '            QProgressBar {{',
            '                background-color: {style.get("background_color", "#e0e0e0")};',
            '                border: {style.get("border_width", 1)}px solid {style.get("border_color", "#999999")};',
            '                border-radius: {style.get("border_radius", 4)}px;',
            '                text-align: center;',
            '            }}',
            '            QProgressBar::chunk {{',
            '                background-color: #0078d7;',
            '                border-radius: {style.get("border_radius", 4)}px;',
            '            }}',
            '        """)',
            '        ',
            '        if data.get("auto_progress", False):',
            '            duration = data.get("duration", 3)',
            '            steps = 100',
            '            interval = int(duration * 1000 / steps)',
            '            ',
            '            def update_progress():',
            '                if pbar.value() < 100:',
            '                    pbar.setValue(pbar.value() + 1)',
            '            ',
            '            timer = QTimer(pbar)',
            '            timer.timeout.connect(update_progress)',
            '            timer.start(interval)',
            '        ',
            '        return pbar',
            '',
            '',
        ]
        return lines
    
    @staticmethod
    def _generate_window_class(window: Dict, components: List[Dict]) -> List[str]:
        """生成窗口类代码。"""
        window_id = window.get('id', '')
        window_name = window.get('name', '')
        window_type = window.get('window_type', 'main')
        width = window.get('width', 800)
        height = window.get('height', 600)
        title = window.get('title', window_name)
        component_ids = window.get('components', [])
        
        class_name = ProjectConverter._to_class_name(window_id, window_name)
        
        lines = [
            f'class {class_name}(QMainWindow):',
            f'    """{window_name}窗口。"""',
            '    ',
            '    def __init__(self, window_manager: WindowManager):',
            '        super().__init__()',
            '        self._window_manager = window_manager',
            f'        self.setWindowTitle("{title}")',
            f'        self.resize({width}, {height})',
            '        ',
            '        central_widget = QWidget()',
            '        self.setCentralWidget(central_widget)',
            '        ',
            '        self._components: Dict[str, QWidget] = {}',
            '        self._create_components(central_widget)',
            '    ',
            '    def _create_components(self, parent: QWidget):',
            '        """创建组件。"""',
        ]
        
        window_components = [c for c in components if c.get('id') in component_ids]
        
        for comp in window_components:
            comp_id = comp.get('id', '')
            comp_type = comp.get('comp_type', '')
            comp_name = comp.get('name', '')
            
            create_method = {
                'button': 'create_button',
                'label': 'create_label',
                'input': 'create_input',
                'checkbox': 'create_checkbox',
                'combobox': 'create_combobox',
                'progressbar': 'create_progressbar',
            }.get(comp_type)
            
            if create_method:
                comp_data_str = json.dumps(comp, ensure_ascii=False, indent=12)
                comp_data_lines = comp_data_str.split('\n')
                comp_data_indented = '\n            '.join(comp_data_lines)
                
                lines.extend([
                    f'        # {comp_name}',
                    f'        self._components["{comp_id}"] = ComponentFactory.{create_method}(',
                    f'            {comp_data_indented},',
                    '            parent,',
                    '            self._window_manager',
                    '        )',
                ])
        
        return lines
    
    @staticmethod
    def _to_class_name(window_id: str, window_name: str) -> str:
        """将窗口ID和名称转换为类名。"""
        name = window_name.replace(' ', '_').replace('-', '_')
        safe_chars = ''.join(c for c in name if c.isalnum() or c == '_')
        if safe_chars and safe_chars[0].isdigit():
            safe_chars = 'Window_' + safe_chars
        return safe_chars or f'Window_{window_id}'

def convert_itexe_to_py(itexe_path: str, py_path: Optional[str] = None) -> bool:
    """将.itexe文件转换为Python脚本。
    
    Args:
        itexe_path: .itexe文件路径
        py_path: 输出的.py文件路径（可选，默认同名）
        
    Returns:
        是否转换成功
    """
    try:
        with open(itexe_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        python_code = ProjectConverter.itexe_to_python(project_data)
        
        if py_path is None:
            py_path = os.path.splitext(itexe_path)[0] + '.py'
        
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"转换成功: {itexe_path} -> {py_path}")
        return True
        
    except Exception as e:
        print(f"转换失败: {e}")
        return False

def convert_py_to_itexe(py_path: str, itexe_path: Optional[str] = None) -> bool:
    """将Python脚本转换为.itexe文件。
    
    Args:
        py_path: .py文件路径
        itexe_path: 输出的.itexe文件路径（可选，默认同名）
        
    Returns:
        是否转换成功
    """
    try:
        with open(py_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        project_data = ProjectConverter.python_to_itexe(code)
        
        if project_data is None:
            print("无法从Python脚本中提取项目数据")
            return False
        
        if itexe_path is None:
            itexe_path = os.path.splitext(py_path)[0] + '.itexe'
        
        with open(itexe_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        print(f"转换成功: {py_path} -> {itexe_path}")
        return True
        
    except Exception as e:
        print(f"转换失败: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法:")
        print("  python converter.py to_py <input.itexe> [output.py]")
        print("  python converter.py to_itexe <input.py> [output.itexe]")
        sys.exit(1)
    
    command = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    if command == 'to_py':
        convert_itexe_to_py(input_path, output_path)
    elif command == 'to_itexe':
        convert_py_to_itexe(input_path, output_path)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
