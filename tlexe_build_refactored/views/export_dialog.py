"""导出对话框模块。

提供两种导出模式：
1. Python 脚本 (.py) - 需要 PySide6 运行环境
2. 独立程序 (.exe) - 无需任何依赖，使用内置 Python + PyInstaller 打包

参照 HtmlDown2-Pro 项目的打包方案，使用 python_env 中的
独立 Python 解释器调用 PyInstaller，避免 sys.executable 递归问题。
"""

import os
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QProgressBar, QTextEdit,
    QGroupBox, QMessageBox, QComboBox, QCheckBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QTextCursor

from services.embedded_python_builder import EmbeddedPythonBuilder
from services.export_service import ExportService

class PyInstallerWorker(QThread):
    """PyInstaller 后台构建线程。"""

    progress_updated = Signal(str)
    build_finished = Signal(bool, str)

    def __init__(self, python_script, output_dir, project_name,
                 icon_path=None, onefile=True, no_console=True):
        super().__init__()
        self._python_script = python_script
        self._output_dir = output_dir
        self._project_name = project_name
        self._icon_path = icon_path
        self._onefile = onefile
        self._no_console = no_console

    def run(self):
        try:
            builder = EmbeddedPythonBuilder()
            available, msg = builder.check_tools()
            self.progress_updated.emit(msg)

            if not available:
                self.build_finished.emit(False, msg)
                return

            exe_path = builder.build_exe(
                python_script=self._python_script,
                output_dir=self._output_dir,
                project_name=self._project_name,
                icon_path=self._icon_path,
                onefile=self._onefile,
                no_console=self._no_console,
                progress_callback=self.progress_updated.emit,
            )

            if exe_path:
                self.build_finished.emit(True, exe_path)
            else:
                self.build_finished.emit(False, "构建失败，请查看日志")
        except Exception as e:
            import traceback
            self.build_finished.emit(False, f"构建异常: {e}\n{traceback.format_exc()}")

class CxFreezeWorker(QThread):
    """cx_Freeze 后台导出线程。"""

    progress = Signal(str, int)
    finished_ok = Signal(str)
    finished_err = Signal(str)

    def __init__(self, export_service, project_data, output_dir, exe_name):
        super().__init__()
        self._service = export_service
        self._project_data = project_data
        self._output_dir = output_dir
        self._exe_name = exe_name

    def run(self):
        try:
            result_dir = self._service.export(
                self._project_data,
                self._output_dir,
                self._exe_name,
                progress_callback=self._on_progress,
            )
            self.finished_ok.emit(result_dir)
        except Exception as e:
            self.finished_err.emit(str(e))

    def _on_progress(self, message: str, percent: int):
        self.progress.emit(message, percent)

