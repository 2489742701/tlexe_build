"""主窗口模块。

本模块包含应用程序主窗口的实现，整合所有视图组件。
"""

from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QMenuBar, QMenu, QStatusBar, QFileDialog,
    QMessageBox, QApplication, QInputDialog, QPushButton, QLabel,
    QDockWidget, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QFont

from .canvas import DesignerView
from .component_tree import ComponentTreeView
from .property_panel import PropertyPanel


class MainWindow(QMainWindow):
    """应用程序主窗口。
    
    整合组件树、设计画布和属性面板三个主要视图区域。
    
    Signals:
        new_project: 新建项目时发射
        open_project: 打开项目时发射 (file_path)
        save_project: 保存项目时发射
        save_project_as: 另存为项目时发射 (file_path)
        export_project: 导出项目时发射
        run_project: 运行完整项目时发射（从主窗口开始）
        run_from_current: 从当前窗口运行时发射
        
        add_component: 添加组件时发射 (comp_type, parent_id)
        delete_component: 删除组件时发射 (comp_id)
        rename_component: 重命名组件时发射 (comp_id, new_name)
        
        component_selected: 选中组件时发射 (comp_id)
        property_changed: 属性改变时发射 (comp_id, property_name, new_value)
        action_config_requested: 请求配置行为时发射 (comp_id)
        
        undo_requested: 请求撤销时发射
        redo_requested: 请求重做时发射
        cut_requested: 请求剪切时发射
        copy_requested: 请求复制时发射
        paste_requested: 请求粘贴时发射
    """
    
    # ==================== 信号定义（出口） ====================
    # 【信号出口】项目操作信号
    new_project = Signal()                      # 新建项目请求
    open_project = Signal(str)                  # 打开项目请求，参数：file_path 项目文件路径
    save_project = Signal()                     # 保存项目请求
    save_project_as = Signal(str)               # 另存为项目请求，参数：file_path 目标文件路径
    export_project = Signal()                   # 导出项目请求
    run_project = Signal()                      # 运行完整项目请求（从主窗口开始）
    run_from_current = Signal()                 # 从当前窗口运行请求
    export_to_python = Signal(str)              # 导出为Python脚本请求，参数：file_path 目标文件路径
    import_from_python = Signal(str)            # 从Python脚本导入请求，参数：file_path 源文件路径
    
    # 【信号出口】组件操作信号
    add_component = Signal(str, str)            # 添加组件请求，参数：comp_type 组件类型, parent_id 父组件ID
    delete_component = Signal(str)              # 删除组件请求，参数：comp_id 组件ID
    delete_components = Signal(list)             # 删除多个组件请求，参数：comp_ids 组件ID列表
    rename_component = Signal(str, str)         # 重命名组件请求，参数：comp_id 组件ID, new_name 新名称
    
    # 【信号出口】窗口/事件操作信号
    window_selected = Signal(str)               # 窗口选中信号，参数：window_id 窗口ID
    create_event_requested = Signal(str)        # 创建事件请求，参数：button_id 按钮ID
    delete_window = Signal(str)                 # 删除窗口请求，参数：window_id 窗口ID
    rename_window = Signal(str, str)            # 重命名窗口请求，参数：window_id 窗口ID, new_name 新名称
    
    # 【信号出口】选择和属性信号
    component_selected = Signal(str)            # 组件选中信号，参数：comp_id 组件ID
    property_changed = Signal(str, str, object, object) # 属性改变信号，参数：comp_id 组件ID, property_name 属性名, old_value 旧值, new_value 新值
    action_config_requested = Signal(str)       # 行为配置请求，参数：comp_id 组件ID
    
    # 【信号出口】编辑操作信号
    undo_requested = Signal()                   # 撤销请求
    redo_requested = Signal()                   # 重做请求
    cut_requested = Signal()                    # 剪切请求
    copy_requested = Signal()                   # 复制请求
    paste_requested = Signal()                  # 粘贴请求
    
    def __init__(self):
        """初始化主窗口。"""
        super().__init__()
        
        self.setWindowTitle("UI快速开发工具")
        self.resize(1400, 900)
        
        self._init_ui()
        self._init_menubar()
        self._init_toolbar()
        self._init_statusbar()
        
        # 面板折叠状态
        self._left_panel_visible = True
        self._right_panel_visible = True
    
    def _init_ui(self):
        """初始化UI布局。
        
        【修改说明】
        将程序逻辑树和组件面板分成两个独立的停靠窗口（QDockWidget）。
        这样用户可以：
        1. 拖动面板到任意位置（左、右、上、下）
        2. 将面板浮动显示为独立窗口
        3. 隐藏/显示面板
        4. 自由排列面板位置
        """
        # ==================== 中间画布（中央部件） ====================
        self.designer_view = DesignerView()
        self.designer_view.zoom_changed.connect(self.update_zoom_display)
        self.designer_view.component_selected.connect(self.component_selected.emit)
        self.setCentralWidget(self.designer_view)
        
        # ==================== 程序逻辑树停靠窗口 ====================
        from views.logic_tree import LogicTreeView
        self.logic_tree = LogicTreeView()
        
        # ==================== 信号连接（逻辑树 -> 主窗口） ====================
        # 【信号连接】逻辑树.window_selected -> 主窗口._on_logic_window_selected
        # 用途：选中窗口时切换当前编辑窗口
        self.logic_tree.window_selected.connect(self._on_logic_window_selected)
        
        # 【信号连接】逻辑树.component_selected -> 主窗口._on_tree_component_selected
        # 用途：选中组件时在画布上高亮显示
        self.logic_tree.component_selected.connect(self._on_tree_component_selected)
        
        # 【信号连接】逻辑树.components_selected -> 主窗口._on_tree_components_selected
        # 用途：多选组件时批量操作
        self.logic_tree.components_selected.connect(self._on_tree_components_selected)
        
        # 【信号连接】逻辑树.create_event_requested -> 主窗口._on_create_event_requested
        # 用途：为按钮创建事件分支窗口
        self.logic_tree.create_event_requested.connect(self._on_create_event_requested)
        
        # 【信号连接】逻辑树.delete_component_requested -> 主窗口.delete_component
        # 用途：删除指定组件
        self.logic_tree.delete_component_requested.connect(self.delete_component.emit)
        
        # 【信号连接】逻辑树.delete_window_requested -> 主窗口._on_delete_window
        # 用途：删除指定窗口及其组件
        self.logic_tree.delete_window_requested.connect(self._on_delete_window)
        
        # 【信号连接】逻辑树.rename_requested -> 主窗口._on_rename_item
        # 用途：重命名窗口或组件
        self.logic_tree.rename_requested.connect(self._on_rename_item)
        
        # 【信号连接】逻辑树.open_state_machine_requested -> 主窗口._toggle_state_machine_panel
        # 用途：打开状态机视图面板
        self.logic_tree.open_state_machine_requested.connect(self._toggle_state_machine_panel)
        
        self.tree_view = self.logic_tree
        
        # 创建程序逻辑树停靠窗口
        self._logic_tree_dock = QDockWidget("程序逻辑树", self)
        self._logic_tree_dock.setWidget(self.logic_tree)
        self._logic_tree_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.TopDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._logic_tree_dock)
        self._logic_tree_dock.visibilityChanged.connect(self._on_logic_tree_dock_visibility_changed)
        
        # ==================== 状态机视图（弹窗形式） ====================
        # 状态机视图现在是 QDialog 弹窗，不再需要停靠窗口
        # 弹窗在用户点击"📊"按钮时按需创建和显示
        
        # ==================== 组件面板停靠窗口 ====================
        from .component_panel import ComponentPanel
        self.component_panel = ComponentPanel()
        self.component_panel.component_selected.connect(lambda t: self.add_component.emit(t, ""))
        
        # 创建组件面板停靠窗口
        self._component_panel_dock = QDockWidget("组件面板", self)
        self._component_panel_dock.setWidget(self.component_panel)
        self._component_panel_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.TopDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._component_panel_dock)
        self._component_panel_dock.visibilityChanged.connect(self._on_component_panel_dock_visibility_changed)
        
        # ==================== 右侧停靠窗口（属性面板 + 信号管理） ====================
        # 创建右侧面板内容
        self._right_panel = QWidget()
        right_layout = QVBoxLayout(self._right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 使用选项卡组织右侧面板
        from PySide6.QtWidgets import QTabWidget
        self._right_tabs = QTabWidget()
        self._right_tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # 属性面板选项卡
        self.property_panel = PropertyPanel()
        self.property_panel.property_changed.connect(self.property_changed.emit)
        self.property_panel.action_config_requested.connect(self.action_config_requested.emit)
        self.property_panel.create_event_requested.connect(self._on_create_event_requested)
        self.property_panel.goto_event_requested.connect(self._on_goto_event)
        self._right_tabs.addTab(self.property_panel, "属性")
        
        # 信号管理面板选项卡
        from .signal_manager import SignalManagerPanel
        self.signal_manager_panel = SignalManagerPanel()
        self._right_tabs.addTab(self.signal_manager_panel, "信号")
        
        right_layout.addWidget(self._right_tabs)
        
        # 创建右侧停靠窗口
        self._right_dock = QDockWidget("属性面板", self)
        self._right_dock.setWidget(self._right_panel)
        self._right_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                         Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._right_dock)
        
        # 【重要】连接停靠窗口的可见性变化信号
        # 当用户通过关闭按钮关闭面板时，同步更新菜单项状态
        self._right_dock.visibilityChanged.connect(self._on_right_dock_visibility_changed)
        
        # 【新增】右侧展开提示条（面板隐藏时显示）
        # 这是一个小的提示按钮，让用户知道如何把面板弄回来
        # 使用停靠窗口来显示，这样可以保持在界面布局中
        self._right_expand_dock = QDockWidget("", self)
        self._right_expand_dock.setObjectName("right_expand_dock")
        self._right_expand_dock.setTitleBarWidget(QWidget())  # 隐藏标题栏
        self._right_expand_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        
        # 创建展开按钮
        self._right_expand_bar = QPushButton("属性面板 ◀")
        self._right_expand_bar.setFixedHeight(28)
        self._right_expand_bar.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
                color: #666;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                color: #333;
            }
        """)
        self._right_expand_bar.clicked.connect(self._toggle_right_panel)
        self._right_expand_dock.setWidget(self._right_expand_bar)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._right_expand_dock)
        self._right_expand_dock.hide()  # 默认隐藏
    
    def _create_expand_dock(self, widget, name):
        """创建一个包含展开提示条的小型停靠窗口。
        
        Args:
            widget: 要显示的控件
            name: 停靠窗口的对象名称
            
        Returns:
            QDockWidget: 创建的停靠窗口
        """
        dock = QDockWidget("", self)
        dock.setObjectName(name)
        dock.setWidget(widget)
        dock.setTitleBarWidget(QWidget())  # 隐藏标题栏
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)  # 禁止拖动
        return dock
    
    def _toggle_logic_tree_panel(self):
        """切换程序逻辑树面板的显示/隐藏。"""
        if self._logic_tree_dock.isVisible():
            self._logic_tree_dock.hide()
        else:
            self._logic_tree_dock.show()
    
    def _toggle_state_machine_panel(self):
        """打开状态机视图弹窗。"""
        from views.state_machine_view import StateMachineDialog
        
        dialog = StateMachineDialog(self._project_model, self)
        dialog.window_selected.connect(self._on_logic_window_selected)
        dialog.create_event_requested.connect(self._on_create_event_requested)
        dialog.show()  # 非模态显示
    
    def _toggle_component_panel(self):
        """切换组件面板的显示/隐藏。"""
        if self._component_panel_dock.isVisible():
            self._component_panel_dock.hide()
        else:
            self._component_panel_dock.show()
    
    def _toggle_right_panel(self):
        """切换右侧面板的显示/隐藏。"""
        if self._right_panel_visible:
            self._right_dock.hide()
            self._right_panel_visible = False
            self._right_expand_dock.show()
        else:
            self._right_dock.show()
            self._right_panel_visible = True
            self._right_expand_dock.hide()
    
    def _on_logic_tree_dock_visibility_changed(self, visible: bool):
        """程序逻辑树停靠窗口可见性变化时的回调。"""
        if hasattr(self, '_logic_tree_toolbar_action'):
            self._logic_tree_toolbar_action.setChecked(visible)
        if hasattr(self, '_logic_tree_toggle_action'):
            self._logic_tree_toggle_action.setChecked(visible)
    
    def _on_component_panel_dock_visibility_changed(self, visible: bool):
        """组件面板停靠窗口可见性变化时的回调。"""
        if hasattr(self, '_component_panel_toolbar_action'):
            self._component_panel_toolbar_action.setChecked(visible)
        if hasattr(self, '_component_panel_toggle_action'):
            self._component_panel_toggle_action.setChecked(visible)
    
    def _on_right_dock_visibility_changed(self, visible: bool):
        """右侧停靠窗口可见性变化时的回调。"""
        self._right_panel_visible = visible
        
        if visible:
            self._right_expand_dock.hide()
        else:
            self._right_expand_dock.show()
        
        if hasattr(self, '_right_toolbar_action'):
            self._right_toolbar_action.setChecked(visible)
        
        if hasattr(self, '_right_toggle_action'):
            self._right_toggle_action.setChecked(visible)
    
    def _on_logic_window_selected(self, window_id: str):
        """逻辑树窗口选中时的回调。"""
        self.window_selected.emit(window_id)
    
    def _on_create_event_requested(self, button_id: str):
        """请求创建事件。"""
        self.create_event_requested.emit(button_id)
    
    def _on_delete_window(self, window_id: str):
        """删除窗口。"""
        self.delete_window.emit(window_id)
    
    def _on_rename_item(self, item_id: str, new_name: str, is_window: bool):
        """重命名项目。"""
        if is_window:
            self.rename_window.emit(item_id, new_name)
        else:
            self.rename_component.emit(item_id, new_name)
    
    def _on_goto_event(self, window_id: str):
        """跳转到事件窗口。"""
        self.window_selected.emit(window_id)
    
    def _init_menubar(self):
        """初始化菜单栏。"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project.emit)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开项目(&O)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project.emit)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._on_save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出项目(&E)...", self)
        export_action.triggered.connect(self.export_project.emit)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo_requested.emit)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo_requested.emit)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("剪切(&T)", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_requested.emit)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("复制(&C)", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_requested.emit)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴(&P)", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_requested.emit)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        delete_action = QAction("删除(&D)", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self._on_delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        align_menu = edit_menu.addMenu("对齐(&A)")
        
        align_left_action = QAction("左对齐(&L)", self)
        align_left_action.triggered.connect(self._on_align_left)
        align_menu.addAction(align_left_action)
        
        align_center_action = QAction("水平居中(&C)", self)
        align_center_action.triggered.connect(self._on_align_center)
        align_menu.addAction(align_center_action)
        
        align_right_action = QAction("右对齐(&R)", self)
        align_right_action.triggered.connect(self._on_align_right)
        align_menu.addAction(align_right_action)
        
        align_menu.addSeparator()
        
        align_top_action = QAction("顶对齐(&T)", self)
        align_top_action.triggered.connect(self._on_align_top)
        align_menu.addAction(align_top_action)
        
        align_v_center_action = QAction("垂直居中(&V)", self)
        align_v_center_action.triggered.connect(self._on_align_v_center)
        align_menu.addAction(align_v_center_action)
        
        align_bottom_action = QAction("底对齐(&B)", self)
        align_bottom_action.triggered.connect(self._on_align_bottom)
        align_menu.addAction(align_bottom_action)
        
        component_menu = menubar.addMenu("组件(&C)")
        
        add_button_action = QAction("添加按钮(&B)", self)
        add_button_action.triggered.connect(lambda: self.add_component.emit("button", ""))
        component_menu.addAction(add_button_action)
        
        add_label_action = QAction("添加文本(&L)", self)
        add_label_action.triggered.connect(lambda: self.add_component.emit("label", ""))
        component_menu.addAction(add_label_action)
        
        add_input_action = QAction("添加输入框(&I)", self)
        add_input_action.triggered.connect(lambda: self.add_component.emit("input", ""))
        component_menu.addAction(add_input_action)
        
        add_container_action = QAction("添加容器(&O)", self)
        add_container_action.triggered.connect(lambda: self.add_component.emit("container", ""))
        component_menu.addAction(add_container_action)
        
        component_menu.addSeparator()
        
        add_checkbox_action = QAction("添加复选框(&K)", self)
        add_checkbox_action.triggered.connect(lambda: self.add_component.emit("checkbox", ""))
        component_menu.addAction(add_checkbox_action)
        
        add_combobox_action = QAction("添加下拉框(&D)", self)
        add_combobox_action.triggered.connect(lambda: self.add_component.emit("combobox", ""))
        component_menu.addAction(add_combobox_action)
        
        add_progressbar_action = QAction("添加进度条(&P)", self)
        add_progressbar_action.triggered.connect(lambda: self.add_component.emit("progressbar", ""))
        component_menu.addAction(add_progressbar_action)
        
        run_menu = menubar.addMenu("运行(&R)")
        
        run_action = QAction("运行项目(&R)", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_project.emit)
        run_menu.addAction(run_action)
        
        view_menu = menubar.addMenu("视图(&V)")
        
        zoom_in_action = QAction("放大(&I)", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.designer_view.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小(&O)", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.designer_view.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("重置缩放(&R)", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.designer_view.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        view_menu.addSeparator()
        
        flow_preview_action = QAction("流程图预览(&F)", self)
        flow_preview_action.setShortcut("Ctrl+Shift+F")
        flow_preview_action.triggered.connect(self._show_flow_preview)
        view_menu.addAction(flow_preview_action)
        
        view_menu.addSeparator()
        
        # 切换面板显示的菜单项
        self._logic_tree_toggle_action = QAction("程序逻辑树", self)
        self._logic_tree_toggle_action.setCheckable(True)
        self._logic_tree_toggle_action.setChecked(True)
        self._logic_tree_toggle_action.setShortcut("Ctrl+1")
        self._logic_tree_toggle_action.triggered.connect(self._toggle_logic_tree_panel)
        view_menu.addAction(self._logic_tree_toggle_action)
        
        self._state_machine_action = QAction("状态机视图", self)
        self._state_machine_action.setShortcut("Ctrl+Shift+1")
        self._state_machine_action.triggered.connect(self._toggle_state_machine_panel)
        view_menu.addAction(self._state_machine_action)
        
        self._component_panel_toggle_action = QAction("组件面板", self)
        self._component_panel_toggle_action.setCheckable(True)
        self._component_panel_toggle_action.setChecked(True)
        self._component_panel_toggle_action.setShortcut("Ctrl+2")
        self._component_panel_toggle_action.triggered.connect(self._toggle_component_panel)
        view_menu.addAction(self._component_panel_toggle_action)
        
        self._right_toggle_action = QAction("属性面板", self)
        self._right_toggle_action.setCheckable(True)
        self._right_toggle_action.setChecked(True)
        self._right_toggle_action.setShortcut("Ctrl+3")
        self._right_toggle_action.triggered.connect(self._toggle_right_panel)
        view_menu.addAction(self._right_toggle_action)
        
        settings_menu = menubar.addMenu("设置(&S)")
        
        preferences_action = QAction("首选项(&P)...", self)
        preferences_action.triggered.connect(self._show_preferences)
        settings_menu.addAction(preferences_action)
        
        settings_menu.addSeparator()
        
        file_assoc_action = QAction("注册文件关联(&F)...", self)
        file_assoc_action.triggered.connect(self._on_register_file_association)
        settings_menu.addAction(file_assoc_action)
        
        tools_menu = menubar.addMenu("工具(&T)")
        
        export_py_action = QAction("导出为 Python 脚本(&E)...", self)
        export_py_action.triggered.connect(self._on_export_to_python)
        tools_menu.addAction(export_py_action)
        
        import_py_action = QAction("从 Python 脚本导入(&I)...", self)
        import_py_action.triggered.connect(self._on_import_from_python)
        tools_menu.addAction(import_py_action)
        
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)...", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _init_toolbar(self):
        """初始化工具栏。"""
        from PySide6.QtWidgets import QToolButton, QMenu
        
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        new_btn = QAction("新建", self)
        new_btn.triggered.connect(self.new_project.emit)
        toolbar.addAction(new_btn)
        
        open_btn = QAction("打开", self)
        open_btn.triggered.connect(self._on_open_project)
        toolbar.addAction(open_btn)
        
        save_btn = QAction("保存", self)
        save_btn.triggered.connect(self.save_project.emit)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        component_menu = QMenu(self)
        
        btn_action = QAction("按钮", self)
        btn_action.triggered.connect(lambda: self.add_component.emit("button", ""))
        component_menu.addAction(btn_action)
        
        label_action = QAction("文本", self)
        label_action.triggered.connect(lambda: self.add_component.emit("label", ""))
        component_menu.addAction(label_action)
        
        input_action = QAction("输入框", self)
        input_action.triggered.connect(lambda: self.add_component.emit("input", ""))
        component_menu.addAction(input_action)
        
        container_action = QAction("容器", self)
        container_action.triggered.connect(lambda: self.add_component.emit("container", ""))
        component_menu.addAction(container_action)
        
        checkbox_action = QAction("复选框", self)
        checkbox_action.triggered.connect(lambda: self.add_component.emit("checkbox", ""))
        component_menu.addAction(checkbox_action)
        
        combobox_action = QAction("下拉框", self)
        combobox_action.triggered.connect(lambda: self.add_component.emit("combobox", ""))
        component_menu.addAction(combobox_action)
        
        progressbar_action = QAction("进度条", self)
        progressbar_action.triggered.connect(lambda: self.add_component.emit("progressbar", ""))
        component_menu.addAction(progressbar_action)
        
        component_btn = QToolButton(self)
        component_btn.setText("添加组件")
        component_btn.setMenu(component_menu)
        component_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        component_btn.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        toolbar.addWidget(component_btn)
        
        toolbar.addSeparator()
        
        panel_menu = QMenu(self)
        
        self._logic_tree_toolbar_action = QAction("程序逻辑树", self)
        self._logic_tree_toolbar_action.setCheckable(True)
        self._logic_tree_toolbar_action.setChecked(True)
        self._logic_tree_toolbar_action.triggered.connect(self._toggle_logic_tree_panel)
        panel_menu.addAction(self._logic_tree_toolbar_action)
        
        self._state_machine_panel_action = QAction("状态机视图", self)
        self._state_machine_panel_action.triggered.connect(self._toggle_state_machine_panel)
        panel_menu.addAction(self._state_machine_panel_action)
        
        self._component_panel_toolbar_action = QAction("组件面板", self)
        self._component_panel_toolbar_action.setCheckable(True)
        self._component_panel_toolbar_action.setChecked(True)
        self._component_panel_toolbar_action.triggered.connect(self._toggle_component_panel)
        panel_menu.addAction(self._component_panel_toolbar_action)
        
        self._right_toolbar_action = QAction("属性面板", self)
        self._right_toolbar_action.setCheckable(True)
        self._right_toolbar_action.setChecked(True)
        self._right_toolbar_action.triggered.connect(self._toggle_right_panel)
        panel_menu.addAction(self._right_toolbar_action)
        
        panel_btn = QToolButton(self)
        panel_btn.setText("面板")
        panel_btn.setMenu(panel_menu)
        panel_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        panel_btn.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        toolbar.addWidget(panel_btn)
        
        toolbar.addSeparator()
        
        run_menu = QMenu(self)
        run_full_action = run_menu.addAction("运行完整流程 (F12)")
        run_full_action.setToolTip("从主窗口开始运行整个项目流程")
        run_full_action.triggered.connect(self.run_project.emit)
        run_full_action.setShortcut("F12")
        
        run_current_action = run_menu.addAction("从当前页面运行")
        run_current_action.setToolTip("从当前编辑的窗口开始运行")
        run_current_action.triggered.connect(self.run_from_current.emit)
        
        run_btn = QToolButton(self)
        run_btn.setText("▶ 运行")
        run_btn.setMenu(run_menu)
        run_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        run_btn.setStyleSheet("QToolButton::menu-indicator { subcontrol-position: right center; }")
        run_btn.setDefaultAction(run_full_action)
        run_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.addWidget(run_btn)
    
    def _init_statusbar(self):
        """初始化状态栏。"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self._status_label = QLabel("就绪")
        self.statusbar.addWidget(self._status_label, 1)
        
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(5, 0, 5, 0)
        zoom_layout.setSpacing(3)
        
        zoom_out_btn = QPushButton("➖")
        zoom_out_btn.setFixedSize(24, 24)
        zoom_out_btn.setToolTip("缩小画布 (滚轮向下)")
        zoom_out_btn.clicked.connect(self.designer_view.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        self._zoom_label = QLabel("100%")
        self._zoom_label.setFixedWidth(45)
        self._zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_label.setStyleSheet("color: #666;")
        zoom_layout.addWidget(self._zoom_label)
        
        zoom_in_btn = QPushButton("➕")
        zoom_in_btn.setFixedSize(24, 24)
        zoom_in_btn.setToolTip("放大画布 (滚轮向上)")
        zoom_in_btn.clicked.connect(self.designer_view.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_reset_btn = QPushButton("重置")
        zoom_reset_btn.setFixedHeight(24)
        zoom_reset_btn.setToolTip("重置缩放")
        zoom_reset_btn.clicked.connect(self.designer_view.zoom_reset)
        zoom_layout.addWidget(zoom_reset_btn)
        
        self.statusbar.addPermanentWidget(zoom_widget)
    
    def _on_open_project(self):
        """打开项目对话框。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "项目文件 (*.itexe);;所有文件 (*.*)"
        )
        if file_path:
            self.open_project.emit(file_path)
    
    def _on_save_project_as(self):
        """另存为项目对话框。"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存项目", "", "项目文件 (*.itexe);;所有文件 (*.*)"
        )
        if file_path:
            self.save_project_as.emit(file_path)
    
    def _on_delete_selected(self):
        """删除选中的组件。"""
        selected = self.designer_view.get_selected_items()
        if selected:
            if len(selected) == 1:
                comp_id = selected[0].component_id
                self.delete_component.emit(comp_id)
            else:
                comp_ids = [item.component_id for item in selected]
                self.delete_components.emit(comp_ids)
    
    def _on_align_left(self):
        """左对齐选中的组件。"""
        self.designer_view.align_selected_items("left")
    
    def _on_align_center(self):
        """水平居中对齐选中的组件。"""
        self.designer_view.align_selected_items("center")
    
    def _on_align_right(self):
        """右对齐选中的组件。"""
        self.designer_view.align_selected_items("right")
    
    def _on_align_top(self):
        """顶对齐选中的组件。"""
        self.designer_view.align_selected_items("top")
    
    def _on_align_v_center(self):
        """垂直居中对齐选中的组件。"""
        self.designer_view.align_selected_items("v_center")
    
    def _on_align_bottom(self):
        """底对齐选中的组件。"""
        self.designer_view.align_selected_items("bottom")
    
    def _on_tree_component_selected(self, comp_id: str):
        """树组件选中时的回调。
        
        Args:
            comp_id: 组件ID
        """
        self.designer_view.select_item(comp_id)
        self.component_selected.emit(comp_id)
    
    def _on_tree_components_selected(self, comp_ids: list):
        """树组件多选时的回调。
        
        Args:
            comp_ids: 组件ID列表
        """
        self.designer_view.clear_selection()
        for comp_id in comp_ids:
            item = self.designer_view.get_item(comp_id)
            if item:
                item.setSelected(True)
    
    def _show_flow_preview(self):
        """显示流程图预览窗口。"""
        from .flow_preview import FlowPreviewWidget
        
        if not hasattr(self, '_flow_preview_window') or self._flow_preview_window is None:
            self._flow_preview_window = QMainWindow(self)
            self._flow_preview_window.setWindowTitle("程序流程图预览")
            self._flow_preview_window.resize(800, 600)
            
            self._flow_preview_widget = FlowPreviewWidget()
            self._flow_preview_window.setCentralWidget(self._flow_preview_widget)
        
        if hasattr(self, '_project_model') and self._project_model:
            self._flow_preview_widget.set_project_model(self._project_model)
        
        self._flow_preview_window.show()
        self._flow_preview_window.raise_()
        self._flow_preview_window.activateWindow()
    
    def _show_preferences(self):
        """显示首选项对话框。"""
        from .preferences_dialog import PreferencesDialog
        
        dialog = PreferencesDialog(self)
        dialog.exec()
    
    def set_project_model(self, model):
        """设置项目模型引用。"""
        self._project_model = model
        self.designer_view.set_project_model(model)
    
    def _on_export_to_python(self):
        """导出为 Python 脚本。"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 Python 脚本", "", "Python 文件 (*.py);;所有文件 (*.*)"
        )
        if file_path:
            self.export_to_python.emit(file_path)
    
    def _on_import_from_python(self):
        """从 Python 脚本导入。
        
        【警告说明】
        目前只能从项目导出的 Python 脚本中导入，普通 Python 脚本无法导入。
        """
        reply = QMessageBox.warning(
            self,
            "功能限制提示",
            """<h3>⚠️ 重要提示</h3>
            <p><b>目前此功能只能从本工具导出的 Python 脚本中导入项目数据。</b></p>
            <p>普通 Python 脚本无法转换为项目文件。</p>
            <p>如果您要导入的 Python 脚本是由本工具导出的，请继续。</p>
            <hr>
            <p>是否继续选择文件？</p>""",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择 Python 脚本", "", "Python 文件 (*.py);;所有文件 (*.*)"
            )
            if file_path:
                self.import_from_python.emit(file_path)
    
    def _on_register_file_association(self):
        """注册文件关联。"""
        from utils.file_association import (
            register_file_association, 
            unregister_file_association,
            is_file_association_registered,
            can_register_file_association
        )
        
        can_register, reason = can_register_file_association()
        
        if not can_register:
            QMessageBox.information(self, "文件关联", reason)
            return
        
        if is_file_association_registered():
            reply = QMessageBox.question(
                self,
                "文件关联",
                "文件关联已注册。\n\n是否要注销文件关联？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success, message = unregister_file_association()
                if success:
                    QMessageBox.information(self, "成功", message)
                else:
                    QMessageBox.warning(self, "失败", message)
        else:
            reply = QMessageBox.question(
                self,
                "注册文件关联",
                "是否要注册 .itexe 文件关联？\n\n"
                "注册后，双击 .itexe 文件即可启动程序并加载项目。\n\n"
                "注意：可能需要管理员权限。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success, message = register_file_association()
                if success:
                    QMessageBox.information(self, "成功", message)
                else:
                    QMessageBox.warning(self, "失败", message)
    
    def _on_about(self):
        """显示关于对话框。"""
        QMessageBox.about(
            self,
            "关于傻瓜桌面开发工具",
            """<h2>傻瓜桌面开发工具 v1.0</h2>
            <p>一个简单易用的桌面应用程序可视化开发工具。</p>
            <p>支持拖拽式设计、属性编辑、行为配置等功能。</p>
            <p>让每个人都能轻松创建桌面应用程序！</p>
            """
        )
    
    def set_window_title(self, title: str):
        """设置窗口标题。
        
        Args:
            title: 标题
        """
        self.setWindowTitle(f"{title} - 傻瓜桌面开发工具")
    
    def show_status_message(self, message: str, timeout: int = 3000):
        """显示状态栏消息。
        
        Args:
            message: 消息内容
            timeout: 显示时间（毫秒）
        """
        self._status_label.setText(message)
        if timeout > 0:
            from PySide6.QtCore import QTimer
            
            def clear_message():
                try:
                    if self._status_label is not None:
                        self._status_label.setText("就绪")
                except RuntimeError:
                    pass
            
            QTimer.singleShot(timeout, clear_message)
    
    def update_zoom_display(self, zoom_factor: float):
        """更新缩放比例显示。
        
        Args:
            zoom_factor: 缩放比例
        """
        self._zoom_label.setText(f"{int(zoom_factor * 100)}%")
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """询问确认。
        
        Args:
            title: 对话框标题
            message: 消息内容
            
        Returns:
            用户是否确认
        """
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def show_error(self, title: str, message: str):
        """显示错误对话框。
        
        Args:
            title: 对话框标题
            message: 错误消息
        """
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """显示信息对话框。
        
        Args:
            title: 对话框标题
            message: 消息内容
        """
        QMessageBox.information(self, title, message)






