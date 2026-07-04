"""cx_Freeze 打包配置。"""

import sys
import os
from cx_Freeze import setup, Executable

base_dir = os.path.dirname(os.path.abspath(__file__))

include_files = []
for subdir in ["icons", "samples", "resources"]:
    src = os.path.join(base_dir, subdir)
    if os.path.isdir(src):
        include_files.append((src, subdir))

build_exe_options = {
    "packages": [
        "PySide6", "shiboken6",
        "models", "views", "controllers", "runtime", "renderers",
        "services", "utils", "dev_mode", "styles", "eventbus",
        "presenters", "templates", "packaging",
    ],
    "includes": [
        "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",
        "PySide6.QtSvg", "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    ],
    "excludes": [
        "tkinter", "unittest", "pytest",
    ],
    "include_files": include_files,
    "optimize": 0,
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="UIDevTool",
    version="1.0.0",
    description="UI Rapid Development Tool",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            script=os.path.join(base_dir, "main.py"),
            base=base,
            target_name="UIDevTool.exe",
        )
    ],
)