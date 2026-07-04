import sys
sys.path.insert(0, r'D:\opencode-窗口编辑器迁移尝试\tlexe_build\packaging\output\test_export\交替变换演示\lib')

from models.registry_init import register_all_components
from runtime.runner import Runner

register_all_components()
print('Components registered')
print('All imports OK')