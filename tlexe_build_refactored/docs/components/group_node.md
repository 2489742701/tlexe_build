# 组节点 (group_node)

## 概述
逻辑分组节点，用于组织组件层级。不产生可见控件，仅作为编辑器中的逻辑分组容器。

## 模型
- **类**: `GroupNodeModel` (models/components.py)
- **类型标识**: `group_node`
- **默认尺寸**: 200 × 150

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| children | list | [] | 子组件ID列表 |
| layout_mode | str | "none" | 布局模式: none/horizontal/vertical/grid |
| spacing | int | 10 | 子组件间距 |
| padding | int | 10 | 内边距 |
| auto_size | bool | False | 是否自适应子组件大小 |
| show_border | bool | True | 是否显示边框 |
| border_style | str | "dashed" | 边框样式: solid/dashed/dotted/none |

## 渲染器
无独立渲染器，在画布中显示为虚线框分组区域