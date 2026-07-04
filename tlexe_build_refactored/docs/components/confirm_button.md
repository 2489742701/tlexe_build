# 确认按钮 (confirm_button)

## 概述
同组确认按钮，同一 `confirm_group` 内的所有按钮必须全部按下，才触发动作（如跳转下一步）。适用于"用户必须确认所有条款才能继续"等场景。

## 模型
- **类**: `ConfirmButtonModel` (models/components.py)
- **类型标识**: `confirm_button`
- **默认尺寸**: 120 × 40

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| confirm_group | str | "default" | 确认组名称，同组按钮互相关联 |
| is_confirmed | bool | False | 当前按钮是否已确认 |

## 信号

| 信号 | 参数 | 说明 |
|------|------|------|
| all_confirmed | (str) | 同组全部确认时发射，携带 group 名称 |
| confirmed_changed | (str, bool) | 单个按钮确认状态变化，携带 (comp_id, is_confirmed) |

## 交互行为
1. 点击按钮 → 切换 `is_confirmed`（未确认→已确认，再点→取消）
2. 已确认时按钮变绿色
3. 同组所有按钮都确认后，执行按钮的 action（跳转窗口/执行动作）
4. 配置 `confirm_group` 名称来分组，不同组的按钮互不影响

## 渲染器
- 复用 `ButtonRenderer`
- 已确认状态用绿色背景表示

## 工厂
- **方法**: `ComponentFactory._create_confirm_button`

## 使用示例
两个确认按钮同组，都按下后跳转：

```python
# 确认按钮1
{'comp_type': 'confirm_button', 'id': 'cf1',
 'text': '我已阅读条款A', 'confirm_group': 'terms'}

# 确认按钮2
{'comp_type': 'confirm_button', 'id': 'cf2',
 'text': '我已阅读条款B', 'confirm_group': 'terms',
 'target_window_id': 'win_next'}
```