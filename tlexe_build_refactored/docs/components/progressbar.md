# 进度条 (progressbar)

## 概述
进度指示条组件，支持水平/垂直方向、范围设定和文字显示。也可作为按钮触发窗口跳转。

## 模型
- **类**: `ProgressBarModel` (models/components.py)
- **类型标识**: `progressbar`
- **默认尺寸**: 200 × 25

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| minimum | int | 0 | 最小值 |
| maximum | int | 100 | 最大值 |
| value | int | 0 | 当前值 |
| direction | str | "horizontal" | 方向: horizontal/vertical |
| show_text | bool | False | 是否显示百分比文字 |
| target_window_id | str | "" | 目标窗口ID（可当按钮用） |
| branch_name | str | "" | 分支名称 |

## 渲染器
- **类**: `ProgressBarRenderer` (renderers/progressbar_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_progressbar`
- 运行时创建 `QProgressBar`