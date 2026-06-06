# 隐藏按钮 (hidden_button)

## 概述
不可见的触发按钮，用于事件联动。在界面上不显示，但可以接收动作触发或作为联动源。

## 模型
- **类**: `HiddenButtonModel` (models/components.py)
- **类型标识**: `hidden_button`
- **默认尺寸**: 0 × 0

## 专有属性
继承 ButtonModel 的所有属性，额外：

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| trigger_event | str | "click" | 触发事件类型 |

## 渲染器
- **类**: `HiddenButtonRenderer` (renderers/hidden_button_renderer.py)
- 画布中渲染为虚线框 + "隐藏" 标记

## 工厂
- **方法**: `ComponentFactory._create_hidden_button`
- 运行时创建不可见 QPushButton，保留 action 执行能力