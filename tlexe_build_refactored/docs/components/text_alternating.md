# 文字交替变换 (text_alternating)

## 概述
文字组交替变换组件。候选项为文字字符串列表，通过"开始/停止"两个动作控制随机滚动动画，停止时输出最终结果。

这是从抽奖组件中抽象出的核心交替变换逻辑的纯文字版本，推荐替代旧的 label + lottery_animation 方案。

## 模型
- **类**: `TextAlternatingModel` (models/components.py)，继承 `AlternatingModel`
- **类型标识**: `text_alternating`
- **默认尺寸**: 300 × 100
- **display_mode**: 固定为 `"text"`

## 核心属性（继承自 AlternatingModel）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| items | list | [] | 候选项列表（文字字符串） |
| item_labels | list | [] | 候选项标签列表 |
| current_index | int | 0 | 当前显示项索引 |
| animation_duration | int | 3000 | 动画时长(ms)，范围 500~30000 |
| is_running | bool | False | 是否正在运行（只读） |
| display_mode | str | "text" | 固定为 text，不可修改 |

## 信号

| 信号 | 参数 | 说明 |
|------|------|------|
| started | () | 开始交替变换时发射 |
| stopped | (int, str) | 停止时发射，携带 (最终索引, 最终值) |
| current_index_changed | (int) | 当前索引变化时发射 |

## 动作类型

| 动作 | ActionType | 说明 |
|------|-----------|------|
| 开始 | `start_alternating` | 启动随机滚动动画，参数 duration_ms 可选 |
| 停止 | `stop_alternating` | 立即停止，发射 stopped 信号 |

## 动画机制
1. 调用 `start_alternating()` → 预先随机确定最终停留位置
2. QTimer 驱动交替切换，使用 **OutQuart 缓动曲线**（先快后慢）
3. 定时器间隔从 50ms 逐步增加到 350ms
4. 到达 duration_ms 后停在最终位置，发射 `stopped(index, value)`

## 渲染器
- **类**: `AlternatingRenderer` (renderers/alternating_renderer.py)
- 文字模式：28号粗体居中显示当前项
- 底部绘制指示器圆点

## 工厂
- **方法**: `ComponentFactory._create_alternating`
- 运行时创建 QLabel 显示区 + 指示器圆点

## 典型用法
配合两个按钮（开始/停止）+ 一个结果 label：

```python
# 交替变换组件
{'comp_type': 'text_alternating', 'id': 'alt01',
 'items': ['张三', '李四', '王五', '赵六', '钱七'],
 'item_labels': ['张三', '李四', '王五', '赵六', '钱七'],
 'animation_duration': 3000}

# 开始按钮
{'comp_type': 'button', 'text': '开始',
 'action': {'action_type': 'start_alternating',
            'params': {'target_component_id': 'alt01', 'action_params': {'duration_ms': 3000}}}}

# 停止按钮
{'comp_type': 'button', 'text': '停止',
 'action': {'action_type': 'stop_alternating',
            'params': {'target_component_id': 'alt01'}}}

# 联动：stopped 信号 → 结果 label
{'source_component': 'alt01', 'source_event': 'stopped',
 'target_component': 'result_label', 'target_action': 'set_text',
 'params': {'text_template': '结果: {value}'}}
```

## 官方案例
- `samples/文字抽奖示例.py`