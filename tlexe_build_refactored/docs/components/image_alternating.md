# 图片交替变换 (image_alternating)

## 概述
图片组交替变换组件。候选项为图片路径列表，通过"开始/停止"两个动作控制随机滚动动画，停止时输出最终结果。

这是从抽奖组件中抽象出的核心交替变换逻辑的纯图片版本，推荐替代旧的 image_carousel + lottery_animation 方案。

## 模型
- **类**: `ImageAlternatingModel` (models/components.py)，继承 `AlternatingModel`
- **类型标识**: `image_alternating`
- **默认尺寸**: 300 × 200
- **display_mode**: 固定为 `"image"`

## 核心属性（继承自 AlternatingModel）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| items | list | [] | 候选项列表（图片路径） |
| item_labels | list | [] | 候选项标签列表 |
| current_index | int | 0 | 当前显示项索引 |
| animation_duration | int | 3000 | 动画时长(ms)，范围 500~30000 |
| is_running | bool | False | 是否正在运行（只读） |
| display_mode | str | "image" | 固定为 image，不可修改 |

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
与 text_alternating 完全相同，使用 OutQuart 缓动曲线先快后慢。

## 渲染器
- **类**: `AlternatingRenderer` (renderers/alternating_renderer.py)
- 图片模式：QPixmap 加载当前项图片，KeepAspectRatioByExpanding 缩放
- 图片加载失败时回退显示 item_labels 文字
- 底部绘制指示器圆点

## 工厂
- **方法**: `ComponentFactory._create_alternating`（与 text_alternating 共用）

## 典型用法
与 text_alternating 相同，只需将 comp_type 改为 `image_alternating`，items 改为图片路径列表。

## 官方案例
- `samples/年会抽奖示例.py`