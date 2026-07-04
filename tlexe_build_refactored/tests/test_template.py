"""测试模板模块。

本模块包含一个预设的测试项目模板，用于验证窗口编辑器的功能。
包含一个完整的"电脑开机检测"恶搞程序。

【开机检测流程说明】
1. 询问窗口：显示"是否检测开机？"，有"是"和"否"两个按钮
2. 点"否"：关闭程序
3. 点"是"：进入测试界面，显示"正在测试电脑是否开机"
4. 假进度条：等待几秒后继续执行
5. 结果窗口：显示"恭喜您的电脑已经成功开机！"

【进度条完成跳转】
- 进度条设置 target_window_id 为结果窗口ID
- 进度条完成后自动打开结果窗口
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import platform

def get_test_template() -> Dict[str, Any]:
    """获取测试项目模板。
    
    【开机检测恶搞程序】
    返回一个包含完整测试项目的字典，包括:
    - 询问窗口：询问是否检测开机
    - 检测窗口：显示假进度条
    - 结果窗口：显示检测结果
    
    Returns:
        Dict[str, Any]: 完整的项目数据字典
    """
    return {
        'name': '电脑开机检测演示',
        'main_window_id': 'ask_001',
        'current_window_id': 'ask_001',
        'windows': [
            {
                'id': 'ask_001',
                'name': '询问窗口',
                'window_type': 'main',
                'width': 500,
                'height': 350,
                'title': '电脑开机检测',
                'components': ['container_ask', 'label_ask', 'button_yes', 'button_no']
            },
            {
                'id': 'testing_001',
                'name': '检测中',
                'window_type': 'event',
                'width': 550,
                'height': 400,
                'title': '正在检测...',
                'components': ['container_testing', 'label_testing', 'progressbar_testing', 'label_hint']
            },
            {
                'id': 'result_001',
                'name': '检测结果',
                'window_type': 'event',
                'width': 600,
                'height': 500,
                'title': '检测结果',
                'components': ['container_result', 'label_result_title', 'label_result_desc', 'label_system_info', 'button_close_result']
            }
        ],
        'components': [
            {
                'id': 'container_ask',
                'comp_type': 'container',
                'name': '询问窗口容器',
                'x': 0,
                'y': 0,
                'width': 500,
                'height': 350,
                'text': '电脑开机检测',
                'parent_id': '',
                'style': {
                    'background_color': '#f0f0f0',
                    'border_color': '#cccccc',
                    'border_width': 1,
                    'border_radius': 8
                },
                'position_mode': 'center'
            },
            {
                'id': 'label_ask',
                'comp_type': 'label',
                'name': '询问标签',
                'x': 100,
                'y': 80,
                'width': 300,
                'height': 60,
                'text': '是否检测电脑是否开机？',
                'parent_id': 'container_ask',
                'style': {
                    'background_color': 'transparent',
                    'text_color': '#333333',
                    'font_size': 16,
                    'font_bold': True
                },
                'alignment': 'center',
                'word_wrap': True
            },
            {
                'id': 'button_yes',
                'comp_type': 'button',
                'name': '是按钮',
                'x': 120,
                'y': 200,
                'width': 120,
                'height': 50,
                'text': '是',
                'parent_id': 'container_ask',
                'style': {
                    'background_color': '#4CAF50',
                    'text_color': '#ffffff',
                    'border_radius': 4,
                    'font_size': 16,
                    'font_bold': True
                },
                'target_window_id': 'testing_001',
                'branch_name': '开始检测',
                'open_mode': 'new_window'
            },
            {
                'id': 'button_no',
                'comp_type': 'button',
                'name': '否按钮',
                'x': 260,
                'y': 200,
                'width': 120,
                'height': 50,
                'text': '否',
                'parent_id': 'container_ask',
                'style': {
                    'background_color': '#f44336',
                    'text_color': '#ffffff',
                    'border_radius': 4,
                    'font_size': 16,
                    'font_bold': True
                },
                'target_window_id': '',
                'action': {
                    'action_type': 'close_window',
                    'params': {}
                }
            },
            
            {
                'id': 'container_testing',
                'comp_type': 'container',
                'name': '检测中容器',
                'x': 0,
                'y': 0,
                'width': 550,
                'height': 400,
                'text': '正在检测...',
                'parent_id': '',
                'style': {
                    'background_color': '#f0f0f0',
                    'border_color': '#cccccc',
                    'border_width': 1,
                    'border_radius': 8
                },
                'position_mode': 'center'
            },
            {
                'id': 'label_testing',
                'comp_type': 'label',
                'name': '检测中标签',
                'x': 100,
                'y': 72,
                'width': 300,
                'height': 40,
                'text': '正在检测您的电脑是否开机...',
                'parent_id': 'container_testing',
                'style': {
                    'background_color': 'transparent',
                    'text_color': '#333333',
                    'font_size': 16,
                    'font_bold': True
                },
                'alignment': 'center'
            },
            {
                'id': 'progressbar_testing',
                'comp_type': 'progressbar',
                'name': '虚假的进度条',
                'x': 100,
                'y': 142,
                'width': 300,
                'height': 30,
                'text': '',
                'parent_id': 'container_testing',
                'style': {
                    'background_color': '#e0e0e0',
                    'border_color': '#0078d7',
                    'border_width': 2,
                    'border_radius': 4
                },
                'value': 0,
                'show_text': True,
                'auto_progress': True,
                'duration': 3,
                'target_window_id': 'result_001'
            },
            {
                'id': 'label_hint',
                'comp_type': 'label',
                'name': '提示标签',
                'x': 100,
                'y': 202,
                'width': 300,
                'height': 30,
                'text': '请稍候，正在检测中...',
                'parent_id': 'container_testing',
                'style': {
                    'background_color': 'transparent',
                    'text_color': '#666666',
                    'font_size': 12
                },
                'alignment': 'center'
            },
            
            {
                'id': 'container_result',
                'comp_type': 'container',
                'name': '结果窗口容器',
                'x': 0,
                'y': 0,
                'width': 600,
                'height': 500,
                'text': '检测结果',
                'parent_id': '',
                'style': {
                    'background_color': '#f0f0f0',
                    'border_color': '#4CAF50',
                    'border_width': 2,
                    'border_radius': 8
                },
                'position_mode': 'center'
            },
            {
                'id': 'label_result_title',
                'comp_type': 'label',
                'name': '结果标题',
                'x': 100,
                'y': 47,
                'width': 300,
                'height': 50,
                'text': '🎉 恭喜！您的电脑已经成功开机！',
                'parent_id': 'container_result',
                'style': {
                    'background_color': 'transparent',
                    'text_color': '#4CAF50',
                    'font_size': 18,
                    'font_bold': True
                },
                'alignment': 'center',
                'word_wrap': True
            },
            {
                'id': 'label_result_desc',
                'comp_type': 'label',
                'name': '结果描述',
                'x': 100,
                'y': 117,
                'width': 300,
                'height': 60,
                'text': '经过严格的检测，我们确认您的电脑确实已经开机。\n这是一个非常了不起的成就！',
                'parent_id': 'container_result',
                'style': {
                    'background_color': 'transparent',
                    'text_color': '#333333',
                    'font_size': 12
                },
                'alignment': 'center',
                'word_wrap': True
            },
            {
                'id': 'label_system_info',
                'comp_type': 'label',
                'name': '系统信息',
                'x': 100,
                'y': 197,
                'width': 300,
                'height': 30,
                'text': f'系统: {platform.system()} {platform.release()}',
                'parent_id': 'container_result',
                'style': {
                    'background_color': 'transparent',
                    'text_color': '#666666',
                    'font_size': 11
                },
                'alignment': 'center'
            },
            {
                'id': 'button_close_result',
                'comp_type': 'button',
                'name': '关闭按钮',
                'x': 200,
                'y': 267,
                'width': 100,
                'height': 40,
                'text': '关闭',
                'parent_id': 'container_result',
                'style': {
                    'background_color': '#0078d7',
                    'text_color': '#ffffff',
                    'border_radius': 4,
                    'font_size': 14
                },
                'target_window_id': '',
                'action': {
                    'action_type': 'close_window',
                    'params': {}
                }
            }
        ]
    }

def save_test_template(file_path: str) -> bool:
    """保存测试模板到文件。
    
    Args:
        file_path: 文件保存路径
    
    Returns:
        是否保存成功
    """
    try:
        template = get_test_template()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存测试模板失败: {e}")
        return False
