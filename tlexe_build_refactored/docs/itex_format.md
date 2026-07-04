# Tlexe 项目文件格式文档

## 概述
Tlexe (.itexe) 是本项目的项目文件格式，基于 JSON 格式存储。

## 文件结构

```json
{
  "name": "项目名称",
  "windows": [...],
  "components": [...],
  "main_window_id": "主窗口ID",
  "current_window_id": "当前窗口ID",
  "linkages": [...],
  "variables": [...],
  "settings": {...}
}
```

## 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 项目名称 |
| windows | array | 窗口列表 |
| components | array | 组件列表 |
| main_window_id | string | 主窗口ID (必需) |
| current_window_id | string | 当前窗口ID (必需) |

## 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| linkages | array | 联动配置列表 |
| variables | array | 变量列表 |
| settings | object | 项目设置 |

## 窗口对象 (Window)

```json
{
  "id": "窗口唯一ID",
  "name": "窗口名称",
  "window_type": "main | event",
  "width": 800,
  "height": 600,
  "title": "窗口标题",
  "components": ["组件ID列表"],
  "trigger_button_id": "触发按钮ID"
}
```

### window_type 可选值
- `main`: 主窗口
- `event`: 事件窗口

### 窗口扩展属性

| 字段 | 类型 | 说明 |
|------|------|------|
| frameless | bool | 无边框窗口（无顶栏）|
| window_color | string | 窗口背景色，如 "#1a1a2e" |

## 组件对象 (Component)

```json
{
  "id": "组件唯一ID",
  "comp_type": "组件类型",
  "name": "组件名称",
  "x": 0,
  "y": 0,
  "width": 100,
  "height": 30,
  "text": "显示文本",
  "parent_id": "父组件ID",
  "style": {...},
  "action": {...},
  "visible": true,
  "enabled": true,
  "custom_props": {},
  "h_align": "none",
  "v_align": "none"
}
```

### 组件类型 (comp_type)

| 类型值 | 说明 | 专有字段 |
|--------|------|----------|
| button | 按钮 | target_window_id, branch_name, open_mode, is_default, is_cancel, alignment |
| label | 标签 | alignment, word_wrap, auto_size |
| input | 输入框 | placeholder, max_length, is_password, is_multiline |
| textarea | 多行输入 | (同 input) |
| container | 容器 | children, position_mode, layout, padding, spacing |
| groupbox | 分组框 | (同 container) |
| checkbox | 复选框 | checked, alignment |
| combobox | 下拉框 | items, current_index |
| listwidget | 列表 | (同 combobox) |
| image | 图片 | image_path, aspect_ratio, scale_mode, border_radius, opacity, hover_effect, click_action, placeholder_text |
| video | 视频 | video_path, auto_play, loop, muted, controls, volume, poster_image, playback_rate, aspect_ratio, placeholder_text |
| progressbar | 进度条 | value, show_text, text_position, auto_progress, duration, target_window_id, branch_name |
| hidden_button | 隐藏按钮 | action, action_params |
| image_button | 图片按钮 | image_path, hover_image_path, pressed_image_path, action, action_params |
| image_carousel | 图片轮播 | images, image_labels, current_index, interval, auto_play, loop |
| lottery | 抽奖 | items, item_labels, display_mode, current_index, animation_duration |
| text_alternating | 文字交替变换 | items, item_labels, current_index, animation_duration, display_mode, toggle_mode |
| image_alternating | 图片交替变换 | (同 text_alternating) |
| confirm_button | 确认按钮 | confirm_group, is_confirmed |
| group_node | 组节点 | children, layout_mode, spacing, padding, auto_size, show_border, border_style |

### 样式对象 (Style)

```json
{
  "background_color": "#ffffff",
  "text_color": "#000000",
  "border_color": "#cccccc",
  "border_width": 1,
  "border_radius": 5,
  "font_family": "Microsoft YaHei",
  "font_size": 12,
  "font_bold": false,
  "use_native_style": false
}
```

### 动作对象 (Action)

```json
{
  "action_type": "动作类型",
  "params": {...},
  "blockly_xml": "",
  "python_code": ""
}
```

### 动作类型 (action_type)