class ExportDialog(QDialog):
    """项目导出对话框。"""

    EXPORT_TYPE_PY = 0
    EXPORT_TYPE_EXE_PYINSTALLER = 1
    EXPORT_TYPE_EXE_CXFREEZE = 2

    def __init__(self, project_data: Dict[str, Any], source_dir: str, parent=None):
        super().__init__(parent)
        self._project_data = project_data
        self._source_dir = source_dir
        self._pyinstaller_worker = None
        self._cxfreeze_worker = None

        project_name = project_data.get("name", "未命名项目")
        self._project_name = project_name

        self.setWindowTitle("导出项目")
        self.setMinimumWidth(560)
        self.setMinimumHeight(520)
        self.setModal(True)

        layout = QVBoxLayout(self)

        info_group = QGroupBox("项目信息")
        info_layout = QVBoxLayout(info_group)
        info_layout.addWidget(QLabel(f"项目名称: {project_name}"))
        comp_count = len(project_data.get("components", []))
        win_count = len(project_data.get("windows", []))
        info_layout.addWidget(QLabel(f"窗口数: {win_count}  组件数: {comp_count}"))
        layout.addWidget(info_group)

        type_group = QGroupBox("导出类型")
        type_layout = QVBoxLayout(type_group)

        self._export_type_combo = QComboBox()
        self._export_type_combo.addItems([
            "Python 脚本 (.py) - 需要 PySide6 环境",
            "独立程序 (.exe) - PyInstaller 打包，无需依赖",
            "独立程序 (.exe) - cx_Freeze 打包（文件夹模式）",
        ])
        self._export_type_combo.setCurrentIndex(1)
        self._export_type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self._export_type_combo)

        self._onefile_checkbox = QCheckBox("单文件模式（体积较大但方便分发）")
        self._onefile_checkbox.setChecked(True)
        type_layout.addWidget(self._onefile_checkbox)

        self._no_console_checkbox = QCheckBox("隐藏控制台窗口")
        self._no_console_checkbox.setChecked(True)
        type_layout.addWidget(self._no_console_checkbox)

        layout.addWidget(type_group)

        settings_group = QGroupBox("导出设置")
        settings_layout = QVBoxLayout(settings_group)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("程序名称:"))
        self._exe_name_edit = QLineEdit(f"{project_name}.exe")
        name_row.addWidget(self._exe_name_edit)
        settings_layout.addLayout(name_row)

        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("输出目录:"))
        self._output_dir_edit = QLineEdit()
        default_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self._output_dir_edit.setText(default_dir)
        dir_row.addWidget(self._output_dir_edit, 1)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._on_browse_dir)
        dir_row.addWidget(browse_btn)
        settings_layout.addLayout(dir_row)

        icon_row = QHBoxLayout()
        icon_row.addWidget(QLabel("程序图标:"))
        self._icon_edit = QLineEdit()
        self._icon_edit.setPlaceholderText("可选，选择 .ico 文件...")
        icon_row.addWidget(self._icon_edit, 1)

        icon_browse = QPushButton("浏览...")
        icon_browse.clicked.connect(self._on_browse_icon)
        icon_row.addWidget(icon_browse)
        settings_layout.addLayout(icon_row)

        layout.addWidget(settings_group)

        progress_group = QGroupBox("导出进度")
        progress_layout = QVBoxLayout(progress_group)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        progress_layout.addWidget(self._progress_bar)

        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setMaximumHeight(150)
        progress_layout.addWidget(self._log_text)

        layout.addWidget(progress_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._export_btn = QPushButton("开始导出")
        self._export_btn.clicked.connect(self._on_export)
        self._export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
        """)
        btn_row.addWidget(self._export_btn)

        self._close_btn = QPushButton("关闭")
        self._close_btn.clicked.connect(self.close)
        btn_row.addWidget(self._close_btn)

        layout.addLayout(btn_row)

        self._on_type_changed(self._export_type_combo.currentIndex())

    def _on_type_changed(self, index: int):
        is_py = (index == self.EXPORT_TYPE_PY)
        is_pyinstaller = (index == self.EXPORT_TYPE_EXE_PYINSTALLER)

        self._onefile_checkbox.setVisible(not is_py)
        self._no_console_checkbox.setVisible(not is_py)
        self._icon_edit.setVisible(not is_py)

        if is_py:
            self._exe_name_edit.setText(f"{self._project_name}.py")
        elif is_pyinstaller:
            self._exe_name_edit.setText(f"{self._project_name}.exe")

    def _on_browse_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", self._output_dir_edit.text()
        )
        if dir_path:
            self._output_dir_edit.setText(dir_path)

    def _on_browse_icon(self):
        icon_path, _ = QFileDialog.getOpenFileName(
            self, "选择程序图标", "",
            "图标文件 (*.ico);;所有文件 (*.*)"
        )
        if icon_path:
            self._icon_edit.setText(icon_path)

    def _on_export(self):
        exe_name = self._exe_name_edit.text().strip()
        if not exe_name:
            from views.custom_dialogs import WarningDialog
            WarningDialog.show_warning(self, "提示", "请输入程序名称")
            return

        output_dir = self._output_dir_edit.text().strip()
        if not output_dir or not os.path.isdir(output_dir):
            from views.custom_dialogs import WarningDialog
            WarningDialog.show_warning(self, "提示", "请选择有效的输出目录")
            return

        export_type = self._export_type_combo.currentIndex()

        self._export_btn.setEnabled(False)
        self._close_btn.setEnabled(False)
        self._progress_bar.setValue(0)
        self._log_text.clear()

        if export_type == self.EXPORT_TYPE_PY:
            self._export_python_script(output_dir, exe_name)
        elif export_type == self.EXPORT_TYPE_EXE_PYINSTALLER:
            self._export_pyinstaller(output_dir, exe_name)
        else:
            self._export_cxfreeze(output_dir, exe_name)

    def _export_python_script(self, output_dir: str, filename: str):
        """导出 Python 脚本。"""
        try:
            from utils.py_project_format import dict_to_python_code
            code = dict_to_python_code(self._project_data, self._project_name)
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)

            self._progress_bar.setValue(100)
            self._log_message("Python 脚本导出成功！")
            self._on_export_success(output_path)
        except Exception as e:
            self._on_export_error(str(e))

    def _export_pyinstaller(self, output_dir: str, exe_name: str):
        """使用 PyInstaller 导出独立 EXE。"""
        try:
            temp_script = self._generate_temp_script(output_dir)
            if not temp_script:
                return

            project_name = os.path.splitext(exe_name)[0]
            icon_path = self._icon_edit.text().strip() or None

            self._log_message("正在使用内置 Python + PyInstaller 构建 EXE...")
            self._log_message("这可能需要 2-5 分钟，请耐心等待...")
            self._progress_bar.setRange(0, 0)

            self._pyinstaller_worker = PyInstallerWorker(
                python_script=temp_script,
                output_dir=output_dir,
                project_name=project_name,
                icon_path=icon_path,
                onefile=self._onefile_checkbox.isChecked(),
                no_console=self._no_console_checkbox.isChecked(),
            )
            self._pyinstaller_worker.progress_updated.connect(self._log_message)
            self._pyinstaller_worker.build_finished.connect(self._on_pyinstaller_finished)
            self._pyinstaller_worker.start()
        except Exception as e:
            self._on_export_error(str(e))

    def _export_cxfreeze(self, output_dir: str, exe_name: str):
        """使用 cx_Freeze 导出独立 EXE。"""
        try:
            service = ExportService(self._source_dir)

            self._cxfreeze_worker = CxFreezeWorker(
                service, self._project_data, output_dir, exe_name
            )
            self._cxfreeze_worker.progress.connect(self._on_cxfreeze_progress)
            self._cxfreeze_worker.finished_ok.connect(self._on_cxfreeze_ok)
            self._cxfreeze_worker.finished_err.connect(self._on_export_error)
            self._cxfreeze_worker.start()
        except Exception as e:
            self._on_export_error(str(e))

    def _generate_temp_script(self, output_dir: str) -> Optional[str]:
        """生成临时运行脚本供 PyInstaller 打包。"""
        try:
            from services.export_service import RUNTIME_ENTRY_TEMPLATE
            import json
            from datetime import datetime

            data_literal = json.dumps(self._project_data, ensure_ascii=False, indent=2)
            data_literal = data_literal.replace("true", "True").replace("false", "False").replace("null", "None")

            code = RUNTIME_ENTRY_TEMPLATE.format(
                project_name=self._project_name,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                project_data_literal=data_literal,
            )

            temp_script = os.path.join(output_dir, '_temp_main.py')
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(code)

            return temp_script
        except Exception as e:
            self._log_message(f"生成临时脚本失败: {e}")
            return None

    def _log_message(self, message: str):
        self._log_text.append(message)
        cursor = self._log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self._log_text.setTextCursor(cursor)

    def _on_cxfreeze_progress(self, message: str, percent: int):
        self._progress_bar.setValue(percent)
        self._log_message(f"[{percent}%] {message}")

    def _on_cxfreeze_ok(self, result_dir: str):
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(100)
        self._log_message(f"cx_Freeze 导出成功: {result_dir}")
        self._on_export_success(result_dir)

    def _on_pyinstaller_finished(self, success: bool, message: str):
        self._progress_bar.setRange(0, 100)
        self._export_btn.setEnabled(True)
        self._close_btn.setEnabled(True)

        if success:
            self._progress_bar.setValue(100)
            self._log_message("导出成功！")
            self._on_export_success(message)
        else:
            self._log_message(f"导出失败: {message}")
            from views.custom_dialogs import ErrorDialog
            ErrorDialog.show_error(self, "导出失败", f"导出过程中出错:\n\n{message}")

    def _on_export_success(self, file_path: str):
        self._export_btn.setEnabled(True)
        self._close_btn.setEnabled(True)

        reply = QMessageBox.question(
            self, "导出成功",
            f"项目已导出到:\n{file_path}\n\n是否打开所在文件夹？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            folder = os.path.dirname(file_path) if os.path.isfile(file_path) else file_path
            if os.path.exists(folder):
                import subprocess
                subprocess.Popen(f'explorer "{folder}"')

    def _on_export_error(self, error_msg: str):
        self._export_btn.setEnabled(True)
        self._close_btn.setEnabled(True)
        self._progress_bar.setRange(0, 100)
        self._log_message(f"导出失败: {error_msg}")
        from views.custom_dialogs import ErrorDialog
        ErrorDialog.show_error(self, "导出失败", f"导出过程中出错:\n{error_msg}")

    def closeEvent(self, event):
        if self._pyinstaller_worker and self._pyinstaller_worker.isRunning():
            self._pyinstaller_worker.terminate()
            self._pyinstaller_worker.wait(3000)
        if self._cxfreeze_worker and self._cxfreeze_worker.isRunning():
            self._cxfreeze_worker.terminate()
            self._cxfreeze_worker.wait(3000)
        event.accept()
