import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("测试导入链...")
print("=" * 60)

try:
    # 测试导入 models
    print("导入 models...")
    from models import ProjectModel
    print("✓ models 导入成功")
    
    # 测试导入 views
    print("导入 views...")
    from views import MainWindow
    print("✓ views 导入成功")
    
    # 测试导入 controllers
    print("导入 controllers...")
    from controllers import ProjectController
    print("✓ controllers 导入成功")
    
    print("\n所有导入测试通过！")
    print("问题可能在于 QApplication 的创建时机")
    
except Exception as e:
    print(f"导入错误: {e}")
    import traceback
    traceback.print_exc()
