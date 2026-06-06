"""应用程序初始化协调器。

本模块负责协调应用程序的初始化流程，将各个子系统的初始化
逻辑从 AppManager 中分离出来，实现单一职责原则。

## 修复说明 (2026-04-02)
【问题】main.py 中的 AppManager 类承担了过多职责：
- 应用初始化
- 会话日志管理
- 开发者模式启用
- UI 设置（字体等）
- 自动保存服务初始化
- 临时文件管理器初始化

【解决方案】创建 AppInitializer 类，将各项初始化封装为独立方法，
AppManager 只需调用 initializer.run() 即可按顺序完成所有初始化。

【收益】
1. 职责分离清晰，每个初始化步骤独立
2. 易于单元测试，可以单独测试每个初始化方法
3. 新增初始化步骤只需扩展此类，无需修改 AppManager
4. 各服务可独立复用

## 修复说明 (2026-04-06)
【新增】SplashWindow 启动画面支持
- 在初始化开始时显示加载界面
- 在各初始化步骤中更新加载状态
- 初始化完成后淡出关闭加载界面
"""

import sys
import os
from typing import Optional, Callable

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from utils.session_logger import SessionLogger
from utils.settings import app_settings


class AppInitializer:
    """应用程序初始化协调器。
    
    负责按顺序初始化各个子系统，将初始化逻辑从 AppManager 中分离。
    
    Attributes:
        _app: QApplication 实例
        _session_logger: 会话日志记录器
        _splash: SplashWindow 实例（可选）
        
    ## 修复说明 (2026-04-02)
    此类是代码重构的核心，将原本散落在 AppManager.__init__ 中的
    初始化代码抽取到这里，使 AppManager 只负责窗口管理相关的逻辑。
    
    ## 修复说明 (2026-04-06)
    新增 SplashWindow 支持，提供更友好的启动体验。
    """
    
    # 初始化步骤定义（步骤名称，进度值）
    INIT_STEPS = [
        ("创建应用实例", 5),
        ("初始化日志系统", 10),
        ("加载开发者模式", 20),
        ("应用界面设置", 30),
        ("统一组件注册", 40),
        ("预加载渲染器", 50),
        ("预加载属性编辑器", 70),
        ("注册一致性检测", 80),
        ("初始化完成", 100),
    ]
    
    def __init__(self, dev_mode: bool = False, skip_welcome: bool = False):
        """初始化协调器。
        
        Args:
            dev_mode: 是否启用开发者模式
            skip_welcome: 是否跳过欢迎页
        """
        self.dev_mode = dev_mode
        self.skip_welcome = skip_welcome
        
        self._app: Optional[QApplication] = None
        self._session_logger: Optional[SessionLogger] = None
    
    def init_qapplication(self) -> QApplication:
        """初始化 Qt 应用实例。
        
        Returns:
            QApplication 实例
            
        ## 修复说明 (2026-04-02)
        从 AppManager.__init__ 中抽取，专门负责 QApplication 创建。
        """
        self._app = QApplication(sys.argv)
        return self._app
    
    def init_logging(self) -> SessionLogger:
        """初始化会话日志系统。
        
        Returns:
            SessionLogger 实例
            
        ## 修复说明 (2026-04-02)
        从 AppManager.__init__ 中抽取，专门负责日志系统初始化。
        移除了全局变量 _session_logger 的直接操作，改为返回实例。
        """
        self._session_logger = SessionLogger()
        self._session_logger.log("INFO", "应用程序启动")
        self._session_logger.log("INFO", f"Python版本: {sys.version}")
        self._session_logger.log("INFO", f"工作目录: {os.getcwd()}")
        self._session_logger.log("INFO", f"命令行参数: {sys.argv}")
        return self._session_logger
    
    def init_dev_mode(self):
        """初始化开发者模式。
        
        ## 修复说明 (2026-04-02)
        从 AppManager.__init__ 中抽取，延迟导入 DevModeManager
        避免循环导入问题。
        """
        if self.dev_mode:
            from dev_mode import DevModeManager
            DevModeManager.get_instance().enable()
            if self._session_logger:
                self._session_logger.log("INFO", "开发者模式已启用")
    
    def init_ui_settings(self):
        """应用 UI 设置（字体、样式等）。
        
        ## 修复说明 (2026-04-02)
        从 AppManager.__init__ 中抽取，专门负责 UI 相关设置。
        后续可扩展为主题管理、样式表加载等。
        """
        font_family = app_settings.font_family
        font_size = app_settings.font_size
        
        font = QFont(font_family, font_size)
        self._app.setFont(font)
    
    def _preload_resources(self):
        """预加载所有核心资源。
        
        预加载内容包括：
        1. 统一组件注册（register_all_components）
        2. 渲染器实例缓存
        3. 属性编辑器注册
        4. 注册一致性检测
        
        此方法应在 QApplication 创建后调用，因为部分资源依赖 Qt 环境。
        """
        if self._session_logger:
            self._session_logger.log("INFO", "开始预加载核心资源...")
        
        try:
            from models.registry_init import register_all_components
            register_all_components()
            
            if self._session_logger:
                self._session_logger.log("INFO", "统一组件注册完成")
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("ERROR", f"统一组件注册失败: {e}")
        
        try:
            from renderers.renderer_factory import RendererFactory
            RendererFactory.preload_all()
            
            if self._session_logger:
                preload_status = RendererFactory.get_preload_status()
                cached_count = sum(1 for v in preload_status.values() if v)
                total_count = len(preload_status)
                self._session_logger.log("INFO", f"渲染器预加载完成: {cached_count}/{total_count}")
            
            self._import_all_property_editors()
            
            if self._session_logger:
                self._session_logger.log("INFO", "核心资源预加载完成")
                
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("ERROR", f"预加载资源失败: {e}")
        
        self._check_registration_consistency()
    
    def _import_all_property_editors(self):
        """导入所有属性编辑器模块以触发自动注册。
        
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        动态导入 views/property_editors 目录下的所有编辑器模块，
        触发类装饰器执行，完成属性编辑器的自动注册。
        
        ## 修复说明 (2026-06-07)
        PyInstaller 打包后 os.listdir 目录不存在，改用 pkgutil 遍历包内模块，
        同时保留显式导入列表作为回退。
        """
        import importlib
        import pkgutil
        
        editors_package = 'views.property_editors'
        imported_count = 0
        
        try:
            package = importlib.import_module(editors_package)
            for importer, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                try:
                    importlib.import_module(f'{editors_package}.{module_name}')
                    imported_count += 1
                except ImportError as e:
                    if self._session_logger:
                        self._session_logger.log("WARNING", f"导入编辑器模块失败 {module_name}: {e}")
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("WARNING", f"pkgutil 遍历失败，尝试显式导入: {e}")
            for module_name in [
                'base_editor', 'alternating_editor', 'lottery_editor', 'registry',
                'button_editor', 'label_editor', 'input_editor', 'container_editor',
                'checkbox_editor', 'combobox_editor', 'progressbar_editor',
                'image_editor', 'video_editor', 'image_carousel_editor',
                'hidden_button_editor', 'image_button_editor', 'groupbox_editor',
                'textarea_editor', 'listwidget_editor', 'confirm_button_editor',
            ]:
                try:
                    importlib.import_module(f'{editors_package}.{module_name}')
                    imported_count += 1
                except ImportError:
                    pass
        
        if self._session_logger:
            self._session_logger.log("INFO", f"已导入 {imported_count} 个属性编辑器模块")
    
    def _check_registration_consistency(self):
        """执行注册一致性检测并输出报告。"""
        try:
            from models.component_registry import ComponentRegistry
            import logging
            
            reports = ComponentRegistry.check_registration_consistency()
            if not reports:
                if self._session_logger:
                    self._session_logger.log("INFO", "注册一致性检测通过: 所有组件注册完整")
                return
            
            for report in reports:
                if report.severity == "ERROR":
                    msg = f"注册一致性: {report.type_name} 缺失 {report.missing_items} - {report.suggestion}"
                    if self._session_logger:
                        self._session_logger.log("ERROR", msg)
                else:
                    msg = f"注册一致性: {report.type_name} 缺失 {report.missing_items}"
                    if self._session_logger:
                        self._session_logger.log("DEBUG", msg)
            
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("WARNING", f"注册一致性检测失败: {e}")
    
    def run(self) -> QApplication:
        """执行所有初始化步骤。
        
        按顺序执行：
        1. QApplication 初始化
        2. 日志系统初始化
        3. 开发者模式初始化
        4. UI 设置应用
        5. 核心资源预加载（新增）
        
        Returns:
            初始化完成的 QApplication 实例
            
        ## 修复说明 (2026-04-02)
        这是核心方法，替代了原来 AppManager 中杂乱的初始化代码。
        
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        新增第5步：核心资源预加载，确保 UI 启动时所有缓存已就绪。
        """
        self._show_splash()
        
        self.init_qapplication()
        self.update_splash("创建应用实例", 5)
        
        self.init_logging()
        self.update_splash("初始化日志系统", 10)
        
        self.init_dev_mode()
        self.update_splash("加载开发者模式", 20)
        
        self.init_ui_settings()
        self.update_splash("应用界面设置", 30)
        
        self._preload_resources()
        self.update_splash("预加载渲染器", 50)
        
        self._import_all_property_editors()
        self.update_splash("预加载属性编辑器", 70)
        
        self._check_registration_consistency()
        self.update_splash("注册一致性检测", 80)
        
        self.update_splash("初始化完成", 100)
        self.finish_splash()
        
        return self._app
    
    def _show_splash(self):
        """显示启动画面（跳过，避免 tkinter 干扰 PyInstaller 打包）"""
        pass
    
    def update_splash(self, text: str, progress: int = None):
        """更新启动画面状态"""
        pass
    
    def finish_splash(self, callback: Callable = None):
        """关闭启动画面"""
        if callback:
            callback()