| 类型值 | 说明 | 常用参数 |
|--------|------|----------|
| none | 无动作 | - |
| close_program | 关闭程序 | - |
| close_window | 关闭窗口 | - |
| open_window | 打开窗口 | target_window_id |
| switch_window | 切换窗口 | target_window_id |
| open_event | 打开事件 | target_event_id |
| open_file | 打开文件 | file_path |
| open_url | 打开网址 | url |
| random_image | 随机选图 | target_component_id |
| next_image | 下一张图 | target_component_id |
| prev_image | 上一张图 | target_component_id |
| start_carousel | 开始轮播 | target_component_id |
| stop_carousel | 停止轮播 | target_component_id |
| lottery_animation | 抽奖动画 | target_component_id |
| start_alternating | 开始交替变换 | target_component_id |
| stop_alternating | 停止交替变换 | target_component_id |
| confirm_check | 确认检查 | target_component_id |
| set_text | 设置文本 | target_component_id, text |
| show_component | 显示组件 | target_component_id |
| hide_component | 隐藏组件 | target_component_id |
| show_message | 显示消息 | title, message, type |
| execute_python | 执行Python | python_code |
| run_script | 运行脚本 | script_path, wait |
| run_command | 运行命令 | command, wait |
| run_cmd | CMD命令 | command, wait |
| run_powershell | PowerShell | command, wait |
| set_property | 设置属性 | component_id, property_name, value |
| delay | 延时 | milliseconds |
| get_system_info | 系统信息 | - |
| run_as_admin | 管理员运行 | command |
| custom | 自定义动作 | - |

### action.params 参数

```json
{
  "target_window_id": "目标窗口ID",
  "target_component_id": "目标组件ID",
  "text_template": "文本模板 {winner} {index} {count}"
}
```

## 联动配置 (Linkage)

```json
{
  "source_component": "源组件ID",
  "source_event": "源事件",
  "target_component": "目标组件ID",
  "target_action": "目标动作",
  "params": {...}
}
```

### 事件名称

| 事件名 | 说明 | 适用组件 |
|--------|------|----------|
| clicked | 点击 | button, hidden_button, image_button, confirm_button |
| text_changed | 文本改变 | input, combobox |
| value_changed | 值改变 | checkbox, progressbar |
| lottery_finished | 抽奖完成 | lottery, image_carousel, label |
| carousel_stopped | 轮播停止 | image_carousel |
| started | 开始交替变换 | text_alternating, image_alternating |
| stopped | 停止交替变换 | text_alternating, image_alternating |
| confirmed_changed | 确认状态改变 | confirm_button |
| all_confirmed | 全部确认 | confirm_button |

### 目标动作

| 动作名 | 说明 |
|--------|------|
| set_text | 设置文本 |
| show | 显示 |
| hide | 隐藏 |

## 文本模板变量

在 `text_template` 中使用：

| 变量 | 说明 |
|------|------|
| {winner} | 抽奖结果 |
| {index} | 当前索引 |
| {count} | 总人数 |

## 使用编辑器

### 组件属性面板

在编辑器左侧的组件树中选中组件后，右侧属性面板会显示：
- **基础属性**：ID、名称、显示文本
- **位置和大小**：X、Y、宽度、高度
- **样式属性**：背景色、文本色、边框颜色、边框宽度、圆角、字体大小、是否粗体
- **特定属性**：根据组件类型不同（如按钮动作、图片路径等）

### 窗口属性面板

在组件树中选中窗口节点（窗口图标）后，属性面板会显示：
- **无边框窗口**：勾选后隐藏标题栏和窗口边框
- **背景色**：设置窗口的背景颜色（覆盖默认的白色背景）

## 示例

### 最小示例

```json
{
  "name": "我的项目",
  "windows": [
    {
      "id": "main001",
      "name": "主窗口",
      "window_type": "main",
      "width": 600,
      "height": 400,
      "title": "标题",
      "components": ["btn_1"]
    }
  ],
  "components": [
    {
      "id": "btn_1",
      "comp_type": "button",
      "name": "按钮",
      "x": 100,
      "y": 100,
      "width": 100,
      "height": 40,
      "text": "点击",
      "parent_id": ""
    }
  ],
  "main_window_id": "main001",
  "current_window_id": "main001"
}
```

### 交替变换示例

```json
{
  "id": "alt_1",
  "comp_type": "text_alternating",
  "name": "文字交替",
  "x": 50, "y": 50, "width": 300, "height": 120,
  "text": "", "parent_id": "",
  "style": {"font_size": 24, "font_bold": true, "text_color": "#333333"},
  "items": ["选项A", "选项B", "选项C"],
  "item_labels": ["选项A", "选项B", "选项C"],
  "animation_duration": 3000,
  "toggle_mode": "same"
}
```
