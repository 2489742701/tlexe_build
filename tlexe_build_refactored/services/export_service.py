"""项目导出服务模块。

将用户编辑好的项目导出为可独立运行的 Windows exe 程序。
使用 cx_Freeze 进行打包，避免 PyInstaller 的 GUI 模式死锁问题。

导出流程：
1. 从 ProjectModel 获取项目数据
2. 生成精简的运行入口脚本（仅依赖 runtime + models + utils + renderers）
3. 将项目数据嵌入入口脚本
4. 调用 cx_Freeze API 打包为 exe
5. 将输出复制到用户指定目录
"""

import os
import sys
import shutil
import tempfile
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime

RUNTIME_ENTRY_TEMPLATE = '''\
"""{project_name} - 自动生成的窗口程序。

生成时间: {timestamp}
由傻瓜桌面开发工具导出。
"""

import sys
import os
import traceback

if getattr(sys, "frozen", False):
    try:
        _exe_dir = os.path.dirname(sys.executable)
        _lib_dir = os.path.join(_exe_dir, "lib")
        _pyside_dir = os.path.join(_lib_dir, "PySide6")
        _shiboken_dir = os.path.join(_lib_dir, "shiboken6")
        for _d in [_lib_dir, _pyside_dir, _shiboken_dir]:
            if os.path.isdir(_d):
                os.environ["PATH"] = _d + os.pathsep + os.environ.get("PATH", "")
                if hasattr(os, "add_dll_directory"):
                    os.add_dll_directory(_d)
        _log = open(os.path.join(_exe_dir, "app.log"), "w", encoding="utf-8")
        sys.stdout = _log
        sys.stderr = _log
    except Exception:
        pass

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    from models.registry_init import register_all_components
    from runtime.runner import Runner

    project_data = {project_data_literal}

    def main():
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_ShareOpenGLContexts)

        register_all_components()

        runner = Runner()
        runner.run(project_data)

        sys.exit(app.exec())

    if __name__ == "__main__":
        main()
except Exception as _e:
    _tb = traceback.format_exc()
    try:
        with open(os.path.join(os.path.dirname(getattr(sys, "executable", ".")), "crash.log"), "w", encoding="utf-8") as _f:
            _f.write(_tb)
    except Exception:
        pass
    raise
'''

