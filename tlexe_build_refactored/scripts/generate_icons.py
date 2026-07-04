"""生成图标资源文件。

运行此脚本将在 icons 文件夹中生成所有SVG图标文件。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.icon_manager import IconManager

def main():
    """主函数。"""
    icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")
    
    print("=" * 60)
    print("UI快速开发工具 - 图标资源生成器")
    print("=" * 60)
    print()
    
    print(f"图标输出目录: {icons_dir}")
    print()
    
    IconManager.save_icons_to_files(icons_dir)
    
    print()
    print("可用图标列表:")
    print("-" * 60)
    for icon_name in sorted(IconManager.get_available_icons()):
        print(f"  - {icon_name}")
    print()
    
    print("=" * 60)
    print("图标生成完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
