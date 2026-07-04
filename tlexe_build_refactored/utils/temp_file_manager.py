"""临时文件管理器。

本模块负责管理应用程序的临时文件，包括未保存项目的临时存储、
临时文件清理等功能。

"""

import os
import json
import tempfile
import random
import string
from datetime import datetime
from typing import List, Dict, Any, Optional

class TempFileManager:
    """临时文件管理器。
    
    负责管理应用程序的临时文件和配置目录。
    
    Attributes:
        _config_dir: 配置目录路径
        _unsaved_file: 未保存项目列表文件路径
        
    """
    
    _instance: Optional['TempFileManager'] = None
    
    def __new__(cls) -> 'TempFileManager':
        """单例模式实现。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化临时文件管理器。"""
        if self._initialized:
            return
            
        self._config_dir = self._get_config_dir()
        self._unsaved_file = os.path.join(self._config_dir, 'unsaved_projects.json')
        self._initialized = True
    
    def _get_config_dir(self) -> str:
        """获取配置目录路径。
        
        Returns:
            配置目录的绝对路径
        """
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'UIDevTool')
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_unsaved_projects(self) -> List[Dict[str, Any]]:
        """获取未保存项目列表。
        
        Returns:
            未保存项目列表，每个项目包含 path, name, saved_at 字段
            
        """
        try:
            if os.path.exists(self._unsaved_file):
                with open(self._unsaved_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # 文件损坏或读取失败，返回空列表
            pass
        return []
    
    def save_unsaved_projects(self, projects: List[Dict[str, Any]]):
        """保存未保存项目列表。
        
        Args:
            projects: 未保存项目列表
            
        """
        try:
            with open(self._unsaved_file, 'w', encoding='utf-8') as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
        except IOError:
            # 保存失败，静默处理
            pass
    
    def generate_temp_save_path(self) -> str:
        """生成临时保存路径。
        
        Returns:
            临时文件路径，格式为 unsaved_project_{随机数字}.py
            
        """
        random_str = ''.join(random.choices(string.digits, k=8))
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, f"unsaved_project_{random_str}.py")
    
    def add_unsaved_project(self, file_path: str, name: str) -> List[Dict[str, Any]]:
        """添加未保存项目到列表。
        
        Args:
            file_path: 项目文件路径
            name: 项目名称
            
        Returns:
            更新后的未保存项目列表
            
        """
        projects = self.get_unsaved_projects()
        
        # 插入到列表开头
        projects.insert(0, {
            'path': file_path,
            'name': name,
            'saved_at': datetime.now().isoformat()
        })
        
        # 清理旧项目（保留最近5个）
        if len(projects) > 5:
            for old_project in projects[5:]:
                try:
                    old_path = old_project.get('path')
                    if old_path and os.path.exists(old_path):
                        os.remove(old_path)
                except OSError:
                    pass
            projects = projects[:5]
        
        self.save_unsaved_projects(projects)
        return projects
    
    def remove_from_unsaved(self, file_path: str) -> List[Dict[str, Any]]:
        """从列表中移除指定项目。
        
        Args:
            file_path: 要移除的项目文件路径
            
        Returns:
            更新后的未保存项目列表
            
        """
        normalized_path = os.path.normpath(os.path.abspath(file_path))
        projects = self.get_unsaved_projects()
        
        updated_projects = []
        for project in projects:
            project_path = os.path.normpath(os.path.abspath(project.get('path', '')))
            if project_path != normalized_path:
                updated_projects.append(project)
            else:
                # 删除对应的临时文件
                try:
                    temp_path = project.get('path')
                    if temp_path and os.path.exists(temp_path):
                        os.remove(temp_path)
                except OSError:
                    pass
        
        self.save_unsaved_projects(updated_projects)
        return updated_projects
    
    def cleanup_old_temp_files(self, max_age_days: int = 7):
        """清理过期的临时文件。
        
        Args:
            max_age_days: 文件最大保留天数，默认7天
            
        """
        temp_dir = tempfile.gettempdir()
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_days * 24 * 3600
        
        try:
            for filename in os.listdir(temp_dir):
                if filename.startswith('unsaved_project_') and (filename.endswith('.py') or filename.endswith('.itexe')):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        file_stat = os.stat(file_path)
                        if current_time - file_stat.st_mtime > max_age_seconds:
                            os.remove(file_path)
                    except OSError:
                        pass
        except OSError:
            pass
