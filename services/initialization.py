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
"""

import sys
import os
from typing import Optional

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
        _auto_save_service: 自动保存服务实例
        _temp_file_manager: 临时文件管理器实例
        
    ## 修复说明 (2026-04-02)
    此类是代码重构的核心，将原本散落在 AppManager.__init__ 中的
    初始化代码抽取到这里，使 AppManager 只负责窗口管理相关的逻辑。
    """
    
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
        
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        【问题】渲染器、属性编辑器等在首次使用时才加载，导致 UI 启动时显示不正确
        【解决】在应用启动时预加载所有缓存，确保 UI 页面正常显示
        【调用时机】在 UI 设置应用后、主窗口显示前调用
        
        预加载内容包括：
        1. 渲染器实例缓存
        2. 属性编辑器注册
        
        此方法应在 QApplication 创建后调用，因为部分资源依赖 Qt 环境。
        """
        if self._session_logger:
            self._session_logger.log("INFO", "开始预加载核心资源...")
        
        try:
            # 1. 预加载所有渲染器实例
            from renderers.renderer_factory_v2 import RendererFactoryV2
            RendererFactoryV2.preload_all()
            
            if self._session_logger:
                preload_status = RendererFactoryV2.get_preload_status()
                cached_count = sum(1 for v in preload_status.values() if v)
                total_count = len(preload_status)
                self._session_logger.log("INFO", f"渲染器预加载完成: {cached_count}/{total_count}")
            
            # 2. 确保属性编辑器已注册
            # 通过导入所有编辑器模块触发装饰器注册
            self._import_all_property_editors()
            
            if self._session_logger:
                self._session_logger.log("INFO", "核心资源预加载完成")
                
        except Exception as e:
            if self._session_logger:
                self._session_logger.log("ERROR", f"预加载资源失败: {e}")
            # 预加载失败不应阻止应用启动，记录错误即可
    
    def _import_all_property_editors(self):
        """导入所有属性编辑器模块以触发自动注册。
        
        ## 修复说明 (2026-04-02 MCP 启动缓存审查)
        动态导入 views/property_editors 目录下的所有编辑器模块，
        触发类装饰器执行，完成属性编辑器的自动注册。
        """
        import importlib
        import os
        
        # 属性编辑器模块所在目录
        editors_package = 'views.property_editors'
        editors_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'views', 'property_editors'
        )
        
        if not os.path.exists(editors_dir):
            if self._session_logger:
                self._session_logger.log("WARNING", f"属性编辑器目录不存在: {editors_dir}")
            return
        
        imported_count = 0
        for filename in os.listdir(editors_dir):
            # 导入所有 .py 文件（排除 __init__.py）
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]  # 去掉 .py
                try:
                    importlib.import_module(f'{editors_package}.{module_name}')
                    imported_count += 1
                except ImportError as e:
                    if self._session_logger:
                        self._session_logger.log("WARNING", f"导入编辑器模块失败 {module_name}: {e}")
        
        if self._session_logger:
            self._session_logger.log("INFO", f"已导入 {imported_count} 个属性编辑器模块")
    
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
        self.init_qapplication()
        self.init_logging()
        self.init_dev_mode()
        self.init_ui_settings()
        self._preload_resources()  # 新增：预加载核心资源
        
        return self._app
