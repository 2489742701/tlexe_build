"""属性面板模块。

本模块包含组件属性编辑面板的实现，是用户编辑组件属性的主要界面。

## 功能
1. 基础属性编辑：ID、名称、位置、尺寸
2. 样式属性编辑：颜色、字体、边框等
3. 类型特定属性：根据组件类型显示不同属性
4. 组件信息展示：中文名称、帮助说明

## 使用方法
```python
panel = PropertyPanel()
panel.set_component(button_model)  # 显示按钮属性
panel.set_component(None)           # 清空面板
```

## 信号
- property_changed: 属性变更信号
- action_config_requested: 请求配置行为信号
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
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_model: Optional[ComponentModel] = None
        self._updating = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ============================================================
        # 滚动区域配置（重要！不要随意修改）
        # 
        # 【关键配置说明】
        # 1. setWidgetResizable(True): 必须为True，否则内容无法自适应滚动
        # 2. setFrameShape(NoFrame): 移除边框，保持界面简洁
        # 3. HorizontalScrollBarAlwaysOff: 禁用水平滚动条，属性面板只需垂直滚动
        # 4. VerticalScrollBarAsNeeded: 内容超出时才显示垂直滚动条
        # 5. setSizePolicy(Expanding, Preferred): 宽度自适应，高度根据内容调整
        # 6. setMinimumHeight(200): 确保最小高度，避免布局压缩
        # 
        # 【常见问题排查】
        # | 问题 | 排查项 | 解决方法 |
        # |------|--------|----------|
        # | 滚动条不出现 | setWidgetResizable 是否为 True | scroll_area.setWidgetResizable(True) |
        # | 内容被截断 | setMinimumHeight 是否设置 | scroll_content.setMinimumHeight(200) |
        # | 布局错乱 | setSizePolicy 是否正确 | scroll_content.setSizePolicy(Expanding, Preferred) |
        # | 滚动条样式异常 | SCROLL_AREA 样式是否应用 | scroll_area.setStyleSheet(PropertyPanelStyles.SCROLL_AREA) |
        # | 内容无法滚动 | addStretch 是否存在 | self._content_layout.addStretch() |
        # | 分组框标题被截断 | margin-top 是否足够大 | 增加 margin-top 值（如 20px） |
        # | 内容紧贴边框 | padding 是否设置 | 增加 padding 值（如 16px 10px 10px 10px） |
        # | 分组框内容为空 | QGroupBox 的 sizePolicy 是否设置 | group.setSizePolicy(Expanding, Minimum) |
        # | 分组框高度不自适应 | QGroupBox 是否设置了固定高度 | 移除 setFixedHeight 或改用 setMinimumHeight |
        # ============================================================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(PropertyPanelStyles.SCROLL_AREA)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background-color: {Colors.BACKGROUND_PRIMARY};")
        scroll_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        scroll_content.setMinimumHeight(200)
        
        # ============================================================
        # 内容布局参数（重要！不要随意修改）
        #
        # 【布局规范】
        # - setContentsMargins(18, 14, 18, 24): 左18px, 上14px, 右18px, 下24px
        #   底部边距较大是为了避免内容紧贴底部边缘
        # - setSpacing(32): 分组之间的间距，较大间距让界面更通透
        #
        # 【间距层级】
        # 1. 内容区域间距: 32px（分组之间）
        # 2. 分组内部间距: 18px（属性行之间）
        # 3. 行内控件间距: 14-16px（标签与控件之间）
        # ============================================================
        self._content_layout = QVBoxLayout(scroll_content)
        self._content_layout.setContentsMargins(18, 14, 18, 24)
        self._content_layout.setSpacing(32)
        
        self._title_widget = self._create_title_header()
        self._content_layout.addWidget(self._title_widget)
        
        self._basic_group = self._create_basic_group()
        self._content_layout.addWidget(self._basic_group)
        
        self._geometry_group = self._create_geometry_group()
        self._content_layout.addWidget(self._geometry_group)
        
        self._style_group = self._create_style_group()
        self._content_layout.addWidget(self._style_group)
        
        self._type_specific_group = self._create_type_specific_group()
        self._content_layout.addWidget(self._type_specific_group)
        
        self._content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def _create_row(self, label_text: str, widget: QWidget, stretch: bool = False) -> QHBoxLayout:
        """创建一行属性控件。"""
        layout = QHBoxLayout()
        layout.setSpacing(16)
        
        label = QLabel(label_text)
        label.setFixedWidth(70)
        label.setStyleSheet(PropertyPanelStyles.LABEL_HINT)
        layout.addWidget(label)
        
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(widget)
        
        if stretch:
            layout.addStretch()
        
        return layout
    
    def _create_title_header(self) -> QFrame:
        """创建组件标题头部（大名称 + 帮助按钮）。"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(PropertyPanelStyles.TITLE_FRAME)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        
        self._title_label = QLabel("未选择")
        self._title_label.setStyleSheet(PropertyPanelStyles.TITLE_LABEL)
        layout.addWidget(self._title_label)
        
        self._help_btn = QPushButton("?")
        self._help_btn.setFixedSize(22, 22)
        self._help_btn.setStyleSheet(PropertyPanelStyles.HELP_BUTTON)
        self._help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._help_btn.setToolTip("点击查看组件说明")
        self._help_btn.clicked.connect(self._on_help_clicked)
        layout.addWidget(self._help_btn)
        
        layout.addStretch()
        
        self._type_badge_label = QLabel("")
        self._type_badge_label.setStyleSheet(PropertyPanelStyles.TYPE_BADGE)
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
        group.setStyleSheet(PropertyPanelStyles.GROUP_STYLE)
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(group)
        layout.setSpacing(18)
        
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
        group.setStyleSheet(PropertyPanelStyles.GROUP_STYLE)
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(group)
        layout.setSpacing(18)
        
        pos_layout = QHBoxLayout()
        pos_layout.setSpacing(14)
        
        x_label = QLabel("X:")
        x_label.setFixedWidth(20)
        pos_layout.addWidget(x_label)
        
        self._x_spin = QSpinBox()
        self._x_spin.setRange(0, 10000)
        self._x_spin.valueChanged.connect(lambda v: self._on_property_changed("x", v))
        pos_layout.addWidget(self._x_spin)
        
        y_label = QLabel("Y:")
        y_label.setFixedWidth(20)
        y_label.setStyleSheet("margin-left: 10px;")
        pos_layout.addWidget(y_label)
        
        self._y_spin = QSpinBox()
        self._y_spin.setRange(0, 10000)
        self._y_spin.valueChanged.connect(lambda v: self._on_property_changed("y", v))
        pos_layout.addWidget(self._y_spin)
        
        pos_layout.addStretch()
        layout.addLayout(pos_layout)
        
        size_layout = QHBoxLayout()
        size_layout.setSpacing(14)
        
        w_label = QLabel("宽:")
        w_label.setFixedWidth(20)
        size_layout.addWidget(w_label)
        
        self._width_spin = QSpinBox()
        self._width_spin.setRange(10, 10000)
        self._width_spin.valueChanged.connect(lambda v: self._on_property_changed("width", v))
        size_layout.addWidget(self._width_spin)
        
        h_label = QLabel("高:")
        h_label.setFixedWidth(20)
        h_label.setStyleSheet("margin-left: 10px;")
        size_layout.addWidget(h_label)
        
        self._height_spin = QSpinBox()
        self._height_spin.setRange(10, 10000)
        self._height_spin.valueChanged.connect(lambda v: self._on_property_changed("height", v))
        size_layout.addWidget(self._height_spin)
        
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        align_layout = QHBoxLayout()
        align_layout.setSpacing(14)
        
        h_align_label = QLabel("水平对齐:")
        h_align_label.setFixedWidth(60)
        align_layout.addWidget(h_align_label)
        
        self._h_align_combo = QComboBox()
        self._h_align_combo.addItems(["无", "左对齐", "居中", "右对齐"])
        self._h_align_combo.setCurrentIndex(0)
        self._h_align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("h_align", ["none", "left", "center", "right"][i]))
        self._h_align_combo.setFixedWidth(80)
        align_layout.addWidget(self._h_align_combo)
        
        v_align_label = QLabel("垂直对齐:")
        v_align_label.setFixedWidth(60)
        v_align_label.setStyleSheet("margin-left: 10px;")
        align_layout.addWidget(v_align_label)
        
        self._v_align_combo = QComboBox()
        self._v_align_combo.addItems(["无", "顶部", "居中", "底部"])
        self._v_align_combo.setCurrentIndex(0)
        self._v_align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("v_align", ["none", "top", "center", "bottom"][i]))
        self._v_align_combo.setFixedWidth(80)
        align_layout.addWidget(self._v_align_combo)
        
        align_layout.addStretch()
        layout.addLayout(align_layout)
        
        return group
    
    def _create_style_group(self) -> QGroupBox:
        group = QGroupBox("样式")
        group.setStyleSheet(PropertyPanelStyles.GROUP_STYLE)
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(group)
        layout.setSpacing(18)
        
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
        
        bw_label = QLabel("边框宽:")
        bw_label.setFixedWidth(50)
        bw_label.setStyleSheet("margin-left: 15px;")
        border_layout.addWidget(bw_label)
        
        self._border_width_spin = QSpinBox()
        self._border_width_spin.setRange(0, 20)
        self._border_width_spin.setFixedWidth(60)
        self._border_width_spin.valueChanged.connect(lambda v: self._on_property_changed("style.border_width", v))
        border_layout.addWidget(self._border_width_spin)
        
        border_layout.addStretch()
        custom_layout.addLayout(border_layout)
        
        other_layout = QHBoxLayout()
        other_layout.setSpacing(14)
        
        radius_label = QLabel("圆角:")
        radius_label.setFixedWidth(50)
        other_layout.addWidget(radius_label)
        
        self._radius_spin = QSpinBox()
        self._radius_spin.setRange(0, 50)
        self._radius_spin.setFixedWidth(60)
        self._radius_spin.valueChanged.connect(lambda v: self._on_property_changed("style.border_radius", v))
        other_layout.addWidget(self._radius_spin)
        
        font_label = QLabel("字号:")
        font_label.setFixedWidth(50)
        font_label.setStyleSheet("margin-left: 15px;")
        other_layout.addWidget(font_label)
        
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(6, 72)
        self._font_size_spin.setFixedWidth(60)
        self._font_size_spin.valueChanged.connect(lambda v: self._on_property_changed("style.font_size", v))
        other_layout.addWidget(self._font_size_spin)
        
        bold_label = QLabel("粗体:")
        bold_label.setFixedWidth(40)
        bold_label.setStyleSheet("margin-left: 15px;")
        other_layout.addWidget(bold_label)
        
        self._bold_check = QCheckBox()
        self._bold_check.stateChanged.connect(lambda v: self._on_property_changed("style.font_bold", bool(v)))
        other_layout.addWidget(self._bold_check)
        
        other_layout.addStretch()
        custom_layout.addLayout(other_layout)
        
        layout.addWidget(self._custom_style_widget)
        
        return group
    
    def _create_type_specific_group(self) -> QGroupBox:
        group = QGroupBox("特定属性")
        group.setStyleSheet(PropertyPanelStyles.GROUP_STYLE)
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._type_layout = QVBoxLayout(group)
        self._type_layout.setSpacing(18)
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
        if self._updating or self._current_model is None:
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
        
        if isinstance(model, ButtonModel):
            self._add_button_properties(model)
        elif isinstance(model, LabelModel):
            self._add_label_properties(model)
        elif isinstance(model, InputModel):
            self._add_input_properties(model)
        elif isinstance(model, ContainerModel):
            self._add_container_properties(model)
        elif isinstance(model, CheckBoxModel):
            self._add_checkbox_properties(model)
        elif isinstance(model, ComboBoxModel):
            self._add_combobox_properties(model)
        elif isinstance(model, ImageModel):
            self._add_image_properties(model)
        elif isinstance(model, VideoModel):
            self._add_video_properties(model)
        elif isinstance(model, ProgressBarModel):
            self._add_progressbar_properties(model)
        elif isinstance(model, ImageCarouselModel):
            self._add_image_carousel_properties(model)
        elif isinstance(model, HiddenButtonModel):
            self._add_hidden_button_properties(model)
        elif isinstance(model, ImageButtonModel):
            self._add_image_button_properties(model)
    
    def _clear_type_specific_properties(self):
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
    
    def _add_type_row(self, label_text: str, widget_or_layout) -> QHBoxLayout:
        """创建特定属性行。支持 QWidget 或 QLayout 类型。"""
        layout = QHBoxLayout()
        layout.setSpacing(14)
        
        label = QLabel(label_text)
        label.setFixedWidth(70)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        
        if isinstance(widget_or_layout, QLayout):
            container = QWidget()
            container.setLayout(widget_or_layout)
            layout.addWidget(container)
        else:
            layout.addWidget(widget_or_layout)
        
        layout.addStretch()
        
        self._type_layout.addLayout(layout)
        return layout
    
    def _add_button_properties(self, model: ButtonModel):
        default_check = QCheckBox()
        default_check.setChecked(model.is_default)
        default_check.stateChanged.connect(lambda v: self._on_property_changed("is_default", bool(v)))
        self._add_type_row("默认按钮:", default_check)
        
        cancel_check = QCheckBox()
        cancel_check.setChecked(model.is_cancel)
        cancel_check.stateChanged.connect(lambda v: self._on_property_changed("is_cancel", bool(v)))
        self._add_type_row("取消按钮:", cancel_check)
        
        align_combo = QComboBox()
        align_combo.addItems(["左对齐", "居中", "右对齐"])
        align_combo.setCurrentIndex({"left": 0, "center": 1, "right": 2}.get(model.alignment, 1))
        align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("alignment", ["left", "center", "right"][i]))
        align_combo.setFixedWidth(100)
        self._add_type_row("对齐:", align_combo)
        
        branch_label = QLabel(model.branch_name or "无")
        branch_label.setStyleSheet("color: #666;")
        self._add_type_row("分支:", branch_label)
        
        if model.has_branch:
            goto_btn = QPushButton("跳转到事件")
            goto_btn.clicked.connect(lambda: self.goto_event_requested.emit(model.target_window_id))
            self._type_layout.addWidget(goto_btn)
        else:
            create_event_btn = QPushButton("创建事件分支")
            create_event_btn.clicked.connect(lambda: self.create_event_requested.emit(model.id))
            self._type_layout.addWidget(create_event_btn)
        
        action_btn = QPushButton("配置行为")
        action_btn.clicked.connect(lambda: self.action_config_requested.emit(model.id))
        self._type_layout.addWidget(action_btn)
    
    def _add_image_carousel_properties(self, model: ImageCarouselModel):
        """添加图片轮播组件属性。"""
        
        interval_spin = QSpinBox()
        interval_spin.setRange(100, 10000)
        interval_spin.setSingleStep(100)
        interval_spin.setValue(model.interval)
        interval_spin.setFixedWidth(80)
        interval_spin.valueChanged.connect(lambda v: self._on_property_changed("interval", v))
        self._add_type_row("轮播间隔(ms):", interval_spin)
        
        auto_play_check = QCheckBox()
        auto_play_check.setChecked(model.auto_play)
        auto_play_check.stateChanged.connect(lambda v: self._on_property_changed("auto_play", bool(v)))
        self._add_type_row("自动播放:", auto_play_check)
        
        loop_check = QCheckBox()
        loop_check.setChecked(model.loop)
        loop_check.stateChanged.connect(lambda v: self._on_property_changed("loop", bool(v)))
        self._add_type_row("循环播放:", loop_check)
        
        index_spin = QSpinBox()
        index_spin.setRange(0, 999)
        index_spin.setValue(model.current_index)
        index_spin.setFixedWidth(60)
        index_spin.valueChanged.connect(lambda v: self._on_property_changed("current_index", v))
        self._add_type_row("当前索引:", index_spin)
    
    def _add_hidden_button_properties(self, model: HiddenButtonModel):
        """添加隐藏按钮组件属性。"""
        
        info_label = QLabel("透明可点击按钮，用于创建热区")
        info_label.setStyleSheet("color: #888; font-size: 11px;")
        info_label.setWordWrap(True)
        self._type_layout.addWidget(info_label)
    
    def _add_image_button_properties(self, model: ImageButtonModel):
        """添加图片按钮组件属性。"""
        
        path_layout = QHBoxLayout()
        path_edit = QLineEdit()
        path_edit.setText(model.image_path or "")
        path_edit.textChanged.connect(lambda v: self._on_property_changed("image_path", v))
        path_edit.setPlaceholderText("按钮图片路径")
        path_layout.addWidget(path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setFixedWidth(60)
        browse_btn.clicked.connect(self._browse_image_file)
        path_layout.addWidget(browse_btn)
        
        self._add_type_row("图片路径:", path_layout)
    
    def _add_image_properties(self, model: ImageModel):
        """添加图片组件属性。"""
        
        # 图片路径选择
        path_layout = QHBoxLayout()
        path_edit = QLineEdit()
        path_edit.setText(model.image_path)
        path_edit.textChanged.connect(lambda v: self._on_property_changed("image_path", v))
        path_edit.setPlaceholderText("图片文件路径")
        path_layout.addWidget(path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setFixedWidth(60)
        browse_btn.clicked.connect(self._browse_image_file)
        path_layout.addWidget(browse_btn)
        
        self._add_type_row("图片路径:", path_layout)
        
        # 缩放模式（已修复：移除与"保持比例"复选框的冲突）
        # 下拉选项改为互斥的缩放方式，不再包含"保持比例"
        scale_combo = QComboBox()
        scale_combo.addItems(["填充", "适应", "拉伸", "居中显示", "平铺"])
        scale_map = {"fill": 0, "fit": 1, "stretch": 2, "center": 3, "tile": 4}
        scale_combo.setCurrentIndex(scale_map.get(model.scale_mode, 1))  # 默认"适应"
        scale_combo.currentIndexChanged.connect(lambda i: self._on_property_changed(
            "scale_mode", ["fill", "fit", "stretch", "center", "tile"][i]
        ))
        scale_combo.setFixedWidth(100)
        self._add_type_row("缩放模式:", scale_combo)
        
        # 保持宽高比（独立控制是否保持原始比例）
        aspect_check = QCheckBox()
        aspect_check.setChecked(model.aspect_ratio)
        aspect_check.stateChanged.connect(lambda v: self._on_property_changed("aspect_ratio", bool(v)))
        self._add_type_row("保持宽高比:", aspect_check)
        
        # 圆角半径
        radius_spin = QSpinBox()
        radius_spin.setRange(0, 100)
        radius_spin.setValue(model.border_radius)
        radius_spin.setFixedWidth(60)
        radius_spin.valueChanged.connect(lambda v: self._on_property_changed("border_radius", v))
        self._add_type_row("圆角半径:", radius_spin)
        
        # 透明度
        opacity_spin = QDoubleSpinBox()
        opacity_spin.setRange(0.0, 1.0)
        opacity_spin.setSingleStep(0.1)
        opacity_spin.setValue(model.opacity)
        opacity_spin.setFixedWidth(60)
        opacity_spin.valueChanged.connect(lambda v: self._on_property_changed("opacity", v))
        self._add_type_row("透明度:", opacity_spin)
        
        # 悬停效果
        hover_check = QCheckBox()
        hover_check.setChecked(model.hover_effect)
        hover_check.stateChanged.connect(lambda v: self._on_property_changed("hover_effect", bool(v)))
        self._add_type_row("悬停效果:", hover_check)
        
        # 点击动作
        click_combo = QComboBox()
        click_combo.addItems(["无动作", "放大查看", "打开原图"])
        click_map = {"none": 0, "zoom": 1, "open_original": 2}
        click_combo.setCurrentIndex(click_map.get(model.click_action, 0))
        click_combo.currentIndexChanged.connect(lambda i: self._on_property_changed(
            "click_action", ["none", "zoom", "open_original"][i]
        ))
        click_combo.setFixedWidth(100)
        self._add_type_row("点击动作:", click_combo)
        
        # 占位文本
        placeholder_edit = QLineEdit()
        placeholder_edit.setText(model.placeholder_text)
        placeholder_edit.textChanged.connect(lambda v: self._on_property_changed("placeholder_text", v))
        placeholder_edit.setPlaceholderText("无图片时显示的文本")
        self._add_type_row("占位文本:", placeholder_edit)
    
    def _add_video_properties(self, model: VideoModel):
        """添加视频组件属性。"""
        
        # 视频路径选择
        path_layout = QHBoxLayout()
        path_edit = QLineEdit()
        path_edit.setText(model.video_path)
        path_edit.textChanged.connect(lambda v: self._on_property_changed("video_path", v))
        path_edit.setPlaceholderText("视频文件路径")
        path_layout.addWidget(path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setFixedWidth(60)
        browse_btn.clicked.connect(self._browse_video_file)
        path_layout.addWidget(browse_btn)
        
        self._add_type_row("视频路径:", path_layout)
        
        # 自动播放
        auto_check = QCheckBox()
        auto_check.setChecked(model.auto_play)
        auto_check.stateChanged.connect(lambda v: self._on_property_changed("auto_play", bool(v)))
        self._add_type_row("自动播放:", auto_check)
        
        # 循环播放
        loop_check = QCheckBox()
        loop_check.setChecked(model.loop)
        loop_check.stateChanged.connect(lambda v: self._on_property_changed("loop", bool(v)))
        self._add_type_row("循环播放:", loop_check)
        
        # 静音
        muted_check = QCheckBox()
        muted_check.setChecked(model.muted)
        muted_check.stateChanged.connect(lambda v: self._on_property_changed("muted", bool(v)))
        self._add_type_row("静音:", muted_check)
        
        # 显示控制条
        controls_check = QCheckBox()
        controls_check.setChecked(model.controls)
        controls_check.stateChanged.connect(lambda v: self._on_property_changed("controls", bool(v)))
        self._add_type_row("控制条:", controls_check)
        
        # 音量
        volume_spin = QDoubleSpinBox()
        volume_spin.setRange(0.0, 1.0)
        volume_spin.setSingleStep(0.1)
        volume_spin.setValue(model.volume)
        volume_spin.setFixedWidth(60)
        volume_spin.valueChanged.connect(lambda v: self._on_property_changed("volume", v))
        self._add_type_row("音量:", volume_spin)
        
        # 封面图片
        poster_edit = QLineEdit()
        poster_edit.setText(model.poster_image)
        poster_edit.textChanged.connect(lambda v: self._on_property_changed("poster_image", v))
        poster_edit.setPlaceholderText("封面图片路径")
        self._add_type_row("封面图片:", poster_edit)
        
        # 播放速度
        speed_spin = QDoubleSpinBox()
        speed_spin.setRange(0.25, 4.0)
        speed_spin.setSingleStep(0.25)
        speed_spin.setValue(model.playback_rate)
        speed_spin.setFixedWidth(60)
        speed_spin.valueChanged.connect(lambda v: self._on_property_changed("playback_rate", v))
        self._add_type_row("播放速度:", speed_spin)
        
        # 保持宽高比（独立控制是否保持原始比例）
        aspect_check = QCheckBox()
        aspect_check.setChecked(model.aspect_ratio)
        aspect_check.stateChanged.connect(lambda v: self._on_property_changed("aspect_ratio", bool(v)))
        self._add_type_row("保持宽高比:", aspect_check)
        
        # 占位文本
        placeholder_edit = QLineEdit()
        placeholder_edit.setText(model.placeholder_text)
        placeholder_edit.textChanged.connect(lambda v: self._on_property_changed("placeholder_text", v))
        placeholder_edit.setPlaceholderText("无视频时显示的文本")
        self._add_type_row("占位文本:", placeholder_edit)
    
    def _browse_image_file(self):
        """浏览图片文件。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.ico *.svg);;所有文件 (*.*)"
        )
        if file_path and self._current_model:
            self._current_model.image_path = file_path
            self._update_type_specific_properties(self._current_model)
    
    def _browse_video_file(self):
        """浏览视频文件。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.webm);;所有文件 (*.*)"
        )
        if file_path and self._current_model:
            self._current_model.video_path = file_path
            self._update_type_specific_properties(self._current_model)
    
    def _add_label_properties(self, model: LabelModel):
        """添加标签组件属性（已修复：添加缺失的 auto_size 属性）。"""
        # 对齐方式
        align_combo = QComboBox()
        align_combo.addItems(["左对齐", "居中", "右对齐"])
        align_combo.setCurrentIndex({"left": 0, "center": 1, "right": 2}.get(model.alignment, 1))
        align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("alignment", ["left", "center", "right"][i]))
        align_combo.setFixedWidth(100)
        self._add_type_row("对齐:", align_combo)
        
        # 自动换行（复选框）
        wrap_check = QCheckBox()
        wrap_check.setChecked(model.word_wrap)
        wrap_check.stateChanged.connect(lambda v: self._on_property_changed("word_wrap", bool(v)))
        self._add_type_row("自动换行:", wrap_check)
        
        # 自动调整大小（修复：添加缺失的属性）
        auto_size_check = QCheckBox()
        auto_size_check.setChecked(model.auto_size)
        auto_size_check.stateChanged.connect(lambda v: self._on_property_changed("auto_size", bool(v)))
        self._add_type_row("自动调整大小:", auto_size_check)
    
    def _add_input_properties(self, model: InputModel):
        placeholder_edit = QLineEdit()
        placeholder_edit.setText(model.placeholder or "")
        placeholder_edit.setPlaceholderText("输入占位符文本")
        placeholder_edit.setMinimumWidth(150)
        placeholder_edit.textChanged.connect(lambda v: self._on_property_changed("placeholder", v))
        self._add_type_row("占位符:", placeholder_edit)
        
        password_check = QCheckBox()
        password_check.setChecked(model.is_password)
        password_check.stateChanged.connect(lambda v: self._on_property_changed("is_password", bool(v)))
        self._add_type_row("密码框:", password_check)
        
        multiline_check = QCheckBox()
        multiline_check.setChecked(model.is_multiline)
        multiline_check.stateChanged.connect(lambda v: self._on_property_changed("is_multiline", bool(v)))
        self._add_type_row("多行:", multiline_check)
        
        max_length_spin = QSpinBox()
        max_length_spin.setRange(0, 32767)
        max_length_spin.setValue(model.max_length)
        max_length_spin.setFixedWidth(80)
        max_length_spin.valueChanged.connect(lambda v: self._on_property_changed("max_length", v))
        self._add_type_row("最大长度:", max_length_spin)
    
    def _add_container_properties(self, model: ContainerModel):
        position_combo = QComboBox()
        position_combo.addItems(["居中", "左上角", "自定义"])
        position_combo.setCurrentIndex({"center": 0, "top_left": 1, "custom": 2}.get(model.position_mode, 0))
        position_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("position_mode", ["center", "top_left", "custom"][i]))
        position_combo.setFixedWidth(100)
        self._add_type_row("定位模式:", position_combo)
        
        layout_combo = QComboBox()
        layout_combo.addItems(["无", "垂直", "水平", "网格"])
        layout_combo.setCurrentIndex({"none": 0, "vertical": 1, "horizontal": 2, "grid": 3}.get(model.layout, 0))
        layout_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("layout", ["none", "vertical", "horizontal", "grid"][i]))
        layout_combo.setFixedWidth(100)
        self._add_type_row("布局:", layout_combo)
        
        padding_spin = QSpinBox()
        padding_spin.setRange(0, 100)
        padding_spin.setValue(model.padding)
        padding_spin.setFixedWidth(60)
        padding_spin.valueChanged.connect(lambda v: self._on_property_changed("padding", v))
        self._add_type_row("内边距:", padding_spin)
        
        spacing_spin = QSpinBox()
        spacing_spin.setRange(0, 100)
        spacing_spin.setValue(model.spacing)
        spacing_spin.setFixedWidth(60)
        spacing_spin.valueChanged.connect(lambda v: self._on_property_changed("spacing", v))
        self._add_type_row("间距:", spacing_spin)
    
    def _add_checkbox_properties(self, model: CheckBoxModel):
        checked_check = QCheckBox()
        checked_check.setChecked(model.checked)
        checked_check.stateChanged.connect(lambda v: self._on_property_changed("checked", bool(v)))
        self._add_type_row("选中:", checked_check)
    
    def _add_combobox_properties(self, model: ComboBoxModel):
        items_edit = QLineEdit()
        items_edit.setText(", ".join(model.items))
        items_edit.setPlaceholderText("用逗号分隔选项")
        items_edit.textChanged.connect(lambda v: self._on_property_changed("items", [x.strip() for x in v.split(",") if x.strip()]))
        self._add_type_row("选项:", items_edit)
        
        index_spin = QSpinBox()
        index_spin.setRange(0, 1000)
        index_spin.setValue(model.current_index)
        index_spin.setFixedWidth(60)
        index_spin.valueChanged.connect(lambda v: self._on_property_changed("current_index", v))
        self._add_type_row("当前索引:", index_spin)
    
    def _add_progressbar_properties(self, model: ProgressBarModel):
        value_spin = QSpinBox()
        value_spin.setRange(0, 100)
        value_spin.setValue(model.value)
        value_spin.setFixedWidth(60)
        value_spin.valueChanged.connect(lambda v: self._on_property_changed("value", v))
        self._add_type_row("当前值:", value_spin)
        
        show_text_check = QCheckBox()
        show_text_check.setChecked(model.show_text)
        show_text_check.stateChanged.connect(lambda v: self._on_property_changed("show_text", bool(v)))
        self._add_type_row("显示文本:", show_text_check)
        
        text_pos_combo = QComboBox()
        text_pos_combo.addItems(["左侧", "居中", "右侧", "跟随进度"])
        text_pos_map = {"left": 0, "center": 1, "right": 2, "follow": 3}
        text_pos_combo.setCurrentIndex(text_pos_map.get(model.text_position, 1))
        text_pos_combo.setFixedWidth(100)
        text_pos_combo.currentIndexChanged.connect(lambda i: self._on_property_changed(
            "text_position", ["left", "center", "right", "follow"][i]
        ))
        self._add_type_row("文本位置:", text_pos_combo)
        
        auto_check = QCheckBox()
        auto_check.setChecked(model.auto_progress)
        auto_check.stateChanged.connect(lambda v: self._on_property_changed("auto_progress", bool(v)))
        self._add_type_row("自动进度:", auto_check)
        
        duration_spin = QSpinBox()
        duration_spin.setRange(1, 60)
        duration_spin.setValue(model.duration)
        duration_spin.setFixedWidth(60)
        duration_spin.valueChanged.connect(lambda v: self._on_property_changed("duration", v))
        self._add_type_row("持续时间:", duration_spin)
        
        branch_label = QLabel(model.branch_name or "无")
        branch_label.setStyleSheet("color: #666;")
        self._add_type_row("分支:", branch_label)
        
        if model.has_branch:
            goto_btn = QPushButton("跳转到事件")
            goto_btn.clicked.connect(lambda: self.goto_event_requested.emit(model.target_window_id))
            self._type_layout.addWidget(goto_btn)
        else:
            create_event_btn = QPushButton("创建事件分支")
            create_event_btn.clicked.connect(lambda: self.create_event_requested.emit(model.id))
            self._type_layout.addWidget(create_event_btn)
        
        action_btn = QPushButton("配置行为")
        action_btn.clicked.connect(lambda: self.action_config_requested.emit(model.id))
        self._type_layout.addWidget(action_btn)
