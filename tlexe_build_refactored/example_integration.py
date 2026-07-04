"""集成示例 - 展示如何使用新的架构模块。

本示例展示如何将新的架构集成到现有项目中：
1. 使用 SignalManager 管理信号-事件
2. 使用 ViewManager 管理视图切换
3. 使用 LayoutRefreshManager 解决布局问题
4. 使用 LeftPanelManager 管理左侧面板
"""

import sys
import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSplitter, QTextEdit,
    QTreeWidget, QTreeWidgetItem, QMenuBar, QMenu
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入新架构模块
from core.signal_event_system import (
    SignalManager, Signal, Event,
    SignalType, EventType,
    create_signal_event_pair
)
from fixes.view_manager import ViewManager
from fixes.ui_fixes import (
    LayoutRefreshManager, LeftPanelManager,
    SignalRegistry, NavigationHelper
)

class MainWindow(QMainWindow):
    """主窗口示例。
    
    展示如何集成新的架构模块。
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TLexe - 集成示例")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化架构组件
        self._init_architecture()
        
        # 构建UI
        self._setup_ui()
        
        # 连接信号
        self._connect_signals()
        
        logger.info("主窗口初始化完成")
    
    def _init_architecture(self):
        """初始化架构组件。"""
        # 1. 信号管理器（核心数据模型）
        self.signal_manager = SignalManager(self)
        
        # 2. 布局刷新管理器（解决文本居中问题）
        self.layout_manager = LayoutRefreshManager(self)
        
        # 3. 左侧面板管理器（解决逻辑树显示问题）
        self.left_panel_manager = LeftPanelManager(self)
        
        # 4. 信号注册表（简化版信号管理）
        self.signal_registry = SignalRegistry(self)
        
        logger.info("架构组件初始化完成")
    
    def _setup_ui(self):
        """设置UI。"""
        # 创建菜单栏
        self._setup_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局：左右分割
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧：逻辑树 + 组件面板
        self._setup_left_panel()
        main_layout.addWidget(self.left_splitter, 1)
        
        # 右侧：视图区域
        self._setup_right_panel()
        main_layout.addWidget(self.stacked_widget, 3)
    
    def _setup_menu_bar(self):
        """设置菜单栏。"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("新建项目", self._on_new_project)
        file_menu.addAction("打开项目", self._on_open_project)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        view_menu.addAction("主菜单", lambda: self.view_manager.switch_to("main_menu"))
        view_menu.addAction("编辑器", lambda: self.view_manager.switch_to("editor"))
        view_menu.addAction("游戏视图", lambda: self.view_manager.switch_to("game"))
    
    def _setup_left_panel(self):
        """设置左侧面板。"""
        # 程序逻辑树
        self.logic_tree = QTreeWidget()
        self.logic_tree.setObjectName("logic_tree")
        self.logic_tree.setHeaderLabel("程序逻辑树")
        
        # 添加示例节点
        root = QTreeWidgetItem(self.logic_tree, ["主程序"])
        container1 = QTreeWidgetItem(root, ["容器 1"])
        container2 = QTreeWidgetItem(root, ["容器 2"])
        QTreeWidgetItem(container1, ["按钮 1"])
        QTreeWidgetItem(container1, ["文本 1"])
        QTreeWidgetItem(container2, ["图片 1"])
        self.logic_tree.expandAll()
        
        # 组件面板
        self.component_panel = QWidget()
        self.component_panel.setObjectName("component_panel")
        comp_layout = QVBoxLayout(self.component_panel)
        comp_layout.addWidget(QLabel("组件面板"))
        
        # 添加一些示例按钮
        add_btn = QPushButton("添加信号")
        add_btn.clicked.connect(self._on_add_signal)
        comp_layout.addWidget(add_btn)
        
        reg_btn = QPushButton("注册信号")
        reg_btn.clicked.connect(self._on_register_signal)
        comp_layout.addWidget(reg_btn)
        
        comp_layout.addStretch()
        
        # 使用 LeftPanelManager 设置布局
        self.left_splitter = self.left_panel_manager.setup_layout(
            self.logic_tree, self.component_panel
        )
    
    def _setup_right_panel(self):
        """设置右侧面板（视图区域）。"""
        # 创建堆叠部件
        self.stacked_widget = QStackedWidget()
        
        # 1. 主菜单视图
        self.main_menu_view = self._create_main_menu_view()
        self.stacked_widget.addWidget(self.main_menu_view)
        
        # 2. 编辑器视图
        self.editor_view = self._create_editor_view()
        self.stacked_widget.addWidget(self.editor_view)
        
        # 3. 游戏视图
        self.game_view = self._create_game_view()
        self.stacked_widget.addWidget(self.game_view)
        
        # 使用 ViewManager 管理视图
        self.view_manager = ViewManager(self.stacked_widget, self)
        self.view_manager.register_view("main_menu", self.main_menu_view, make_default=True)
        self.view_manager.register_view("editor", self.editor_view)
        self.view_manager.register_view("game", self.game_view)
    
    def _create_main_menu_view(self) -> QWidget:
        """创建主菜单视图。"""
        view = QWidget()
        view.setObjectName("main_menu_view")
        layout = QVBoxLayout(view)
        layout.setAlignment(Qt.AlignCenter)
        
        # 标题 - 使用 LayoutRefreshManager 确保居中
        title = QLabel("主菜单")
        title.setObjectName("main_title")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 使用延迟刷新确保文本居中
        self.layout_manager.schedule_refresh(title, 100)
        
        # 按钮
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        new_btn = QPushButton("新建项目")
        new_btn.setMinimumWidth(200)
        new_btn.clicked.connect(self._on_new_project)
        btn_layout.addWidget(new_btn)
        
        open_btn = QPushButton("打开项目")
        open_btn.setMinimumWidth(200)
        open_btn.clicked.connect(self._on_open_project)
        btn_layout.addWidget(open_btn)
        
        editor_btn = QPushButton("进入编辑器")
        editor_btn.setMinimumWidth(200)
        editor_btn.clicked.connect(lambda: self.view_manager.switch_to("editor"))
        btn_layout.addWidget(editor_btn)
        
        game_btn = QPushButton("开始游戏")
        game_btn.setMinimumWidth(200)
        game_btn.clicked.connect(lambda: self.view_manager.switch_to("game"))
        btn_layout.addWidget(game_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return view
    
    def _create_editor_view(self) -> QWidget:
        """创建编辑器视图。"""
        view = QWidget()
        view.setObjectName("editor_view")
        layout = QVBoxLayout(view)
        
        # 标题
        title = QLabel("编辑器")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 内容区域
        content = QTextEdit()
        content.setPlaceholderText("在此编辑内容...")
        layout.addWidget(content)
        
        # 返回按钮
        back_btn = QPushButton("返回主菜单")
        back_btn.clicked.connect(lambda: self.view_manager.switch_to("main_menu"))
        layout.addWidget(back_btn)
        
        return view
    
    def _create_game_view(self) -> QWidget:
        """创建游戏视图。"""
        view = QWidget()
        view.setObjectName("game_view")
        layout = QVBoxLayout(view)
        layout.setAlignment(Qt.AlignCenter)
        
        # 游戏标题 - 使用延迟刷新确保居中
        title = QLabel("游戏内容区域")
        title.setObjectName("game_title")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 使用延迟刷新确保文本居中
        self.layout_manager.schedule_refresh(title, 150)
        
        # 游戏说明
        desc = QLabel("这是游戏内容区域，文本应该居中显示")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # 返回按钮
        back_btn = QPushButton("返回主菜单")
        back_btn.setMinimumWidth(200)
        back_btn.clicked.connect(lambda: self.view_manager.switch_to("main_menu"))
        layout.addWidget(back_btn)
        
        layout.addStretch()
        
        return view
    
    def _connect_signals(self):
        """连接信号。"""
        # 监听视图切换
        self.view_manager.view_changed.connect(self._on_view_changed)
        
        # 监听信号注册
        self.signal_registry.signal_registered.connect(self._on_signal_registered)
    
    def _on_view_changed(self, from_view: str, to_view: str):
        """视图切换回调。"""
        logger.info(f"视图切换: {from_view} -> {to_view}")
        
        # 切换后刷新布局（解决文本居中问题）
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            self.layout_manager.schedule_refresh(current_widget, 50)
    
    def _on_add_signal(self):
        """添加信号按钮回调。"""
        import uuid
        signal_name = f"信号_{len(self.signal_registry.get_all_signals()) + 1}"
        signal = self.signal_registry.create_signal(signal_name)
        logger.info(f"创建信号: {signal_name} ({signal.id})")
    
    def _on_register_signal(self):
        """注册信号按钮回调。"""
        signals = self.signal_registry.get_all_signals()
        if not signals:
            logger.warning("没有可注册的信号")
            return
        
        # 注册最后一个创建的信号
        last_signal = signals[-1]
        if self.signal_registry.register_signal(last_signal.id):
            logger.info(f"信号已注册: {last_signal.name}")
    
    def _on_signal_registered(self, signal_id: str):
        """信号注册成功回调。"""
        signal = self.signal_registry.get_signal(signal_id)
        if signal:
            logger.info(f"信号注册成功: {signal.name}")
    
    def _on_new_project(self):
        """新建项目。"""
        logger.info("新建项目")
        self.view_manager.switch_to("editor")
    
    def _on_open_project(self):
        """打开项目。"""
        logger.info("打开项目")
        self.view_manager.switch_to("editor")

def main():
    """主函数。"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 启动后刷新布局（确保文本居中）
    QTimer.singleShot(200, lambda: window.layout_manager.refresh_all(window))
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()