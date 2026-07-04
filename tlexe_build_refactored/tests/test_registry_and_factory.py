"""组件注册表和工厂完整性测试。

验证：
1. 所有组件在 ComponentRegistry 中注册完备（model/renderer/editor）
2. ComponentFactory.create_widget 支持所有已注册类型
3. ComponentFactory.update_widget 支持所有已注册类型
4. TechComponentManager 模板可用
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.component_registry import ComponentRegistry
from models.registry_init import register_all_components
from utils.component_factory import ComponentFactory

def test_registration_consistency():
    """测试所有注册组件的元数据完整性。"""
    register_all_components()
    reports = ComponentRegistry.check_registration_consistency()
    errors = [r for r in reports if r.severity == "ERROR"]
    warnings = [r for r in reports if r.severity == "WARNING"]

    if errors:
        print("[ERROR] 严重缺失（缺少 model_class）:")
        for r in errors:
            print(f"   - {r.type_name}: 缺失 {', '.join(r.missing_items)}")
    if warnings:
        print("[WARN] 警告（缺少 renderer 或 editor）:")
        for r in warnings:
            print(f"   - {r.type_name}: 缺失 {', '.join(r.missing_items)}")
    if not errors and not warnings:
        print("[OK] 所有组件注册完整")

    return len(errors) == 0

def test_factory_supports_all_registered_types():
    """测试 ComponentFactory 支持所有已注册的组件类型。"""
    register_all_components()
    all_types = ComponentRegistry.get_all_types()
    failed = []

    from models.component_registry import ComponentRegistry as CR
    for comp_type in all_types:
        model_class = CR.get_model_class(comp_type)
        if model_class is None:
            failed.append((comp_type, "没有模型类"))
            continue
        try:
            model = model_class(**{"name": f"test_{comp_type}"})
            widget = ComponentFactory.create_widget(model)
            if widget is None:
                failed.append((comp_type, "create_widget 返回 None"))
        except Exception as e:
            failed.append((comp_type, str(e)))

    if failed:
        print("[FAIL] 工厂创建失败的组件:")
        for t, reason in failed:
            print(f"   - {t}: {reason}")
    else:
        print(f"[OK] 所有 {len(all_types)} 种组件类型均可通过工厂创建")

    return len(failed) == 0

def test_factory_supports_all_update_widget():
    """测试 ComponentFactory.update_widget 支持所有类型。"""
    register_all_components()
    all_types = ComponentRegistry.get_all_types()
    failed = []

    from models.component_registry import ComponentRegistry as CR
    for comp_type in all_types:
        model_class = CR.get_model_class(comp_type)
        if model_class is None:
            failed.append((comp_type, "没有模型类"))
            continue
        try:
            model = model_class(**{"name": f"test_{comp_type}"})
            widget = ComponentFactory.create_widget(model)
            if widget is None:
                failed.append((comp_type, "无法创建控件"))
                continue
            try:
                ComponentFactory.update_widget(widget, model)
            except Exception as e:
                failed.append((comp_type, f"update_widget 失败: {e}"))
        except Exception as e:
            failed.append((comp_type, f"整体失败: {e}"))

    if failed:
        print("[FAIL] update_widget 失败的组件:")
        for t, reason in failed:
            print(f"   - {t}: {reason}")
    else:
        print(f"[OK] 所有 {len(all_types)} 种组件类型均可通过 update_widget 更新")

    return len(failed) == 0

def test_tech_components_available():
    """测试技术类控件模板可访问。"""
    from models.tech_components import TechComponentManager
    templates = TechComponentManager.get_tech_templates()
    expected = ["lottery", "login", "form", "progress_panel"]

    missing = [t for t in expected if t not in templates]
    if missing:
        print(f"[FAIL] 缺失模板: {missing}")
        return False

    for tid in expected:
        try:
            components, linkages = TechComponentManager.create_tech_component(tid)
            if not components:
                print(f"[WARN] 模板 {tid} 生成了空组件列表")
        except Exception as e:
            print(f"[FAIL] 模板 {tid} 生成失败: {e}")
            return False

    print(f"[OK] 所有 {len(expected)} 个技术类控件模板可用")
    return True

def run_all():
    """运行所有完整性测试。"""
    print("=" * 60)
    print("组件注册表和工厂完整性测试")
    print("=" * 60)
    print()

    results = [
        ("注册一致性检查", test_registration_consistency()),
        ("工厂创建支持", test_factory_supports_all_registered_types()),
        ("update_widget支持", test_factory_supports_all_update_widget()),
        ("技术类控件模板", test_tech_components_available()),
    ]

    print()
    print("=" * 60)
    print("汇总")
    print("=" * 60)
    all_pass = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} - {name}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print("[OK] 全部通过")
    else:
        print("[WARN] 存在失败项")

    return all_pass

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