class ExportService:
    """项目导出服务，将项目打包为可独立运行的 exe。"""

    RUNTIME_PACKAGES = [
        "PySide6", "shiboken6",
        "models", "runtime", "renderers",
        "utils", "styles", "eventbus",
        "presenters", "templates",
    ]

    RUNTIME_INCLUDES = [
        "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",
        "PySide6.QtSvg", "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    ]

    RUNTIME_EXCLUDES = [
        "tkinter", "unittest", "pytest", "torch", "numpy",
        "views", "controllers", "services", "dev_mode",
    ]

    def __init__(self, project_source_dir: str):
        self._source_dir = project_source_dir

    def export(
        self,
        project_data: Dict[str, Any],
        output_dir: str,
        exe_name: str = "MyApp.exe",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> str:
        """导出项目为 exe。

        Args:
            project_data: 项目数据字典（ProjectModel.to_dict()）
            output_dir: 输出目录
            exe_name: exe 文件名
            progress_callback: 进度回调 (message, percent)

        Returns:
            输出目录路径

        Raises:
            RuntimeError: 打包失败
        """
        self._notify(progress_callback, "准备导出环境...", 5)

        with tempfile.TemporaryDirectory(prefix="uidt_export_") as tmp_dir:
            entry_script = self._generate_entry_script(
                project_data, tmp_dir, exe_name
            )
            self._notify(progress_callback, "入口脚本生成完成", 15)

            self._copy_runtime_modules(tmp_dir)
            self._notify(progress_callback, "运行时模块复制完成", 30)

            build_dir = os.path.join(tmp_dir, "build_output")
            self._run_cx_freeze(
                entry_script=entry_script,
                target_dir=build_dir,
                exe_name=exe_name,
                source_dir=tmp_dir,
            )
            self._notify(progress_callback, "cx_Freeze 打包完成", 85)

            final_dir = self._collect_output(build_dir, output_dir, exe_name)

            self._notify(progress_callback, "导出完成！", 100)

            return final_dir

    def _generate_entry_script(
        self,
        project_data: Dict[str, Any],
        tmp_dir: str,
        exe_name: str,
    ) -> str:
        """生成运行入口脚本。"""
        project_name = project_data.get("name", "未命名项目")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_literal = json.dumps(project_data, ensure_ascii=False, indent=2)
        data_literal = data_literal.replace("true", "True").replace("false", "False").replace("null", "None")

        code = RUNTIME_ENTRY_TEMPLATE.format(
            project_name=project_name,
            timestamp=timestamp,
            project_data_literal=data_literal,
        )

        script_path = os.path.join(tmp_dir, "main.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        return script_path

    def _copy_runtime_modules(self, tmp_dir: str):
        """复制运行时所需的模块到临时目录。"""
        runtime_modules = [
            "models", "runtime", "renderers", "utils",
            "styles", "eventbus", "presenters", "templates",
        ]

        for mod in runtime_modules:
            src = os.path.join(self._source_dir, mod)
            dst = os.path.join(tmp_dir, mod)
            if os.path.isdir(src):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", "*.pyo", "tests", "*.test.py"
                ))

        resource_dirs = ["icons", "resources"]
        for res in resource_dirs:
            src = os.path.join(self._source_dir, res)
            dst = os.path.join(tmp_dir, res)
            if os.path.isdir(src):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)

    def _run_cx_freeze(
        self,
        entry_script: str,
        target_dir: str,
        exe_name: str,
        source_dir: str,
    ):
        """调用 cx_Freeze 进行打包。

        使用子进程调用以隔离环境，避免项目目录中的 packaging/ 等目录
        遮蔽 pip 安装的标准库模块。
        优先使用 cx_env 中的 Python 3.10 进行打包（Python 3.13 有 DLL 加载问题）。
        """
        import subprocess

        python_exe = self._find_packaging_python()

        build_script = self._generate_build_script(
            entry_script, target_dir, exe_name, source_dir
        )

        script_path = os.path.join(target_dir, "_cx_build.py")
        os.makedirs(target_dir, exist_ok=True)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(build_script)

        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=os.path.dirname(target_dir),
        )

        if result.returncode != 0:
            error_detail = result.stderr or result.stdout or "未知错误"
            raise RuntimeError(f"cx_Freeze 打包失败:\n{error_detail}")

    def _generate_build_script(
        self,
        entry_script: str,
        target_dir: str,
        exe_name: str,
        source_dir: str,
    ) -> str:
        """生成 cx_Freeze 构建脚本。"""
        packages_str = repr(self.RUNTIME_PACKAGES)
        includes_str = repr(self.RUNTIME_INCLUDES)
        excludes_str = repr(self.RUNTIME_EXCLUDES)

        include_files_lines = []
        for res_name in ["icons", "resources"]:
            res_path = os.path.join(source_dir, res_name)
            if os.path.isdir(res_path):
                include_files_lines.append(
                    f"    ({repr(res_path)}, {repr(res_name)}),"
                )

        include_files_str = "[\n" + "\n".join(include_files_lines) + "\n]" if include_files_lines else "[]"

        return f'''\
import sys
import os

_source_dir = {repr(source_dir)}
for _mod_dir in ["models", "runtime", "renderers", "utils", "styles", "eventbus", "presenters", "templates"]:
    _path = os.path.join(_source_dir, _mod_dir)
    if os.path.isdir(_path):
        sys.path.insert(0, _path)
sys.path.insert(0, _source_dir)

from cx_Freeze.freezer import Freezer
from cx_Freeze.executable import Executable

exe = Executable(
    script={repr(entry_script)},
    base="gui",
    target_name={repr(exe_name)},
)

source_lib_dir = {repr(source_dir)}
bin_path_includes = [source_lib_dir]
for _root, _dirs, _files in os.walk(source_lib_dir):
    for _d in _dirs:
        _path = os.path.join(_root, _d)
        bin_path_includes.append(_path)

freezer = Freezer(
    executables=[exe],
    packages={packages_str},
    includes={includes_str},
    excludes={excludes_str},
    target_dir={repr(target_dir)},
    include_files={include_files_str},
    bin_path_includes=bin_path_includes,
)

freezer.freeze()
print("cx_Freeze build completed")
'''

    def _collect_output(
        self,
        build_dir: str,
        output_dir: str,
        exe_name: str,
    ) -> str:
        """收集打包输出到最终目录。"""
        project_name = os.path.splitext(exe_name)[0]
        final_dir = os.path.join(output_dir, project_name)

        if os.path.isdir(final_dir):
            shutil.rmtree(final_dir)

        shutil.copytree(build_dir, final_dir)

        return final_dir

    @staticmethod
    def _notify(
        callback: Optional[Callable[[str, int], None]],
        message: str,
        percent: int,
    ):
        if callback:
            callback(message, percent)

    @staticmethod
    def _fix_dll_layout(output_dir: str):
        """修复 DLL 布局，确保 PySide6 能找到 shiboken6 的 DLL。"""
        lib_dir = os.path.join(output_dir, "lib")
        if not os.path.isdir(lib_dir):
            return

        pyside_dir = os.path.join(lib_dir, "PySide6")
        shiboken_dir = os.path.join(lib_dir, "shiboken6")

        if not os.path.isdir(pyside_dir) or not os.path.isdir(shiboken_dir):
            return

        for fname in os.listdir(shiboken_dir):
            if fname.endswith(".dll") or fname.endswith(".pyd"):
                src = os.path.join(shiboken_dir, fname)
                dst = os.path.join(pyside_dir, fname)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)

    def _find_packaging_python(self) -> str:
        """查找用于打包的 Python 解释器。

        优先使用 cx_env 中的 Python 3.10（Python 3.13 有 DLL 加载问题），
        找不到则回退到当前 Python。
        """
        cx_env_python = os.path.join(
            self._source_dir, "packaging", "cx_env", "Scripts", "python.exe"
        )
        if os.path.isfile(cx_env_python):
            return cx_env_python

        clean_env_python = os.path.join(
            self._source_dir, "packaging", "clean_env", "Scripts", "python.exe"
        )
        if os.path.isfile(clean_env_python):
            return clean_env_python

        return sys.executable
