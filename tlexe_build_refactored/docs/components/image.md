# 图片 (image)

## 概述
图片显示组件，支持多种缩放模式、圆角、透明度、悬停效果。

## 模型
- **类**: `ImageModel` (models/components.py)
- **类型标识**: `image`
- **默认尺寸**: 200 × 150

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image_path | str | "" | 图片文件路径 |
| aspect_ratio | bool | True | 是否保持宽高比（旧属性，推荐用 scale_mode） |
| scale_mode | str | "fit" | 缩放模式: fill/fit/stretch/center/tile |
| border_radius | int | 0 | 圆角半径 |
| opacity | float | 1.0 | 透明度 (0.0~1.0) |
| hover_effect | bool | False | 是否启用悬停效果 |
| click_action | str | "none" | 点击动作: none/zoom/open_original |
| placeholder_text | str | "点击选择图片" | 无图片时的占位文字 |

## 渲染器
- **类**: `ImageRenderer` (renderers/image_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_image`
- 运行时创建 `QLabel`，加载 QPixmap 显示图片

## 使用示例
```python
{
    'comp_type': 'image',
    'name': '头像',
    'image_path': 'avatar.png',
    'scale_mode': 'fit',
    'border_radius': 50,
}
```