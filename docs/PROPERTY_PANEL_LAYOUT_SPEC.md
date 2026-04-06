# 属性面板布局规范

本文档记录属性面板（PropertyPanel）的布局规范，确保布局参数不会被随意修改。

## 1. 滚动区域配置

### 1.1 QScrollArea 配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `setWidgetResizable` | `True` | **必须为True**，否则内容无法自适应滚动 |
| `setFrameShape` | `NoFrame` | 移除边框，保持界面简洁 |
| `HorizontalScrollBarPolicy` | `ScrollBarAlwaysOff` | 禁用水平滚动条，属性面板只需垂直滚动 |
| `VerticalScrollBarPolicy` | `ScrollBarAsNeeded` | 内容超出时才显示垂直滚动条 |

### 1.2 滚动内容配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `setSizePolicy` | `(Expanding, Preferred)` | 宽度自适应，高度根据内容调整 |
| `setMinimumHeight` | `400` | 确保最小高度，避免布局压缩 |

### 1.3 常见问题排查

| 问题 | 排查项 | 解决方法 |
|------|--------|----------|
| 滚动条不出现 | 检查 `setWidgetResizable` 是否为 `True` | 设置 `scroll_area.setWidgetResizable(True)` |
| 内容被截断 | 检查 `setMinimumHeight` 是否设置 | 设置 `scroll_content.setMinimumHeight(200)` |
| 布局错乱 | 检查 `setSizePolicy` 是否正确 | 设置 `scroll_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)` |
| 滚动条样式异常 | 检查 `SCROLL_AREA` 样式是否应用 | 确保 `scroll_area.setStyleSheet(PropertyPanelStyles.SCROLL_AREA)` |
| 内容无法滚动 | 检查 `QVBoxLayout` 的 `addStretch` 是否存在 | 在布局末尾添加 `self._content_layout.addStretch()` |
| 分组框标题被截断 | 检查 `margin-top` 是否足够大 | 增加 `margin-top` 值（如 20px） |
| 内容紧贴边框 | 检查 `padding` 是否设置 | 增加 `padding` 值（如 16px 10px 10px 10px） |
| **分组框内容为空** | 检查 `QGroupBox` 的 `sizePolicy` 是否设置 | 设置 `group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)` |
| **分组框高度不自适应** | 检查 `QGroupBox` 是否设置了固定高度 | 移除 `setFixedHeight` 或改用 `setMinimumHeight` |

## 2. 滚动条样式

### 2.1 样式参数

| 元素 | 属性 | 值 | 说明 |
|------|------|-----|------|
| QScrollArea | border | none | 无边框 |
| QScrollArea | background-color | #ffffff | 白色背景 |
| QScrollBar:vertical | background-color | #f0f0f0 | 淡灰色背景 |
| QScrollBar:vertical | width | 10px | 滚动条宽度 |
| QScrollBar::handle | background-color | #c0c0c0 | 灰色滑块 |
| QScrollBar::handle | min-height | 20px | 滑块最小高度 |
| QScrollBar::handle | border-radius | 5px | 滑块圆角 |
| QScrollBar::handle:hover | background-color | #a0a0a0 | 悬停时颜色加深 |
| QScrollBar::add-line | height | 0px | 隐藏下箭头 |
| QScrollBar::sub-line | height | 0px | 隐藏上箭头 |

### 2.2 注意事项

- `width: 10px` 是合适的滚动条宽度，太小不易操作，太大占用空间
- `border-radius: 5px` 让滚动条更美观
- 隐藏箭头可以节省空间，现代UI通常不需要箭头

## 3. 内容布局参数

### 3.1 间距层级

```
内容区域间距: 32px（分组之间）
    └── 分组内部间距: 18px（属性行之间）
        └── 行内控件间距: 14-16px（标签与控件之间）
```

### 3.2 内容区域边距

| 参数 | 值 | 说明 |
|------|-----|------|
| 左边距 | 18px | 内容与左边缘的距离 |
| 上边距 | 14px | 内容与上边缘的距离 |
| 右边距 | 18px | 内容与右边缘的距离 |
| 下边距 | 24px | 内容与下边缘的距离（较大，避免紧贴底部） |

### 3.3 标签宽度

- 固定宽度: `70px`
- 确保每个标签对齐，视觉效果更一致

## 4. 分组框样式

### 4.1 样式参数

| 属性 | 值 | 说明 |
|------|-----|------|
| font-size | 13px | 标题字号，适中大小 |
| border | 1px solid #e0e0e0 | 淡灰色边框，不突兀 |
| border-radius | 10px | 圆角，现代感 |
| margin-top | 20px | 标题区域高度，给标题留出空间 |
| padding | 20px 14px 14px 14px | 内边距，上20px左右14px下14px |
| background-color | #f8f9fa | 淡灰色背景，区分内容区域 |

### 4.2 注意事项

- `margin-top` 必须足够大以容纳标题
- `padding` 上边距要大于其他边距，避免内容紧贴标题
- 背景色要比滚动区域背景稍深，形成层次感

## 5. 标题头部样式

### 5.1 样式参数

| 属性 | 值 | 说明 |
|------|-----|------|
| background-color | #f1f6fc | 淡蓝色背景，突出显示 |
| border | 1px solid #d8e4ff | 淡蓝色边框，与背景协调 |
| border-radius | 12px | 较大圆角，柔和感 |
| padding | 12px 16px | 内边距，上下12px左右16px |

### 5.2 标题标签

| 属性 | 值 | 说明 |
|------|-----|------|
| font-size | 18px | 较大字号，醒目 |
| font-weight | bold | 粗体 |
| color | #2563eb | 蓝色，与背景协调 |

## 6. 修改记录

| 日期 | 修改内容 | 修改原因 |
|------|----------|----------|
| 2026-04-06 | 初始版本 | 记录布局规范，防止参数被随意修改 |

## 7. 相关文件

- `views/property_panel.py` - 属性面板实现
- `styles/panel_styles.py` - 面板样式定义
- `styles/theme.py` - 主题颜色定义
