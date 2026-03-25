# UI快速开发工具 - 完整上下文手册

## 项目概述

这是一个基于 PyQt6 的可视化 UI 设计工具，允许用户通过拖拽方式创建桌面应用程序界面。支持 Galgame 模式的多窗口/事件管理。

---

## 项目结构

```
测试项目-窗口编辑器/
├── main.py                    # 程序入口，AppManager 管理欢迎页和编辑器切换
├── models/                    # 数据模型层
│   ├── __init__.py           # 导出所有模型类
│   ├── base.py               # 基础模型：ComponentModel, ProjectModel, StyleConfig, ActionConfig
│   ├── components.py         # 组件模型：ButtonModel, LabelModel, InputModel, ContainerModel, ProgressBarModel
│   ├── window.py             # 窗口模型：WindowModel, WindowType, ActionType
│   └── signals.py            # 信号系统：SignalDefinition, SignalManager
├── views/                     # 视图层
│   ├── __init__.py           # 导出 MainWindow
│   ├── main_window.py        # 主窗口：菜单栏、工具栏、状态栏、布局
│   ├── canvas.py             # 设计画布：组件图形项、绘制逻辑
│   ├── component_tree.py     # 组件树视图
│   ├── logic_tree.py         # 逻辑树视图：窗口和组件的树状结构
│   ├── property_panel.py     # 属性面板：组件属性编辑
│   ├── welcome_page.py       # 欢迎页：问候语、官方案例、最近项目
│   ├── flow_preview.py       # 流程图预览
│   ├── preferences_dialog.py # 首选项对话框
│   └── blockly_editor.py     # Blockly编辑器（开发中占位符）
├── controllers/               # 控制器层
│   ├── __init__.py           # 导出 ProjectController
│   └── project_controller.py # 项目控制器：协调模型和视图
├── runtime/                   # 运行时
│   ├── runner.py             # 运行器：导出并运行生成的程序
│   └── action_executor.py    # 行为执行器
├── utils/                     # 工具类
│   ├── settings.py           # 应用设置：单例模式，持久化存储，字体智能识别
│   ├── undo_manager.py       # 撤销管理器
│   ├── font_utils.py         # 字体工具
│   └── crash_log.py          # 崩溃日志
├── templates/                 # 模板
│   ├── __init__.py           # 导出 get_test_template
│   └── test_template.py      # 测试模板：电脑开机检测演示
├── dev_mode/                  # 开发模式
│   ├── dev_console.py        # 开发控制台
│   ├── dev_manager.py        # 开发管理器
│   └── debug_logger.py       # 调试日志
└── exports/                   # 导出目录
```

---

## 核心类说明

### 1. ProjectModel (models/base.py)
项目数据模型，管理所有窗口和组件。

**关键属性：**
- `_name`: 项目名称
- `_windows`: Dict[str, WindowModel] - 窗口字典
- `_components`: Dict[str, ComponentModel] - 组件字典
- `_main_window_id`: 主窗口ID
- `_current_window_id`: 当前窗口ID

**关键方法：**
- `add_component(comp, window_id)`: 添加组件到窗口
- `remove_component(comp_id)`: 删除组件
- `get_components_for_window(window_id)`: 获取窗口的所有组件
- `to_dict() / from_dict(data)`: 序列化/反序列化
- `save_to_file(path) / load_from_file(path)`: 文件操作

### 2. ComponentModel (models/base.py)
组件基类，所有组件的父类。

**基础属性：**
- `_id, _type, _name`: 组件标识
- `_x, _y, _width, _height`: 位置和尺寸
- `_text`: 文本内容
- `_parent_id`: 父容器ID
- `_style`: StyleConfig - 样式配置
- `_action`: ActionConfig - 行为配置
- `_visible, _enabled`: 可见性和启用状态

**子类特有属性：**
- ButtonModel: `_is_default, _is_cancel, _target_window_id, _branch_name, _open_mode`
- LabelModel: `_alignment, _word_wrap`
- InputModel: `_placeholder, _is_password, _is_multiline, _max_length`
- ContainerModel: `_layout, _padding, _spacing`
- ProgressBarModel: `_value, _show_text, _auto_progress, _duration, _signals`

