# 复选框 (checkbox)

## 概述
可勾选的复选框组件，支持选中状态和文字对齐。

## 模型
- **类**: `CheckBoxModel` (models/components.py)
- **类型标识**: `checkbox`
- **默认尺寸**: 100 × 30

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| checked | bool | False | 是否选中 |
| alignment | str | "left" | 文字对齐: left/center/right |

## 渲染器
- **类**: `CheckBoxRenderer` (renderers/checkbox_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_checkbox`
- 运行时创建 `QCheckBox`