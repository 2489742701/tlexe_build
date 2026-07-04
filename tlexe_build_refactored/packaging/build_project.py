"""一键打包脚本。

将用户项目（.py 格式）打包成独立 exe。
使用 packaging/build_env 中的 python-embed + PyInstaller。

使用方式：
    python packaging/build_project.py <项目文件.py> [--icon 图标.ico] [--name 应用名]

示例：
    python packaging/build_project.py samples/按钮演示.py
    python packaging/build_project.py my_app.py --icon my_icon.ico --name 我的应用
"""

import os
import sys
import subprocess
import shutil
import tempfile

PACKAGING_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_ENV = os.path.join(PACKAGING_DIR, "build_env")
PYTHON_EXE = os.path.join(BUILD_ENV, "python", "python.exe")
PYINSTALLER_ENV = os.path.join(BUILD_ENV, "python", "Scripts", "pyinstaller.exe")
PYINSTALLER_SYS = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Programs", "Python", "Python310", "Scripts", "pyinstaller.exe"
)
PYINSTALLER = PYINSTALLER_ENV if os.path.exists(PYINSTALLER_ENV) else PYINSTALLER_SYS

RUNTIME_DIR = os.path.join(os.path.dirname(PACKAGING_DIR), "runtime")
OUTPUT_DIR = os.path.join(PACKAGING_DIR, "output")

