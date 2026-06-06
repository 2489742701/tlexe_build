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
  "enabled": true
}
```

### 组件类型 (comp_type)

| 类型值 | 说明 | 备注 |
|--------|------|------|
| container | 容器 | 可包含子组件 |
| label | 标签 | 显示文本 |
| button | 按钮 | 可点击 |
| input | 输入框 | 文本输入 |
| image | 图片 | 显示图片 |
| image_carousel | 图片轮播 | 抽奖动画 |
| video | 视频 | 视频播放 |
| progressbar | 进度条 | 进度显示 |
| checkbox | 复选框 | 多选 |
| hidden_button | 隐藏按钮 | 透明可点击 |

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
  "font_bold": false
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

| 类型值 | 说明 |
|--------|------|
| none | 无动作 |
| close_program | 关闭程序 |
| open_window | 打开窗口 |
| switch_window | 切换窗口 |
| lottery_animation | 抽奖动画 |
| set_text | 设置文本 |
| show_component | 显示组件 |
| hide_component | 隐藏组件 |
| random_image | 随机选图 |
| start_carousel | 开始轮播 |
| stop_carousel | 停止轮播 |

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

| 事件名 | 说明 |
|--------|------|
| clicked | 点击 |
| text_changed | 文本改变 |
| lottery_finished | 抽奖完成 |
| carousel_stopped | 轮播停止 |

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

### 带联动的示例

```json
{
  "name": "抽奖示例",
  "windows": [...],
  "components": [...],
  "linkages": [
    {
      "source_component": "carousel_1",
      "source_event": "lottery_finished",
      "target_component": "lbl_result",
      "target_action": "set_text",
      "params": {"text_template": "中奖者: {winner}"}
    }
  ],
  "main_window_id": "main001",
  "current_window_id": "main001"
}
```
