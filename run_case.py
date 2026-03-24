"""测试运行脚本。

用于测试项目的基本功能。
"""

import sys
from PySide6.QtWidgets import QApplication

from models import ProjectModel
from runtime.runner import Runner
from templates import get_test_template


def main():
    """主函数。"""
    app = QApplication(sys.argv)
    
    project_model = ProjectModel()
    template_data = get_test_template()
    project_model.from_dict(template_data)
    
    print(f"项目名称: {project_model.name}")
    print(f"组件数量: {len(project_model.get_all_components())}")
    print(f"窗口数量: {len(project_model.get_all_windows())}")
    
    runner = Runner()
    runner.run(project_model.to_dict())
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
