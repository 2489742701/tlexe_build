"""属性面板模块。

本模块包含组件属性编辑面板的实现。
支持基础属性、样式属性、类型特定属性的编辑。
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QCheckBox, QComboBox,
    QPushButton, QGroupBox, QColorDialog, QFrame, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from models import (
    ComponentModel, ButtonModel, LabelModel, InputModel, 
    ContainerModel, CheckBoxModel, ComboBoxModel, ImageModel, VideoModel, ProgressBarModel
)


GROUP_STYLE = """
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #c0c0c0;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 8px;
        background-color: #fafafa;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: #333333;
    }
"""


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
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #ffffff;")
        scroll_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._content_layout = QVBoxLayout(scroll_content)
        self._content_layout.setContentsMargins(12, 12, 12, 12)
        self._content_layout.setSpacing(16)
        
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
        layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setFixedWidth(60)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        
        layout.addWidget(widget)
        
        if stretch:
            layout.addStretch()
        
        return layout
    
    def _create_basic_group(self) -> QGroupBox:
        group = QGroupBox("基础属性")
        group.setStyleSheet(GROUP_STYLE)
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
        self._name_edit.textChanged.connect(lambda v: self._on_property_changed("name", v))
        layout.addLayout(self._create_row("名称:", self._name_edit))
        
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("输入显示文本")
        self._text_edit.setMaximumHeight(80)
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
        group.setStyleSheet(GROUP_STYLE)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        pos_layout = QHBoxLayout()
        pos_layout.setSpacing(8)
        
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
        size_layout.setSpacing(8)
        
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
        align_layout.setSpacing(8)
        
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
        group.setStyleSheet(GROUP_STYLE)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        style_mode_layout = QHBoxLayout()
        style_mode_layout.setSpacing(8)
        
        mode_label = QLabel("样式模式:")
        mode_label.setFixedWidth(60)
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
        custom_layout.setSpacing(10)
        
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(8)
        
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
        border_layout.setSpacing(8)
        
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
        other_layout.setSpacing(8)
        
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
        group.setStyleSheet(GROUP_STYLE)
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
    
    def _clear_type_specific_properties(self):
        while self._type_layout.count():
            item = self._type_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _add_type_row(self, label_text: str, widget: QWidget) -> QHBoxLayout:
        """创建特定属性行。"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setFixedWidth(70)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        
        layout.addWidget(widget)
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
    
    def _add_label_properties(self, model: LabelModel):
        align_combo = QComboBox()
        align_combo.addItems(["左对齐", "居中", "右对齐"])
        align_combo.setCurrentIndex({"left": 0, "center": 1, "right": 2}.get(model.alignment, 1))
        align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("alignment", ["left", "center", "right"][i]))
        align_combo.setFixedWidth(100)
        self._add_type_row("对齐:", align_combo)
        
        wrap_check = QCheckBox()
        wrap_check.setChecked(model.word_wrap)
        wrap_check.stateChanged.connect(lambda v: self._on_property_changed("word_wrap", bool(v)))
        self._add_type_row("自动换行:", wrap_check)
    
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
