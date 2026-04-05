"""自动保存服务。

本模块负责管理项目的自动保存功能，包括未保存项目的自动保存、
临时文件管理等。

## 修复说明 (2026-04-02)
【问题】main.py 中的 AppManager 类包含了自动保存逻辑：
- _auto_save_unsaved_project() - 自动保存未保存项目
- _check_unsaved_before_exit() - 退出前检查未保存修改

【解决方案】创建 AutoSaveService 类，将自动保存逻辑从 AppManager 中分离。

【收益】
1. 自动保存逻辑独立，便于配置和测试
2. 支持设置自动保存间隔、启用/禁用等
3. 与 TempFileManager 协作，实现完整的临时文件管理
"""

import os
from datetime import datetime
from typing import Optional, Callable

from models import ProjectModel
from utils.temp_file_manager import TempFileManager
from utils.session_logger import SessionLogger


class AutoSaveService:
    """自动保存服务。
    
    负责自动保存未保存的项目到临时目录。
    
    Attributes:
        _temp_file_manager: 临时文件管理器实例
        _session_logger: 会话日志记录器
        _enabled: 是否启用自动保存
        
    ## 修复说明 (2026-04-02)
    此类从 AppManager 中抽取，专门处理自动保存相关逻辑。
    """
    
    def __init__(self, session_logger: Optional[SessionLogger] = None):
        """初始化自动保存服务。
        
        Args:
            session_logger: 会话日志记录器，用于记录自动保存操作
        """
        self._temp_file_manager = TempFileManager()
        self._session_logger = session_logger
        self._enabled = True
    
    def auto_save_project(self, project_model: ProjectModel) -> Optional[str]:
        """自动保存未保存的项目。
        
        Args:
            project_model: 项目数据模型
            
        Returns:
            保存的文件路径，如果保存失败则返回 None
            
        ## 修复说明 (2026-04-02)
        从 AppManager._auto_save_unsaved_project() 方法抽取。
        简化了逻辑，直接使用 TempFileManager 的方法。
        """
        if not self._enabled or not project_model:
            return None
        
        # 生成临时保存路径
        temp_path = self._temp_file_manager.generate_temp_save_path()
        
        # 保存项目
        if project_model.save_to_file(temp_path):
            # 添加到未保存项目列表
            self._temp_file_manager.add_unsaved_project(
                temp_path,
                project_model.name or "未保存项目"
            )
            
            if self._session_logger:
                self._session_logger.log("INFO", f"自动保存未保存项目: {temp_path}")
            
            return temp_path
        
        return None
    
    def should_auto_save(self, project_model: Optional[ProjectModel]) -> bool:
        """检查是否应该自动保存。
        
        Args:
            project_model: 项目数据模型
            
        Returns:
            如果项目有未保存的修改且启用了自动保存，返回 True
        """
        if not self._enabled:
            return False
        
        if not project_model:
            return False
        
        return project_model.is_dirty
    
    def on_application_exit(self, project_model: Optional[ProjectModel]) -> bool:
        """应用程序退出时的处理。
        
        检查是否有未保存的修改，如果有则自动保存。
        
        Args:
            project_model: 当前项目数据模型
            
        Returns:
            是否允许退出（始终返回 True，因为自动保存不会阻止退出）
            
        ## 修复说明 (2026-04-02)
        从 AppManager._check_unsaved_before_exit() 方法抽取。
        移除了用户交互逻辑（询问是否保存），专注于自动保存。
        用户交互应在调用此方法前处理。
        """
        if self.should_auto_save(project_model):
            self.auto_save_project(project_model)
        
        return True
    
    def set_enabled(self, enabled: bool):
        """设置是否启用自动保存。
        
        Args:
            enabled: 是否启用
        """
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        """检查自动保存是否启用。
        
        Returns:
            是否启用自动保存
        """
        return self._enabled
    
    def get_unsaved_projects(self):
        """获取未保存项目列表。
        
        Returns:
            未保存项目列表
        """
        return self._temp_file_manager.get_unsaved_projects()
    
    def remove_from_unsaved(self, file_path: str):
        """从列表中移除指定项目。
        
        Args:
            file_path: 要移除的项目文件路径
        """
        self._temp_file_manager.remove_from_unsaved(file_path)
