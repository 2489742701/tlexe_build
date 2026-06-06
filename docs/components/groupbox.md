# 分组框 (groupbox)

## 概述
带标题的分组容器，基于 QGroupBox 实现。模型复用 ContainerModel。

## 模型
- **类**: `ContainerModel` (models/components.py) — 复用容器模型
- **类型标识**: `groupbox`
- **默认尺寸**: 200 × 150

## 专有属性
与 container 相同。text 属性作为分组框标题。

## 工厂
- **方法**: `ComponentFactory._create_groupbox`
- 运行时创建 `QGroupBox`，text 作为标题