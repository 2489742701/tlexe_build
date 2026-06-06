# 列表控件 (listwidget)

## 概述
列表选择控件，基于 QListWidget 实现。模型复用 ComboBoxModel，候选项列表共用 items 属性。

## 模型
- **类**: `ComboBoxModel` (models/components.py) — 复用下拉框模型
- **类型标识**: `listwidget`
- **默认尺寸**: 150 × 200

## 专有属性
与 combobox 相同（items, current_index）。

## 工厂
- **方法**: `ComponentFactory._create_listwidget`
- 运行时创建 `QListWidget`