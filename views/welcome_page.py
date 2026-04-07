"""欢迎页面模块。

本模块包含应用程序欢迎页面的实现。
支持时间问候、用户名设置、官方案例和最近项目列表。
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QLineEdit, QMessageBox,
    QFileDialog, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette


class WelcomePage(QWidget):
    """欢迎页面。
    
    显示时间问候、用户名设置、官方案例和最近项目列表。
    
    Signals:
        new_project_requested: 新建项目请求
        open_project_requested: 打开项目请求 (file_path)
        open_template_requested: 打开模板请求 (template_data)
    """
    
    # ==================== 信号定义（出口） ====================
    new_project_requested = Signal()       # 【信号出口】新建项目请求
    open_project_requested = Signal(str)   # 【信号出口】打开项目请求，参数：file_path 项目文件路径
    open_template_requested = Signal(dict) # 【信号出口】打开模板请求，参数：template_data 模板数据字典
    logout_requested = Signal()            # 【信号出口】注销账户请求
    
    def __init__(self):
        super().__init__()
        
        self._config_path = self._get_config_path()
        self._config = self._load_config()
        
        self._init_ui()
        self._update_greeting()
        
        self._greeting_timer = QTimer(self)
        self._greeting_timer.timeout.connect(self._update_greeting)
        self._greeting_timer.start(60000)
    
    def closeEvent(self, event):
        """关闭事件处理，清理定时器。"""
        if self._greeting_timer:
            self._greeting_timer.stop()
        super().closeEvent(event)
    
    def _get_config_path(self) -> str:
        """获取配置文件路径。"""
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'UIDevTool')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件。"""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            'user_name': '',
            'recent_projects': []
        }
    
    def _save_config(self):
        """保存配置文件。"""
        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _init_ui(self):
        """初始化UI。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        self._greeting_label = QLabel()
        self._greeting_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        self._greeting_label.setStyleSheet("color: #333333;")
        header_layout.addWidget(self._greeting_label)
        
        header_layout.addStretch()
        
        self._logout_btn = QPushButton("注销账户")
        self._logout_btn.setFixedHeight(32)
        self._logout_btn.setFont(QFont("Microsoft YaHei", 10))
        self._logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #333333;
                border-color: #999999;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        self._logout_btn.clicked.connect(self._on_logout_clicked)
        header_layout.addWidget(self._logout_btn)
        
        layout.addLayout(header_layout)
        
        self._message_label = QLabel()
        self._message_label.setFont(QFont("Microsoft YaHei", 12))
        self._message_label.setStyleSheet("color: #666666;")
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label)
        
        layout.addSpacing(20)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        new_btn = QPushButton("新建项目")
        new_btn.setFixedSize(150, 45)
        new_btn.setFont(QFont("Microsoft YaHei", 12))
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        new_btn.clicked.connect(self.new_project_requested.emit)  # 【信号入口】新建按钮 -> 发射新建项目请求
        buttons_layout.addWidget(new_btn)
        
        open_btn = QPushButton("打开项目")
        open_btn.setFixedSize(150, 45)
        open_btn.setFont(QFont("Microsoft YaHei", 12))
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #e5f3ff;
                border-color: #0078d7;
            }
            QPushButton:pressed {
                background-color: #cce8ff;
            }
        """)
        open_btn.clicked.connect(self._on_open_project)  # 【信号入口】打开按钮 -> 打开项目对话框
        buttons_layout.addWidget(open_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        layout.addSpacing(20)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)
        
        unsaved_section = CollapsibleSection("未保存项目", expanded=True)
        self._unsaved_list = unsaved_section.content_widget
        self._update_unsaved_projects()
        scroll_layout.addWidget(unsaved_section)
        
        examples_section = CollapsibleSection("官方案例", expanded=True)
        self._examples_list = examples_section.content_widget
        self._populate_examples()
        scroll_layout.addWidget(examples_section)
        
        recent_section = CollapsibleSection("最近项目", expanded=True)
        self._recent_list = recent_section.content_widget
        self._update_recent_projects()
        scroll_layout.addWidget(recent_section)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def _update_greeting(self):
        """更新问候语。"""
        from utils.settings import app_settings
        
        now = datetime.now()
        hour = now.hour
        
        user_name = app_settings.user_name
        name_suffix = f"，{user_name}" if user_name else ""
        
        if 6 <= hour < 11:
            greeting = f"早上好{name_suffix}"
            message = "新的一天，新的开始。祝你工作顺利！"
        elif 11 <= hour < 14:
            greeting = f"中午好{name_suffix}"
            message = "记得休息一下，吃个午饭。"
        elif 14 <= hour < 18:
            greeting = f"下午好{name_suffix}"
            message = "下午茶时间到了，来杯咖啡提提神？"
        elif 18 <= hour < 22:
            greeting = f"傍晚好{name_suffix}"
            message = "今天辛苦了，记得放松一下。"
        else:
            greeting = f"夜深了{name_suffix}"
            message = "深夜开发真不易，早点休息吧，明天继续！"
        
        self._greeting_label.setText(greeting)
        self._message_label.setText(message)
    
    def _on_logout_clicked(self):
        """注销账户按钮点击。"""
        self.logout_requested.emit()
    
    def _on_open_project(self):
        """打开项目对话框。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "项目文件 (*.itexe);;所有文件 (*.*)"
        )
        if file_path:
            self.open_project_requested.emit(file_path)
    
    def _populate_examples(self):
        """填充官方案例列表。"""
        # 清除旧的布局
        old_layout = self._examples_list.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)
        
        layout = QGridLayout(self._examples_list)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        cols = 6
        for col in range(cols):
            layout.setColumnStretch(col, 1)
        
        examples = [
            ("Galgame示例项目", "一个完整的Galgame风格示例", "samples/galgame示例.itexe"),
            ("文字抽奖", "文字轮播抽奖演示（lottery_animation）", "samples/文字抽奖示例.itexe"),
            ("年会抽奖", "图片轮播抽奖演示（lottery_animation + set_text）", "samples/年会抽奖示例.itexe"),
            ("电脑开机检测演示", "一个有趣的恶搞程序模板", "templates/test_template.py"),
        ]
        
        for i, (title, desc, path) in enumerate(examples):
            row = i // cols
            col = i % cols
            example = ProjectCardWidget(title, desc, path, can_delete=False)
            example.clicked.connect(self._on_example_clicked)
            layout.addWidget(example, row, col)
    
    def _on_example_clicked(self, template_path: str):
        """点击案例时的回调。"""
        import traceback
        from datetime import datetime
        
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 点击案例: {template_path}")
        print(f"{'='*60}")
        
        try:
            if template_path == "templates/test_template.py":
                print("正在导入 templates.get_test_template...")
                from templates import get_test_template
                print("导入成功，正在获取模板数据...")
                template_data = get_test_template()
                print(f"模板数据获取成功: {template_data.get('name', '未命名')}")
                self.open_template_requested.emit(template_data)
                print("模板打开信号已发射")
            elif template_path.endswith('.itexe'):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                full_path = os.path.join(base_dir, template_path)
                print(f"尝试打开示例文件: {full_path}")
                print(f"文件存在: {os.path.exists(full_path)}")
                if os.path.exists(full_path):
                    self.open_project_requested.emit(full_path)
                    print("项目打开信号已发射")
                else:
                    print(f"错误: 文件不存在 - {full_path}")
                    QMessageBox.warning(self, "文件不存在", f"示例文件不存在: {full_path}")
            else:
                print(f"错误: 未知的模板路径类型 - {template_path}")
        except Exception as e:
            error_msg = f"打开案例失败: {template_path}\n错误: {str(e)}\n\n{traceback.format_exc()}"
            print(f"\n{'!'*60}\n{error_msg}\n{'!'*60}")
            
            appdata = os.environ.get('APPDATA', '')
            crash_log_dir = os.path.join(appdata, 'UIDevTool', 'crash_logs')
            os.makedirs(crash_log_dir, exist_ok=True)
            
            crash_file = os.path.join(crash_log_dir, f"example_crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            with open(crash_file, 'w', encoding='utf-8') as f:
                f.write(f"UI快速开发工具 - 案例打开失败日志\n")
                f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"模板路径: {template_path}\n")
                f.write(f"{'='*60}\n\n")
                f.write(error_msg)
            
            print(f"错误日志已保存到: {crash_file}")
            QMessageBox.critical(self, "打开案例失败", f"无法打开案例:\n{str(e)}\n\n错误日志已保存到:\n{crash_file}")
    
    def _update_recent_projects(self):
        """更新最近项目列表。"""
        # 清除旧的布局和控件
        old_layout = self._recent_list.layout()
        if old_layout is not None:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # 删除旧布局
            QWidget().setLayout(old_layout)
        
        # 创建新的 QGridLayout
        grid_layout = QGridLayout(self._recent_list)
        grid_layout.setContentsMargins(10, 5, 10, 5)
        grid_layout.setSpacing(8)
        
        cols = 6
        for col in range(cols):
            grid_layout.setColumnStretch(col, 1)
        
        recent_projects = self._config.get('recent_projects', [])
        if recent_projects:
            for i, project in enumerate(recent_projects):
                row = i // cols
                col = i % cols
                
                # 获取最后打开时间并格式化
                last_opened = project.get('last_opened', '')
                time_desc = ''
                if last_opened:
                    try:
                        dt = datetime.fromisoformat(last_opened)
                        now = datetime.now()
                        diff = now - dt
                        
                        if diff.days == 0:
                            time_desc = f"今天 {dt.strftime('%H:%M')}"
                        elif diff.days == 1:
                            time_desc = f"昨天 {dt.strftime('%H:%M')}"
                        elif diff.days < 7:
                            time_desc = f"{diff.days}天前"
                        else:
                            time_desc = dt.strftime("%Y-%m-%d")
                    except:
                        time_desc = ""
                
                card = ProjectCardWidget(
                    project.get('name', '未命名项目'),
                    time_desc,
                    project.get('path', '')
                )
                card.clicked.connect(self._on_recent_project_clicked)
                card.delete_requested.connect(self._on_delete_recent_project)
                grid_layout.addWidget(card, row, col)
        else:
            empty_label = QLabel("暂无最近项目")
            empty_label.setStyleSheet("color: #999999; padding: 10px;")
            grid_layout.addWidget(empty_label, 0, 0, 1, cols)
    
    def _update_unsaved_projects(self):
        """更新未保存项目列表。"""
        import json
        from datetime import datetime
        
        old_layout = self._unsaved_list.layout()
        if old_layout is not None:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old_layout)
        
        grid_layout = QGridLayout(self._unsaved_list)
        grid_layout.setContentsMargins(10, 5, 10, 5)
        grid_layout.setSpacing(8)
        
        cols = 6
        for col in range(cols):
            grid_layout.setColumnStretch(col, 1)
        
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'UIDevTool')
        unsaved_file = os.path.join(config_dir, 'unsaved_projects.json')
        
        unsaved_projects = []
        try:
            if os.path.exists(unsaved_file):
                with open(unsaved_file, 'r', encoding='utf-8') as f:
                    unsaved_projects = json.load(f)
        except Exception:
            pass
        
        if unsaved_projects:
            for i, project in enumerate(unsaved_projects):
                row = i // cols
                col = i % cols
                
                saved_at = project.get('saved_at', '')
                try:
                    dt = datetime.fromisoformat(saved_at)
                    time_str = dt.strftime("%m-%d %H:%M")
                except:
                    time_str = ""
                
                desc = f"自动保存于 {time_str}" if time_str else "未保存项目"
                
                card = ProjectCardWidget(
                    project.get('name', '未保存项目'),
                    desc,
                    project.get('path', '')
                )
                card.clicked.connect(self._on_unsaved_project_clicked)
                card.delete_requested.connect(self._on_delete_unsaved_project)
                grid_layout.addWidget(card, row, col)
        else:
            empty_label = QLabel("暂无未保存项目")
            empty_label.setStyleSheet("color: #999999; padding: 10px;")
            grid_layout.addWidget(empty_label, 0, 0, 1, cols)
    
    def _on_unsaved_project_clicked(self, file_path: str):
        """点击未保存项目时的回调。"""
        if os.path.exists(file_path):
            self.open_project_requested.emit(file_path)
        else:
            QMessageBox.warning(self, "文件不存在", "未保存项目文件已不存在")
            self._on_delete_unsaved_project(file_path)
    
    def _on_delete_unsaved_project(self, file_path: str):
        """从删除未保存项目。"""
        import json
        
        normalized_path = os.path.normpath(os.path.abspath(file_path))
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'UIDevTool')
        unsaved_file = os.path.join(config_dir, 'unsaved_projects.json')
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        unsaved_projects = []
        try:
            if os.path.exists(unsaved_file):
                with open(unsaved_file, 'r', encoding='utf-8') as f:
                    unsaved_projects = json.load(f)
        except Exception:
            pass
        
        unsaved_projects = [p for p in unsaved_projects 
                          if os.path.normpath(os.path.abspath(p.get('path', ''))) != normalized_path]
        
        try:
            with open(unsaved_file, 'w', encoding='utf-8') as f:
                json.dump(unsaved_projects, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        
        self._update_unsaved_projects()
    
    def _on_delete_recent_project(self, file_path: str):
        """从最近项目列表中删除项目。"""
        normalized_path = os.path.normpath(os.path.abspath(file_path))
        recent_projects = self._config.get('recent_projects', [])
        recent_projects = [p for p in recent_projects 
                          if os.path.normpath(os.path.abspath(p.get('path', ''))) != normalized_path]
        
        self._config['recent_projects'] = recent_projects
        self._save_config()
        self._update_recent_projects()
    
    def _on_recent_project_clicked(self, file_path: str):
        """点击最近项目时的回调。"""
        if os.path.exists(file_path):
            self.open_project_requested.emit(file_path)
        else:
            QMessageBox.warning(self, "文件不存在", f"项目文件不存在: {file_path}")
    
    def add_recent_project(self, name: str, path: str):
        """添加最近项目。
        
        Args:
            name: 项目名称
            path: 项目路径
        """
        normalized_path = os.path.normpath(os.path.abspath(path))
        
        recent_projects = self._config.get('recent_projects', [])
        
        def is_official_example(project_path: str) -> bool:
            normalized = os.path.normpath(project_path).lower()
            return 'samples' in normalized or 'templates' in normalized
        
        def normalize_path_for_comparison(project_path: str) -> str:
            """规范化路径用于去重比较。"""
            # 转换为绝对路径并规范化
            abs_path = os.path.abspath(project_path)
            # 统一大小写（Windows下路径不区分大小写）
            normalized = os.path.normcase(abs_path)
            # 移除多余的路径分隔符
            normalized = os.path.normpath(normalized)
            return normalized
        
        is_new_official = is_official_example(normalized_path)
        
        # 分离官方案例和个人项目
        official_examples = [p for p in recent_projects if is_official_example(p.get('path', ''))]
        personal_projects = [p for p in recent_projects if not is_official_example(p.get('path', ''))]
        
        # 根据新项目类型更新对应列表，使用路径规范化去重
        new_project = {
            'name': name,
            'path': normalized_path,
            'last_opened': datetime.now().isoformat()
        }
        
        new_normalized = normalize_path_for_comparison(normalized_path)
        
        if is_new_official:
            # 官方案例：移除所有重复路径，只保留最新的
            official_examples = [p for p in official_examples 
                               if normalize_path_for_comparison(p.get('path', '')) != new_normalized]
            official_examples = [new_project] + official_examples  # 新项目放在最前面
        else:
            # 个人项目：移除所有重复路径，只保留最新的
            personal_projects = [p for p in personal_projects 
                               if normalize_path_for_comparison(p.get('path', '')) != new_normalized]
            personal_projects = [new_project] + personal_projects  # 新项目放在最前面
        
        # 合并：最多保留5个项目（1个官方案例 + 4个个人项目）
        recent_projects = official_examples[:1] + personal_projects[:4]
        
        self._config['recent_projects'] = recent_projects
        self._save_config()
        self._update_recent_projects()


class CollapsibleSection(QWidget):
    """可折叠区域组件。"""
    
    def __init__(self, title: str, expanded: bool = True, parent=None):
        super().__init__(parent)
        
        self._expanded = expanded
        self._title = title
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QPushButton(f"{'▼' if self._expanded else '▶'} {self._title}")
        header.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        header.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        header.clicked.connect(self._toggle)
        layout.addWidget(header)
        self._header_btn = header
        
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.content_widget.setVisible(self._expanded)
        layout.addWidget(self.content_widget)
    
    def _toggle(self):
        """切换折叠状态。"""
        self._expanded = not self._expanded
        self._header_btn.setText(f"{'▼' if self._expanded else '▶'} {self._title}")
        self.content_widget.setVisible(self._expanded)


class ProjectCardWidget(QFrame):
    """项目卡片组件。"""
    
    clicked = Signal(str)
    delete_requested = Signal(str)
    
    def __init__(self, title: str, description: str, path: str, can_delete: bool = True, parent=None):
        super().__init__(parent)
        
        self._path = path
        self._title = title
        self._can_delete = can_delete
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(80)
        self.setMinimumWidth(200)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            QFrame:hover {
                border-color: #0078d7;
                background-color: #f5f9ff;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333333; background: transparent;")
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Microsoft YaHei", 9))
        desc_label.setStyleSheet("color: #666666; background: transparent;")
        desc_label.setWordWrap(True)
        desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(desc_label)
    
    def mousePressEvent(self, event):
        """鼠标点击事件。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._path)
        super().mousePressEvent(event)
    
    def _on_context_menu(self, pos):
        """右键菜单。"""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        open_action = menu.addAction("打开项目")
        open_action.triggered.connect(lambda: self.clicked.emit(self._path))
        
        if self._path and os.path.exists(self._path):
            open_dir_action = menu.addAction("打开所在目录")
            open_dir_action.triggered.connect(self._open_file_location)
        
        if self._can_delete:
            menu.addSeparator()
            delete_action = menu.addAction("从列表中删除")
            delete_action.triggered.connect(lambda: self.delete_requested.emit(self._path))
        
        menu.exec_(self.mapToGlobal(pos))
    
    def _open_file_location(self):
        """打开项目所在目录。"""
        import platform
        
        if not self._path or not os.path.exists(self._path):
            return
        
        if platform.system() == "Windows":
            os.startfile(os.path.dirname(self._path))
        elif platform.system() == "Darwin":
            import subprocess
            subprocess.call(["open", os.path.dirname(self._path)])
        else:
            import subprocess
            subprocess.call(["xdg-open", os.path.dirname(self._path)])
