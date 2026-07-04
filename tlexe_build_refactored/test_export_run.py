import sys
import os

sys.path.insert(0, r'D:\opencode-窗口编辑器迁移尝试\tlexe_build')

from utils.py_project_format import python_code_to_dict

with open(r'D:\opencode-窗口编辑器迁移尝试\tlexe_build\samples\交替变换演示.py', 'r', encoding='utf-8') as f:
    code = f.read()

project_data = python_code_to_dict(code)
print(f'Project: {project_data.get("name")}')
print(f'Windows: {len(project_data.get("windows", []))}')
print(f'Components: {len(project_data.get("components", []))}')

from services.export_service import ExportService

source_dir = r'D:\opencode-窗口编辑器迁移尝试\tlexe_build'
output_dir = r'D:\opencode-窗口编辑器迁移尝试\tlexe_build\packaging\output\test_export'

service = ExportService(source_dir)

def on_progress(msg, pct):
    print(f'[{pct}%] {msg}')

result = service.export(project_data, output_dir, '交替变换演示.exe', on_progress)
print(f'Export result: {result}')