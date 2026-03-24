# 窗口编辑器项目 - 上下文手册

## 项目概述
这是一个基于 PyQt6 的窗口编辑器项目，用于创建和编辑 Galgame 风格的界面。支持多窗口/事件管理、组件拖拽、属性编辑等功能。

## 最近完成的修复 (2026-03-21)

### 1. 修复程序启动崩溃问题
**文件**: `dev_mode/debug_logger.py`

**问题**: `DebugLogger` 继承自 `QObject`，在发射信号时需要 `QApplication` 实例存在，否则会导致程序崩溃。

**修复**: 在 `_add_log()` 和 `clear_logs()` 方法中添加了 `QApplication.instance()` 检查：
```python
try:
    from PyQt6.QtWidgets import QApplication
    if QApplication.instance() is not None:
        self.log_added.emit(entry)
except Exception:
    pass
```

### 2. 修复进度条属性面板崩溃问题
**文件**: `views/property_panel.py`

**问题**: 第1110行 `self._project_model.windows` 是字典，不能直接迭代。

**修复**: 改为 `self._project_model.get_all_windows()`

### 3. 修复二级菜单点击后无法跳转回一级菜单的问题
**文件**: `views/logic_tree.py`

**问题**: `_on_current_item_changed` 方法只检查直接父节点，无法处理嵌套的组件。

**修复**: 添加了 `_find_parent_window_id()` 方法，递归查找组件所属的窗口ID。

### 4. 添加进度条百分比显示位置选项
**文件**: 
- `models/components.py` - 添加 `text_position` 属性
- `views/property_panel.py` - 添加文本位置下拉框
- `views/canvas.py` - 支持四种文本位置绘制

**功能**: 支持左侧、居中、右侧、跟随进度四种文本位置。

### 5. 添加Windows系统字体缓存功能
**文件**: `utils/font_utils.py` (新建)

**功能**: 
- `get_system_fonts()` - 获取系统所有可用字体（带缓存）
- `get_common_chinese_fonts()` - 获取常用中文字体
- `is_font_available()` - 检查字体是否可用

**属性面板**: 添加了 `QFontComboBox` 字体选择下拉框。

### 6. 修复撤回/重做功能问题
**文件**: `controllers/project_controller.py`

**修复**:
- 修正方法调用: `get_undo_text()` → `get_undo_description()`
- 添加 `_apply_undo_state()` 和 `_apply_redo_state()` 方法来实际应用状态变化
- 添加多选移动的撤回支持
- 添加 `_on_multi_move_started()` 和 `_on_multi_move_finished()` 方法

### 7. 修复多选拖动问题
**文件**: `views/canvas.py`

**修复**: 
- 按住 Ctrl/Shift 时切换选中状态（多选模式）
- 普通点击时使用 Qt 默认拖动行为
- 添加 `RuntimeError` 异常保护防止 C++ 对象被删除后崩溃
- 添加 `multi_move_started` 和 `multi_move_finished` 信号

### 8. 修复数值类型问题
**文件**: `models/base.py`, `models/window.py`

**问题**: JSON 文件中保存的数值在 Python 中会被解析为 `float` 类型，但 `QSpinBox.setValue()` 需要 `int` 类型。

**修复**: 在 `from_dict` 方法中添加 `int()` 类型转换。

## 项目结构
```
测试项目-窗口编辑器/
├── main.py                 # 程序入口
├── controllers/
│   └── project_controller.py  # 项目控制器
├── models/
│   ├── __init__.py
│   ├── base.py             # 基础模型、项目模型
│   ├── components.py       # 组件模型
│   ├── signals.py          # 信号模型
│   └── window.py           # 窗口模型
├── views/
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── canvas.py           # 画布视图
│   ├── property_panel.py   # 属性面板
│   ├── logic_tree.py       # 逻辑树视图
│   ├── component_tree.py   # 组件树视图
│   ├── welcome_page.py     # 欢迎页面
│   ├── blockly_editor.py   # Blockly编辑器
│   ├── flow_preview.py     # 流程预览
│   └── preferences_dialog.py # 首选项对话框
├── utils/
│   ├── undo_manager.py     # 撤回管理器
│   ├── font_utils.py       # 字体工具
│   ├── settings.py         # 设置管理
│   └── crash_log.py        # 崩溃日志
├── runtime/
│   ├── runner.py           # 运行时启动器
│   └── action_executor.py  # 动作执行器
├── templates/
│   └── test_template.py    # 测试模板
├── dev_mode/
│   ├── __init__.py
│   ├── debug_logger.py     # 调试日志
│   ├── dev_manager.py      # 开发模式管理器
│   ├── dev_console.py      # 开发者控制台
│   └── test_runner.py      # 测试运行器
└── samples/
    └── galgame示例.fool    # 示例项目
```

