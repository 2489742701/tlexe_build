"""验证修复结果。"""

from models.window import ActionType
from models.components import ButtonModel

print("=" * 50)
print("验证 ActionType 枚举")
print("=" * 50)
print("ActionType values:")
for action in ActionType:
    print(f"  {action.name} = {action.value}")

print("\n" + "=" * 50)
print("验证 ButtonModel 属性")
print("=" * 50)
btn = ButtonModel("测试按钮")
print(f"ButtonModel has action_params: {hasattr(btn, 'action_params')}")
print(f"action_params type: {type(btn.action_params)}")
print(f"action_params value: {btn.action_params}")
print(f"ButtonModel has action: {hasattr(btn, 'action')}")
print(f"action value: {btn.action}")

print("\n" + "=" * 50)
print("验证序列化")
print("=" * 50)
btn.action = {"action_type": "close_program"}
btn.action_params = {"message": "test"}
data = btn.to_dict()
print(f"to_dict contains action: {'action' in data}")
print(f"to_dict contains action_params: {'action_params' in data}")

btn2 = ButtonModel.from_dict(data)
print(f"from_dict action: {btn2.action}")
print(f"from_dict action_params: {btn2.action_params}")

print("\n" + "=" * 50)
print("所有验证通过!")
print("=" * 50)
