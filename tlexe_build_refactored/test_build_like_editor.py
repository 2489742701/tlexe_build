import sys
import os

base_dir = r"D:\opencode-窗口编辑器迁移尝试\tlexe_build"

from cx_Freeze.freezer import Freezer
from cx_Freeze.executable import Executable

sys.path.insert(0, base_dir)

output_dir = os.path.join(base_dir, "packaging", "output", "test_export", "交替变换演示")

entry_script = os.path.join(base_dir, "packaging", "output", "test_export", "交替变换演示", "main_src", "main.py")

exe = Executable(
    script=entry_script,
    base="gui",
    target_name="交替变换演示.exe",
)

freezer = Freezer(
    executables=[exe],
    packages=[
        "PySide6", "shiboken6",
        "models", "views", "controllers", "runtime", "renderers",
        "services", "utils", "dev_mode", "styles", "eventbus",
        "presenters", "templates",
    ],
    includes=[
        "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",
        "PySide6.QtSvg", "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    ],
    excludes=["tkinter", "unittest", "pytest", "torch", "numpy"],
    target_dir=output_dir,
    include_files=[
        (os.path.join(base_dir, "icons"), "icons"),
        (os.path.join(base_dir, "samples"), "samples"),
    ],
)

print("开始 cx_Freeze 打包...")
freezer.freeze()
print(f"打包完成！输出目录: {output_dir}")