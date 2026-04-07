"""技术类控件模板系统。

本模块提供技术类控件的模板定义和生成功能。
技术类控件是一体整合控件，点击后可以自动生成多个相关联的控件。

## 技术类控件特点
1. 一体整合：多个控件组合成一个整体
2. 自动布局：自动设置控件的位置和大小
3. 预设联动：控件之间有预设的联动关系
4. 快速开发：一键生成复杂功能模块

## 使用方法
```python
from models.tech_components import TechComponentManager

# 获取技术类控件列表
templates = TechComponentManager.get_tech_templates()

# 生成技术类控件
components = TechComponentManager.create_tech_component("lottery", parent_id="cont_main")
```
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from models import ComponentModel, create_component


@dataclass
class TechComponentTemplate:
    """技术类控件模板。
    
    Attributes:
        template_id: 模板ID
        display_name: 显示名称
        description: 描述
        icon: 图标名称
        components: 组件定义列表
        layout_config: 布局配置
    """
    template_id: str
    display_name: str
    description: str
    icon: str
    components: List[Dict[str, Any]]
    layout_config: Dict[str, Any]


LOTTERY_TEMPLATE = TechComponentTemplate(
    template_id="lottery",
    display_name="抽奖系统",
    description="包含标题、轮播、按钮、结果标签的完整抽奖功能",
    icon="lottery",
    components=[
        {
            "comp_type": "label",
            "name": "抽奖标题",
            "text": "抽奖活动",
            "x": 0,
            "y": 0,
            "width": 200,
            "height": 35,
            "style": {
                "background_color": "transparent",
                "text_color": "#333333",
                "font_size": 18,
                "font_bold": True
            },
            "alignment": "center"
        },
        {
            "comp_type": "image_carousel",
            "name": "候选人轮播",
            "text": "",
            "x": 0,
            "y": 45,
            "width": 300,
            "height": 180,
            "style": {
                "background_color": "#e0e0e0",
                "border_color": "#999999",
                "border_radius": 5
            },
            "images": [],
            "image_labels": ["候选人1", "候选人2", "候选人3"],
            "current_index": 0
        },
        {
            "comp_type": "button",
            "name": "开始抽奖",
            "text": "开始抽奖",
            "x": 0,
            "y": 235,
            "width": 120,
            "height": 40,
            "style": {
                "background_color": "#4CAF50",
                "text_color": "#ffffff",
                "border_radius": 5,
                "font_size": 14,
                "font_bold": True
            },
            "action": {
                "action_type": "lottery_animation",
                "params": {
                    "target_component_id": ""
                }
            }
        },
        {
            "comp_type": "label",
            "name": "抽奖结果",
            "text": "等待抽奖...",
            "x": 0,
            "y": 285,
            "width": 300,
            "height": 30,
            "style": {
                "background_color": "transparent",
                "text_color": "#666666",
                "font_size": 14
            },
            "alignment": "center"
        }
    ],
    layout_config={
        "width": 300,
        "height": 320,
        "spacing": 10,
        "auto_position": True
    }
)


LOGIN_TEMPLATE = TechComponentTemplate(
    template_id="login",
    display_name="登录表单",
    description="包含用户名、密码输入框和登录按钮的完整登录功能",
    icon="login",
    components=[
        {
            "comp_type": "label",
            "name": "登录标题",
            "text": "用户登录",
            "x": 0,
            "y": 0,
            "width": 200,
            "height": 35,
            "style": {
                "background_color": "transparent",
                "text_color": "#333333",
                "font_size": 18,
                "font_bold": True
            },
            "alignment": "center"
        },
        {
            "comp_type": "label",
            "name": "用户名标签",
            "text": "用户名：",
            "x": 0,
            "y": 50,
            "width": 80,
            "height": 30,
            "style": {
                "background_color": "transparent",
                "text_color": "#333333",
                "font_size": 12
            },
            "alignment": "right"
        },
        {
            "comp_type": "input",
            "name": "用户名输入框",
            "text": "",
            "x": 90,
            "y": 50,
            "width": 200,
            "height": 30,
            "style": {
                "border_color": "#cccccc",
                "border_radius": 3
            },
            "placeholder": "请输入用户名",
            "max_length": 50
        },
        {
            "comp_type": "label",
            "name": "密码标签",
            "text": "密码：",
            "x": 0,
            "y": 90,
            "width": 80,
            "height": 30,
            "style": {
                "background_color": "transparent",
                "text_color": "#333333",
                "font_size": 12
            },
            "alignment": "right"
        },
        {
            "comp_type": "input",
            "name": "密码输入框",
            "text": "",
            "x": 90,
            "y": 90,
            "width": 200,
            "height": 30,
            "style": {
                "border_color": "#cccccc",
                "border_radius": 3
            },
            "placeholder": "请输入密码",
            "is_password": True,
            "max_length": 50
        },
        {
            "comp_type": "button",
            "name": "登录按钮",
            "text": "登录",
            "x": 90,
            "y": 140,
            "width": 200,
            "height": 40,
            "style": {
                "background_color": "#1a56db",
                "text_color": "#ffffff",
                "border_radius": 5,
                "font_size": 14,
                "font_bold": True
            },
            "action": {
                "action_type": "execute_python",
                "params": {}
            }
        }
    ],
    layout_config={
        "width": 290,
        "height": 190,
        "spacing": 10,
        "auto_position": True
    }
)


FORM_TEMPLATE = TechComponentTemplate(
    template_id="form",
    display_name="表单组",
    description="包含标签和输入框的标准表单行",
    icon="form",
    components=[
        {
            "comp_type": "label",
            "name": "字段标签",
            "text": "字段名：",
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 30,
            "style": {
                "background_color": "transparent",
                "text_color": "#333333",
                "font_size": 12
            },
            "alignment": "right"
        },
        {
            "comp_type": "input",
            "name": "字段输入框",
            "text": "",
            "x": 110,
            "y": 0,
            "width": 200,
            "height": 30,
            "style": {
                "border_color": "#cccccc",
                "border_radius": 3
            },
            "placeholder": "请输入内容",
            "max_length": 100
        }
    ],
    layout_config={
        "width": 310,
        "height": 30,
        "spacing": 10,
        "auto_position": True
    }
)


PROGRESS_PANEL_TEMPLATE = TechComponentTemplate(
    template_id="progress_panel",
    display_name="进度面板",
    description="包含标题、进度条和状态标签的进度显示面板",
    icon="progress",
    components=[
        {
            "comp_type": "label",
            "name": "进度标题",
            "text": "处理进度",
            "x": 0,
            "y": 0,
            "width": 200,
            "height": 25,
            "style": {
                "background_color": "transparent",
                "text_color": "#333333",
                "font_size": 14,
                "font_bold": True
            },
            "alignment": "left"
        },
        {
            "comp_type": "progressbar",
            "name": "进度条",
            "text": "",
            "x": 0,
            "y": 30,
            "width": 300,
            "height": 25,
            "style": {
                "border_radius": 3
            },
            "value": 0,
            "show_text": True
        },
        {
            "comp_type": "label",
            "name": "状态标签",
            "text": "准备就绪",
            "x": 0,
            "y": 60,
            "width": 300,
            "height": 20,
            "style": {
                "background_color": "transparent",
                "text_color": "#666666",
                "font_size": 11
            },
            "alignment": "center"
        }
    ],
    layout_config={
        "width": 300,
        "height": 80,
        "spacing": 5,
        "auto_position": True
    }
)


TECH_TEMPLATES: Dict[str, TechComponentTemplate] = {
    "lottery": LOTTERY_TEMPLATE,
    "login": LOGIN_TEMPLATE,
    "form": FORM_TEMPLATE,
    "progress_panel": PROGRESS_PANEL_TEMPLATE,
}


class TechComponentManager:
    """技术类控件管理器。
    
    提供技术类控件的模板管理和生成功能。
    """
    
    @staticmethod
    def get_tech_templates() -> Dict[str, TechComponentTemplate]:
        """获取所有技术类控件模板。
        
        Returns:
            技术类控件模板字典
        """
        return TECH_TEMPLATES.copy()
    
    @staticmethod
    def get_template(template_id: str) -> Optional[TechComponentTemplate]:
        """获取指定的技术类控件模板。
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板对象，如果不存在则返回None
        """
        return TECH_TEMPLATES.get(template_id)
    
    @staticmethod
    def create_tech_component(
        template_id: str,
        parent_id: str = "",
        offset_x: int = 0,
        offset_y: int = 0
    ) -> List[ComponentModel]:
        """根据模板创建技术类控件组件列表。
        
        Args:
            template_id: 模板ID
            parent_id: 父组件ID
            offset_x: X轴偏移量
            offset_y: Y轴偏移量
            
        Returns:
            创建的组件列表
            
        Raises:
            ValueError: 未知的模板ID
        """
        template = TECH_TEMPLATES.get(template_id)
        if not template:
            raise ValueError(f"未知的模板ID: {template_id}")
        
        components = []
        component_ids = []
        
        for comp_def in template.components:
            comp_type = comp_def["comp_type"]
            
            comp_data = comp_def.copy()
            comp_data.pop("comp_type", None)
            
            comp_data["x"] = comp_def.get("x", 0) + offset_x
            comp_data["y"] = comp_def.get("y", 0) + offset_y
            
            if parent_id:
                comp_data["parent_id"] = parent_id
            
            style_dict = comp_data.pop("style", None)
            action_dict = comp_data.pop("action", None)
            alignment = comp_data.pop("alignment", None)
            word_wrap = comp_data.pop("word_wrap", None)
            auto_size = comp_data.pop("auto_size", None)
            placeholder = comp_data.pop("placeholder", None)
            max_length = comp_data.pop("max_length", None)
            is_password = comp_data.pop("is_password", None)
            images = comp_data.pop("images", None)
            image_labels = comp_data.pop("image_labels", None)
            current_index = comp_data.pop("current_index", None)
            value = comp_data.pop("value", None)
            show_text = comp_data.pop("show_text", None)
            
            comp = create_component(comp_type, **comp_data)
            
            if style_dict:
                from models.base import StyleConfig
                style_config = StyleConfig.from_dict(style_dict)
                comp._style = style_config
            
            if action_dict:
                from models.base import ActionConfig
                action_config = ActionConfig(**action_dict)
                comp._action = action_config
            
            if alignment and hasattr(comp, 'alignment'):
                comp.alignment = alignment
            
            if word_wrap is not None and hasattr(comp, 'word_wrap'):
                comp.word_wrap = word_wrap
            
            if auto_size is not None and hasattr(comp, 'auto_size'):
                comp.auto_size = auto_size
            
            if placeholder is not None and hasattr(comp, 'placeholder'):
                comp.placeholder = placeholder
            
            if max_length is not None and hasattr(comp, 'max_length'):
                comp.max_length = max_length
            
            if is_password is not None and hasattr(comp, 'is_password'):
                comp.is_password = is_password
            
            if images is not None and hasattr(comp, 'images'):
                comp.images = images
            
            if image_labels is not None and hasattr(comp, 'image_labels'):
                comp.image_labels = image_labels
            
            if current_index is not None and hasattr(comp, 'current_index'):
                comp.current_index = current_index
            
            if value is not None and hasattr(comp, 'value'):
                comp.value = value
            
            if show_text is not None and hasattr(comp, 'show_text'):
                comp.show_text = show_text
            
            components.append(comp)
            component_ids.append(comp.id)
        
        if template_id == "lottery":
            for comp in components:
                if comp.name == "开始抽奖":
                    carousel_id = None
                    result_label_id = None
                    for c in components:
                        if c.name == "候选人轮播":
                            carousel_id = c.id
                        elif c.name == "抽奖结果":
                            result_label_id = c.id
                    
                    if carousel_id:
                        comp._action.params["target_component_id"] = carousel_id
        
        return components
    
    @staticmethod
    def get_template_info(template_id: str) -> Dict[str, Any]:
        """获取模板信息。
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板信息字典
        """
        template = TECH_TEMPLATES.get(template_id)
        if not template:
            return {}
        
        return {
            "template_id": template.template_id,
            "display_name": template.display_name,
            "description": template.description,
            "icon": template.icon,
            "component_count": len(template.components),
            "layout_config": template.layout_config
        }
    
    @staticmethod
    def register_template(template: TechComponentTemplate) -> None:
        """注册新的技术类控件模板。
        
        Args:
            template: 技术类控件模板对象
        """
        TECH_TEMPLATES[template.template_id] = template
    
    @staticmethod
    def get_available_templates() -> List[str]:
        """获取所有可用的模板ID列表。
        
        Returns:
            模板ID列表
        """
        return list(TECH_TEMPLATES.keys())
