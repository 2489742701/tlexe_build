import sys
import os

lib_dir = r'D:\opencode-窗口编辑器迁移尝试\tlexe_build\packaging\output\test_export\交替变换演示\lib'
sys.path.insert(0, lib_dir)

os.add_dll_directory(os.path.join(lib_dir, 'PySide6'))
os.add_dll_directory(os.path.join(lib_dir, 'shiboken6'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

print("PySide6 imported OK")

from models.registry_init import register_all_components
from runtime.runner import Runner

register_all_components()
print("Components registered OK")

app = QApplication(sys.argv)
print("QApplication created OK")