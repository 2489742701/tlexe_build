"""示例生成器 - 生成示例项目文件。

本模块生成示例项目文件，确保示例与程序功能一致。

【使用方法】
python generate_samples.py
"""

import json
import os
from typing import Dict, Any, List

def create_style(background_color: str = "#f5f5f5",
                 text_color: str = "#333333",
                 border_color: str = "#cccccc",
                 border_width: int = 1,
                 border_radius: int = 5,
                 font_family: str = "Microsoft YaHei",
                 font_size: int = 12,
                 font_bold: bool = False) -> Dict[str, Any]:
    """创建样式配置。"""
    return {
        "background_color": background_color,
        "text_color": text_color,
        "border_color": border_color,
        "border_width": border_width,
        "border_radius": border_radius,
        "font_family": font_family,
        "font_size": font_size,
        "font_bold": font_bold
    }

def create_action(action_type: str = "none", params: Dict = None) -> Dict[str, Any]:
    """创建动作配置。"""
    return {
        "action_type": action_type,
        "params": params or {},
        "blockly_xml": "",
        "python_code": ""
    }

def create_boot_detection_sample() -> Dict[str, Any]:
    """创建电脑开机检测示例。
    
    流程：
    1. 询问窗口：询问是否检测
    2. 检测中窗口：显示进度条
    3. 结果窗口：显示检测结果
    """
    return {
        "name": "电脑开机检测",
        "windows": [
            {
                "id": "ask001",
                "name": "询问窗口",
                "window_type": "main",
                "width": 420,
                "height": 200,
                "title": "系统检测",
                "components": ["cont_ask", "lbl_ask", "btn_yes", "btn_no"],
                "trigger_button_id": None
            },
            {
                "id": "detect001",
                "name": "检测中",
                "window_type": "event",
                "width": 450,
                "height": 220,
                "title": "正在检测...",
                "components": ["cont_detect", "lbl_detect", "prog_detect"],
                "trigger_button_id": None
            },
            {
                "id": "result001",
                "name": "检测结果",
                "window_type": "event",
                "width": 450,
                "height": 220,
                "title": "检测结果",
                "components": ["cont_result", "lbl_result", "lbl_detail", "btn_close"],
                "trigger_button_id": None
            }
        ],
        "components": [
            {
                "id": "cont_ask",
                "comp_type": "container",
                "name": "询问容器",
                "x": 10, "y": 10,
                "width": 390, "height": 170,
                "text": "系统检测程序",
                "parent_id": "",
                "style": create_style(
                    background_color="#f5f5f5",
                    text_color="#333333",
                    border_color="#cccccc",
                    border_width=1,
                    border_radius=8,
                    font_bold=True
                ),
                "action": create_action(),
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
                "x": 45, "y": 50,
                "width": 300, "height": 50,
                "text": "是否要开始检测电脑是否开机？",
                "parent_id": "cont_ask",
                "style": create_style(
                    background_color="transparent",
                    border_width=0,
                    font_size=14
                ),
                "action": create_action(),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": True,
                "auto_size": False
            },
            {
                "id": "btn_yes",
                "comp_type": "button",
                "name": "是按钮",
                "x": 70, "y": 115,
                "width": 100, "height": 35,
                "text": "是",
                "parent_id": "cont_ask",
                "style": create_style(
                    background_color="#4CAF50",
                    text_color="#ffffff",
                    border_color="#45a049",
                    border_radius=5,
                    font_size=13,
                    font_bold=True
                ),
                "action": create_action(),
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
                "x": 220, "y": 115,
                "width": 100, "height": 35,
                "text": "否",
                "parent_id": "cont_ask",
                "style": create_style(
                    background_color="#f44336",
                    text_color="#ffffff",
                    border_color="#d32f2f",
                    border_radius=5,
                    font_size=13,
                    font_bold=True
                ),
                "action": create_action("close_program"),
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
                "x": 25, "y": 15,
                "width": 400, "height": 180,
                "text": "正在检测...",
                "parent_id": "",
                "style": create_style(
                    background_color="#f5f5f5",
                    text_color="#2196F3",
                    border_color="#2196F3",
                    border_width=1,
                    border_radius=8,
                    font_bold=True
                ),
                "action": create_action(),
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
                "x": 50, "y": 55,
                "width": 300, "height": 40,
                "text": "正在检测电脑是否开机...",
                "parent_id": "cont_detect",
                "style": create_style(
                    background_color="transparent",
                    border_width=0,
                    font_size=14
                ),
                "action": create_action(),
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
                "x": 50, "y": 105,
                "width": 300, "height": 25,
                "text": "",
                "parent_id": "cont_detect",
                "style": create_style(
                    background_color="#e0e0e0",
                    text_color="#ffffff",
                    border_color="#cccccc",
                    border_width=1,
                    border_radius=3,
                    font_size=11
                ),
                "action": create_action(),
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
                "x": 25, "y": 15,
                "width": 400, "height": 180,
                "text": "检测完成",
                "parent_id": "",
                "style": create_style(
                    background_color="#f5f5f5",
                    text_color="#4CAF50",
                    border_color="#4CAF50",
                    border_width=2,
                    border_radius=8,
                    font_bold=True
                ),
                "action": create_action(),
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
                "x": 50, "y": 45,
                "width": 300, "height": 45,
                "text": "经过我们的判断，\n你的电脑确实已经开机了！",
                "parent_id": "cont_result",
                "style": create_style(
                    background_color="transparent",
                    text_color="#4CAF50",
                    border_color="#4CAF50",
                    border_width=0,
                    font_size=16,
                    font_bold=True
                ),
                "action": create_action(),
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
                "x": 50, "y": 95,
                "width": 300, "height": 30,
                "text": "检测耗时：3秒 | 置信度：100%",
                "parent_id": "cont_result",
                "style": create_style(
                    background_color="transparent",
                    text_color="#666666",
                    border_color="#666666",
                    border_width=0,
                    font_size=11
                ),
                "action": create_action(),
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
                "x": 100, "y": 130,
                "width": 200, "height": 35,
                "text": "关闭程序",
                "parent_id": "cont_result",
                "style": create_style(
                    background_color="#4CAF50",
                    text_color="#ffffff",
                    border_color="#45a049",
                    border_radius=5,
                    font_size=13,
                    font_bold=True
                ),
                "action": create_action("close_program"),
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

def create_galgame_sample() -> Dict[str, Any]:
    """创建 Galgame 示例。"""
    return {
        "name": "Galgame示例",
        "windows": [
            {
                "id": "main001",
                "name": "主菜单",
                "window_type": "main",
                "width": 800,
                "height": 600,
                "title": "Galgame示例",
                "components": ["cont_main", "lbl_title", "btn_start", "btn_settings"],
                "trigger_button_id": None
            },
            {
                "id": "game001",
                "name": "游戏内容",
                "window_type": "event",
                "width": 800,
                "height": 600,
                "title": "游戏内容",
                "components": ["lbl_game", "btn_back"],
                "trigger_button_id": None
            },
            {
                "id": "settings001",
                "name": "设置",
                "window_type": "event",
                "width": 400,
                "height": 300,
                "title": "设置",
                "components": ["lbl_player", "inp_player", "btn_save"],
                "trigger_button_id": None
            }
        ],
        "components": [
            {
                "id": "cont_main",
                "comp_type": "container",
                "name": "主容器",
                "x": 150, "y": 100,
                "width": 500, "height": 400,
                "text": "游戏主菜单",
                "parent_id": "",
                "style": create_style(border_radius=5),
                "action": create_action(),
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
                "id": "lbl_title",
                "comp_type": "label",
                "name": "标题",
                "x": 250, "y": 130,
                "width": 300, "height": 40,
                "text": "欢迎来到Galgame示例",
                "parent_id": "cont_main",
                "style": create_style(
                    background_color="transparent",
                    border_width=0,
                    font_size=18,
                    font_bold=True
                ),
                "action": create_action(),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": False
            },
            {
                "id": "btn_start",
                "comp_type": "button",
                "name": "开始按钮",
                "x": 300, "y": 200,
                "width": 200, "height": 50,
                "text": "开始游戏",
                "parent_id": "cont_main",
                "style": create_style(
                    background_color="#4CAF50",
                    text_color="#ffffff",
                    border_color="#45a049",
                    border_radius=8,
                    font_size=14,
                    font_bold=True
                ),
                "action": create_action(),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "target_window_id": "game001",
                "branch_name": "开始游戏",
                "open_mode": "new_window",
                "is_default": False,
                "is_cancel": False
            },
            {
                "id": "btn_settings",
                "comp_type": "button",
                "name": "设置按钮",
                "x": 300, "y": 280,
                "width": 200, "height": 50,
                "text": "设置",
                "parent_id": "cont_main",
                "style": create_style(
                    background_color="#2196F3",
                    text_color="#ffffff",
                    border_color="#1976D2",
                    border_radius=8,
                    font_size=14,
                    font_bold=True
                ),
                "action": create_action(),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "target_window_id": "settings001",
                "branch_name": "设置",
                "open_mode": "new_window",
                "is_default": False,
                "is_cancel": False
            },
            {
                "id": "lbl_game",
                "comp_type": "label",
                "name": "游戏内容",
                "x": 200, "y": 250,
                "width": 400, "height": 100,
                "text": "这里是游戏内容区域\n点击返回按钮回到主菜单",
                "parent_id": "",
                "style": create_style(
                    background_color="transparent",
                    text_color="#666666",
                    border_width=0,
                    font_size=14
                ),
                "action": create_action(),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "center",
                "word_wrap": True
            },
            {
                "id": "btn_back",
                "comp_type": "button",
                "name": "返回按钮",
                "x": 300, "y": 400,
                "width": 200, "height": 50,
                "text": "返回主菜单",
                "parent_id": "",
                "style": create_style(
                    background_color="#f44336",
                    text_color="#ffffff",
                    border_color="#d32f2f",
                    border_radius=8,
                    font_size=14,
                    font_bold=True
                ),
                "action": create_action("close_window"),
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
                "id": "lbl_player",
                "comp_type": "label",
                "name": "玩家名称标签",
                "x": 50, "y": 80,
                "width": 100, "height": 30,
                "text": "玩家名称:",
                "parent_id": "",
                "style": create_style(
                    background_color="transparent",
                    border_width=0
                ),
                "action": create_action(),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "alignment": "right",
                "word_wrap": False
            },
            {
                "id": "inp_player",
                "comp_type": "input",
                "name": "玩家名称输入",
                "x": 160, "y": 80,
                "width": 180, "height": 30,
                "text": "",
                "parent_id": "",
                "style": create_style(
                    background_color="#ffffff",
                    border_radius=4
                ),
                "action": create_action(),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "placeholder": "请输入玩家名称",
                "is_password": False,
                "is_multiline": False,
                "max_length": 20
            },
            {
                "id": "btn_save",
                "comp_type": "button",
                "name": "保存设置",
                "x": 100, "y": 150,
                "width": 200, "height": 40,
                "text": "保存并返回",
                "parent_id": "",
                "style": create_style(
                    background_color="#4CAF50",
                    text_color="#ffffff",
                    border_color="#45a049",
                    border_radius=8,
                    font_bold=True
                ),
                "action": create_action("show_message", {"message": "设置已保存!"}),
                "visible": True,
                "enabled": True,
                "custom_props": {},
                "target_window_id": "",
                "branch_name": "",
                "open_mode": "new_window",
                "is_default": True,
                "is_cancel": False
            }
        ],
        "main_window_id": "main001",
        "current_window_id": "main001"
    }

def create_lottery_sample_images() -> Dict[str, Any]:
    """创建图片轮播抽奖示例（年会抽奖风格）。
    
    使用 TechComponentManager 工厂组件生成，确保：
    1. 组件ID由工厂自动生成，保证唯一性
    2. 联动关系由工厂自动配置，保证引用正确
    3. action.params.target_component_id 指向正确的轮播组件ID
    """
    from models.registry_init import register_all_components
    from models.tech_components import TechComponentManager
    from models.components import ContainerModel, create_component
    
    register_all_components()
    
    container = create_component('container', name='主容器', x=10, y=10, width=480, height=400, text='')
    container._style = StyleConfig(
        background_color="#f5f5f5", text_color="#333333",
        border_color="#cccccc", border_width=1, border_radius=8
    )
    
    components, linkages = TechComponentManager.create_tech_component(
        'lottery', parent_id=container.id
    )
    
    title_comp = None
    carousel_comp = None
    button_comp = None
    result_comp = None
    for c in components:
        if c.name == "抽奖标题":
            title_comp = c
            title_comp.text = "年会抽奖"
            title_comp.x = 150
            title_comp.y = 40
            title_comp.width = 200
            title_comp.height = 35
            title_comp.alignment = "center"
            title_comp._style = StyleConfig(
                background_color="transparent", text_color="#333333",
                font_size=18, font_bold=True
            )
        elif c.name == "奖品轮播":
            carousel_comp = c
            carousel_comp.x = 90
            carousel_comp.y = 90
            carousel_comp.width = 300
            carousel_comp.height = 180
            carousel_comp.images = ["张三.png", "李四.png", "王五.png", "赵六.png", "钱七.png"]
            carousel_comp.image_labels = ["张三", "李四", "王五", "赵六", "钱七"]
            carousel_comp._style = StyleConfig(
                background_color="#e0e0e0", border_color="#999999", border_radius=5
            )
        elif c.name == "开始抽奖":
            button_comp = c
            button_comp.x = 175
            button_comp.y = 290
            button_comp.width = 130
            button_comp.height = 36
            button_comp._style = StyleConfig(
                background_color="#4CAF50", text_color="#ffffff",
                border_radius=5, font_size=14, font_bold=True
            )
            if button_comp._action and button_comp._action.params:
                button_comp._action.params["action_params"] = {"duration_ms": 2000}
        elif c.name == "抽奖结果":
            result_comp = c
            result_comp.text = "点击按钮开始抽奖"
            result_comp.x = 50
            result_comp.y = 340
            result_comp.width = 400
            result_comp.height = 40
            result_comp.alignment = "center"
            result_comp._style = StyleConfig(
                background_color="transparent", text_color="#4CAF50",
                font_size=18, font_bold=True
            )
    
    all_components = [container] + components
    component_ids = [c.id for c in all_components]
    
    window_id = f"win_{container.id[:8]}"
    
    return {
        "name": "年会抽奖",
        "windows": [
            {
                "id": window_id,
                "name": "抽奖主界面",
                "window_type": "main",
                "width": 500,
                "height": 420,
                "title": "年会抽奖",
                "components": component_ids
            }
        ],
        "components": [c.to_dict() for c in all_components],
        "linkages": linkages,
        "main_window_id": window_id,
        "current_window_id": window_id
    }

def create_lottery_sample_text() -> Dict[str, Any]:
    """创建文字抽奖示例。
    
    使用 TechComponentManager 工厂组件生成，文字抽奖使用 label 组件
    替代 image_carousel 进行文字轮播动画。
    """
    from models.registry_init import register_all_components
    from models.tech_components import TechComponentManager
    from models.components import ContainerModel, LabelModel, ButtonModel, create_component
    from models.schemas import ActionConfig
    
    register_all_components()
    
    container = create_component('container', name='主容器', x=10, y=10, width=480, height=400, text='')
    container._style = StyleConfig(
        background_color="#f5f5f5", text_color="#333333",
        border_color="#cccccc", border_width=1, border_radius=8
    )
    
    title_label = create_component('label', name='抽奖标题', x=150, y=40, width=200, height=35, text='文字抽奖')
    title_label.parent_id = container.id
    title_label.alignment = "center"
    title_label._style = StyleConfig(
        background_color="transparent", text_color="#333333",
        font_size=18, font_bold=True
    )
    
    text_label = create_component('label', name='文字轮播', x=90, y=90, width=300, height=180, text='张三')
    text_label.parent_id = container.id
    text_label.alignment = "center"
    text_label._style = StyleConfig(
        background_color="#e0e0e0", text_color="#333333",
        border_color="#999999", border_radius=5,
        font_size=24, font_bold=True
    )
    
    draw_button = create_component('button', name='开始抽奖', x=175, y=290, width=130, height=36, text='开始抽奖')
    draw_button.parent_id = container.id
    draw_button._action = ActionConfig(
        action_type="lottery_animation",
        params={
            "target_component_id": text_label.id,
            "action_params": {"duration_ms": 2000, "candidates": ["张三", "李四", "王五", "赵六", "钱七"]}
        }
    )
    draw_button._style = StyleConfig(
        background_color="#4CAF50", text_color="#ffffff",
        border_radius=5, font_size=14, font_bold=True
    )
    
    result_label = create_component('label', name='抽奖结果', x=50, y=340, width=400, height=40, text='点击按钮开始抽奖')
    result_label.parent_id = container.id
    result_label.alignment = "center"
    result_label._style = StyleConfig(
        background_color="transparent", text_color="#4CAF50",
        font_size=18, font_bold=True
    )
    
    linkages = [
        {
            "source_component": text_label.id,
            "source_event": "lottery_finished",
            "target_component": result_label.id,
            "target_action": "set_text",
            "params": {"text_template": "恭喜中奖: {winner}"}
        }
    ]
    
    all_components = [container, title_label, text_label, draw_button, result_label]
    component_ids = [c.id for c in all_components]
    
    window_id = f"win_{container.id[:8]}"
    
    return {
        "name": "文字抽奖",
        "windows": [
            {
                "id": window_id,
                "name": "抽奖主界面",
                "window_type": "main",
                "width": 500,
                "height": 420,
                "title": "文字抽奖",
                "components": component_ids
            }
        ],
        "components": [c.to_dict() for c in all_components],
        "linkages": linkages,
        "main_window_id": window_id,
        "current_window_id": window_id
    }

from models.schemas import StyleConfig

def save_sample(data: Dict[str, Any], filename: str):
    """保存示例到文件。"""
    samples_dir = os.path.join(os.path.dirname(__file__), "samples")
    os.makedirs(samples_dir, exist_ok=True)
    
    filepath = os.path.join(samples_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已生成: {filepath}")

def main():
    """主函数。"""
    print("生成示例项目...")
    
    boot_detection = create_boot_detection_sample()
    save_sample(boot_detection, "系统检测示例.itexe")
    
    galgame = create_galgame_sample()
    save_sample(galgame, "galgame示例.itexe")
    
    lottery_images = create_lottery_sample_images()
    save_sample(lottery_images, "年会抽奖示例.itexe")
    
    lottery_text = create_lottery_sample_text()
    save_sample(lottery_text, "文字抽奖示例.itexe")
    
    print("\n示例生成完成！")
    print("注意：抽奖示例已改用 TechComponentManager 工厂组件生成，")
    print("确保组件ID和联动关系正确。")

if __name__ == "__main__":
    main()