### 3. WindowModel (models/window.py)
窗口模型。

**属性：**
- `_id, _name, _title`: 窗口标识
- `_window_type`: WindowType 枚举 (main/event)
- `_width, _height`: 窗口尺寸
- `_components`: List[str] - 组件ID列表

### 4. ProjectController (controllers/project_controller.py)
项目控制器，协调模型和视图。

**关键方法：**
- `_on_add_component(comp_type, parent_id)`: 添加组件
- `_on_delete_component(comp_id)`: 删除组件
- `_on_project_loaded()`: 项目加载完成，刷新画布
- `_create_graphics_item(comp)`: 创建组件图形项
- `run_project()`: 运行项目
- `export_project()`: 导出项目

### 5. MainWindow (views/main_window.py)
主窗口视图。

**信号：**
- `add_component(str, str)`: 添加组件 (comp_type, parent_id)
- `delete_component(str)`: 删除组件 (comp_id)
- `run_project`: 运行项目
- `export_project`: 导出项目

### 6. AppSettings (utils/settings.py)
应用设置管理器，单例模式。

**默认设置：**
```python
DEFAULT_SETTINGS = {
    "handle_size": 18,
    "handle_click_tolerance": 20,
    "grid_size": 10,
    "snap_to_grid": True,
    "show_grid": True,
    "font_family": "",  # 空表示智能检测
    "font_size": 10,
}
```

**字体智能识别：**
- Windows: Microsoft YaHei, SimHei, SimSun, Arial, Segoe UI
- macOS: PingFang SC, Hiragino Sans GB, STHeiti, Arial, Helvetica
- Linux: WenQuanYi Micro Hei, Noto Sans CJK SC, Ubuntu, DejaVu Sans

---

## 数据格式

### 项目文件格式 (.fool 或 .uix)
```json
{
    "name": "项目名称",
    "main_window_id": "win_001",
    "current_window_id": "win_001",
    "windows": [
        {
            "id": "win_001",
            "name": "主窗口",
            "window_type": "main",
            "width": 800,
            "height": 600,
            "title": "窗口标题",
            "components": ["comp_001", "comp_002"]
        }
    ],
    "components": [
        {
            "id": "comp_001",
            "type": "button",
            "name": "按钮1",
            "x": 100,
            "y": 100,
            "width": 120,
            "height": 40,
            "text": "点击我",
            "parent_id": "",
            "style": {...},
            "action": {...}
        }
    ]
}
```

### 组件类型映射
```python
COMPONENT_TYPE_MAP = {
    'button': ButtonModel,
    'label': LabelModel,
    'input': InputModel,
    'container': ContainerModel,
    'progressbar': ProgressBarModel,
}
```

---

## 信号系统

### SignalDefinition (models/signals.py)
信号定义，用于组件间通信和窗口跳转。

**属性：**
- `signal_id`: 信号唯一ID
- `signal_name`: 信号名称（用户可见）
- `signal_type`: 信号类型 (progress_complete, progress_start, timer_timeout, custom)
- `target_window_id`: 目标窗口ID
- `description`: 信号描述

### 预定义信号类型
```python
PREDEFINED_SIGNAL_TYPES = {
    'progress_complete': {'name': '进度条完成信号', 'description': '当进度条达到100%时触发'},
    'progress_start': {'name': '进度条开始信号', 'description': '当进度条开始运行时触发'},
    'timer_timeout': {'name': '定时器超时信号', 'description': '当定时器超时时触发'},
    'custom': {'name': '自定义信号', 'description': '用户自定义信号'},
}
```

---

## 运行时系统

### Runner (runtime/runner.py)
运行器，负责显示和运行导出的程序。

**关键方法：**
- `_create_button(comp_data)`: 创建按钮，支持跳转窗口
- `_create_label(comp_data)`: 创建标签
- `_create_input(comp_data)`: 创建输入框
- `_create_progressbar(comp_data)`: 创建进度条，支持假进度动画
- `_start_fake_progress(progressbar, duration, signals, comp_id)`: 启动假进度动画
- `_open_window(window_id)`: 打开窗口

