"""逻辑树视图模块。

本模块包含左侧逻辑树面板的实现，用于显示程序的界面流转逻辑。
支持Galgame模式：主程序 -> 按钮 -> 事件窗口的分支结构。

树模式说明：
- 多叉树模式（MULTI_BRANCH）：一个节点下面可以有多个子节点，适合展示集合关系
- 二叉树模式（BINARY）：每个节点严格一分为二，像树枝一样层层往下分叉
"""

from enum import Enum
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QMenu, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon

from models import (
    ProjectModel, ComponentModel, ButtonModel, 
    WindowModel, WindowType, DEFAULT_ACTIONS
)
from models.components import ProgressBarModel


class LogicTreeView(QWidget):
    """逻辑树视图。
    
    展示程序的界面流转逻辑，支持Galgame模式：
    - 主程序窗口作为根节点
    - 按钮自动创建分支，指向事件窗口
    - 事件窗口可以继续包含按钮和组件
    
    支持滚轮缩放功能，用户可以通过滚轮放大/缩小树的显示。
    
    ## 信号说明
    
    ### 输出信号（本组件发射）
    - window_selected(str): 选中窗口时发射
参数为 window_id
        - 接收者：MainWindow._on_logic_window_selected
        - 用途：切换当前编辑窗口
显示该窗口的组件
    
    - component_selected(str): 选中组件时发射，参数为 comp_id
        - 接收者：MainWindow._on_tree_component_selected
        - 用途：在画布上选中对应组件
    
    - components_selected(list): 多选组件选中时发射，参数为 comp_ids
        - 接收者：MainWindow._on_tree_components_selected
        - 用途：批量操作多个组件
    
    - create_event_requested(str): 请求为按钮创建事件时发射，参数为 button_id
        - 接收者：MainWindow._on_create_event_requested
        - 用途：为按钮创建事件分支窗口
    
    - delete_component_requested(str): 请求删除组件时发射，参数为 comp_id
        - 接收者：MainWindow.delete_component
        - 用途：删除指定组件
    
    - delete_window_requested(str): 请求删除窗口时发射，参数为 window_id
        - 接收者：MainWindow._on_delete_window
        - 用途：删除指定窗口及其组件
    
    - rename_requested(str, str, bool): 请求重命名时发射，参数为 item_id, new_name, is_window
        - 接收者：MainWindow._on_rename_item
        - 用途：重命名窗口或组件
    
    - open_state_machine_requested(): 请求打开状态机视图时发射
        - 接收者：MainWindow._toggle_state_machine_panel
        - 用途：打开状态机视图面板
    
    ### 输入信号（本组件接收）
    - set_project_model(model): 设置项目模型，由 MainWindow 调用
        - 用途：初始化逻辑树数据，连接项目信号
 """
    
    # ==================== 信号定义（出口） ====================
    window_selected = Signal(str)
    component_selected = Signal(str)
    components_selected = Signal(list)
    create_event_requested = Signal(str)
    delete_component_requested = Signal(str)
    delete_window_requested = Signal(str)
    rename_requested = Signal(str, str, bool)
    open_state_machine_requested = Signal()
    
    NODE_TYPE_WINDOW = "window"
    NODE_TYPE_COMPONENT = "component"
    
    DEFAULT_FONT_SIZE = 13
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 24
    
    def __init__(self, parent=None):
        """初始化逻辑树视图。
        
        Args:
            parent: 父控件
        """
        super().__init__(parent)
        
        self._project_model: Optional[ProjectModel] = None
        self._node_map: dict = {}
        self._zoom_level: float = 1.0
        self._font_size: int = self.DEFAULT_FONT_SIZE
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI。
        
        【布局说明】
        - 顶部：标题栏
        - 中间：树控件
        - 底部：操作提示和缩放控件
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QLabel("🌳 程序逻辑树")
        header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
            }
        """)
        layout.addWidget(header)
        
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self._tree.setAnimated(True)
        self._tree.setExpandsOnDoubleClick(False)
        self._tree.setHorizontalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self._tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._tree.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self._tree.currentItemChanged.connect(self._on_current_item_changed)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.wheelEvent = self._tree_wheel_event
        layout.addWidget(self._tree, 1)
        
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(5, 5, 5, 5)
        bottom_bar.setSpacing(5)
        
        self._btn_hint = QPushButton("💡")
        self._btn_hint.setFixedSize(28, 28)
        self._btn_hint.setToolTip("点击查看操作提示")
        self._btn_hint.clicked.connect(self._show_hint_popup)
        self._btn_hint.setStyleSheet("""
            QPushButton {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 14px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffe69c;
            }
        """)
        bottom_bar.addWidget(self._btn_hint)
        
        self._btn_state_machine = QPushButton("📊")
        self._btn_state_machine.setFixedSize(28, 28)
        self._btn_state_machine.setToolTip("打开状态机视图")
        self._btn_state_machine.clicked.connect(self._open_state_machine)
        self._btn_state_machine.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 14px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #bbdefb;
            }
        """)
        self._btn_state_machine.setParent(None)
        bottom_bar.addWidget(self._btn_state_machine)
        
        bottom_bar.addStretch()
        
        self._btn_zoom_out = QPushButton("➖")
        self._btn_zoom_out.setFixedSize(28, 28)
        self._btn_zoom_out.setToolTip("缩小 (滚轮向下)")
        self._btn_zoom_out.clicked.connect(self.zoom_out)
        bottom_bar.addWidget(self._btn_zoom_out)
        
        self._zoom_label = QLabel("100%")
        self._zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_label.setFixedWidth(45)
        self._zoom_label.setStyleSheet("color: #666; font-size: 11px;")
        bottom_bar.addWidget(self._zoom_label)
        
        self._btn_zoom_in = QPushButton("➕")
        self._btn_zoom_in.setFixedSize(28, 28)
        self._btn_zoom_in.setToolTip("放大 (滚轮向上)")
        self._btn_zoom_in.clicked.connect(self.zoom_in)
        bottom_bar.addWidget(self._btn_zoom_in)
        
        self._btn_zoom_reset = QPushButton("重置")
        self._btn_zoom_reset.setFixedHeight(28)
        self._btn_zoom_reset.setToolTip("重置缩放")
        self._btn_zoom_reset.clicked.connect(self.zoom_reset)
        bottom_bar.addWidget(self._btn_zoom_reset)
        
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_bar)
        bottom_widget.setStyleSheet("background-color: #fafafa; border-top: 1px solid #ddd;")
        layout.addWidget(bottom_widget)
        
        self._update_tree_style()
    
    def set_project_model(self, model: ProjectModel):
        """设置项目模型。
        
        Args:
            model: 项目模型
        """
        self._project_model = model
        
        # ==================== 信号连接（入口） ====================
        # 【信号入口】项目模型信号 -> 逻辑树视图槽
        model.window_added.connect(self._on_window_added)              # 窗口添加 -> 刷新节点
        model.window_removed.connect(self._on_window_removed)          # 窗口移除 -> 移除节点
        model.window_changed.connect(self._on_window_changed)          # 窗口改变 -> 更新节点
        model.component_added.connect(self._on_component_added)        # 组件添加 -> 添加节点
        model.component_removed.connect(self._on_component_removed)    # 组件移除 -> 移除节点
        model.component_changed.connect(self._on_component_changed)    # 组件改变 -> 更新节点
        model.current_window_changed.connect(self._on_current_window_changed)  # 当前窗口改变 -> 同步选择
        model.project_loaded.connect(self._refresh_tree)               # 项目加载 -> 刷新树
        
        self._refresh_tree()
    
    def _refresh_tree(self):
        """刷新整个树。
        
        根据当前树模式选择不同的渲染方式：
        - 多叉树模式：使用原有的子集复集结构
        - 二叉树模式：每个节点严格一分为二
        """
        self._tree.clear()
        self._node_map.clear()
        
        if not self._project_model:
            return
        
        self._refresh_tree_multi_branch()
    
    def _refresh_tree_multi_branch(self):
        """多叉树模式刷新：一个节点下可以有多个子节点。
        
        这是原有的渲染逻辑，展示子集复集关系。
        """
        main_window = self._project_model.get_main_window()
        if main_window:
            self._add_window_node(main_window)
        
        for window in self._project_model.get_all_windows():
            if window.is_event and window.trigger_button_id:
                self._add_window_node(window)
    
    def _add_window_node(self, window: WindowModel, parent_item: Optional[QTreeWidgetItem] = None):
        """添加窗口节点。
        
        Args:
            window: 窗口模型
            parent_item: 父节点（用于事件窗口挂载在按钮下）
        """
        if window.id in self._node_map:
            return
        
        icon = "🏠" if window.is_main else "📄"
        type_text = "主程序" if window.is_main else "事件"
        item = QTreeWidgetItem(parent_item if parent_item else self._tree)
        item.setText(0, f"{icon} {window.name} ({type_text})")
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": self.NODE_TYPE_WINDOW,
            "id": window.id
        })
        item.setToolTip(0, f"窗口ID: {window.id}\n类型: {type_text}\n大小: {window.width}x{window.height}")
        
        font = item.font(0)
        font.setBold(window.is_main)
        item.setFont(0, font)
        
        self._node_map[window.id] = item
        
        components = self._project_model.get_components_for_window(window.id)
        for comp in components:
            self._add_component_node(comp, item)
        
        if parent_item:
            parent_item.setExpanded(True)
        else:
            self._tree.expandItem(item)
    
    def _add_component_node(self, comp: ComponentModel, parent_item: QTreeWidgetItem):
        """添加组件节点。
        
        Args:
            comp: 组件模型
            parent_item: 父节点
        """
        if comp.id in self._node_map:
            return
        
        type_icons = {
            "button": "🔘",
            "label": "📝",
            "input": "✏️",
            "container": "📦",
        }
        icon = type_icons.get(comp.type, "❓")
        
        item = QTreeWidgetItem(parent_item)
        
        # 显示组件文本（修复：进度条也显示分支名称）
        if isinstance(comp, ButtonModel) and comp.has_branch:
            text = f"{icon} {comp.text} → {comp.branch_name}"
        elif isinstance(comp, ProgressBarModel) and comp.has_branch:
            text = f"{icon} {comp.text or comp.name} → {comp.branch_name or '完成'}"
        else:
            text = f"{icon} {comp.text or comp.name}"
        
        item.setText(0, text)
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": self.NODE_TYPE_COMPONENT,
            "id": comp.id
        })
        item.setToolTip(0, f"组件ID: {comp.id}\n类型: {comp.type}\n位置: ({comp.x}, {comp.y})")
        
        self._node_map[comp.id] = item
        
        # 处理按钮的分支
        if isinstance(comp, ButtonModel) and comp.target_window_id:
            target_window = self._project_model.get_window(comp.target_window_id)
            if target_window:
                self._add_window_node(target_window, item)
        
        # 处理进度条的分支（修复：进度条完成后跳转到目标窗口）
        if isinstance(comp, ProgressBarModel) and comp.target_window_id:
            target_window = self._project_model.get_window(comp.target_window_id)
            if target_window:
                self._add_window_node(target_window, item)
        
        parent_item.setExpanded(True)
    
    def _on_window_added(self, window_id: str):
        """窗口添加时的回调。"""
        if not self._project_model:
            return
        
        window = self._project_model.get_window(window_id)
        if not window:
            return
        
        if window.is_event and window.trigger_button_id:
            button_item = self._node_map.get(window.trigger_button_id)
            if button_item:
                self._add_window_node(window, button_item)
                return
        
        self._add_window_node(window)
    
    def _on_window_removed(self, window_id: str):
        """窗口移除时的回调。"""
        if window_id in self._node_map:
            item = self._node_map[window_id]
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self._tree.indexOfTopLevelItem(item)
                self._tree.takeTopLevelItem(index)
            
            del self._node_map[window_id]
    
    def _on_window_changed(self, window_id: str):
        """窗口变化时的回调。"""
        if window_id not in self._node_map:
            return
        
        if not self._project_model:
            return
        
        window = self._project_model.get_window(window_id)
        if not window:
            return
        
        item = self._node_map[window_id]
        icon = "🏠" if window.is_main else "📄"
        type_text = "主程序" if window.is_main else "事件"
        item.setText(0, f"{icon} {window.name} ({type_text})")
    
    def _on_component_added(self, comp_id: str):
        """组件添加时的回调。"""
        if not self._project_model:
            return
        
        comp = self._project_model.get_component(comp_id)
        if not comp:
            return
        
        current_window = self._project_model.current_window
        if not current_window:
            return
        
        window_item = self._node_map.get(current_window.id)
        if window_item:
            self._add_component_node(comp, window_item)
    
    def _on_component_removed(self, comp_id: str):
        """组件移除时的回调。"""
        if comp_id in self._node_map:
            item = self._node_map[comp_id]
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            
            del self._node_map[comp_id]
    
    def _on_component_changed(self, comp_id: str):
        """组件变化时的回调。"""
        if comp_id not in self._node_map:
            return
        
        if not self._project_model:
            return
        
        comp = self._project_model.get_component(comp_id)
        if not comp:
            return
        
        item = self._node_map[comp_id]
        
        type_icons = {
            "button": "🔘",
            "label": "📝",
            "input": "✏️",
            "container": "📦",
        }
        icon = type_icons.get(comp.type, "❓")
        
        if isinstance(comp, ButtonModel) and comp.has_branch:
            text = f"{icon} {comp.text} → {comp.branch_name}"
        else:
            text = f"{icon} {comp.text or comp.name}"
        
        item.setText(0, text)
    
    def _on_current_window_changed(self, window_id: str):
        """当前窗口切换时的回调。"""
        if window_id in self._node_map:
            item = self._node_map[window_id]
            self._tree.setCurrentItem(item)
    
    def _on_current_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        """当前项改变时的回调。"""
        if not current:
            return
        
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == self.NODE_TYPE_WINDOW:
            self.window_selected.emit(data["id"])
        elif data["type"] == self.NODE_TYPE_COMPONENT:
            self.component_selected.emit(data["id"])
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """项双击时的回调。"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == self.NODE_TYPE_WINDOW:
            self._on_rename_window(data["id"])
        elif data["type"] == self.NODE_TYPE_COMPONENT:
            self._on_rename_component(data["id"])
    
    def _on_context_menu(self, position):
        """显示上下文菜单。"""
        item = self._tree.itemAt(position)
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        menu = QMenu(self)
        
        if data["type"] == self.NODE_TYPE_WINDOW:
            self._build_window_context_menu(menu, data["id"])
        elif data["type"] == self.NODE_TYPE_COMPONENT:
            self._build_component_context_menu(menu, data["id"])
        
        menu.exec(self._tree.viewport().mapToGlobal(position))
    
    def _build_window_context_menu(self, menu: QMenu, window_id: str):
        """构建窗口节点的上下文菜单。"""
        if not self._project_model:
            return
        
        window = self._project_model.get_window(window_id)
        if not window:
            return
        
        rename_action = QAction("✏️ 重命名", self)
        rename_action.triggered.connect(lambda: self._on_rename_window(window_id))
        menu.addAction(rename_action)
        
        if window.is_main:
            menu.addSeparator()
            info_action = QAction("ℹ️ 主程序入口", self)
            info_action.setEnabled(False)
            menu.addAction(info_action)
        else:
            menu.addSeparator()
            
            delete_action = QAction("🗑️ 删除事件", self)
            delete_action.triggered.connect(lambda: self._on_delete_window(window_id))
            menu.addAction(delete_action)
    
    def _build_component_context_menu(self, menu: QMenu, comp_id: str):
        """构建组件节点的上下文菜单。"""
        if not self._project_model:
            return
        
        comp = self._project_model.get_component(comp_id)
        if not comp:
            return
        
        rename_action = QAction("✏️ 重命名", self)
        rename_action.triggered.connect(lambda: self._on_rename_component(comp_id))
        menu.addAction(rename_action)
        
        # 按钮的右键菜单
        if isinstance(comp, ButtonModel):
            menu.addSeparator()
            
            if not comp.has_branch:
                create_event_action = QAction("➕ 创建事件分支", self)
                create_event_action.triggered.connect(lambda: self.create_event_requested.emit(comp_id))
                menu.addAction(create_event_action)
            else:
                goto_event_action = QAction("🔗 跳转到事件", self)
                goto_event_action.triggered.connect(lambda: self._goto_window(comp.target_window_id))
                menu.addAction(goto_event_action)
        
        # 进度条的右键菜单（修复：添加跳转到事件选项）
        if isinstance(comp, ProgressBarModel):
            menu.addSeparator()
            
            if comp.target_window_id:
                goto_event_action = QAction("🔗 跳转到事件", self)
                goto_event_action.triggered.connect(lambda: self._goto_window(comp.target_window_id))
                menu.addAction(goto_event_action)
            else:
                create_event_action = QAction("➕ 创建事件分支", self)
                create_event_action.triggered.connect(lambda: self.create_event_requested.emit(comp_id))
                menu.addAction(create_event_action)
        
        menu.addSeparator()
        
        delete_action = QAction("🗑️ 删除组件", self)
        delete_action.triggered.connect(lambda: self.delete_component_requested.emit(comp_id))
        menu.addAction(delete_action)
    
    def _on_rename_window(self, window_id: str):
        """重命名窗口。"""
        if not self._project_model:
            return
        
        window = self._project_model.get_window(window_id)
        if not window:
            return
        
        new_name, ok = QInputDialog.getText(
            self, "重命名窗口", "新名称:", 
            text=window.name
        )
        
        if ok and new_name:
            self.rename_requested.emit(window_id, new_name, True)
    
    def _on_rename_component(self, comp_id: str):
        """重命名组件。"""
        if not self._project_model:
            return
        
        comp = self._project_model.get_component(comp_id)
        if not comp:
            return
        
        if comp.type == 'container':
            return
        
        new_name, ok = QInputDialog.getText(
            self, "重命名组件", "新名称:", 
            text=comp.name
        )
        
        if ok and new_name:
            self.rename_requested.emit(comp_id, new_name, False)
    
    def _on_delete_window(self, window_id: str):
        """删除窗口。"""
        if not self._project_model:
            return
        
        window = self._project_model.get_window(window_id)
        if not window or window.is_main:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除事件「{window.name}」吗？\n这将同时删除该事件中的所有组件。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_window_requested.emit(window_id)
    
    def _goto_window(self, window_id: str):
        """跳转到指定窗口。"""
        if window_id in self._node_map:
            item = self._node_map[window_id]
            self._tree.setCurrentItem(item)
            self._tree.expandItem(item)
            
            parent = item.parent()
            while parent:
                self._tree.expandItem(parent)
                parent = parent.parent()
    
    def select_component(self, comp_id: str):
        """选中指定组件。"""
        if comp_id in self._node_map:
            item = self._node_map[comp_id]
            self._tree.setCurrentItem(item)
            
            parent = item.parent()
            while parent:
                parent.setExpanded(True)
                parent = parent.parent()
    
    def select_window(self, window_id: str):
        """选中指定窗口。"""
        if window_id in self._node_map:
            item = self._node_map[window_id]
            self._tree.setCurrentItem(item)
    
    def clear_selection(self):
        """清除选择。"""
        self._tree.clearSelection()
    
    def _update_tree_style(self):
        """更新树的样式（根据缩放级别）。"""
        padding = max(3, int(6 * self._zoom_level))
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                border: 1px solid #cccccc;
                background-color: #fafafa;
                font-size: {self._font_size}px;
            }}
            QTreeWidget::item {{
                padding: {padding}px;
                border-bottom: 1px solid #eeeeee;
            }}
            QTreeWidget::item:selected {{
                background-color: #0078d7;
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: #e5f3ff;
            }}
            QLabel {{
                color: #333333;
            }}
            QPushButton {{
                padding: 3px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
        """)
        
        self._zoom_label.setText(f"{int(self._zoom_level * 100)}%")
    
    def _tree_wheel_event(self, event):
        """树的滚轮事件处理。
        
        Ctrl+滚轮：缩放
        普通滚轮：滚动
        """
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            QTreeWidget.wheelEvent(self._tree, event)
    
    def _show_hint_popup(self):
        """显示操作提示弹出框。"""
        from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
        
        if hasattr(self, '_hint_popup') and self._hint_popup is not None:
            self._hint_popup.close()
            self._hint_popup = None
            return
        
        popup = QFrame(self)
        popup.setWindowFlags(Qt.WindowType.Popup)
        popup.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #856404;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(popup)
        layout.setSpacing(8)
        
        title = QLabel("📋 操作提示")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)
        
        hints = [
            "• 点击按钮自动创建分支窗口",
            "• 右键点击项目可重命名或删除",
            "• 双击窗口可快速跳转",
            "• 滚轮可缩放树视图",
            "• 🌳/🌿 切换多叉树/二叉树模式",
        ]
        
        for hint in hints:
            label = QLabel(hint)
            label.setWordWrap(True)
            layout.addWidget(label)
        
        btn_pos = self._btn_hint.mapToGlobal(self._btn_hint.rect().bottomLeft())
        popup.move(btn_pos.x(), btn_pos.y() + 5)
        popup.show()
        
        self._hint_popup = popup
    
    def zoom_in(self):
        """放大树视图。"""
        if self._font_size < self.MAX_FONT_SIZE:
            self._zoom_level = min(2.0, self._zoom_level + 0.1)
            self._font_size = min(self.MAX_FONT_SIZE, int(self.DEFAULT_FONT_SIZE * self._zoom_level))
            self._update_tree_style()
    
    def zoom_out(self):
        """缩小树视图。"""
        if self._font_size > self.MIN_FONT_SIZE:
            self._zoom_level = max(0.5, self._zoom_level - 0.1)
            self._font_size = max(self.MIN_FONT_SIZE, int(self.DEFAULT_FONT_SIZE * self._zoom_level))
            self._update_tree_style()
    
    def zoom_reset(self):
        """重置缩放。"""
        self._zoom_level = 1.0
        self._font_size = self.DEFAULT_FONT_SIZE
        self._update_tree_style()
    
    @property
    def zoom_level(self) -> float:
        """获取当前缩放级别。"""
        return self._zoom_level
    
    def _open_state_machine(self):
        """打开状态机视图。"""
        self.open_state_machine_requested.emit()



