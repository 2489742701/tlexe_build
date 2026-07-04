import json
with open('tlexe_build/samples/年会抽奖示例.itexe', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== Linkages ===")
for linkage in data.get('linkages', []):
    print(f"Source: {linkage.get('source_component')}")
    print(f"  Event: {linkage.get('source_event')}")
    print(f"  Target: {linkage.get('target_component')}")
    print(f"  Action: {linkage.get('target_action')}")
    print(f"  Params: {linkage.get('params')}")
    print()