### 假进度动画实现
```python
def _start_fake_progress(self, progressbar, duration, signals, comp_id):
    # 每50毫秒更新一次，在指定时间内从0%到100%
    # 完成后检查 signals，如果有 progress_complete 信号则跳转目标窗口
```

---

## 已修复的问题

### 1. ComponentModel.from_dict 初始化不完整
**问题**：使用 `__new__` 手动初始化，子类特有属性丢失。
**修复**：改用正常构造函数创建实例，再通过反射设置属性。

### 2. 粘贴功能不完整
**问题**：使用 `create_component` 无法处理完整字典。
**修复**：直接使用 `ComponentModel.from_dict()` 创建组件。

### 3. 导出代码双花括号语法错误
**问题**：f-string 中 `{{}}` 导致生成的代码有语法错误。
**修复**：改用字符串模板 + `.replace()` 方法。

### 4. create_component 缺少 ProgressBarModel
**问题**：工厂函数没有包含进度条组件。
**修复**：添加 `elif comp_type == 'progressbar': return ProgressBarModel(**kwargs)`

### 5. 字体硬编码
**问题**：硬编码 "Microsoft YaHei"，跨平台兼容性差。
**修复**：添加字体智能识别，根据操作系统选择可用字体。

### 6. 测试模板窗口组件列表不完整
**问题**：窗口的 `components` 列表只包含容器ID。
**修复**：将所有属于该窗口的组件ID都添加到列表中。

### 7. BOM字符问题
**问题**：37个Python文件包含UTF-8 BOM字符，导致语法错误。
**修复**：使用脚本批量移除BOM字符。

---

## 测试模板：电脑开机检测演示

### 流程
1. **询问窗口**：显示"是否检测电脑是否开机？"，有"是"和"否"按钮
2. **点"是"**：进入检测中窗口
3. **点"否"**：关闭程序
4. **检测中窗口**：显示假进度条（3秒），完成后自动跳转
5. **结果窗口**：显示"恭喜您的电脑已经成功开机！"

### 窗口和组件
- 询问窗口：container_ask, label_ask, button_yes, button_no
- 检测中窗口：container_testing, label_testing, progressbar_testing, label_hint
- 结果窗口：container_result, label_result_title, label_result_desc, label_system_info, button_close_result

---

## 待实现功能

1. **属性面板信号配置**：用户点击"+"添加信号，配置目标窗口
2. **撤销/重做功能**：UndoManager 已实现但未完全集成
3. **输入验证**：属性面板输入验证
4. **异常处理**：更多地方的异常处理
5. **进度条组件添加到工具栏**：需要在工具栏添加进度条按钮

---

## 关键代码片段

### 创建组件工厂函数
```python
def create_component(comp_type: str, **kwargs) -> ComponentModel:
    comp_class = COMPONENT_TYPE_MAP.get(comp_type)
    if comp_class:
        return comp_class(**kwargs)
    raise ValueError(f"未知的组件类型: {comp_type}")
```

### 组件工具栏添加进度条
```python
progressbar_action = QAction("进度条", self)
progressbar_action.setToolTip("添加进度条组件，支持假进度动画和信号触发")
progressbar_action.triggered.connect(lambda: self.add_component.emit("progressbar", ""))
display_menu.addAction(progressbar_action)
```

---

## 注意事项

1. **文件编码**：所有Python文件必须使用UTF-8无BOM编码
2. **窗口组件列表**：窗口的 `components` 列表必须包含所有属于该窗口的组件ID，不仅仅是容器
3. **信号系统**：进度条的信号需要在属性面板中配置目标窗口ID
4. **假进度动画**：需要在运行时系统中实现 `_start_fake_progress` 方法

---

## 程序入口

```python
# main.py
class AppManager:
    def __init__(self):
        self._app = QApplication(sys.argv)
        font_family = app_settings.font_family
        font_size = app_settings.font_size
        font = QFont(font_family, font_size)
        self._app.setFont(font)
        # ... 初始化欢迎页和编辑器
    
    def _on_open_template(self, template_data: dict):
        self._project_model = ProjectModel()
        self._project_model.from_dict(template_data)
        self._show_editor()
```

---

*此手册记录了程序的核心架构、关键实现、已修复问题和待实现功能，可用于恢复或重构项目。*
*创建时间：2026-03-21*
