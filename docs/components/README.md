# 工程组件开发说明索引

本目录包含所有工程组件的开发说明文档。修改组件时必须同步更新对应文档。

## 组件分类

### 基础组件
| 组件 | 类型标识 | 文档 | 说明 |
|------|---------|------|------|
| 按钮 | button | [button.md](button.md) | 可点击交互触发 |
| 确认按钮 | confirm_button | [confirm_button.md](confirm_button.md) | 同组全部按下才触发 |
| 文本标签 | label | [label.md](label.md) | 静态文字显示 |
| 图片 | image | [image.md](image.md) | 图片显示，多缩放模式 |
| 视频 | video | [video.md](video.md) | 视频播放 |
| 进度条 | progressbar | [progressbar.md](progressbar.md) | 进度指示 |
| 隐藏按钮 | hidden_button | [hidden_button.md](hidden_button.md) | 不可见触发器 |
| 图片按钮 | image_button | [image_button.md](image_button.md) | 图片外观按钮 |
| 图片轮播 | image_carousel | [image_carousel.md](image_carousel.md) | 图片自动轮播+抽奖 |

### 输入组件
| 组件 | 类型标识 | 文档 | 说明 |
|------|---------|------|------|
| 输入框 | input | [input.md](input.md) | 单行文本输入 |
| 复选框 | checkbox | [checkbox.md](checkbox.md) | 勾选状态 |
| 下拉框 | combobox | [combobox.md](combobox.md) | 下拉选择 |
| 多行文本框 | textarea | [textarea.md](textarea.md) | 多行输入（复用InputModel） |
| 列表控件 | listwidget | [listwidget.md](listwidget.md) | 列表选择（复用ComboBoxModel） |

### 容器组件
| 组件 | 类型标识 | 文档 | 说明 |
|------|---------|------|------|
| 容器 | container | [container.md](container.md) | 布局容器，子组件嵌套 |
| 组节点 | group_node | [group_node.md](group_node.md) | 逻辑分组 |
| 分组框 | groupbox | [groupbox.md](groupbox.md) | 带标题分组（复用ContainerModel） |

### 交替变换组件（推荐）
| 组件 | 类型标识 | 文档 | 说明 |
|------|---------|------|------|
| 文字交替变换 | text_alternating | [text_alternating.md](text_alternating.md) | **推荐** 文字随机滚动+停止出结果 |
| 图片交替变换 | image_alternating | [image_alternating.md](image_alternating.md) | **推荐** 图片随机滚动+停止出结果 |

### 兼容组件
| 组件 | 类型标识 | 文档 | 说明 |
|------|---------|------|------|
| 抽奖 | lottery | [lottery.md](lottery.md) | 旧接口，推荐用交替变换替代 |

## 修改规范
1. 修改组件 Model 属性 → 同步更新对应 .md 的属性表
2. 新增组件类型 → 新建 .md 并在此索引中添加
3. 修改信号/动作 → 同步更新 .md 的信号表和动作表
4. 修改渲染器/工厂 → 同步更新 .md 的渲染器和工厂章节