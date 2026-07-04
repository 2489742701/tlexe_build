"""属性面板模块。

组件属性编辑面板，是用户编辑组件属性的主要界面。

功能:
    1. 基础属性编辑：ID、名称、位置、尺寸
    2. 样式属性编辑：颜色、字体、边框等
    3. 类型特定属性：根据组件类型显示不同属性
    4. 组件信息展示：中文名称、帮助说明

命名约定:
    - UI 控件：_{属性名}_{控件类型}（_name_edit, _x_spin, _bg_btn）
    - 属性添加方法：_add_{类型}_properties（_add_button_properties）
    - 行创建方法：_add_type_row（统一属性行布局）

Signals:
    property_changed: 属性变更信号 (comp_id, property_name, old_value, new_value)
    action_config_requested: 请求配置行为信号 (comp_id)
    create_event_requested: 请求创建事件分支信号 (button_id)
    goto_event_requested: 请求跳转到事件信号 (window_id)
"""

from typing import Optional, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QPushButton, QGroupBox, QColorDialog, QFileDialog, QFrame, QGridLayout, QSizePolicy, QLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from models import (
    ComponentModel, ButtonModel, LabelModel, InputModel, 
    ContainerModel, CheckBoxModel, ComboBoxModel, ImageModel, VideoModel, ProgressBarModel,
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel,
    AlternatingModel, 
    GroupNodeModel, ConfirmButtonModel
)
from styles import PropertyPanelStyles, Colors

# ============================================================
# 组件信息字典
# 定义每种组件的中文名称和帮助说明
# ============================================================
COMPONENT_INFO: Dict[str, Dict[str, str]] = {
    'button': {
        'name': '按钮', 
        'desc': '可点击的按钮控件，用于触发动作（如打开窗口、执行联动等）。'
    },
    'label': {
        'name': '文本标签', 
        'desc': '显示静态文本，支持自动换行、对齐方式设置。'
    },
    'input': {
        'name': '输入框', 
        'desc': '单行文本输入控件，支持占位符、密码模式、最大长度限制。'
    },
    'container': {
        'name': '容器', 
        'desc': '用于组织其他组件的容器，支持定位模式和布局管理。'
    },
    'checkbox': {
        'name': '复选框', 
        'desc': '勾选/取消勾选的开关控件，用于布尔值选项。'
    },
    'combobox': {
        'name': '下拉框', 
        'desc': '下拉选择列表，用户可以从预定义选项中选择一个值。'
    },
    'image': {
        'name': '图片', 
        'desc': '显示图片控件，支持多种缩放模式和圆角效果。'
    },
    'video': {
        'name': '视频', 
        'desc': '视频播放控件，支持自动播放、循环、音量控制。'
    },
    'progressbar': {
        'name': '进度条', 
        'desc': '显示进度信息，支持手动或自动进度更新。'
    },
    'hidden_button': {'name': '隐藏按钮', 'desc': '透明但可点击的热区按钮，用于创建不可见的触发区域。'},
    'image_button': {'name': '图片按钮', 'desc': '使用图片作为外观的按钮，支持悬停和按下状态切换。'},
    'image_carousel': {'name': '图片轮播', 'desc': '多张图片轮播展示控件，支持自动播放、抽奖动画。'},
    'text_alternating': {'name': '文字交替变换', 'desc': '文字组交替变换，支持开始/停止信号控制，减速停在随机位置。'},
    'image_alternating': {'name': '图片交替变换', 'desc': '图片组交替变换，支持开始/停止信号控制，减速停在随机位置。'},
    'lottery': {'name': '抽奖', 'desc': '抽奖组件，支持图片/文字模式，可设定开始按钮触发抽奖动画。'},
    'group_node': {'name': '组节点', 'desc': '将多个组件编组，支持布局模式和自动调整大小。'},
    'confirm_button': {'name': '确认按钮', 'desc': '需同窗口所有确认按钮全部按下才触发动作的按钮控件。'},
}