def build(project_file: str, icon: str = None, app_name: str = None):
    project_file = os.path.abspath(project_file)
    if not os.path.exists(project_file):
        print(f"[ERROR] 项目文件不存在: {project_file}")
        return False

    if not os.path.exists(PYINSTALLER):
        print(f"[ERROR] 打包环境未准备，请先运行: python packaging/setup_env.py")
        return False

    if not app_name:
        app_name = os.path.splitext(os.path.basename(project_file))[0]

    print(f"=== 打包项目 ===")
    print(f"项目文件: {project_file}")
    print(f"应用名称: {app_name}")
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    entry_script, data_path = _generate_entry_script(project_file, app_name)

    cmd = [
        PYINSTALLER,
        "--onefile",
        "--windowed",
        "--name", app_name,
        "--distpath", OUTPUT_DIR,
        "--workpath", os.path.join(PACKAGING_DIR, "build_temp"),
        "--specpath", os.path.join(PACKAGING_DIR, "build_temp"),
        "--clean",
        "--noconfirm",
        "--collect-all", "PySide6",
        "--collect-all", "shiboken6",
    ]

    if icon and os.path.exists(icon):
        cmd.extend(["--icon", icon])

    tlexe_build_dir = os.path.dirname(PACKAGING_DIR)
    hidden_imports = _get_hidden_imports()
    for hi in hidden_imports:
        cmd.extend(["--hidden-import", hi])
    cmd.extend(["-p", tlexe_build_dir])

    data_files = _get_data_files(tlexe_build_dir)
    for src, dst in data_files:
        cmd.extend(["--add-data", f"{src};{dst}"])

    cmd.extend(["--add-data", f"{data_path};."])

    cmd.append(entry_script)

    print(f"[执行] PyInstaller ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    exe_path = os.path.join(OUTPUT_DIR, f"{app_name}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n=== 打包成功 ===")
        print(f"输出文件: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        return True
    else:
        print(f"\n=== 打包失败 ===")
        if result.stdout:
            print(result.stdout[-1000:])
        if result.stderr:
            print(result.stderr[-1000:])
        return False

def _get_hidden_imports():
    return [
        "PySide6.QtWidgets",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtSvg",
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "runtime",
        "runtime.runner",
        "runtime.action_executor",
        "runtime.linkage_manager",
        "runtime.runtime_console",
        "runtime.secure_executor",
        "models",
        "models.base",
        "models.components",
        "models.window",
        "models.component_registry",
        "models.registry_init",
        "models.signals",
        "models.model_helpers",
        "models.tech_components",
        "models.communication_system",
        "models.variable_system",
        "utils",
        "utils.component_factory",
        "utils.py_project_format",
        "utils.settings",
        "utils.style_helper",
        "utils.session_logger",
        "utils.icon_manager",
        "utils.converter",
        "utils.undo_manager",
        "utils.safe_code_generator",
        "utils.text_size_calculator",
        "utils.font_utils",
        "utils.temp_file_manager",
        "utils.file_association",
        "utils.crash_log",
        "utils.signal_manager",
        "utils.indexed_communication",
        "utils.safe_expression",
        "renderers",
        "renderers.component_renderer",
        "renderers.button_renderer",
        "renderers.label_renderer",
        "renderers.input_renderer",
        "renderers.container_renderer",
        "renderers.checkbox_renderer",
        "renderers.combobox_renderer",
        "renderers.progressbar_renderer",
        "renderers.image_renderer",
        "renderers.image_button_renderer",
        "renderers.image_carousel_renderer",
        "renderers.hidden_button_renderer",
        "renderers.video_renderer",
        "renderers.alternating_renderer",
        "renderers.lottery_renderer",
        "renderers.renderer_factory",
        "views",
        "views.main_window",
        "views.welcome_page",
        "views.property_panel",
        "views.component_panel",
        "views.canvas",
        "views.register_dialog",
        "views.blockly_editor",
        "views.tk_splash",
        "views.logic_tree",
        "views.state_machine_view",
        "views.signal_manager",
        "views.component_tree",
        "views.flow_preview",
        "views.variable_panel",
        "views.preferences_dialog",
        "views.splash_window",
        "views.property_editors",
        "views.property_editors.base_editor",
        "views.property_editors.alternating_editor",
        "views.property_editors.lottery_editor",
        "views.property_editors.registry",
        "controllers",
        "controllers.project_controller",
        "controllers.canvas_controller",
        "controllers.canvas_controller_v2",
        "services",
        "services.initialization",
        "services.auto_save_service",
        "services.layout",
        "services.layout.layout_engine",
        "services.layout.overlap_avoider",
        "services.layout.overlap_detector",
        "services.layout.overlap_visualizer",
        "presenters",
        "presenters.canvas_presenter",
        "eventbus",
        "eventbus.event_bus",
        "styles",
        "styles.panel_styles",
        "styles.component_styles",
        "styles.theme",
        "templates",
        "templates.test_template",
        "dev_mode",
        "dev_mode.debug_logger",
        "dev_mode.dev_console",
        "dev_mode.dev_manager",
        "dev_mode.test_runner",
    ]

def _get_data_files(tlexe_build_dir):
    data_files = []
    for subdir in ["icons", "samples", "resources"]:
        src = os.path.join(tlexe_build_dir, subdir)
        if os.path.isdir(src):
            data_files.append((src, subdir))
    return data_files

def _generate_entry_script(project_file: str, app_name: str) -> str:
    tlexe_build_dir = os.path.dirname(PACKAGING_DIR)
    if tlexe_build_dir not in sys.path:
        sys.path.insert(0, tlexe_build_dir)

    with open(project_file, 'r', encoding='utf-8') as f:
        project_content = f.read()

    from utils.py_project_format import python_code_to_dict
    project_data = python_code_to_dict(project_content)

    data_path = os.path.join(PACKAGING_DIR, "build_temp", f"{app_name}_data.json")
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    import json
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)

    script = f'''"""自动生成的打包入口脚本（项目数据内嵌）。"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from runtime.runner import Runner

def get_project_data():
    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "{app_name}_data.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    app = QApplication(sys.argv)
    runner = Runner()
    runner.run(get_project_data())
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''
    script_path = os.path.join(PACKAGING_DIR, "build_temp", f"{app_name}_entry.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    return script_path, data_path

def build_main_app(icon: str = None, app_name: str = "傻瓜桌面开发工具", debug: bool = False, onedir: bool = False):
    tlexe_build_dir = os.path.dirname(PACKAGING_DIR)
    main_py = os.path.join(tlexe_build_dir, "main.py")

    if not os.path.exists(main_py):
        print(f"[ERROR] 主程序入口不存在: {main_py}")
        return False

    if not os.path.exists(PYINSTALLER):
        print(f"[ERROR] 打包环境未准备，请先运行: python packaging/setup_env.py")
        return False

    print(f"=== 打包主程序 ===")
    print(f"应用名称: {app_name}")
    print(f"Debug模式: {debug}")
    print(f"文件夹模式: {onedir}")
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    cmd = [
        PYINSTALLER,
        "--onedir" if onedir else "--onefile",
        "--name", app_name,
        "--distpath", OUTPUT_DIR,
        "--workpath", os.path.join(PACKAGING_DIR, "build_temp"),
        "--specpath", os.path.join(PACKAGING_DIR, "build_temp"),
        "--clean",
        "--noconfirm",
        "--collect-all", "PySide6",
        "--collect-all", "shiboken6",
    ]

    if not debug:
        cmd.append("--windowed")

    if icon and os.path.exists(icon):
        cmd.extend(["--icon", icon])

    hidden_imports = _get_hidden_imports()
    hidden_imports.extend([
        "packaging",
        "packaging.packaging_service",
    ])
    for hi in hidden_imports:
        cmd.extend(["--hidden-import", hi])
    cmd.extend(["-p", tlexe_build_dir])

    data_files = _get_data_files(tlexe_build_dir)
    for src, dst in data_files:
        cmd.extend(["--add-data", f"{src};{dst}"])

    cmd.append(main_py)

    print(f"[执行] PyInstaller ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if onedir:
        exe_path = os.path.join(OUTPUT_DIR, app_name, f"{app_name}.exe")
    else:
        exe_path = os.path.join(OUTPUT_DIR, f"{app_name}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n=== 打包成功 ===")
        print(f"输出文件: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        return True
    else:
        print(f"\n=== 打包失败 ===")
        if result.stdout:
            print(result.stdout[-2000:])
        if result.stderr:
            print(result.stderr[-2000:])
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="一键打包项目为 exe")
    sub = parser.add_subparsers(dest="command")

    proj_parser = sub.add_parser("project", help="打包用户项目")
    proj_parser.add_argument("project", help="项目文件路径 (.py)")
    proj_parser.add_argument("--icon", help="应用图标 (.ico)", default=None)
    proj_parser.add_argument("--name", help="应用名称", default=None)

    app_parser = sub.add_parser("app", help="打包主程序")
    app_parser.add_argument("--icon", help="应用图标 (.ico)", default=None)
    app_parser.add_argument("--name", help="应用名称", default="傻瓜桌面开发工具")
    app_parser.add_argument("--debug", action="store_true", help="Debug模式（显示控制台）")
    app_parser.add_argument("--onedir", action="store_true", help="文件夹模式（方便排查缺失文件）")

    args = parser.parse_args()

    if args.command == "project":
        success = build(args.project, icon=args.icon, app_name=args.name)
    elif args.command == "app":
        success = build_main_app(icon=args.icon, app_name=args.name, debug=args.debug, onedir=args.onedir)
    else:
        parser.print_help()
        success = False

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