## 组件类型
| 类型 | 模型类 | 特殊属性 |
|------|--------|----------|
| button | ButtonModel | is_default, is_cancel, branch_name, target_window_id |
| label | LabelModel | - |
| input | InputModel | placeholder, is_password, is_multiline, max_length |
| container | ContainerModel | layout, padding, spacing, position_mode |
| checkbox | CheckBoxModel | checked |
| combobox | ComboBoxModel | items, current_index |
| progressbar | ProgressBarModel | value, show_text, text_position, auto_progress, duration, signals |

## 重要注意事项

1. **QObject 信号发射**: 在发射 Qt 信号前，必须确保 `QApplication` 实例存在。

2. **数值类型**: 从 JSON 加载数据时，数值可能是 `float` 类型，需要转换为 `int` 后再用于 Qt 控件。

3. **多选拖动**: 使用自定义拖动逻辑处理多选，单选使用 Qt 默认行为。

4. **组件嵌套**: 逻辑树中的组件可能嵌套在容器内，查找窗口时需要递归向上查找。

5. **进度条属性**: 进度条组件有特殊属性（假进度动画、信号配置、文本位置），属性面板需要特殊处理。

6. **布局警告**: 启动时有 `QLayout: Attempting to add QLayout "" to QWidget ""` 警告，不影响功能，后续可优化。

## 信号连接关系

### 主窗口信号
- `window_selected` → 控制器切换当前窗口
- `component_selected` → 控制器选中组件
- `create_event_requested` → 控制器创建事件窗口

### 逻辑树信号
- `window_selected` → 主窗口转发
- `component_selected` → 主窗口转发
- `create_event_requested` → 主窗口转发
- `delete_component_requested` → 主窗口转发
- `delete_window_requested` → 主窗口转发
- `rename_requested` → 主窗口转发

### 属性面板信号
- `property_changed` → 主窗口转发到控制器
- `action_config_requested` → 主窗口转发
- `create_event_requested` → 主窗口转发
- `goto_event_requested` → 主窗口转发

### 画布组件信号
- `moved` → 控制器处理移动
- `selected` → 控制器处理选择
- `resized` → 控制器处理大小调整
- `parent_changed` → 控制器处理父容器变化
- `multi_move_started` → 控制器记录多选移动起始位置
- `multi_move_finished` → 控制器记录多选移动到撤回栈

## 已知问题
1. 布局警告：`QLayout: Attempting to add QLayout "" to QWidget ""` - 不影响功能

## 待办事项
- 无明确的待办事项，项目功能基本完善

## 最近补充的功能 (2026-03-21)

### 进度条文本位置属性
**文件**: 
- `models/components.py` - `ProgressBarModel.text_position` 属性
- `views/property_panel.py` - 添加文本位置下拉框
- `views/canvas.py` - `_paint_progressbar()` 支持四种文本位置

**支持的位置**:
- `left` - 左侧显示
- `center` - 居中显示（默认）
- `right` - 右侧显示
- `follow` - 跟随进度条末端显示

### 修复的问题
1. **welcome_page.py** - 添加缺失的 `QGridLayout` 导入
2. **ProgressBarModel** - 添加完整的 `text_position` 属性（getter/setter/to_dict/from_dict）
3. **官方案例列表** - 移除未实现的模板，只保留"电脑开机检测演示"
4. **welcome_page.py布局问题** - 修复 `CollapsibleSection.content_widget` 的布局问题，移除重复的 `QVBoxLayout`
5. **logic_tree.py语法错误** - 修复第58行的换行符错误
6. **main_window.py工具栏** - 将组件按钮改为下拉菜单"添加组件"
7. **LabelModel默认样式** - 设置透明背景和边框
8. **main_window.py引用错误** - 移除不存在的 `self.component_tree` 引用
9. **load_from_file错误处理** - 添加详细的错误日志输出
10. **命令行参数支持** - 添加 `--dev` 开发者模式和直接打开项目文件功能
11. **会话日志功能** - 新增 `utils/session_logger.py`，自动保留最近8个日志文件
12. **创建窗口提示** - 添加组件时如果没有窗口，提示用户先创建窗口，支持"不再显示"选项
13. **逻辑树布局优化** - 移除重复的标题，添加💡提示按钮，点击显示操作提示弹出框
14. **画布坐标计算修复** - 修复 `_fit_desktop_to_view` 方法使用场景实际桌面尺寸而非默认值，解决窗口移动后组件位置偏差问题
15. **默认桌面尺寸调整** - 将默认桌面尺寸从 1920x1080 改为 800x600，符合游戏窗口大小
16. **属性面板滚动修复** - 添加垂直滚动条策略和最小宽度设置，解决属性叠在一起的问题
17. **属性面板样式布局优化** - 将样式组改为两列布局，更紧凑美观
18. **容器组件选择修复** - 修改容器组件的 `shape()` 方法，使用奇偶填充规则，只响应边框区域的点击，内部区域可以点击到其他组件
19. **手柄点击容差增加** - 将 `handle_click_tolerance` 从 16 增加到 24，使调整手柄更容易点击
20. **组件切换选择修复** - 修复点击已选中组件无法切换到其他组件的问题，现在点击任何组件都会正确选中该组件并取消其他组件的选中状态
