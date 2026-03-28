"""电脑开机检测演示模板。

一个有趣的恶搞程序模板，模拟电脑开机检测过程。
"""

from typing import Dict, Any


def get_test_template() -> Dict[str, Any]:
    """获取电脑开机检测演示模板。
    
    Returns:
        项目数据字典
    """
    return {
        "name": "电脑开机检测演示",
        "windows": [
            {
                "id": "main001",
                "name": "开机检测",
                "window_type": "main",
                "width": 600,
                "height": 400,
                "title": "系统启动检测",
                "components": [
                    "cont001",
                    "lbl001",
                    "prog001",
                    "lbl002",
                    "btn001"
                ],
                "trigger_button_id": None
            },
            {
                "id": "event001",
                "name": "检测完成",
                "window_type": "event",
                "width": 500,
                "height": 300,
                "title": "检测完成",
                "components": [
                    "cont002",
                    "lbl003",
                    "btn002"
                ],
                "trigger_button_id": None
            }
        ],
        "components": [
            {
                "id": "cont001",
                "comp_type": "container",
                "name": "主容器",
                "x": 50,
                "y": 30,
                "width": 500,
                "height": 340,
                "text": "系统启动检测程序 v1.0",
                "parent_id": "",
                "style": {
                    "background_color": "#1a1a2e",
                    "text_color": "#00ff00",
                    "border_color": "#00ff00",
                    "border_width": 2,
                    "border_radius": 5,
                    "font_family": "Consolas",
                    "font_size": 10,
                    "font_bold": False
                },
                "action": {
                    "action_type": "none",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "children": [],
                "position_mode": "center",
                "layout": "none",
                "padding": 10,
                "spacing": 5
            },
            {
                "id": "lbl001",
                "comp_type": "label",
                "name": "检测标题",
                "x": 150,
                "y": 80,
                "width": 300,
                "height": 40,
                "text": "正在检测系统硬件...",
                "parent_id": "cont001",
                "style": {
                    "background_color": "transparent",
                    "text_color": "#00ff00",
                    "border_color": "#999999",
                    "border_width": 0,
                    "border_radius": 0,
                    "font_family": "Consolas",
                    "font_size": 14,
                    "font_bold": True
                },
                "action": {
                    "action_type": "none",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": False
            },
            {
                "id": "prog001",
                "comp_type": "progressbar",
                "name": "检测进度",
                "x": 100,
                "y": 150,
                "width": 400,
                "height": 30,
                "text": "",
                "parent_id": "cont001",
                "style": {
                    "background_color": "#16213e",
                    "text_color": "#ffffff",
                    "border_color": "#00ff00",
                    "border_width": 1,
                    "border_radius": 3,
                    "font_family": "Consolas",
                    "font_size": 10,
                    "font_bold": False
                },
                "action": {
                    "action_type": "none",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {
                    "value": 0,
                    "show_text": True,
                    "text_position": "center"
                },
                "value": 0,
                "show_text": True,
                "text_position": "center",
                "auto_progress": True,
                "duration": 5,
                "target_window_id": "event001"
            },
            {
                "id": "lbl002",
                "comp_type": "label",
                "name": "检测信息",
                "x": 100,
                "y": 210,
                "width": 400,
                "height": 100,
                "text": "CPU: 检测中...\n内存: 等待中...\n硬盘: 等待中...\n显卡: 等待中...",
                "parent_id": "cont001",
                "style": {
                    "background_color": "transparent",
                    "text_color": "#00ff00",
                    "border_color": "#999999",
                    "border_width": 0,
                    "border_radius": 0,
                    "font_family": "Consolas",
                    "font_size": 11,
                    "font_bold": False
                },
                "action": {
                    "action_type": "none",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "left",
                "word_wrap": True
            },
            {
                "id": "btn001",
                "comp_type": "button",
                "name": "跳过检测",
                "x": 200,
                "y": 310,
                "width": 200,
                "height": 40,
                "text": "跳过检测 (仅演示)",
                "parent_id": "cont001",
                "style": {
                    "background_color": "#e94560",
                    "text_color": "#ffffff",
                    "border_color": "#ff6b6b",
                    "border_width": 1,
                    "border_radius": 5,
                    "font_family": "Microsoft YaHei",
                    "font_size": 12,
                    "font_bold": True
                },
                "action": {
                    "action_type": "none",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "target_window_id": "event001",
                "branch_name": "跳过",
                "open_mode": "new_window",
                "is_default": False,
                "is_cancel": False
            },
            {
                "id": "cont002",
                "comp_type": "container",
                "name": "结果容器",
                "x": 50,
                "y": 30,
                "width": 400,
                "height": 240,
                "text": "检测结果",
                "parent_id": "",
                "style": {
                    "background_color": "#1a1a2e",
                    "text_color": "#00ff00",
                    "border_color": "#00ff00",
                    "border_width": 2,
                    "border_radius": 5,
                    "font_family": "Consolas",
                    "font_size": 10,
                    "font_bold": False
                },
                "action": {
                    "action_type": "none",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "children": [],
                "position_mode": "center",
                "layout": "none",
                "padding": 10,
                "spacing": 5
            },
            {
                "id": "lbl003",
                "comp_type": "label",
                "name": "结果信息",
                "x": 100,
                "y": 90,
                "width": 300,
                "height": 80,
                "text": "系统检测完成！\n所有硬件运行正常。\n\n(这只是一个演示程序)",
                "parent_id": "cont002",
                "style": {
                    "background_color": "transparent",
                    "text_color": "#00ff00",
                    "border_color": "#999999",
                    "border_width": 0,
                    "border_radius": 0,
                    "font_family": "Consolas",
                    "font_size": 12,
                    "font_bold": False
                },
                "action": {
                    "action_type": "none",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": True
            },
            {
                "id": "btn002",
                "comp_type": "button",
                "name": "关闭",
                "x": 150,
                "y": 200,
                "width": 200,
                "height": 40,
                "text": "关闭程序",
                "parent_id": "cont002",
                "style": {
                    "background_color": "#4CAF50",
                    "text_color": "#ffffff",
                    "border_color": "#45a049",
                    "border_width": 1,
                    "border_radius": 5,
                    "font_family": "Microsoft YaHei",
                    "font_size": 12,
                    "font_bold": True
                },
                "action": {
                    "action_type": "close_program",
                    "params": {},
                    "blockly_xml": "",
                    "python_code": ""
                },
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "target_window_id": "",
                "branch_name": "",
                "open_mode": "new_window",
                "is_default": False,
                "is_cancel": False
            }
        ],
        "main_window_id": "main001",
        "current_window_id": "main001"
    }
