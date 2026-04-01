#!/usr/bin/env python3
"""清理最近项目列表中的重复项目。"""

import json
import os
from datetime import datetime

def normalize_path(path):
    """规范化路径，用于去重比较。"""
    # 转换为绝对路径并规范化
    abs_path = os.path.abspath(path)
    # 统一大小写（Windows下路径不区分大小写）
    normalized = os.path.normcase(abs_path)
    # 移除多余的路径分隔符
    normalized = os.path.normpath(normalized)
    return normalized

def cleanup_recent_projects():
    """清理最近项目列表中的重复项目。"""
    
    # 配置文件路径
    config_path = os.path.join(os.environ.get('APPDATA', ''), 'UIDevTool', 'config.json')
    
    if not os.path.exists(config_path):
        print("配置文件不存在，无需清理")
        return
    
    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    recent_projects = config.get('recent_projects', [])
    print(f"清理前项目数量: {len(recent_projects)}")
    
    # 按最后打开时间排序（最新的在前）
    recent_projects.sort(key=lambda x: x.get('last_opened', ''), reverse=True)
    
    # 去重逻辑：保留每个项目的唯一版本（基于规范化路径）
    seen_paths = set()
    cleaned_projects = []
    
    for project in recent_projects:
        path = project.get('path', '')
        if not path:
            continue
            
        normalized = normalize_path(path)
        
        # 如果路径已经存在，跳过（保留第一个出现的，即最新的）
        if normalized in seen_paths:
            print(f"移除重复项目: {path}")
            continue
            
        seen_paths.add(normalized)
        cleaned_projects.append(project)
    
    print(f"清理后项目数量: {len(cleaned_projects)}")
    
    # 更新配置文件
    config['recent_projects'] = cleaned_projects
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("清理完成！")
    
    # 显示保留的项目
    print("\n保留的项目:")
    for i, project in enumerate(cleaned_projects, 1):
        path = project.get('path', '')
        name = project.get('name', '未命名')
        last_opened = project.get('last_opened', '')
        
        # 格式化时间
        try:
            dt = datetime.fromisoformat(last_opened)
            now = datetime.now()
            diff = now - dt
            
            if diff.days == 0:
                time_str = f"今天 {dt.strftime('%H:%M')}"
            elif diff.days == 1:
                time_str = f"昨天 {dt.strftime('%H:%M')}"
            elif diff.days < 7:
                time_str = f"{diff.days}天前"
            else:
                time_str = dt.strftime("%Y-%m-%d")
        except:
            time_str = "未知时间"
        
        print(f"{i}. {name} - {time_str}")
        print(f"   路径: {path}")

if __name__ == "__main__":
    cleanup_recent_projects()