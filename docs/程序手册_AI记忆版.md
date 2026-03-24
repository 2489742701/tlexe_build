# 窗口编辑器 - 程序手册（AI记忆版）

> 本文档基于AI对话上下文记忆编写，记录程序架构和核心功能。

## 项目概述

这是一个基于 **PyQt6** 的可视化窗口编辑器，支持拖拽式UI设计、组件属性编辑、逻辑流程设计等功能。

---

## 目录结构

```
测试项目-窗口编辑器/
├── main.py                 # 程序入口
├── devtools.py             # 开发工具
├── models/                 # 数据模型层
│   ├── __init__.py
│   ├── base.py             # 基础模型类
│   ├── components.py       # 组件模型
│   ├── signals.py          # 信号定义
│   └── window.py           # 窗口模型
├── views/                  # 视图层
│   ├── __init__.py
│   ├── canvas.py           # 画布视图（核心）
│   ├── main_window.py      # 主窗口
│   ├── property_panel.py   # 属性面板
│   ├── component_tree.py   # 组件树
│   ├── preferences_dialog.py # 设置对话框
│   ├── welcome_page.py     # 欢迎页面
│   ├── blockly_editor.py   # Blockly编辑器
│   ├── logic_tree.py       # 逻辑树
│   └── flow_preview.py     # 流程预览
├── controllers/            # 控制器层
│   ├── __init__.py
│   └── project_controller.py # 项目控制器
├── utils/                  # 工具类
│   ├── __init__.py
│   ├── settings.py         # 应用设置
│   ├── undo_manager.py     # 撤销管理器
│   ├── crash_log.py        # 崩溃日志
│   └── font_utils.py       # 字体工具
├── runtime/                # 运行时
│   ├── __init__.py
│   ├── runner.py           # 运行器
│   └── action_executor.py  # 动作执行器
├── dev_mode/               # 开发模式
│   ├── __init__.py
│   ├── dev_console.py      # 开发控制台
│   ├── debug_logger.py     # 调试日志
│   ├── dev_manager.py      # 开发模式管理
│   └── test_runner.py      # 测试运行器
├── templates/              # 模板
│   ├── __init__.py
│   └── test_template.py    # 测试模板
└── docs/                   # 文档
```

---

## 核心模块详解

### 1. views/canvas.py - 画布视图模块

这是程序的核心模块，包含三个主要类：

#### 1.1 ComponentGraphicsItem（组件图形项）

**功能：** 画布上的可交互组件，支持拖拽移动、选中高亮、大小调整。

**信号：**
- `moved(id, new_x, new_y)` - 组件移动时发射
- `selected(id)` - 组件被选中时发射
- `resized(id, new_width, new_height)` - 组件大小改变时发射
- `parent_changed(id, new_parent_id)` - 父容器改变时发射

**常量：**
- `MIN_SIZE = 20` - 最小尺寸
- `TITLE_BAR_HEIGHT = 28` - 容器标题栏高度

**核心方法：**

| 方法 | 功能 |
|------|------|
| `boundingRect()` | 返回组件边界矩形 |
| `paint()` | 绘制组件 |
| `_paint_container()` | 绘制容器组件（Windows窗口样式） |
| `_paint_component()` | 绘制普通组件 |
| `_draw_resize_handles()` | 绘制调整大小的手柄（8个） |
| `_get_handle_at(pos)` | 获取鼠标位置的手柄索引 |
| `_do_resize(scene_pos)` | 执行调整大小操作 |
| `_check_and_update_parent()` | 检查并更新父容器关系 |
| `itemChange(change, value)` | 处理位置变化（支持网格吸附） |
| `hoverMoveEvent(event)` | 鼠标悬停时设置光标形状 |

**手柄布局：**
```
[0]-----[1]-----[2]
  |             |
[7]    组件     [3]
  |             |
[6]-----[5]-----[4]
```

**手柄光标映射：**
- 0, 4: SizeFDiagCursor（对角线）
- 1, 5: SizeVerCursor（垂直）
- 2, 6: SizeBDiagCursor（反对角线）
- 3, 7: SizeHorCursor（水平）

#### 1.2 DesignerScene（设计器场景）

**功能：** 管理画布场景，支持桌面区域模拟、网格背景。

**属性：**
- `_desktop_width` / `_desktop_height` - 桌面尺寸（默认1920x1080）
- `_grid_color` - 网格颜色（#e0e0e0）
- `_desktop_border_color` - 桌面边框颜色（#333333）
- `_outside_color` - 桌面外区域颜色（#1a1a1a）
- `_desktop_bg_color` - 桌面背景颜色（#f5f5f5）

**核心方法：**
- `drawBackground()` - 绘制背景（桌面区域、网格）
- `_draw_grid()` - 绘制网格线
- `set_desktop_size()` - 设置桌面尺寸

#### 1.3 DesignerView（设计器视图）

**功能：** 主画布视图，支持缩放、平移、组件管理。

**信号：**
- `zoom_changed(zoom_factor)` - 缩放比例改变时发射

**属性：**
- `_zoom_factor` - 当前缩放比例（默认1.0）
- `_min_zoom` / `_max_zoom` - 缩放范围（0.1 ~ 4.0）
- `_items` - 组件ID到图形项的映射字典
- `_panning` - 是否正在平移

**核心方法：**

| 方法 | 功能 |
|------|------|
| `add_component_item(model)` | 添加组件到画布 |
| `remove_component_item(comp_id)` | 移除组件 |
| `select_item(comp_id)` | 选中组件 |
| `clear_selection()` | 清除选择 |
| `get_selected_items()` | 获取选中组件列表 |
| `zoom_in()` / `zoom_out()` | 放大/缩小 |
| `zoom_reset()` | 重置缩放 |
| `_fit_desktop_to_view()` | 将桌面适配到视图 |
| `_update_z_values()` | 更新组件Z值（容器在下层） |

