"""电脑开机检测演示模板。

一个有趣的恶搞程序模板，模拟检测电脑是否开机的过程。
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
                "id": "ask001",
                "name": "询问窗口",
                "window_type": "main",
                "width": 420,
                "height": 200,
                "title": "系统检测",
                "components": [
                    "cont_ask",
                    "lbl_ask",
                    "btn_yes",
                    "btn_no"
                ],
                "trigger_button_id": None
            },
            {
                "id": "detect001",
                "name": "检测中",
                "window_type": "event",
                "width": 450,
                "height": 220,
                "title": "正在检测...",
                "components": [
                    "cont_detect",
                    "lbl_detect",
                    "prog_detect"
                ],
                "trigger_button_id": None
            },
            {
                "id": "result001",
                "name": "检测结果",
                "window_type": "event",
                "width": 450,
                "height": 220,
                "title": "检测结果",
                "components": [
                    "cont_result",
                    "lbl_result",
                    "lbl_detail",
                    "btn_close"
                ],
                "trigger_button_id": None
            }
        ],
        "components": [
            {
                "id": "cont_ask",
                "comp_type": "container",
                "name": "询问容器",
                "x": 10,
                "y": 10,
                "width": 390,
                "height": 170,
                "text": "系统检测程序",
                "parent_id": "",
                "style": {
                    "background_color": "#f5f5f5",
                    "text_color": "#333333",
                    "border_color": "#cccccc",
                    "border_width": 1,
                    "border_radius": 8,
                    "font_family": "Microsoft YaHei",
                    "font_size": 12,
                    "font_bold": True
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "children": [],
                "position_mode": "center",
                "layout": "none",
                "padding": 15,
                "spacing": 10
            },
            {
                "id": "lbl_ask",
                "comp_type": "label",
                "name": "询问文字",
                "x": 45,
                "y": 50,
                "width": 300,
                "height": 50,
                "text": "是否要开始检测电脑是否开机？",
                "parent_id": "cont_ask",
                "style": {
                    "background_color": "transparent",
                    "text_color": "#333333",
                    "border_color": "#cccccc",
                    "border_width": 0,
                    "border_radius": 0,
                    "font_family": "Microsoft YaHei",
                    "font_size": 14,
                    "font_bold": False
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": True
            },
            {
                "id": "btn_yes",
                "comp_type": "button",
                "name": "是按钮",
                "x": 70,
                "y": 115,
                "width": 100,
                "height": 35,
                "text": "是",
                "parent_id": "cont_ask",
                "style": {
                    "background_color": "#4CAF50",
                    "text_color": "#ffffff",
                    "border_color": "#45a049",
                    "border_width": 1,
                    "border_radius": 5,
                    "font_family": "Microsoft YaHei",
                    "font_size": 13,
                    "font_bold": True
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "target_window_id": "detect001",
                "branch_name": "开始检测",
                "open_mode": "new_window",
                "is_default": True,
                "is_cancel": False
            },
            {
                "id": "btn_no",
                "comp_type": "button",
                "name": "否按钮",
                "x": 220,
                "y": 115,
                "width": 100,
                "height": 35,
                "text": "否",
                "parent_id": "cont_ask",
                "style": {
                    "background_color": "#f44336",
                    "text_color": "#ffffff",
                    "border_color": "#d32f2f",
                    "border_width": 1,
                    "border_radius": 5,
                    "font_family": "Microsoft YaHei",
                    "font_size": 13,
                    "font_bold": True
                },
                "action": {"action_type": "close_program", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "target_window_id": "",
                "branch_name": "",
                "open_mode": "new_window",
                "is_default": False,
                "is_cancel": True
            },
            {
                "id": "cont_detect",
                "comp_type": "container",
                "name": "检测容器",
                "x": 25,
                "y": 15,
                "width": 400,
                "height": 180,
                "text": "正在检测...",
                "parent_id": "",
                "style": {
                    "background_color": "#f5f5f5",
                    "text_color": "#2196F3",
                    "border_color": "#2196F3",
                    "border_width": 1,
                    "border_radius": 8,
                    "font_family": "Microsoft YaHei",
                    "font_size": 12,
                    "font_bold": True
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "children": [],
                "position_mode": "center",
                "layout": "none",
                "padding": 15,
                "spacing": 10
            },
            {
                "id": "lbl_detect",
                "comp_type": "label",
                "name": "检测提示",
                "x": 50,
                "y": 55,
                "width": 300,
                "height": 40,
                "text": "正在检测电脑是否开机...",
                "parent_id": "cont_detect",
                "style": {
                    "background_color": "transparent",
                    "text_color": "#333333",
                    "border_color": "#cccccc",
                    "border_width": 0,
                    "border_radius": 0,
                    "font_family": "Microsoft YaHei",
                    "font_size": 14,
                    "font_bold": False
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": True
            },
            {
                "id": "prog_detect",
                "comp_type": "progressbar",
                "name": "检测进度条",
                "x": 50,
                "y": 105,
                "width": 300,
                "height": 25,
                "text": "",
                "parent_id": "cont_detect",
                "style": {
                    "background_color": "#e0e0e0",
                    "text_color": "#ffffff",
                    "border_color": "#cccccc",
                    "border_width": 1,
                    "border_radius": 3,
                    "font_family": "Microsoft YaHei",
                    "font_size": 11,
                    "font_bold": False
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "value": 0,
                "show_text": True,
                "text_position": "center",
                "auto_progress": True,
                "duration": 3,
                "target_window_id": "result001"
            },
            {
                "id": "cont_result",
                "comp_type": "container",
                "name": "结果容器",
                "x": 25,
                "y": 15,
                "width": 400,
                "height": 180,
                "text": "检测完成",
                "parent_id": "",
                "style": {
                    "background_color": "#f5f5f5",
                    "text_color": "#4CAF50",
                    "border_color": "#4CAF50",
                    "border_width": 2,
                    "border_radius": 8,
                    "font_family": "Microsoft YaHei",
                    "font_size": 12,
                    "font_bold": True
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "children": [],
                "position_mode": "center",
                "layout": "none",
                "padding": 15,
                "spacing": 10
            },
            {
                "id": "lbl_result",
                "comp_type": "label",
                "name": "结果标题",
                "x": 50,
                "y": 45,
                "width": 300,
                "height": 45,
                "text": "经过我们的判断，\n你的电脑确实已经开机了！",
                "parent_id": "cont_result",
                "style": {
                    "background_color": "transparent",
                    "text_color": "#4CAF50",
                    "border_color": "#4CAF50",
                    "border_width": 0,
                    "border_radius": 0,
                    "font_family": "Microsoft YaHei",
                    "font_size": 16,
                    "font_bold": True
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": True
            },
            {
                "id": "lbl_detail",
                "comp_type": "label",
                "name": "详情",
                "x": 50,
                "y": 95,
                "width": 300,
                "height": 30,
                "text": "检测耗时：3秒 | 置信度：100%",
                "parent_id": "cont_result",
                "style": {
                    "background_color": "transparent",
                    "text_color": "#666666",
                    "border_color": "#666666",
                    "border_width": 0,
                    "border_radius": 0,
                    "font_family": "Microsoft YaHei",
                    "font_size": 11,
                    "font_bold": False
                },
                "action": {"action_type": "none", "params": {}, "blockly_xml": "", "python_code": ""},
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": True
            },
            {
                "id": "btn_close",
                "comp_type": "button",
                "name": "关闭按钮",
                "x": 100,
                "y": 130,
                "width": 200,
                "height": 35,
                "text": "关闭程序",
                "parent_id": "cont_result",
                "style": {
                    "background_color": "#4CAF50",
                    "text_color": "#ffffff",
                    "border_color": "#45a049",
                    "border_width": 1,
                    "border_radius": 5,
                    "font_family": "Microsoft YaHei",
                    "font_size": 13,
                    "font_bold": True
                },
                "action": {"action_type": "close_program", "params": {}, "blockly_xml": "", "python_code": ""},
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
        "main_window_id": "ask001",
        "current_window_id": "ask001"
    }
