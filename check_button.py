import json
with open('tlexe_build/samples/年会抽奖示例.itexe', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== Button Components ===")
for comp in data.get('components', []):
    if comp.get('comp_type') == 'button':
        print(f"Button: {comp.get('name')}")
        print(f"  ID: {comp.get('id')}")
        print(f"  action: {comp.get('action')}")
        print(f"  target_window_id: {comp.get('target_window_id', 'N/A')}")
        print()