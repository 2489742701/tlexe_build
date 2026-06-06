# 抽奖 (lottery)

## 概述
独立抽奖组件，自包含动画逻辑，支持图片/文字双模式。

**注意**: 推荐使用 `text_alternating` / `image_alternating` 替代，它们将"交替变换"逻辑抽象为独立基类，接口更清晰（start/stop 两个动作），且与按钮绑定更自然。lottery 保留作为兼容。

## 模型
- **类**: `LotteryModel` (models/components.py)
- **类型标识**: `lottery`
- **默认尺寸**: 300 × 180

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| items | list | [] | 候选项列表（图片路径或文字） |
| item_labels | list | [] | 候选项标签列表 |
| display_mode | str | "image" | 显示模式: image/text |
| current_index | int | 0 | 当前显示项索引 |
| animation_duration | int | 3000 | 动画时长(ms)，范围 500~30000 |
| is_animating | bool | False | 是否正在执行动画（只读） |

## 信号
- `lottery_finished(int, str)`: 抽奖结束，携带(中奖索引, 中奖标签)
- `current_index_changed(int)`: 当前索引变化

## 动作类型
- `lottery_animation`: 执行抽奖动画（一次性，自动减速停止）

## 与交替变换的区别

| 特性 | lottery | text/image_alternating |
|------|---------|----------------------|
| 控制方式 | 一次性触发 | 开始/停止两个动作 |
| 按钮需求 | 1个（开始抽奖） | 2个（开始+停止） |
| 信号 | lottery_finished | started + stopped |
| 模式切换 | 运行时禁止切换 | 子类固定，不可切换 |
| 推荐度 | 兼容保留 | **推荐** |

## 渲染器
- **类**: `LotteryRenderer` (renderers/lottery_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_lottery`