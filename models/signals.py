"""全局信号总线模块。

本模块提供项目级别的统一信号管理中心，实现模块间解耦通信。

## 设计原则
1. **单一职责**：每个信号只负责一种类型的事件传递
2. **命名规范**：信号名称采用 `模块_动作` 格式，如 `project_loaded`
3. **参数明确**：每个信号都有明确的参数类型和含义注释
4. **可追溯性**：信号发射和连接处都有清晰的注释标记

## 使用方式

### 发射信号（信号源）
```python
from models.signals import global_signals

# 发射信号
global_signals.project_loaded.emit("/path/to/project.py")
```

### 连接信号（信号接收者）
```python
from models.signals import global_signals

# 连接信号
global_signals.project_loaded.connect(self._on_project_loaded)
```

## 信号分类

| 分类 | 前缀 | 说明 |
|------|------|------|
| 项目信号 | project_ | 项目级别的操作（加载、保存、关闭） |
| 窗口信号 | window_ | 窗口相关操作（创建、删除、切换） |
| 组件信号 | component_ | 组件相关操作（创建、删除、更新） |
| 编辑器信号 | editor_ | 编辑器操作（撤销、重做、复制） |
| 视图信号 | view_ | 视图切换（树视图、状态机视图） |
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional


class ProjectSignals(QObject):
    """项目相关信号。
    
    用于项目级别的操作通知，如加载、保存、关闭等。
    
    Signals:
        loaded: 项目加载完成
            - 参数 file_path: 项目文件路径
            - 发射时机: 项目文件成功加载后
            - 接收者: MainWindow, LogicTreeView, StateMachineView 等
            
        saved: 项目保存完成
            - 参数 file_path: 项目保存路径
            - 发射时机: 项目成功保存后
            - 接收者: MainWindow, 状态栏等
            
        closed: 项目关闭
            - 参数: 无
            - 发射时机: 项目关闭前
            - 接收者: 各面板进行清理
            
        changed: 项目内容变更
            - 参数: 无
            - 发射时机: 项目内容被修改
            - 接收者: 标题栏显示修改标记
    """
    loaded = Signal(str)
    saved = Signal(str)
    closed = Signal()
    changed = Signal()


class WindowSignals(QObject):
    """窗口相关信号。
    
    用于窗口操作的跨模块通知。
    
    Signals:
        created: 窗口创建完成
            - 参数 window_id: 新创建的窗口ID
            - 发射时机: 窗口模型创建后
            - 接收者: LogicTreeView, StateMachineView
            
        deleted: 窗口删除完成
            - 参数 window_id: 被删除的窗口ID
            - 发射时机: 窗口删除后
            - 接收者: LogicTreeView, StateMachineView
            
        selected: 窗口被选中
            - 参数 window_id: 选中的窗口ID
            - 发射时机: 用户点击选择窗口
            - 接收者: Canvas, PropertyPanel
            
        changed: 窗口属性变更
            - 参数 window_id: 变更的窗口ID
            - 发射时机: 窗口属性被修改
            - 接收者: LogicTreeView, Canvas
    """
    created = Signal(str)
    deleted = Signal(str)
    selected = Signal(str)
    changed = Signal(str)


class ComponentSignals(QObject):
    """组件相关信号。
    
    用于组件操作的跨模块通知。
    
    Signals:
        created: 组件创建完成
            - 参数 comp_id: 新创建的组件ID
            - 发射时机: 组件添加到画布后
            - 接收者: LogicTreeView, PropertyPanel
            
        deleted: 组件删除完成
            - 参数 comp_id: 被删除的组件ID
            - 发射时机: 组件删除后
            - 接收者: LogicTreeView, PropertyPanel
            
        selected: 组件被选中
            - 参数 comp_id: 选中的组件ID（空字符串表示取消选择）
            - 发射时机: 用户点击选择组件
            - 接收者: PropertyPanel, LogicTreeView
            
        multi_selected: 多个组件被选中
            - 参数 comp_ids: 选中的组件ID列表
            - 发射时机: 用户框选多个组件
            - 接收者: PropertyPanel
            
        changed: 组件属性变更
            - 参数 comp_id: 变更的组件ID
            - 发射时机: 组件属性被修改
            - 接收者: LogicTreeView, Canvas
            
        moved: 组件位置移动
            - 参数 comp_id: 移动的组件ID
            - 参数 x: 新X坐标
            - 参数 y: 新Y坐标
            - 发射时机: 组件在画布上移动
            - 接收者: 撤销系统
    """
    created = Signal(str)
    deleted = Signal(str)
    selected = Signal(str)
    multi_selected = Signal(list)
    changed = Signal(str)
    moved = Signal(str, int, int)


class EditorSignals(QObject):
    """编辑器操作信号。
    
    用于编辑操作的跨模块通知。
    
    Signals:
        undo_available: 撤销可用状态变更
            - 参数 available: 是否可撤销
            - 发射时机: 撤销栈状态变化
            - 接收者: 工具栏撤销按钮
            
        redo_available: 重做可用状态变更
            - 参数 available: 是否可重做
            - 发射时机: 重做栈状态变化
            - 接收者: 工具栏重做按钮
            
        copy_available: 复制可用状态变更
            - 参数 available: 是否可复制
            - 发射时机: 选择状态变化
            - 接收者: 工具栏复制按钮
            
        paste_available: 粘贴可用状态变更
            - 参数 available: 是否可粘贴
            - 发射时机: 剪贴板状态变化
            - 接收者: 工具栏粘贴按钮
    """
    undo_available = Signal(bool)
    redo_available = Signal(bool)
    copy_available = Signal(bool)
    paste_available = Signal(bool)


class ViewSignals(QObject):
    """视图切换信号。
    
    用于视图面板的显示/隐藏通知。
    
    Signals:
        logic_tree_toggled: 逻辑树视图切换
            - 参数 visible: 是否显示
            - 发射时机: 用户切换逻辑树面板
            - 接收者: MainWindow
            
        state_machine_toggled: 状态机视图切换
            - 参数 visible: 是否显示
            - 发射时机: 用户切换状态机面板
            - 接收者: MainWindow
            
        property_panel_toggled: 属性面板切换
            - 参数 visible: 是否显示
            - 发射时机: 用户切换属性面板
            - 接收者: MainWindow
    """
    logic_tree_toggled = Signal(bool)
    state_machine_toggled = Signal(bool)
    property_panel_toggled = Signal(bool)


class GlobalSignals(QObject):
    """全局信号总线。
    
    集中管理所有跨模块信号，提供统一的访问入口。
    
    使用示例:
        ```python
        from models.signals import global_signals
        
        # 连接信号
        global_signals.project.loaded.connect(self._on_project_loaded)
        global_signals.window.selected.connect(self._on_window_selected)
        
        # 发射信号
        global_signals.project.loaded.emit("/path/to/project.py")
        global_signals.window.selected.emit(window_id)
        ```
    
    Attributes:
        project: 项目相关信号
        window: 窗口相关信号
        component: 组件相关信号
        editor: 编辑器操作信号
        view: 视图切换信号
    """
    
    def __init__(self):
        super().__init__()
        self.project = ProjectSignals()
        self.window = WindowSignals()
        self.component = ComponentSignals()
        self.editor = EditorSignals()
        self.view = ViewSignals()


global_signals = GlobalSignals()
