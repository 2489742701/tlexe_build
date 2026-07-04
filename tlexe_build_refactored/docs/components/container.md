# 容器 (container)

## 概述
布局容器，支持子组件嵌套和多种布局模式。是窗口内容的核心承载组件，通常一个窗口有一个顶层容器。

## 模型
- **类**: `ContainerModel` (models/components.py)
- **类型标识**: `container`
- **默认尺寸**: 400 × 300

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| children | list | [] | 子组件ID列表 |
| position_mode | str | "center" | 定位模式: center/absolute |
| layout | str | "none" | 布局模式: none/horizontal/vertical/grid |
| padding | int | 10 | 内边距 |
| spacing | int | 5 | 子组件间距 |

## 重要说明
- 容器的尺寸**不再覆盖**窗口逻辑尺寸（窗口有独立 width/height）
- 编辑器中调整容器大小会同步画布桌面尺寸，但不修改窗口模型尺寸
- 运行时容器作为 centralWidget 的子组件，位置从 (0,0) 开始

## 渲染器
- **类**: `ContainerRenderer` (renderers/container_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_container`
- 运行时创建 `QFrame` 作为容器