# 多行文本框 (textarea)

## 概述
多行文本输入框，基于 QTextEdit 实现。模型复用 InputModel，运行时工厂创建 QTextEdit。

## 模型
- **类**: `InputModel` (models/components.py) — 复用输入框模型
- **类型标识**: `textarea`
- **默认尺寸**: 200 × 100

## 专有属性
与 input 相同（placeholder, max_length, is_password, is_multiline），其中 is_multiline 固定为 True。

## 工厂
- **方法**: `ComponentFactory._create_textarea`
- 运行时创建 `QTextEdit`（多行编辑）