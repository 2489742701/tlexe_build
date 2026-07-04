import sys
import os

# 确保能找到项目根目录
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from runtime.runner import Runner
import json

def run_test(json_path: str):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    with open(json_path, 'r', encoding='utf-8') as f:
        project_data = json.load(f)
        
    runner = Runner()
    runner.run(project_data)
    
    # 设置 5 秒后自动关闭
    QTimer.singleShot(5000, app.quit)
    
    # 进入事件循环
    sys.exit(app.exec())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python runtime_test_driver.py <project_json_path>")
        sys.exit(1)
        
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"File not found: {json_file}")
        sys.exit(1)
        
    try:
        run_test(json_file)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(2)
