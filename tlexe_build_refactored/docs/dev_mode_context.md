# 开发者模式模块上下文手册


> **重构版备注（2026-07）**: 本文档基于重构版 	lexe_build_refactored/，部分代码引用路径可能已变更（如 models.base.StyleConfig → models.schemas.StyleConfig，PyQt6 → PySide6）。核心分析逻辑仍有效。

## 概述

本文档记录了项目代码的注释增强工作，供后续维护和其他AI参考。

## 已完成的工作

### 1. dev_manager.py 注释增强

**文件路径**: `dev_mode/dev_manager.py`

**状态**: ✅ 已完成（重新添加注释）

**改进内容**:

#### 模块级别注释
- 添加了主要功能列表
- 添加了使用方法示例

#### 类级别注释
- `LogLevel` 枚举：添加了各级别的含义说明
- `_DevModeManagerSignals` 类：添加了设计说明和 Signals 文档
- `DevModeManager` 类：添加了设计模式说明、核心职责列表、Attributes 说明

#### 方法注释增强
| 方法 | 改进内容 |
|------|----------|
| `__new__` | 说明单例实现 |
| `__init__` | 详细说明初始化流程、各属性用途 |
| `get_instance` | 说明类方法的作用 |
| `mode_changed` | 添加返回值和使用示例 |
| `log_added_signal` | 添加返回值和使用示例 |
| `enabled` | 添加返回值说明 |
| `enable/disable` | 添加参数说明和执行流程 |
| `toggle` | 说明适用场景 |
| `set_project_model` | 添加参数说明 |
| `add_log` | 详细说明日志条目结构、参数、示例 |
| `get_logs` | 添加过滤功能说明和示例 |
| `clear_logs` | 添加注意事项 |
| `get_dev_manager` | 添加函数说明和使用示例 |

#### 行内注释
- 为所有关键代码行添加了解释性注释

---

### 2. component_tree.py 注释增强

**文件路径**: `views/component_tree.py`

**状态**: ✅ 已完成

**改进内容**:

#### 类级别注释
- `ComponentTreeView` 类：添加了设计模式说明（MVC视图层）、功能特性列表、Attributes说明

#### 信号注释
- 为所有信号添加了用途说明注释

#### 方法注释增强
| 方法 | 改进内容 |
|------|----------|
| `__init__` | 说明参数和属性初始化 |
| `_setup_ui` | 详细说明UI配置项（表头、右键菜单、单选、拖拽等）|
| `set_project_model` | 说明模型关联和信号连接 |
| `_refresh_tree` | 说明树刷新流程 |
| `_create_tree_item` | 说明节点数据结构（显示文本、UserRole数据）|
| `_on_component_added/removed` | 说明事件处理逻辑 |
| `_on_item_clicked/double_clicked` | 说明点击事件处理 |
| `_get_comp_id_from_index` | 说明辅助方法的作用 |
| `_show_context_menu` | 说明菜单项的条件显示逻辑 |
| `_on_rename/delete/add_component` | 说明操作处理流程 |
| `select_component` | 说明程序化选中用途 |
| `clear_selection` | 说明清除选中状态 |
| `get_selected_component_id` | 说明获取选中组件的用途 |

#### 行内注释
- 为所有关键代码行添加了解释性注释
- UI配置、信号连接、数据处理等都有详细说明

---

## 模块结构

```
dev_mode/
├── dev_manager.py      # 开发者模式管理器（已增强注释）✅
├── debug_logger.py     # 调试日志系统
├── test_runner.py      # 测试运行器
├── dev_console.py      # 开发者控制台UI
└── CONTEXT.md          # 本上下文手册

views/
├── component_tree.py   # 组件树视图（已增强注释）✅
└── ...
```

## 设计要点

### DevModeManager 单例模式实现
`DevModeManager` 采用 `__new__` + `_initialized` 标志实现单例：
- 不继承 QObject，避免初始化顺序问题
- 信号功能通过组合 `_DevModeManagerSignals` 实现

### ComponentTreeView MVC模式
- 作为视图层，与 `ProjectModel` 配合使用
- 通过信号与外部控制器通信，保持解耦
- 支持拖拽排序、右键菜单等交互

## 待办事项

- [x] dev_manager.py ✅
- [x] component_tree.py ✅
- [ ] debug_logger.py
- [ ] test_runner.py
- [ ] dev_console.py
- [ ] views 目录下其他文件

## 使用示例

### DevModeManager
```python
# 初始化开发者模式
dev_manager = init_dev_mode(project_model, main_window)

# 开启开发者模式
dev_manager.enable()

# 显示控制台（停靠窗口模式）
dev_manager.show_console()

# 记录日志
dev_manager.log_ui("按钮点击", source="MainWindow")

# 运行测试
dev_manager.run_all_tests()
```

### ComponentTreeView
```python
# 创建组件树视图
tree_view = ComponentTreeView()

# 设置项目模型
tree_view.set_project_model(project_model)

# 连接信号
tree_view.component_selected.connect(self._on_component_selected)
tree_view.delete_requested.connect(self._on_delete_component)

# 程序化选中组件
tree_view.select_component(comp_id)

# 获取当前选中
selected_id = tree_view.get_selected_component_id()
```

---
*最后更新: 2026-03-21*
