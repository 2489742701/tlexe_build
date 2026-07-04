# 文本标签 (label)

## 概述
文本显示组件，支持静态文字、自动换行和自适应大小。也支持文字抽奖动画（旧接口，推荐用 text_alternating 替代）。

## 模型
- **类**: `LabelModel` (models/components.py)
- **类型标识**: `label`
- **默认尺寸**: 100 × 30

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| alignment | str | "left" | 文字对齐: left/center/right |
| word_wrap | bool | False | 是否自动换行 |
| auto_size | bool | False | 是否根据内容自适应大小 |

## 信号
- `lottery_finished(int, str)`: 抽奖动画结束时发射（旧接口）
- `current_index_changed(int)`: 当前索引变化

## 动作类型
- `set_text`: 设置标签文本（常用于联动接收结果）

## 渲染器
- **类**: `LabelRenderer` (renderers/label_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_label`
- 运行时创建 `QLabel`，支持对齐、换行、自适应

## 使用示例
```python
{
    'comp_type': 'label',
    'name': '结果',
    'text': '等待结果...',
    'alignment': 'center',
    'word_wrap': True,
}
```