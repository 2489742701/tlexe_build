"""Tlexe 项目构建器 - 使用 Python 代码构建 .itexe 项目

【使用方法】
1. 在 Python 脚本中定义项目结构
2. 调用 build() 函数生成 .itexe 文件

【示例】
    from itexe_builder import *
    
    project("我的抽奖项目",
        window("主窗口", 600, 400,
            container("主容器", x=20, y=20, w=560, h=360),
            label("标题", x=180, y=40, w=200, h=40, text="抽奖系统"),
            button("开始抽奖", x=220, y=120, w=160, h=50,
                   action("lottery_animation", target="carousel_1")),
            image_carousel("轮播", x=180, y=190, w=240, h=120,
                         images=["1.png", "2.png", "3.png"],
                         labels=["张三", "李四", "王五"]),
            label("结果", x=180, y=320, w=240, h=30)
        ),
        linkage("轮播完成", source="carousel_1", event="lottery_finished",
                target="结果", action="set_text", 
                template="中奖者: {winner}")
    ).save("抽奖.itexe")
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

def generate_id(prefix: str = "") -> str:
    """生成唯一ID"""
    short_id = uuid.uuid4().hex[:8]
    return f"{prefix}{short_id}" if prefix else short_id

# ============================================================================
# 样式构建函数
# ============================================================================

def style(background_color: str = "#f5f5f5",
          text_color: str = "#333333",
          border_color: str = "#cccccc",
          border_width: int = 1,
          border_radius: int = 5,
          font_family: str = "Microsoft YaHei",
          font_size: int = 12,
          font_bold: bool = False) -> Dict[str, Any]:
    """创建样式配置"""
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

# ============================================================================
# 动作构建函数
# ============================================================================

def action(action_type: str = "none",
           target_window_id: str = "",
           target_component_id: str = "",
           text_template: str = "") -> Dict[str, Any]:
    """创建动作配置"""
    params = {}
    if target_window_id:
        params["target_window_id"] = target_window_id
    if target_component_id:
        params["target_component_id"] = target_component_id
    if text_template:
        params["text_template"] = text_template
    return {
        "action_type": action_type,
        "params": params,
        "blockly_xml": "",
        "python_code": ""
    }

# ============================================================================
# 组件构建函数
# ============================================================================

def container(name: str, x: int = 0, y: int = 0, w: int = 400, h: int = 300,
             text: str = "", parent_id: str = "",
             bg: str = "#f5f5f5", radius: int = 5) -> Dict[str, Any]:
    """创建容器组件"""
    return {
        "id": generate_id("cont_"),
        "comp_type": "container",
        "name": name,
        "x": x, "y": y, "width": w, "height": h,
        "text": text,
        "parent_id": parent_id,
        "style": style(background_color=bg, border_radius=radius),
        "action": action(),
        "visible": True,
        "enabled": True,
        "custom_props": {},
        "children": [],
        "position_mode": "center",
        "layout": "none",
        "padding": 15,
        "spacing": 10
    }

def label(name: str, x: int = 0, y: int = 0, w: int = 100, h: int = 30,
          text: str = "标签", parent_id: str = "",
          color: str = "#333333", size: int = 12, bold: bool = False,
          bg: str = "transparent") -> Dict[str, Any]:
    """创建标签组件"""
    return {
        "id": generate_id("lbl_"),
        "comp_type": "label",
        "name": name,
        "x": x, "y": y, "width": w, "height": h,
        "text": text,
        "parent_id": parent_id,
        "style": style(background_color=bg, text_color=color, 
                       font_size=size, font_bold=bold),
        "action": action(),
        "visible": True,
        "enabled": True,
        "custom_props": {}
    }

def button(name: str, x: int = 0, y: int = 0, w: int = 100, h: int = 40,
           text: str = "按钮", parent_id: str = "",
           action_type: str = "none", target: str = "",
           target_window: str = "") -> Dict[str, Any]:
    """创建按钮组件"""
    return {
        "id": generate_id("btn_"),
        "comp_type": "button",
        "name": name,
        "x": x, "y": y, "width": w, "height": h,
        "text": text,
        "parent_id": parent_id,
        "style": style(background_color="#4CAF50", text_color="#ffffff",
                       border_radius=5, font_size=12),
        "action": action(action_type, target_component_id=target,
                        target_window_id=target_window),
        "visible": True,
        "enabled": True,
        "custom_props": {}
    }

def input(name: str, x: int = 0, y: int = 0, w: int = 150, h: int = 30,
          placeholder: str = "", parent_id: str = "") -> Dict[str, Any]:
    """创建输入框组件"""
    return {
        "id": generate_id("inp_"),
        "comp_type": "input",
        "name": name,
        "x": x, "y": y, "width": w, "height": h,
        "text": "",
        "placeholder": placeholder,
        "parent_id": parent_id,
        "style": style(border_radius=3),
        "action": action(),
        "visible": True,
        "enabled": True,
        "custom_props": {}
    }

def image_carousel(name: str, x: int = 0, y: int = 0, w: int = 300, h: int = 150,
                  images: List[str] = None, labels: List[str] = None,
                  parent_id: str = "", auto_start: bool = False) -> Dict[str, Any]:
    """创建图片轮播组件（抽奖用）"""
    if images is None:
        images = []
    if labels is None:
        labels = []
    return {
        "id": generate_id("carousel_"),
        "comp_type": "image_carousel",
        "name": name,
        "x": x, "y": y, "width": w, "height": h,
        "images": images,
        "image_labels": labels,
        "parent_id": parent_id,
        "style": style(border_radius=5),
        "action": action(),
        "visible": True,
        "enabled": True,
        "auto_start": auto_start,
        "interval": 100,
        "custom_props": {}
    }

def progressbar(name: str, x: int = 0, y: int = 0, w: int = 200, h: int = 30,
               value: int = 0, show_text: bool = True,
               parent_id: str = "", auto_progress: bool = False,
               duration: int = 3, target_window: str = "") -> Dict[str, Any]:
    """创建进度条组件"""
    return {
        "id": generate_id("prog_"),
        "comp_type": "progressbar",
        "name": name,
        "x": x, "y": y, "width": w, "height": h,
        "value": value,
        "show_text": show_text,
        "parent_id": parent_id,
        "style": style(),
        "action": action("open_window", target_window_id=target_window),
        "visible": True,
        "enabled": True,
        "auto_progress": auto_progress,
        "duration": duration,
        "custom_props": {}
    }

# ============================================================================
# 窗口构建函数
# ============================================================================

def window(name: str, w: int = 800, h: int = 600, 
          window_type: str = "main", title: str = "", 
          frameless: bool = False, window_color: str = "",
          *components) -> Dict[str, Any]:
    """创建窗口
    
    Args:
        name: 窗口名称
        w: 宽度
        h: 高度
        window_type: "main" 或 "event"
        title: 窗口标题
        frameless: 是否无边框（无顶栏）
        window_color: 窗口背景色，如 "#1a1a2e"
    """
    win_id = generate_id("win_")
    result = {
        "id": win_id,
        "name": name,
        "window_type": window_type,
        "width": w,
        "height": h,
        "title": title or name,
        "components": [c["id"] for c in components],
        "trigger_button_id": None
    }
    if frameless:
        result["frameless"] = True
    if window_color:
        result["window_color"] = window_color
    return result

# ============================================================================
# 联动构建函数
# ============================================================================

def linkage(name: str, source: str, event: str, 
            target: str, action: str, template: str = "") -> Dict[str, Any]:
    """创建联动配置"""
    return {
        "source_component": source,
        "source_event": event,
        "target_component": target,
        "target_action": action,
        "params": {"text_template": template} if template else {}
    }

# ============================================================================
# 项目构建器
# ============================================================================

class ItexeBuilder:
    """Tlexe 项目构建器"""
    
    def __init__(self, name: str):
        self._name = name
        self._windows: List[Dict[str, Any]] = []
        self._components: List[Dict[str, Any]] = []
        self._linkages: List[Dict[str, Any]] = []
        self._main_window_id: Optional[str] = None
    
    def add_window(self, win: Dict[str, Any]) -> 'ItexeBuilder':
        """添加窗口"""
        self._windows.append(win)
        if not self._main_window_id:
            self._main_window_id = win["id"]
        return self
    
    def add_component(self, comp: Dict[str, Any]) -> 'ItexeBuilder':
        """添加组件"""
        self._components.append(comp)
        return self
    
    def add_linkage(self, link: Dict[str, Any]) -> 'ItexeBuilder':
        """添加联动"""
        self._linkages.append(link)
        return self
    
    def build(self) -> Dict[str, Any]:
        """构建项目数据"""
        current_window_id = self._windows[0]["id"] if self._windows else self._main_window_id
        return {
            "name": self._name,
            "windows": self._windows,
            "components": self._components,
            "main_window_id": self._main_window_id,
            "current_window_id": current_window_id,
            "linkages": self._linkages
        }
    
    def save(self, filepath: str) -> bool:
        """保存到文件"""
        try:
            data = self.build()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"项目已保存: {filepath}")
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False

def project(name: str, *windows) -> ItexeBuilder:
    """创建项目"""
    builder = ItexeBuilder(name)
    for win in windows:
        if isinstance(win, dict):
            # 检查是否是窗口
            if "window_type" in win and "components" in win:
                builder.add_window(win)
                # 添加窗口中的组件
                for comp in win.get("components", []):
                    if isinstance(comp, dict):
                        builder.add_component(comp)
    return builder

# ============================================================================
# 便捷函数
# ============================================================================

def simple_project(name: str, 
                  main_window: Dict[str, Any],
                  components: List[Dict[str, Any]],
                  linkages: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """创建简单项目（所有组件在同一窗口）"""
    win_id = main_window["id"]
    main_window["components"] = [c["id"] for c in components]
    
    return {
        "name": name,
        "windows": [main_window],
        "components": components,
        "main_window_id": win_id,
        "current_window_id": win_id,
        "linkages": linkages or []
    }

# ============================================================================
# 示例
# ============================================================================

def create_lottery_sample() -> Dict[str, Any]:
    """创建文字抽奖示例"""
    # 主窗口
    main_win = window("抽奖主界面", 600, 450, "main", "文字抽奖系统")
    
    # 组件
    cont_main = container("主容器", x=20, y=20, w=560, h=410, bg="#1a1a2e", radius=15)
    lbl_title = label("标题", x=180, y=40, w=200, h=50, text="🎲 抽奖系统", 
                     color="#ffffff", size=24, bold=True, bg="transparent")
    lbl_candidates = label("名单", x=100, y=100, w=360, h=100, 
                         text="参与者: 张三, 李四, 王五, 赵六, 钱七", 
                         color="#aaaaaa", size=14, bg="transparent")
    btn_start = button("开始抽奖", x=220, y=220, w=120, h=50, 
                      text="开始", action_type="lottery_animation", target="carousel_1")
    carousel = image_carousel("轮播", x=150, y=290, w=260, h=100,
                             labels=["张三", "李四", "王五", "赵六", "钱七"])
    lbl_result = label("结果", x=150, y=400, w=260, h=30, 
                     text="点击开始按钮抽奖", color="#4CAF50", size=14, bold=True,
                     bg="transparent")
    
    # 联动
    link1 = linkage("显示结果", carousel["id"], "lottery_finished",
                   lbl_result["id"], "set_text", "中奖者: {winner}")
    
    return simple_project("文字抽奖", main_win, 
                        [cont_main, lbl_title, lbl_candidates, btn_start, carousel, lbl_result],
                        [link1])

def create_lottery_sample_file(filepath: str = "tlexe_build/samples/文字抽奖示例.itexe"):
    """保存文字抽奖示例到文件"""
    data = create_lottery_sample()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已生成: {filepath}")

if __name__ == "__main__":
    create_lottery_sample_file()
