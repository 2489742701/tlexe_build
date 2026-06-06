"""打包环境准备脚本。

下载 python-embed 并安装 PySide6 + PyInstaller，
为用户项目打包成独立 exe 提供最小运行时。

使用方式：
    python packaging/setup_env.py
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

PYTHON_VERSION = "3.13.2"
PYTHON_EMBED_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
ENV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_env")


def setup():
    print(f"=== 打包环境准备 ===")
    print(f"Python 版本: {PYTHON_VERSION}")
    print(f"环境目录: {ENV_DIR}")
    print()

    os.makedirs(ENV_DIR, exist_ok=True)

    python_dir = os.path.join(ENV_DIR, "python")
    pip_path = os.path.join(python_dir, "Scripts", "pip.exe")
    python_exe = os.path.join(python_dir, "python.exe")

    if not os.path.exists(python_exe):
        _download_and_extract_embed(python_dir)
    else:
        print(f"[OK] python-embed 已存在: {python_exe}")

    _enable_pip(python_dir)

    if not os.path.exists(pip_path):
        _bootstrap_pip(python_dir, python_exe)

    _install_packages(pip_path)

    print()
    print(f"=== 环境准备完成 ===")
    print(f"Python: {python_exe}")
    print(f"Pip:   {pip_path}")


def _download_and_extract_embed(python_dir):
    zip_path = os.path.join(ENV_DIR, "python-embed.zip")

    if not os.path.exists(zip_path):
        print(f"[下载] {PYTHON_EMBED_URL}")
        urllib.request.urlretrieve(PYTHON_EMBED_URL, zip_path)
        print(f"[OK] 下载完成: {zip_path}")
    else:
        print(f"[OK] 已有下载: {zip_path}")

    os.makedirs(python_dir, exist_ok=True)
    print(f"[解压] -> {python_dir}")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(python_dir)
    print(f"[OK] 解压完成")


def _enable_pip(python_dir):
    pth_file = os.path.join(python_dir, f"python{PYTHON_VERSION[0]}{PYTHON_VERSION[2]}._pth")
    if not os.path.exists(pth_file):
        for f in os.listdir(python_dir):
            if f.endswith("._pth"):
                pth_file = os.path.join(python_dir, f)
                break

    if os.path.exists(pth_file):
        with open(pth_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'Lib\\site-packages' not in content or content.startswith('#'):
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') and 'import site' not in stripped:
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            if not any('import site' in l for l in new_lines):
                new_lines.append('import site')
            if not any('Lib\\\\site-packages' in l or 'Lib/site-packages' in l for l in new_lines):
                new_lines.append('Lib\\site-packages')

            with open(pth_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print(f"[OK] 已启用 pip: {pth_file}")


def _bootstrap_pip(python_dir, python_exe):
    print(f"[安装] get-pip.py ...")
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip_path = os.path.join(ENV_DIR, "get-pip.py")

    if not os.path.exists(get_pip_path):
        urllib.request.urlretrieve(get_pip_url, get_pip_path)

    subprocess.run([python_exe, get_pip_path, "--no-warn-script-location"],
                   check=True, cwd=python_dir)
    print(f"[OK] pip 安装完成")


def _install_packages(pip_path):
    packages = ["PySide6", "pyinstaller"]
    for pkg in packages:
        print(f"[安装] {pkg} ...")
        result = subprocess.run(
            [pip_path, "install", pkg, "--no-warn-script-location"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"[OK] {pkg} 安装完成")
        else:
            print(f"[WARN] {pkg} 安装可能失败: {result.stderr[-200:]}")


if __name__ == "__main__":
    setup()
