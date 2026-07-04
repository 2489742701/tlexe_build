# 按钮 (button)

## 概述
可点击的按钮组件，支持文本、样式和动作配置。是最常用的交互触发组件。

## 模型
- **类**: `ButtonModel` (models/components.py)
- **类型标识**: `button`
- **默认尺寸**: 120 × 40

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| target_window_id | str | "" | 点击后跳转的目标窗口ID |
| branch_name | str | "" | 分支名称（用于窗口跳转标记） |
| open_mode | str | "new_window" | 窗口打开模式 |
| is_default | bool | False | 是否为默认按钮（回车触发） |
| is_cancel | bool | False | 是否为取消按钮（Esc触发） |
| alignment | str | "center" | 文字对齐: left/center/right |

## 动作类型
按钮的 `action` 配置决定点击行为：
- `none`: 无动作
- `open_window`: 打开目标窗口（由 target_window_id 决定）
- `lottery_animation`: 触发抽奖动画
- `start_alternating`: 开始交替变换
- `stop_alternating`: 停止交替变换
- `set_text`: 设置目标组件文本
- `set_value`: 设置目标组件值

## 渲染器
- **类**: `ButtonRenderer` (renderers/button_renderer.py)
- 画布中渲染为带文字的矩形按钮，支持选中虚线框

## 工厂
- **方法**: `ComponentFactory._create_button` (utils/component_factory.py)
- 运行时创建 `QPushButton`，应用样式和文字对齐

## 编辑器
- 属性面板显示: name, text, alignment, target_window_id, action 配置
- 支持拖拽调整大小和位置

## 使用示例
```python
{
    'comp_type': 'button',
    'name': '开始',
    'text': '开始',
    'x': 100, 'y': 200, 'width': 120, 'height': 36,
    'action': {
        'action_type': 'start_alternating',
        'params': {'target_component_id': 'alt01', 'action_params': {'duration_ms': 3000}},
    },
}
```