**交互方式：**
- 滚轮：缩放
- 中键拖拽：平移画布
- 左键：选择/拖拽组件

---

### 2. models/components.py - 组件模型

**ComponentModel 类：**

组件的数据模型，存储组件的所有属性。

**核心属性：**
- `id` - 唯一标识符
- `name` - 组件名称
- `type` - 组件类型（container, button, label等）
- `x, y` - 位置坐标
- `width, height` - 尺寸
- `text` - 显示文本
- `style` - 样式对象（ComponentStyle）
- `parent_id` - 父容器ID
- `children` - 子组件列表

**信号：**
- `data_changed` - 数据变化时发射

**ComponentStyle 类：**

组件样式配置。

**属性：**
- `background_color` - 背景颜色
- `border_color` - 边框颜色
- `border_width` - 边框宽度
- `border_radius` - 圆角半径
- `text_color` - 文本颜色
- `font_family` - 字体
- `font_size` - 字号
- `font_bold` - 是否粗体

---

### 3. utils/settings.py - 应用设置

**app_settings 单例对象：**

全局应用设置管理。

**设置项：**

| 设置项 | 默认值 | 说明 |
|--------|--------|------|
| `handle_size` | 8 | 调整手柄大小 |
| `handle_click_tolerance` | 4 | 手柄点击容差 |
| `grid_size` | 20 | 网格大小 |
| `snap_to_grid` | True | 是否吸附网格 |
| `show_grid` | True | 是否显示网格 |

**方法：**
- `add_change_callback(callback)` - 添加设置变化回调
- `save()` / `load()` - 保存/加载设置

---

### 4. utils/undo_manager.py - 撤销管理器

**功能：** 管理操作历史，支持撤销/重做。

**核心方法：**
- `push_action(action)` - 压入操作
- `undo()` - 撤销
- `redo()` - 重做
- `can_undo()` / `can_redo()` - 是否可撤销/重做

---

### 5. controllers/project_controller.py - 项目控制器

**功能：** 协调模型和视图，处理业务逻辑。

**职责：**
- 管理项目生命周期
- 处理组件的增删改查
- 协调撤销/重做操作
- 处理文件保存/加载

---

### 6. views/main_window.py - 主窗口

**功能：** 应用程序主界面，整合所有面板。

**布局结构：**
```
┌─────────────────────────────────────────────────────┐
│                    工具栏                            │
├──────────┬──────────────────────────┬───────────────┤
│          │                          │               │
│ 组件树   │        画布区域          │   属性面板    │
│          │                          │               │
├──────────┴──────────────────────────┴───────────────┤
│                    状态栏                            │
└─────────────────────────────────────────────────────┘
```

---

### 7. views/property_panel.py - 属性面板

**功能：** 编辑选中组件的属性。

**可编辑属性：**
- 基础属性：名称、文本、位置、尺寸
- 样式属性：背景色、边框、字体等
- 高级属性：父容器、子组件

---

### 8. views/component_tree.py - 组件树

**功能：** 以树形结构显示所有组件的层级关系。

**特性：**
- 显示父子容器关系
- 支持拖拽调整层级
- 点击选中对应组件

---

### 9. views/preferences_dialog.py - 设置对话框

**功能：** 应用程序设置界面。

**设置分类：**
- 画布设置：网格、吸附
- 显示设置：手柄大小、颜色
- 编辑器设置：字体、主题

---

### 10. runtime/runner.py - 运行器

**功能：** 运行设计好的界面。

**流程：**
1. 解析组件树
2. 创建实际窗口
3. 应用样式和布局
4. 启动事件循环

---

### 11. dev_mode/ - 开发模式

**dev_console.py：** 开发者控制台，用于调试。

**debug_logger.py：** 调试日志记录。

**test_runner.py：** 测试用例运行器。

---

## 组件类型

| 类型 | 说明 |
|------|------|
| `container` | 容器（Windows窗口样式） |
| `button` | 按钮 |
| `label` | 标签 |
| `textbox` | 文本框 |
| `checkbox` | 复选框 |
| `radiobutton` | 单选按钮 |
| `combobox` | 下拉框 |
| `listbox` | 列表框 |
| `progressbar` | 进度条 |
| `slider` | 滑块 |

---

## 交互操作

### 画布操作
- **左键点击**：选择组件
- **左键拖拽**：移动组件
- **左键拖拽手柄**：调整组件大小
- **滚轮**：缩放画布
- **中键拖拽**：平移画布

### 组件操作
- **双击组件**：编辑文本
- **右键菜单**：复制、删除、置顶等
- **拖拽到容器**：设置父容器关系

### 快捷键
- `Ctrl+Z`：撤销
- `Ctrl+Y`：重做
- `Ctrl+C`：复制
- `Ctrl+V`：粘贴
- `Delete`：删除选中组件

---

## 文件格式

### 项目文件（.uix）

JSON格式，包含：
- 项目元信息
- 组件列表
- 组件属性
- 样式配置

---

## 开发注意事项

### 1. 手柄位置
手柄应完全绘制在组件边界外侧，不应遮挡组件内容。

### 2. Z值管理
容器组件Z值较低（在下层），普通组件Z值较高（在上层）。

### 3. 父容器检测
组件移动后自动检测是否在某个容器内，并更新父子关系。

### 4. 网格吸附
移动组件时可根据设置自动吸附到网格点。

### 5. 信号机制
使用Qt信号槽机制实现模块间通信，避免紧耦合。

---

## 版本信息

- **框架**：PyQt6
- **Python版本**：3.10+
- **平台**：Windows

---

*本文档由AI基于对话上下文记忆生成*
