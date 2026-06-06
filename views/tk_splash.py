"""Tkinter 启动画面模块。

在 Qt 应用初始化之前显示加载界面，避免 QApplication 创建过早的问题。
"""

import tkinter as tk
from tkinter import ttk
import sys


class TkSplash:
    """Tkinter 启动画面"""
    
    def __init__(self):
        self._root = None
        self._progress = None
        self._status = None
        self._steps = []
        self._current_step = 0
    
    def show(self):
        """显示启动画面"""
        self._root = tk.Tk()
        self._root.title("UI快速开发工具")
        self._root.resizable(False, False)
        
        # 居中显示
        self._root.update_idletasks()
        ws = self._root.winfo_screenwidth()
        hs = self._root.winfo_screenheight()
        x = (ws - 400) // 2
        y = (hs - 200) // 2
        self._root.geometry(f"400x200+{x}+{y}")
        
        # 无边框
        self._root.overrideredirect(True)
        
        # 样式
        self._root.configure(bg="#1a56db")
        
        # 标题
        title = tk.Label(
            self._root,
            text="UI快速开发工具",
            font=("Microsoft YaHei", 16, "bold"),
            bg="#1a56db",
            fg="white"
        )
        title.pack(pady=(30, 10))
        
        # 状态文字
        self._status = tk.Label(
            self._root,
            text="正在初始化...",
            font=("Microsoft YaHei", 10),
            bg="#1a56db",
            fg="white"
        )
        self._status.pack(pady=5)
        
        # 进度条
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "custom.Horizontal.TProgressbar",
            troughcolor="#0f3460",
            background="white",
            thickness=8
        )
        self._progress = ttk.Progressbar(
            self._root,
            mode='determinate',
            length=320,
            style="custom.Horizontal.TProgressbar"
        )
        self._progress.pack(pady=15)
        self._progress['maximum'] = 100
        self._progress['value'] = 0
        
        # 底部提示
        footer = tk.Label(
            self._root,
            text="首次启动可能需要较长时间...",
            font=("Microsoft YaHei", 8),
            bg="#1a56db",
            fg="#cccccc"
        )
        footer.pack(side=tk.BOTTOM, pady=10)
        
        self._root.update()
    
    def update_status(self, text: str, progress: int = None):
        """更新状态
        
        Args:
            text: 状态文字
            progress: 进度值 0-100
        """
        if self._root:
            if text:
                self._status.config(text=text)
            if progress is not None:
                self._progress['value'] = progress
            self._root.update()
    
    def close(self):
        """关闭启动画面"""
        if self._root:
            self._root.destroy()
            self._root = None


# 全局实例
_splash_instance = None


def show_splash():
    """显示启动画面"""
    global _splash_instance
    _splash_instance = TkSplash()
    _splash_instance.show()


def update_splash(text: str, progress: int = None):
    """更新启动画面"""
    if _splash_instance:
        _splash_instance.update_status(text, progress)


def close_splash():
    """关闭启动画面"""
    if _splash_instance:
        _splash_instance.close()
