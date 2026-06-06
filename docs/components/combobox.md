# 下拉框 (combobox)

## 概述
下拉选择框组件，支持候选项列表和当前选中索引。

## 模型
- **类**: `ComboBoxModel` (models/components.py)
- **类型标识**: `combobox`
- **默认尺寸**: 150 × 28

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| items | list | [] | 下拉候选项列表 |
| current_index | int | 0 | 当前选中索引 |

## 渲染器
- **类**: `ComboBoxRenderer` (renderers/combobox_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_combobox`
- 运行时创建 `QComboBox`