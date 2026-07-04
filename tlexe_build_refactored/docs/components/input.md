# 输入框 (input)

## 概述
单行文本输入框，支持占位符、最大长度、密码模式和密码显示切换。

## 模型
- **类**: `InputModel` (models/components.py)
- **类型标识**: `input`
- **默认尺寸**: 200 × 30

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| placeholder | str | "" | 占位提示文字 |
| max_length | int | 32767 | 最大输入长度 |
| is_password | bool | False | 是否为密码输入框 |
| is_multiline | bool | False | 是否多行（内部标记） |

## 渲染器
- **类**: `InputRenderer` (renderers/input_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_input`
- 运行时创建 `QLineEdit`，密码模式用 `setEchoMode`