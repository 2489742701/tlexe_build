"""路径工具模块。

兼容 Nuitka / PyInstaller / 源码三种运行模式的路径处理。
参照 HtmlDown2-Pro 项目的路径处理方案，确保打包后的程序
能正确找到资源文件和内置 Python 环境。

## 三种运行模式
- 源码模式: 直接 python main.py 运行
- PyInstaller 模式: sys._MEIPASS 指向解压临时目录
- Nuitka 模式: __compiled__ 全局变量存在，资源在 EXE 同目录

## 关键设计
- get_base_path(): 获取内部资源路径（只读）
- get_external_base_path(): 获取外部数据路径（可读写）
- get_resource_path(): 获取资源文件路径
- ensure_python_env(): 确保内置 Python 环境可用
"""

import os
import sys
import tarfile

def get_base_path() -> str:
    """获取内部资源基础路径（只读）。

    PyInstaller 模式下指向解压临时目录，
    Nuitka/源码模式下指向项目根目录。

    Returns:
        内部资源基础路径
    """
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    if globals().get('__compiled__') is not None:
        return os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_external_base_path() -> str:
    """获取外部数据基础路径（可读写）。

    打包模式下指向 EXE 所在目录，
    源码模式下指向项目根目录。
    用于存放用户数据、日志、python_env 等。

    Returns:
        外部数据基础路径
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    if globals().get('__compiled__') is not None:
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径。

    兼容三种运行模式，自动在正确的位置查找资源文件。

    Args:
        relative_path: 相对于项目根目录的路径

    Returns:
        资源文件的绝对路径
    """
    if globals().get('__compiled__') is not None:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, relative_path)

    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        bundled_path = os.path.join(exe_dir, relative_path)
        if os.path.exists(bundled_path):
            return bundled_path

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def ensure_python_env() -> str:
    """确保内置 Python 环境可用。

    首次使用时自动从 python_env.zip 解压。
    解压后验证环境完整性。

    Returns:
        python_env/python.exe 的路径

    Raises:
        FileNotFoundError: python_env.zip 不存在
        RuntimeError: Python 环境验证失败
    """
    base = get_external_base_path()
    python_exe = os.path.join(base, 'python_env', 'python.exe')
    env_zip = os.path.join(base, 'python_env.zip')

    if os.path.isfile(python_exe):
        return python_exe

    if not os.path.isfile(env_zip):
        raise FileNotFoundError(
            f"缺少 python_env.zip，请将其放到程序同目录下:\n{base}"
        )

    import subprocess

    try:
        with tarfile.open(env_zip, 'r') as tar:
            tar.extractall(base)
    except tarfile.ReadError:
        import zipfile
        with zipfile.ZipFile(env_zip, 'r') as zf:
            zf.extractall(base)

    venv_cfg = os.path.join(base, 'python_env', 'pyvenv.cfg')
    if os.path.isfile(venv_cfg):
        os.remove(venv_cfg)

    result = subprocess.run(
        [python_exe, '-c', 'import sys; print("OK")'],
        capture_output=True, text=True, timeout=10
    )

    if 'OK' not in result.stdout:
        raise RuntimeError(
            f"Python 环境验证失败:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    return python_exe

def get_python_env_tcl_paths() -> tuple:
    """获取 python_env 中 TCL/TK 库的路径。

    PyInstaller 打包 tkinter 程序时必须设置
    TCL_LIBRARY 和 TK_LIBRARY 环境变量，
    否则 tkinter 会报 "broken" 错误。

    Returns:
        (tcl_library_path, tk_library_path)
    """
    base = get_external_base_path()
    python_dir = os.path.join(base, 'python_env')

    tcl_lib = os.path.join(python_dir, 'tcl', 'tcl8.6')
    tk_lib = os.path.join(python_dir, 'tcl', 'tk8.6')

    if not os.path.isdir(tcl_lib):
        for item in os.listdir(os.path.join(python_dir, 'tcl')) if os.path.isdir(os.path.join(python_dir, 'tcl')) else []:
            item_path = os.path.join(python_dir, 'tcl', item)
            if os.path.isdir(item_path):
                if item.startswith('tcl'):
                    tcl_lib = item_path
                elif item.startswith('tk'):
                    tk_lib = item_path

    return tcl_lib, tk_lib