class PropertyPanel(QWidget):
    """属性面板。
    
    用于显示和编辑选中组件的属性。
    
    Signals:
        property_changed: 属性改变时发射 (comp_id, property_name, old_value, new_value)
        action_config_requested: 请求配置行为时发射 (comp_id)
        create_event_requested: 请求创建事件分支时发射 (button_id)
        goto_event_requested: 请求跳转到事件时发射 (window_id)
    """
    
    property_changed = Signal(str, str, object, object)
    action_config_requested = Signal(str)
    create_event_requested = Signal(str)
    goto_event_requested = Signal(str)
    unbind_extension_requested = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_model: Optional[ComponentModel] = None
        self._current_window: Optional[object] = None
        self._current_editor = None
        self._updating = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")
        
        self._content_layout = QVBoxLayout(content_widget)
        self._content_layout.setContentsMargins(10, 10, 10, 10)
        self._content_layout.setSpacing(10)
        self._content_layout.addWidget(self._create_title_header())
        self._content_layout.addWidget(self._create_basic_group())
        self._content_layout.addWidget(self._create_geometry_group())
        self._content_layout.addWidget(self._create_style_group())
        self._content_layout.addWidget(self._create_window_group())
        self._content_layout.addWidget(self._create_type_specific_group())
        self._content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def _create_row(self, label_text: str, widget: QWidget, stretch: bool = False) -> QHBoxLayout:
        """创建一行属性控件。"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setFixedWidth(70)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(widget)
        
        if stretch:
            layout.addStretch()
        
        return layout
    
    def _create_title_header(self) -> QFrame:
        """创建组件标题头部。"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-bottom: 1px solid #eee;
                padding: 6px 10px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self._title_label = QLabel("未选择")
        self._title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #555;")
        layout.addWidget(self._title_label)
        
        layout.addStretch()
        
        self._help_btn = QPushButton("?")
        self._help_btn.setFixedSize(20, 20)
        self._help_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 10px;
                font-size: 11px;
                color: #666;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        self._help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._help_btn.setToolTip("点击查看组件说明")
        self._help_btn.clicked.connect(self._on_help_clicked)
        layout.addWidget(self._help_btn)
        
        self._type_badge_label = QLabel("")
        self._type_badge_label.setStyleSheet("""
            font-size: 10px;
            color: #888;
            background-color: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        """)
        layout.addWidget(self._type_badge_label)
        
        return frame
    
    def _on_help_clicked(self):
        """点击帮助按钮时显示组件说明。"""
        if not self._current_model:
            return
        
        comp_type = self._current_model.type
        info = COMPONENT_INFO.get(comp_type, {})
        name = info.get('name', comp_type)
        desc = info.get('desc', '暂无说明')
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            f"组件说明 - {name}",
            f"<h3>{name}</h3>"
            f"<p style='color:#555; line-height:1.6;'>{desc}</p>",
            QMessageBox.StandardButton.Ok
        )
    
    def _update_title_header(self, model: ComponentModel):
        """更新标题头部显示。"""
        comp_type = model.type
        info = COMPONENT_INFO.get(comp_type, {})
        display_name = info.get('name', model.name or comp_type)
        
        self._title_label.setText(display_name)
        self._type_badge_label.setText(model.name if model.name != display_name else "")
        self._type_badge_label.setVisible(bool(model.name and model.name != display_name))
        
        has_desc = comp_type in COMPONENT_INFO
        self._help_btn.setVisible(has_desc)
    
    def _create_basic_group(self) -> QGroupBox:
        group = QGroupBox("基础属性")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        self._id_label = QLabel("-")
        self._id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._id_label.setStyleSheet("color: #666; font-family: monospace;")
        layout.addLayout(self._create_row("ID:", self._id_label, stretch=True))
        
        self._type_label = QLabel("-")
        self._type_label.setStyleSheet("color: #666;")
        layout.addLayout(self._create_row("类型:", self._type_label, stretch=True))
        
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("输入组件名称")
        self._name_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._name_edit.textChanged.connect(lambda v: self._on_property_changed("name", v))
        layout.addLayout(self._create_row("名称:", self._name_edit))
        
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("输入显示文本")
        self._text_edit.setMaximumHeight(80)
        self._text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._text_edit.textChanged.connect(self._on_text_edit_changed)
        layout.addLayout(self._create_row("文本:", self._text_edit))
        
        return group
    
    def _on_text_edit_changed(self):
        if self._updating:
            return
        text = self._text_edit.toPlainText()
        self._on_property_changed("text", text)
    
    def _create_geometry_group(self) -> QGroupBox:
        group = QGroupBox("位置和大小")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        from views.flow_layout import FlowLayout
        
        layout = FlowLayout(margin=5, hSpacing=10, vSpacing=10)
        group.setLayout(layout)
        
        # X
        x_widget = QWidget()
        x_layout = QHBoxLayout(x_widget)
        x_layout.setContentsMargins(0, 0, 0, 0)
        x_layout.setSpacing(5)
        x_label = QLabel("X:")
        x_label.setFixedWidth(20)
        x_layout.addWidget(x_label)
        self._x_spin = QSpinBox()
        self._x_spin.setRange(0, 10000)
        self._x_spin.setFixedWidth(80)
        self._x_spin.valueChanged.connect(lambda v: self._on_property_changed("x", v))
        x_layout.addWidget(self._x_spin)
        layout.addWidget(x_widget)
        
        # Y
        y_widget = QWidget()
        y_layout = QHBoxLayout(y_widget)
        y_layout.setContentsMargins(0, 0, 0, 0)
        y_layout.setSpacing(5)
        y_label = QLabel("Y:")
        y_label.setFixedWidth(20)
        y_layout.addWidget(y_label)
        self._y_spin = QSpinBox()
        self._y_spin.setRange(0, 10000)
        self._y_spin.setFixedWidth(80)
        self._y_spin.valueChanged.connect(lambda v: self._on_property_changed("y", v))
        y_layout.addWidget(self._y_spin)
        layout.addWidget(y_widget)
        
        # 宽
        w_widget = QWidget()
        w_layout = QHBoxLayout(w_widget)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.setSpacing(5)
        w_label = QLabel("宽:")
        w_label.setFixedWidth(20)
        w_layout.addWidget(w_label)
        
        self._width_spin = QSpinBox()
        self._width_spin.setRange(10, 10000)
        self._width_spin.setFixedWidth(80)
        self._width_spin.valueChanged.connect(lambda v: self._on_property_changed("width", v))
        w_layout.addWidget(self._width_spin)
        layout.addWidget(w_widget)
        
        # 高
        h_widget = QWidget()
        h_layout = QHBoxLayout(h_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(5)
        h_label = QLabel("高:")
        h_label.setFixedWidth(20)
        h_layout.addWidget(h_label)
        self._height_spin = QSpinBox()
        self._height_spin.setRange(10, 10000)
        self._height_spin.setFixedWidth(80)
        self._height_spin.valueChanged.connect(lambda v: self._on_property_changed("height", v))
        h_layout.addWidget(self._height_spin)
        layout.addWidget(h_widget)
        
        # 水平对齐
        h_align_widget = QWidget()
        h_align_layout = QHBoxLayout(h_align_widget)
        h_align_layout.setContentsMargins(0, 0, 0, 0)
        h_align_layout.setSpacing(5)
        h_align_label = QLabel("水平对齐:")
        h_align_label.setFixedWidth(60)
        h_align_layout.addWidget(h_align_label)
        self._h_align_combo = QComboBox()
        self._h_align_combo.addItems(["无", "左对齐", "居中", "右对齐"])
        self._h_align_combo.setCurrentIndex(0)
        self._h_align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("h_align", ["none", "left", "center", "right"][i]))
        self._h_align_combo.setFixedWidth(80)
        h_align_layout.addWidget(self._h_align_combo)
        layout.addWidget(h_align_widget)
        
        # 垂直对齐
        v_align_widget = QWidget()
        v_align_layout = QHBoxLayout(v_align_widget)
        v_align_layout.setContentsMargins(0, 0, 0, 0)
        v_align_layout.setSpacing(5)
        v_align_label = QLabel("垂直对齐:")
        v_align_label.setFixedWidth(60)
        v_align_layout.addWidget(v_align_label)
        self._v_align_combo = QComboBox()
        self._v_align_combo.addItems(["无", "顶部", "居中", "底部"])
        self._v_align_combo.setCurrentIndex(0)
        self._v_align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("v_align", ["none", "top", "center", "bottom"][i]))
        self._v_align_combo.setFixedWidth(80)
        v_align_layout.addWidget(self._v_align_combo)
        layout.addWidget(v_align_widget)
        
        return group
    
    def _create_style_group(self) -> QGroupBox:
        group = QGroupBox("样式")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        style_mode_layout = QHBoxLayout()
        style_mode_layout.setSpacing(14)
        
        mode_label = QLabel("样式模式:")
        mode_label.setFixedWidth(70)
        style_mode_layout.addWidget(mode_label)
        
        self._style_mode_combo = QComboBox()
        self._style_mode_combo.addItems(["自定义样式", "系统原生风格"])
        self._style_mode_combo.setCurrentIndex(0)
        self._style_mode_combo.currentIndexChanged.connect(self._on_style_mode_changed)
        self._style_mode_combo.setFixedWidth(120)
        style_mode_layout.addWidget(self._style_mode_combo)
        
        style_mode_layout.addStretch()
        layout.addLayout(style_mode_layout)
        
        self._custom_style_widget = QWidget()
        custom_layout = QVBoxLayout(self._custom_style_widget)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(18)
        
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(14)
        
        bg_label = QLabel("背景色:")
        bg_label.setFixedWidth(50)
        colors_layout.addWidget(bg_label)
        
        self._bg_btn = QPushButton()
        self._bg_btn.setFixedSize(50, 24)
        self._bg_btn.clicked.connect(self._on_bg_color_click)
        colors_layout.addWidget(self._bg_btn)
        
        text_label = QLabel("文本色:")
        text_label.setFixedWidth(50)
        text_label.setStyleSheet("margin-left: 15px;")
        colors_layout.addWidget(text_label)
        
        self._text_color_btn = QPushButton()
        self._text_color_btn.setFixedSize(50, 24)
        self._text_color_btn.clicked.connect(self._on_text_color_click)
        colors_layout.addWidget(self._text_color_btn)
        
        colors_layout.addStretch()
        custom_layout.addLayout(colors_layout)
        
        border_layout = QHBoxLayout()
        border_layout.setSpacing(14)
        
        border_label = QLabel("边框色:")
        border_label.setFixedWidth(50)
        border_layout.addWidget(border_label)
        
        self._border_color_btn = QPushButton()
        self._border_color_btn.setFixedSize(50, 24)
        self._border_color_btn.clicked.connect(self._on_border_color_click)
        border_layout.addWidget(self._border_color_btn)
        
        border_layout.addStretch()
        custom_layout.addLayout(border_layout)
        
        size_layout = QHBoxLayout()
        size_layout.setSpacing(14)
        
        bw_label = QLabel("边框宽:")
        bw_label.setFixedWidth(50)
        size_layout.addWidget(bw_label)
        
        self._border_width_spin = QSpinBox()
        self._border_width_spin.setRange(0, 20)
        self._border_width_spin.setFixedWidth(60)
        self._border_width_spin.valueChanged.connect(lambda v: self._on_property_changed("style.border_width", v))
        size_layout.addWidget(self._border_width_spin)
        
        radius_label = QLabel("圆角:")
        radius_label.setFixedWidth(40)
        radius_label.setStyleSheet("margin-left: 15px;")
        size_layout.addWidget(radius_label)
        
        self._radius_spin = QSpinBox()
        self._radius_spin.setRange(0, 50)
        self._radius_spin.setFixedWidth(60)
        self._radius_spin.valueChanged.connect(lambda v: self._on_property_changed("style.border_radius", v))
        size_layout.addWidget(self._radius_spin)
        
        size_layout.addStretch()
        custom_layout.addLayout(size_layout)
        
        font_layout = QHBoxLayout()
        font_layout.setSpacing(14)
        
        font_label = QLabel("字号:")
        font_label.setFixedWidth(50)
        font_layout.addWidget(font_label)
        
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(6, 72)
        self._font_size_spin.setFixedWidth(60)
        self._font_size_spin.valueChanged.connect(lambda v: self._on_property_changed("style.font_size", v))
        font_layout.addWidget(self._font_size_spin)
        
        bold_label = QLabel("粗体:")
        bold_label.setFixedWidth(40)
        bold_label.setStyleSheet("margin-left: 15px;")
        font_layout.addWidget(bold_label)
        
        self._bold_check = QCheckBox()
        self._bold_check.stateChanged.connect(lambda v: self._on_property_changed("style.font_bold", bool(v)))
        font_layout.addWidget(self._bold_check)
        
        font_layout.addStretch()
        custom_layout.addLayout(font_layout)
        
        layout.addWidget(self._custom_style_widget)
        
        return group
    
    def _create_window_group(self) -> QGroupBox:
        """创建窗口属性组"""
        group = QGroupBox("窗口属性")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        self._window_frameless_check = QCheckBox("无边框窗口（无顶栏）")
        self._window_frameless_check.stateChanged.connect(lambda v: self._on_window_property_changed("frameless", v == 2))
        layout.addWidget(self._window_frameless_check)
        
        window_color_layout = QHBoxLayout()
        window_color_layout.setSpacing(14)
        
        window_color_label = QLabel("背景色:")
        window_color_label.setFixedWidth(50)
        window_color_layout.addWidget(window_color_label)
        
        self._window_color_btn = QPushButton()
        self._window_color_btn.setFixedSize(50, 24)
        self._window_color_btn.clicked.connect(self._on_window_color_click)
        window_color_layout.addWidget(self._window_color_btn)
        
        window_color_layout.addStretch()
        layout.addLayout(window_color_layout)
        
        return group
    
    def _on_window_property_changed(self, property_name: str, new_value):
        if self._updating or self._current_window is None:
            return
        
        old_value = getattr(self._current_window, property_name, None)
        if old_value == new_value:
            return
        
        setattr(self._current_window, property_name, new_value)
        self.property_changed.emit("", property_name, old_value, new_value)
    
    def _on_window_color_click(self):
        if self._current_window is None:
            return
        
        color = QColorDialog.getColor(
            QColor(self._current_window.window_color or "#ffffff"),
            self,
            "选择窗口背景色"
        )
        if color.isValid():
            self._update_color_btn(self._window_color_btn, color.name())
            self._on_window_property_changed("window_color", color.name())
    
    def set_window(self, window_model):
        """设置窗口属性编辑"""
        self._current_model = None
        self._current_window = window_model
        self._updating = True
        
        try:
            if window_model is None:
                self._clear_window()
                return
            
            self._title_label.setText("窗口属性")
            self._help_btn.setVisible(False)
            self._type_badge_label.setVisible(False)
            self._id_label.setText(window_model.id)
            self._type_label.setText("window")
            
            self._window_frameless_check.setChecked(window_model.frameless)
            self._update_color_btn(self._window_color_btn, window_model.window_color or "#ffffff")
            
            self._width_spin.setValue(window_model.width)
            self._height_spin.setValue(window_model.height)
            self._x_spin.setValue(0)
            self._y_spin.setValue(0)
            
            self._x_spin.setEnabled(False)
            self._y_spin.setEnabled(False)
            
            self.setEnabled(True)
        finally:
            self._updating = False
    
    def _clear_window(self):
        self._title_label.setText("未选择")
        self._help_btn.setVisible(False)
        self._type_badge_label.setVisible(False)
        self._id_label.setText("-")
        self._type_label.setText("-")
        self._window_frameless_check.setChecked(False)
        self._update_color_btn(self._window_color_btn, "#ffffff")
        self.setEnabled(False)
    
    def _create_type_specific_group(self) -> QGroupBox:
        group = QGroupBox("特定属性")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        self._type_layout = QVBoxLayout(group)
        self._type_layout.setSpacing(10)
        return group
    
    def set_component(self, model: Optional[ComponentModel]):
        self._current_model = model
        self._updating = True
        
        try:
            if model is None:
                self._clear()
                return
            
            self._update_title_header(model)
            self._id_label.setText(model.id)
            self._type_label.setText(model.type)
            self._name_edit.setText(model.name)
            self._text_edit.setPlainText(model.text or "")
            
            self._x_spin.setEnabled(True)
            self._y_spin.setEnabled(True)
            
            self._x_spin.setValue(model.x)
            self._y_spin.setValue(model.y)
            self._width_spin.setValue(model.width)
            self._height_spin.setValue(model.height)
            
            h_align = getattr(model, 'h_align', 'none')
            v_align = getattr(model, 'v_align', 'none')
            self._h_align_combo.setCurrentIndex({"none": 0, "left": 1, "center": 2, "right": 3}.get(h_align, 0))
            self._v_align_combo.setCurrentIndex({"none": 0, "top": 1, "center": 2, "bottom": 3}.get(v_align, 0))
            
            style = model.style
            self._style_mode_combo.setCurrentIndex(1 if style.use_native_style else 0)
            self._custom_style_widget.setEnabled(not style.use_native_style)
            self._update_color_btn(self._bg_btn, style.background_color)
            self._update_color_btn(self._text_color_btn, style.text_color)
            self._update_color_btn(self._border_color_btn, style.border_color)
            self._border_width_spin.setValue(style.border_width)
            self._radius_spin.setValue(style.border_radius)
            self._font_size_spin.setValue(style.font_size)
            self._bold_check.setChecked(style.font_bold)
            
            self._update_type_specific_properties(model)
            
            self.setEnabled(True)
        finally:
            self._updating = False
    
    def _clear(self):
        self._title_label.setText("未选择")
        self._help_btn.setVisible(False)
        self._type_badge_label.setVisible(False)
        
        self._id_label.setText("-")
        self._type_label.setText("-")
        self._name_edit.clear()
        self._text_edit.clear()
        self._x_spin.setValue(0)
        self._y_spin.setValue(0)
        self._width_spin.setValue(100)
        self._height_spin.setValue(100)
        self._h_align_combo.setCurrentIndex(0)
        self._v_align_combo.setCurrentIndex(0)
        self._style_mode_combo.setCurrentIndex(0)
        self._custom_style_widget.setEnabled(True)
        self._update_color_btn(self._bg_btn, "#ffffff")
        self._update_color_btn(self._text_color_btn, "#333333")
        self._update_color_btn(self._border_color_btn, "#cccccc")
        self._border_width_spin.setValue(1)
        self._radius_spin.setValue(4)
        self._font_size_spin.setValue(12)
        self._bold_check.setChecked(False)
        
        self._clear_type_specific_properties()
        self.setEnabled(False)
    
    def _update_color_btn(self, btn: QPushButton, color: str):
        btn.setStyleSheet(f"background-color: {color}; border: 1px solid #999; border-radius: 3px;")
        btn.setProperty("color", color)
    
    def _on_property_changed(self, property_name: str, new_value):
        if self._updating:
            return
            
        if self._current_model is None:
            if self._current_window is not None and property_name in ("width", "height"):
                old_value = getattr(self._current_window, property_name, None)
                if old_value == new_value:
                    return
                setattr(self._current_window, property_name, new_value)
                self.property_changed.emit("", property_name, old_value, new_value)
            return
        
        if property_name.startswith("style."):
            style_prop = property_name.split(".")[1]
            old_value = getattr(self._current_model.style, style_prop)
            if old_value == new_value:
                return
            setattr(self._current_model.style, style_prop, new_value)
            self._current_model.style_changed.emit()
            self._current_model.data_changed.emit()
        else:
            old_value = getattr(self._current_model, property_name, None)
            if old_value == new_value:
                return
            setattr(self._current_model, property_name, new_value)
        
        self.property_changed.emit(self._current_model.id, property_name, old_value, new_value)
    
    def _on_bg_color_click(self):
        color = QColorDialog.getColor(QColor(self._current_model.style.background_color), self, "选择背景色")
        if color.isValid():
            self._on_property_changed("style.background_color", color.name())
            self._update_color_btn(self._bg_btn, color.name())
    
    def _on_text_color_click(self):
        color = QColorDialog.getColor(QColor(self._current_model.style.text_color), self, "选择文本色")
        if color.isValid():
            self._on_property_changed("style.text_color", color.name())
            self._update_color_btn(self._text_color_btn, color.name())
    
    def _on_border_color_click(self):
        color = QColorDialog.getColor(QColor(self._current_model.style.border_color), self, "选择边框色")
        if color.isValid():
            self._on_property_changed("style.border_color", color.name())
            self._update_color_btn(self._border_color_btn, color.name())
    
    def _on_style_mode_changed(self, index: int):
        use_native = (index == 1)
        self._custom_style_widget.setEnabled(not use_native)
        self._on_property_changed("style.use_native_style", use_native)
    
    def _update_type_specific_properties(self, model: ComponentModel):
        self._clear_type_specific_properties()
        self._add_editor_to_type_layout(model)
    
    def _add_editor_to_type_layout(self, model):
        """使用 PropertyEditorRegistry 查找并嵌入编辑器。"""
        from views.property_editors.registry import PropertyEditorRegistry
        editor_class = PropertyEditorRegistry.get_editor(model.type)
        if editor_class:
            self._current_editor = editor_class(parent=self)
            self._current_editor.set_model(model)
            
            # Connect standard editor signals to PropertyPanel signals
            self._current_editor.property_changed.connect(
                lambda prop, old, new: self.property_changed.emit(model.id, prop, old, new)
            )
            self._current_editor.action_config_requested.connect(
                lambda: self.action_config_requested.emit(model.id)
            )
            self._current_editor.create_event_requested.connect(
                lambda comp_id: self.create_event_requested.emit(comp_id)
            )
            self._current_editor.goto_event_requested.connect(
                lambda target_id: self.goto_event_requested.emit(target_id)
            )
            self._current_editor.unbind_extension_requested.connect(
                lambda comp_id, target_id, action_type: self.unbind_extension_requested.emit(comp_id, target_id, action_type)
            )
            
            if hasattr(self._current_editor, 'type_switch_requested'):
                self._current_editor.type_switch_requested.connect(self._on_type_switch_requested)
            self._type_layout.addWidget(self._current_editor)
        else:
            fallback_label = QLabel(f"暂无针对 {model.type} 类型的专属属性编辑器")
            fallback_label.setStyleSheet("color: #999; font-style: italic; padding: 10px;")
            self._type_layout.addWidget(fallback_label)
    
    def _on_type_switch_requested(self, comp_id: str, new_type: str):
        """处理交替变换类型切换请求。"""
        if not self._current_model or self._current_model.id != comp_id:
            return
        
        from models.component_registry import ComponentRegistry
        from models import create_component
        
        old_model = self._current_model
        new_model = create_component(new_type,
            name=old_model.name,
            x=old_model.x, y=old_model.y,
            width=old_model.width, height=old_model.height,
        )
        new_model.style = old_model.style
        new_model._id = old_model.id
        
        project_model = None
        widget = self.parent()
        while widget:
            for attr in ('_project_model', 'project_model'):
                pm = getattr(widget, attr, None)
                if pm:
                    project_model = pm
                    break
            if project_model:
                break
            widget = widget.parent()
        
        if project_model:
            project_model.remove_component(comp_id)
            project_model.add_component(new_model)
            self.set_component(new_model)
    
    def _clear_type_specific_properties(self):
        if hasattr(self, '_current_editor') and self._current_editor:
            self._current_editor.deleteLater()
            self._current_editor = None
        while self._type_layout.count():
            item = self._type_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout_items(item.layout())
    
    def _clear_layout_items(self, layout: QLayout):
        """递归清理布局中的所有子项。"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout_items(item.layout())

