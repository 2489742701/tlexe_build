# 图片轮播 (image_carousel)

## 概述
图片轮播组件，支持自动播放、手动切换和抽奖动画。候选项为图片路径列表。

## 模型
- **类**: `ImageCarouselModel` (models/components.py)
- **类型标识**: `image_carousel`
- **默认尺寸**: 300 × 200

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| images | list | [] | 图片路径列表 |
| image_labels | list | [] | 图片标签列表 |
| current_index | int | 0 | 当前显示索引 |
| interval | int | 2000 | 自动播放间隔(ms) |
| auto_play | bool | False | 是否自动播放 |
| loop | bool | True | 是否循环 |

## 信号
- `lottery_finished(int, str)`: 抽奖动画结束
- `current_index_changed(int)`: 当前索引变化

## 渲染器
- **类**: `ImageCarouselRenderer` (renderers/image_carousel_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_image_carousel`