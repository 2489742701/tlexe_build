# 黑白UI图标系统

## 概述

本项目已成功实现黑白UI图标系统，用于替换组件面板中的文本图标，提升视觉效果。

## 更新日期

2026-04-07

## 实现内容

### 1. 图标管理模块 (`utils/icon_manager.py`)

- **SVG图标**：13个矢量图标，支持无损缩放
- **Unicode图标**：备选方案，使用Unicode符号
- **缓存机制**：提高图标加载性能
- **双格式支持**：SVG和Unicode两种格式可选

### 2. 图标资源文件夹 (`icons/`)

包含13个SVG格式的黑白图标文件：
- `button.svg` - 按钮图标
- `checkbox.svg` - 复选框图标（已选中）
- `checkbox_unchecked.svg` - 复选框图标（未选中）
- `combobox.svg` - 下拉框图标
- `container.svg` - 容器图标
- `hidden_button.svg` - 隐藏按钮图标
- `image.svg` - 图片图标
- `image_button.svg` - 图片按钮图标
- `image_carousel.svg` - 图片轮播图标
- `input.svg` - 输入框图标
- `label.svg` - 文本标签图标
- `progressbar.svg` - 进度条图标
- `video.svg` - 视频图标

### 3. 组件面板更新 (`views/component_panel.py`)

- 导入 `IconManager` 图标管理器
- `ComponentButton` 类使用真实图标
- 图标大小：20x20像素
- 保留原有样式和交互效果

## 使用方法

### 基本使用

```python
from utils.icon_manager import IconManager

# 获取图标
icon = IconManager.get_icon("button")

# 在按钮上使用
button.setIcon(icon)
button.setIconSize(QSize(20, 20))
```

### 获取像素图

```python
# 获取指定大小的像素图
pixmap = IconManager.get_pixmap("button", size=32)
```

### 使用Unicode图标

```python
# 使用Unicode符号而非SVG
icon = IconManager.get_icon("button", use_svg=False)
```

### 保存图标到文件

```python
# 将所有SVG图标保存到指定目录
IconManager.save_icons_to_files("path/to/icons")
```

## 测试

运行测试脚本查看所有图标：

```bash
python tests/test_icons.py
```

## 重新生成图标

如果需要重新生成图标文件：

```bash
python scripts/generate_icons.py
```

## 技术特点

1. **矢量图标**：SVG格式，支持无损缩放
2. **黑白风格**：使用 #333333 颜色，简洁专业
3. **性能优化**：图标缓存机制，避免重复渲染
4. **易于扩展**：只需在 `SVG_ICONS` 字典中添加新图标定义
5. **双格式支持**：SVG和Unicode两种格式，兼容性好

## 文件结构

```
tlexe_build/
├── utils/
│   └── icon_manager.py          # 图标管理模块
├── icons/                        # 图标资源文件夹
│   ├── button.svg
│   ├── checkbox.svg
│   ├── ... (其他图标)
│   └── video.svg
├── views/
│   └── component_panel.py       # 已更新的组件面板
├── scripts/
│   └── generate_icons.py        # 图标生成脚本
└── tests/
    └── test_icons.py            # 图标测试脚本
```

## 后续改进建议

1. **主题支持**：添加彩色主题选项
2. **图标编辑器**：可视化图标编辑工具
3. **更多图标**：根据需要添加新的组件图标
4. **动画效果**：为图标添加悬停动画
5. **自定义颜色**：支持用户自定义图标颜色

## 注意事项

- 所有图标使用统一的黑白风格（#333333）
- SVG图标需要 PySide6.QtSvg 模块支持
- 图标缓存会占用一定内存，可在不需要时调用 `IconManager.clear_cache()` 清除
