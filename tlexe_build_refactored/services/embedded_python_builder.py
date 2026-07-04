"""内置 Python 构建工具模块。

使用 python_env 中的 PyInstaller 将用户项目打包为独立 EXE。
参照 HtmlDown2-Pro 项目的打包方案，解决以下关键问题：

1. 打包后 EXE 的 sys.executable 指向自身，不能用来执行 PyInstaller
   → 使用独立的 python_env/python.exe
2. PyInstaller 打包 tkinter 程序需设置 TCL_LIBRARY/TK_LIBRARY
   → 自动从 python_env 中检测并设置
3. python_env 首次使用需从 zip 解压
   → 调用 path_utils.ensure_python_env() 自动处理

## 使用示例
    builder = EmbeddedPythonBuilder()
    exe_path = builder.build_exe(
        python_script="my_app.py",
        output_dir="C:/output",
        project_name="我的应用",
        progress_callback=lambda msg: print(msg),
    )
"""

import os
import sys
import subprocess
from typing import Optional, Callable, Tuple

from utils.path_utils import ensure_python_env, get_python_env_tcl_paths

class EmbeddedPythonBuilder:
    """使用内置 Python 环境和 PyInstaller 构建 EXE。"""

    def __init__(self):
        self._python_exe: Optional[str] = None

    def check_tools(self) -> Tuple[bool, str]:
        """检查构建工具是否可用。

        Returns:
            (是否可用, 消息)
        """
        try:
            python_exe = ensure_python_env()
        except (FileNotFoundError, RuntimeError) as e:
            return False, str(e)

        result = subprocess.run(
            [python_exe, '-m', 'PyInstaller', '--version'],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode != 0:
            return False, f"PyInstaller 不可用: {result.stderr}"

        version = result.stdout.strip()
        self._python_exe = python_exe
        return True, f"构建工具可用 (PyInstaller {version})"

    def build_exe(
        self,
        python_script: str,
        output_dir: str,
        project_name: str,
        icon_path: Optional[str] = None,
        onefile: bool = True,
        no_console: bool = True,
        key: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[str]:
        """构建 EXE。

        Args:
            python_script: Python 脚本路径
            output_dir: 输出目录
            project_name: 项目名称（EXE 文件名）
            icon_path: 图标路径（.ico）
            onefile: 是否打包为单文件
            no_console: 是否隐藏控制台
            key: PyInstaller 字节码加密密钥
            progress_callback: 进度回调

        Returns:
            生成的 EXE 路径，失败返回 None
        """
        if self._python_exe is None:
            try:
                self._python_exe = ensure_python_env()
            except (FileNotFoundError, RuntimeError) as e:
                if progress_callback:
                    progress_callback(f"环境准备失败: {e}")
                return None

        os.makedirs(output_dir, exist_ok=True)

        if progress_callback:
            progress_callback("正在准备构建环境...")

        cmd = self._build_command(
            python_script=python_script,
            output_dir=output_dir,
            project_name=project_name,
            icon_path=icon_path,
            onefile=onefile,
            no_console=no_console,
            key=key,
        )

        env = self._build_env()

        if progress_callback:
            progress_callback(f"正在使用 PyInstaller 构建 EXE...")

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            if progress_callback:
                progress_callback("构建超时（超过 10 分钟）")
            return None

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "未知错误"
            if progress_callback:
                progress_callback(f"构建失败: {error_msg[:500]}")
            return None

        exe_name = f"{project_name}.exe"
        exe_path = os.path.join(output_dir, exe_name)

        if not os.path.isfile(exe_path):
            dist_dir = os.path.join(output_dir, 'dist')
            exe_in_dist = os.path.join(dist_dir, exe_name)
            if os.path.isfile(exe_in_dist):
                import shutil
                shutil.move(exe_in_dist, exe_path)

        if os.path.isfile(exe_path):
            if progress_callback:
                progress_callback(f"EXE 已生成: {exe_path}")
            return exe_path

        if progress_callback:
            progress_callback("未找到生成的 EXE 文件")
        return None

    def _build_command(
        self,
        python_script: str,
        output_dir: str,
        project_name: str,
        icon_path: Optional[str],
        onefile: bool,
        no_console: bool,
        key: Optional[str],
    ) -> list:
        """构建 PyInstaller 命令行参数。"""
        cmd = [
            self._python_exe, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--name', project_name,
            '--distpath', output_dir,
            '--workpath', os.path.join(output_dir, 'build'),
            '--specpath', output_dir,
        ]

        if onefile:
            cmd.append('--onefile')

        if no_console:
            cmd.append('--noconsole')

        if icon_path and os.path.isfile(icon_path):
            cmd.extend(['--icon', icon_path])

        if key:
            cmd.extend(['--key', key])

        cmd.extend([
            '--hidden-import', 'PySide6',
            '--hidden-import', 'PySide6.QtCore',
            '--hidden-import', 'PySide6.QtGui',
            '--hidden-import', 'PySide6.QtWidgets',
            '--collect-all', 'PySide6',
            '--collect-all', 'shiboken6',
        ])

        cmd.append(os.path.abspath(python_script))

        return cmd

    def _build_env(self) -> dict:
        """构建子进程环境变量。

        关键：设置 TCL_LIBRARY/TK_LIBRARY，否则 tkinter 会报 broken。
        """
        env = os.environ.copy()

        try:
            tcl_lib, tk_lib = get_python_env_tcl_paths()
            if os.path.isdir(tcl_lib):
                env['TCL_LIBRARY'] = tcl_lib
            if os.path.isdir(tk_lib):
                env['TK_LIBRARY'] = tk_lib
        except Exception:
            pass

        return env