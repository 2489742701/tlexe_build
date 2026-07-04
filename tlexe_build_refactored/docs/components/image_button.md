# 图片按钮 (image_button)

## 概述
用图片作为外观的按钮组件，同时具备按钮的点击动作和图片的视觉展示能力。

## 模型
- **类**: `ImageButtonModel` (models/components.py)
- **类型标识**: `image_button`
- **默认尺寸**: 120 × 40

## 专有属性
继承 ButtonModel 属性，额外：

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image_path | str | "" | 按钮图片路径 |
| hover_image_path | str | "" | 悬停状态图片路径 |
| pressed_image_path | str | "" | 按下状态图片路径 |
| scale_mode | str | "fit" | 图片缩放模式 |

## 渲染器
- **类**: `ImageButtonRenderer` (renderers/image_button_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_image_button`
- 运行时创建 QPushButton + QIcon，支持三种状态图片