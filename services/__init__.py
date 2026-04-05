"""服务层模块。

本模块包含应用程序级别的服务，负责处理特定的业务逻辑。
通过将服务从主程序中分离，实现职责分离和更好的可测试性。

## 修复说明 (2026-04-02)
根据 MCP 二轮代码审查建议，将 main.py 中 AppManager 的初始化逻辑
抽取到独立的服务模块，解决 AppManager 职责过多的问题。

主要服务：
- AppInitializer: 应用程序初始化协调器
- AutoSaveService: 自动保存服务
"""

from .initialization import AppInitializer
from .auto_save_service import AutoSaveService

__all__ = ['AppInitializer', 'AutoSaveService']
