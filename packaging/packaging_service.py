"""打包服务模块。

从编辑器内部调用，提供项目打包为 exe 的服务接口。
后台执行打包，通过信号报告进度和结果。
"""

import os
import sys
import subprocess
from PySide6.QtCore import QObject, Signal, QThread

PACKAGING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packaging")


class PackWorker(QThread):
    """打包工作线程。"""

    progress = Signal(str)
    finished_ok = Signal(str)
    finished_err = Signal(str)

    def __init__(self, project_path: str, app_name: str = "", icon_path: str = ""):
        super().__init__()
        self._project_path = project_path
        self._app_name = app_name
        self._icon_path = icon_path

    def run(self):
        try:
            self.progress.emit("检查打包环境...")

            build_env = os.path.join(PACKAGING_DIR, "build_env")
            pyinstaller = os.path.join(build_env, "python", "Scripts", "pyinstaller.exe")

            if not os.path.exists(pyinstaller):
                self.progress.emit("打包环境未就绪，正在准备...")
                setup_script = os.path.join(PACKAGING_DIR, "setup_env.py")
                result = subprocess.run(
                    [sys.executable, setup_script],
                    capture_output=True, text=True, timeout=600
                )
                if result.returncode != 0:
                    self.finished_err.emit(f"环境准备失败:\n{result.stderr[-500:]}")
                    return

            if not self._app_name:
                self._app_name = os.path.splitext(os.path.basename(self._project_path))[0]

            self.progress.emit(f"开始打包: {self._app_name}...")

            build_script = os.path.join(PACKAGING_DIR, "build_project.py")
            cmd = [sys.executable, build_script, self._project_path, "--name", self._app_name]
            if self._icon_path:
                cmd.extend(["--icon", self._icon_path])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            exe_path = os.path.join(PACKAGING_DIR, "output", f"{self._app_name}.exe")
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                self.finished_ok.emit(f"打包成功!\n\n文件: {exe_path}\n大小: {size_mb:.1f} MB")
            else:
                err_msg = result.stderr[-800:] if result.stderr else "未知错误"
                self.finished_err.emit(f"打包失败:\n{err_msg}")

        except Exception as e:
            self.finished_err.emit(f"打包异常: {e}")


class PackagingService(QObject):
    """打包服务（单例）。

    从编辑器 UI 调用，后台执行打包。
    """

    progress = Signal(str)
    finished_ok = Signal(str)
    finished_err = Signal(str)

    _instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

    @classmethod
    def get_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance

    def is_busy(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    def pack(self, project_path: str, app_name: str = "", icon_path: str = ""):
        if self.is_busy():
            self.finished_err.emit("已有打包任务在运行")
            return

        self._worker = PackWorker(project_path, app_name, icon_path)
        self._worker.progress.connect(self.progress.emit)
        self._worker.finished_ok.connect(self._on_finished_ok)
        self._worker.finished_err.connect(self._on_finished_err)
        self._worker.start()

    def _on_finished_ok(self, msg: str):
        self.finished_ok.emit(msg)
        self._cleanup()

    def _on_finished_err(self, msg: str):
        self.finished_err.emit(msg)
        self._cleanup()

    def _cleanup(self):
        if self._worker:
            self._worker.progress.disconnect()
            self._worker.finished_ok.disconnect()
            self._worker.finished_err.disconnect()
            self._worker = None
