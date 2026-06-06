# 视频 (video)

## 概述
视频播放组件，基于 QMediaPlayer 实现视频加载和播放控制。

## 模型
- **类**: `VideoModel` (models/components.py)
- **类型标识**: `video`
- **默认尺寸**: 320 × 240

## 专有属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| video_path | str | "" | 视频文件路径 |
| auto_play | bool | False | 是否自动播放 |
| muted | bool | False | 是否静音 |
| volume | int | 100 | 音量 (0~100) |
| loop | bool | False | 是否循环播放 |
| show_controls | bool | True | 是否显示播放控制栏 |

## 渲染器
- **类**: `VideoRenderer` (renderers/video_renderer.py)

## 工厂
- **方法**: `ComponentFactory._create_video`
- 运行时创建视频播放控件