"""样式管理模块。

本模块集中管理所有UI样式，将CSS样式从Python代码中分离出来，
提高可维护性和可读性。

## 模块结构
- panel_styles.py: 面板相关样式（属性面板、组件面板等）
- component_styles.py: 组件相关样式（按钮、输入框等）
- theme.py: 主题配置（颜色、字体等）

## 使用示例
```python
from styles import PropertyPanelStyles, ComponentStyles

# 应用属性面板样式
label.setStyleSheet(PropertyPanelStyles.TITLE_LABEL)

# 应用组件样式
button.setStyleSheet(ComponentStyles.HIDDEN_BUTTON)
```
"""

from .panel_styles import PropertyPanelStyles, ComponentPanelStyles
from .component_styles import ComponentStyles, StyleHelper
from .theme import Theme, Colors, Fonts

__all__ = [
    'PropertyPanelStyles',
    'ComponentPanelStyles',
    'ComponentStyles',
    'StyleHelper',
    'Theme',
    'Colors',
    'Fonts',
]