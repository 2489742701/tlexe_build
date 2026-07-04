"""基础组件属性编辑器。

包含 Label, Input, Container, CheckBox, ComboBox, ProgressBar 等组件的属性编辑器。
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
    QComboBox, QSpinBox, QPushButton
)
from .base_editor import BasePropertyEditor
from .registry import register_property_editor

class BaseBasicEditor(BasePropertyEditor):
    """基础属性编辑器，提供辅助方法。"""
    
    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)
        self._setup_specific_ui()
        
    def _setup_specific_ui(self):
        pass
        
    def _add_row(self, label_text, widget_or_layout):
        layout = QHBoxLayout()
        layout.setSpacing(14)
        label = QLabel(label_text)
        label.setFixedWidth(70)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        
        from PySide6.QtWidgets import QWidget, QLayout
        if isinstance(widget_or_layout, QLayout):
            container = QWidget()
            container.setLayout(widget_or_layout)
            layout.addWidget(container)
        else:
            layout.addWidget(widget_or_layout)
            
        layout.addStretch()
        self._layout.addLayout(layout)

@register_property_editor('label')
class LabelEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.align_combo = QComboBox()
        self.align_combo.addItems(["左对齐", "居中", "右对齐"])
        self.align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("alignment", ["left", "center", "right"][i]))
        self.align_combo.setFixedWidth(100)
        self._add_row("对齐:", self.align_combo)
        
        self.wrap_check = QCheckBox()
        self.wrap_check.stateChanged.connect(lambda v: self._on_property_changed("word_wrap", bool(v)))
        self._add_row("自动换行:", self.wrap_check)
        
        self.auto_size_check = QCheckBox()
        self.auto_size_check.stateChanged.connect(lambda v: self._on_property_changed("auto_size", bool(v)))
        self._add_row("自动调整大小:", self.auto_size_check)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.align_combo.setCurrentIndex({"left": 0, "center": 1, "right": 2}.get(self._model.alignment, 1))
            self.wrap_check.setChecked(self._model.word_wrap)
            self.auto_size_check.setChecked(self._model.auto_size)
        finally:
            self._updating = False

@register_property_editor('input')
@register_property_editor('textarea')
class InputEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.placeholder_edit = QLineEdit()
        self.placeholder_edit.setPlaceholderText("输入占位符文本")
        self.placeholder_edit.setMinimumWidth(150)
        self.placeholder_edit.textChanged.connect(lambda v: self._on_property_changed("placeholder", v))
        self._add_row("占位符:", self.placeholder_edit)
        
        self.password_check = QCheckBox()
        self.password_check.stateChanged.connect(lambda v: self._on_property_changed("is_password", bool(v)))
        self._add_row("密码框:", self.password_check)
        
        self.multiline_check = QCheckBox()
        self.multiline_check.stateChanged.connect(lambda v: self._on_property_changed("is_multiline", bool(v)))
        self._add_row("多行:", self.multiline_check)
        
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(0, 32767)
        self.max_length_spin.setFixedWidth(80)
        self.max_length_spin.valueChanged.connect(lambda v: self._on_property_changed("max_length", v))
        self._add_row("最大长度:", self.max_length_spin)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.placeholder_edit.setText(self._model.placeholder or "")
            self.password_check.setChecked(self._model.is_password)
            self.multiline_check.setChecked(self._model.is_multiline)
            self.max_length_spin.setValue(self._model.max_length)
        finally:
            self._updating = False

@register_property_editor('container')
@register_property_editor('groupbox')
class ContainerEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.position_combo = QComboBox()
        self.position_combo.addItems(["居中", "左上角", "自定义"])
        self.position_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("position_mode", ["center", "top_left", "custom"][i]))
        self.position_combo.setFixedWidth(100)
        self._add_row("定位模式:", self.position_combo)
        
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["无", "垂直", "水平", "网格"])
        self.layout_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("layout", ["none", "vertical", "horizontal", "grid"][i]))
        self.layout_combo.setFixedWidth(100)
        self._add_row("布局:", self.layout_combo)
        
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 100)
        self.padding_spin.setFixedWidth(60)
        self.padding_spin.valueChanged.connect(lambda v: self._on_property_changed("padding", v))
        self._add_row("内边距:", self.padding_spin)
        
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 100)
        self.spacing_spin.setFixedWidth(60)
        self.spacing_spin.valueChanged.connect(lambda v: self._on_property_changed("spacing", v))
        self._add_row("间距:", self.spacing_spin)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.position_combo.setCurrentIndex({"center": 0, "top_left": 1, "custom": 2}.get(self._model.position_mode, 0))
            self.layout_combo.setCurrentIndex({"none": 0, "vertical": 1, "horizontal": 2, "grid": 3}.get(self._model.layout, 0))
            self.padding_spin.setValue(self._model.padding)
            self.spacing_spin.setValue(self._model.spacing)
        finally:
            self._updating = False

@register_property_editor('checkbox')
class CheckBoxEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.checked_check = QCheckBox()
        self.checked_check.stateChanged.connect(lambda v: self._on_property_changed("checked", bool(v)))
        self._add_row("选中:", self.checked_check)
        
        self.align_combo = QComboBox()
        self.align_combo.addItems(["左对齐", "居中", "右对齐"])
        self.align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("alignment", ["left", "center", "right"][i]))
        self.align_combo.setFixedWidth(100)
        self._add_row("对齐:", self.align_combo)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.checked_check.setChecked(self._model.checked)
            self.align_combo.setCurrentIndex({"left": 0, "center": 1, "right": 2}.get(self._model.alignment, 0))
        finally:
            self._updating = False

@register_property_editor('combobox')
@register_property_editor('listwidget')
class ComboBoxEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.items_edit = QLineEdit()
        self.items_edit.setPlaceholderText("用逗号分隔选项")
        self.items_edit.textChanged.connect(lambda v: self._on_property_changed("items", [x.strip() for x in v.split(",") if x.strip()]))
        self._add_row("选项:", self.items_edit)
        
        self.index_spin = QSpinBox()
        self.index_spin.setRange(0, 1000)
        self.index_spin.setFixedWidth(60)
        self.index_spin.valueChanged.connect(lambda v: self._on_property_changed("current_index", v))
        self._add_row("当前索引:", self.index_spin)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.items_edit.setText(", ".join(self._model.items))
            self.index_spin.setValue(self._model.current_index)
        finally:
            self._updating = False

@register_property_editor('progressbar')
class ProgressBarEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.value_spin = QSpinBox()
        self.value_spin.setRange(0, 100)
        self.value_spin.setFixedWidth(60)
        self.value_spin.valueChanged.connect(lambda v: self._on_property_changed("value", v))
        self._add_row("当前值:", self.value_spin)
        
        self.show_text_check = QCheckBox()
        self.show_text_check.stateChanged.connect(lambda v: self._on_property_changed("show_text", bool(v)))
        self._add_row("显示文本:", self.show_text_check)
        
        self.text_pos_combo = QComboBox()
        self.text_pos_combo.addItems(["左侧", "居中", "右侧", "跟随进度"])
        self.text_pos_combo.setFixedWidth(100)
        self.text_pos_combo.currentIndexChanged.connect(lambda i: self._on_property_changed(
            "text_position", ["left", "center", "right", "follow"][i]
        ))
        self._add_row("文本位置:", self.text_pos_combo)
        
        self.auto_check = QCheckBox()
        self.auto_check.stateChanged.connect(lambda v: self._on_property_changed("auto_progress", bool(v)))
        self._add_row("自动进度:", self.auto_check)
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setFixedWidth(60)
        self.duration_spin.valueChanged.connect(lambda v: self._on_property_changed("duration", v))
        self._add_row("持续时间:", self.duration_spin)
        
        self.branch_label = QLabel("无")
        self.branch_label.setStyleSheet("color: #666;")
        self._add_row("分支:", self.branch_label)
        
        self.action_btn = QPushButton("配置行为")
        self.action_btn.clicked.connect(self.action_config_requested.emit)
        self._layout.addWidget(self.action_btn)
        
        self._event_btn = None

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.value_spin.setValue(self._model.value)
            self.show_text_check.setChecked(self._model.show_text)
            text_pos_map = {"left": 0, "center": 1, "right": 2, "follow": 3}
            self.text_pos_combo.setCurrentIndex(text_pos_map.get(self._model.text_position, 1))
            self.auto_check.setChecked(self._model.auto_progress)
            self.duration_spin.setValue(self._model.duration)
            self.branch_label.setText(self._model.branch_name or "无")
            
            if self._event_btn:
                self._event_btn.deleteLater()
                self._event_btn = None
                
            if self._model.has_branch:
                self._event_btn = QPushButton("跳转到事件")
                self._event_btn.clicked.connect(lambda: self.parent().goto_event_requested.emit(self._model.target_window_id))
            else:
                self._event_btn = QPushButton("创建事件分支")
                self._event_btn.clicked.connect(lambda: self.parent().create_event_requested.emit(self._model.id))
                
            self._layout.insertWidget(self._layout.count() - 1, self._event_btn)
        finally:
            self._updating = False

@register_property_editor('group_node')
class GroupNodeEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["无", "垂直", "水平", "网格"])
        self.layout_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("layout_mode", ["none", "vertical", "horizontal", "grid"][i]))
        self.layout_combo.setFixedWidth(100)
        self._add_row("布局:", self.layout_combo)
        
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 100)
        self.spacing_spin.setFixedWidth(60)
        self.spacing_spin.valueChanged.connect(lambda v: self._on_property_changed("spacing", v))
        self._add_row("间距:", self.spacing_spin)
        
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 100)
        self.padding_spin.setFixedWidth(60)
        self.padding_spin.valueChanged.connect(lambda v: self._on_property_changed("padding", v))
        self._add_row("内边距:", self.padding_spin)
        
        self.auto_size_check = QCheckBox()
        self.auto_size_check.stateChanged.connect(lambda v: self._on_property_changed("auto_size", bool(v)))
        self._add_row("自动大小:", self.auto_size_check)
        
        self.show_border_check = QCheckBox()
        self.show_border_check.stateChanged.connect(lambda v: self._on_property_changed("show_border", bool(v)))
        self._add_row("显示边框:", self.show_border_check)
        
        self.border_style_combo = QComboBox()
        self.border_style_combo.addItems(["实线", "虚线", "点线", "无"])
        self.border_style_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("border_style", ["solid", "dashed", "dotted", "none"][i]))
        self.border_style_combo.setFixedWidth(100)
        self._add_row("边框样式:", self.border_style_combo)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.layout_combo.setCurrentIndex({"none": 0, "vertical": 1, "horizontal": 2, "grid": 3}.get(self._model.layout_mode, 0))
            self.spacing_spin.setValue(self._model.spacing)
            self.padding_spin.setValue(self._model.padding)
            self.auto_size_check.setChecked(self._model.auto_size)
            self.show_border_check.setChecked(self._model.show_border)
            self.border_style_combo.setCurrentIndex({"solid": 0, "dashed": 1, "dotted": 2, "none": 3}.get(self._model.border_style, 1))
        finally:
            self._updating = False

@register_property_editor('confirm_button')
class ConfirmButtonEditor(BaseBasicEditor):
    def _setup_specific_ui(self):
        self.group_edit = QLineEdit()
        self.group_edit.textChanged.connect(lambda v: self._on_property_changed("confirm_group", v))
        self._add_row("确认组:", self.group_edit)
        
        self.confirmed_check = QCheckBox()
        self.confirmed_check.stateChanged.connect(lambda v: self._on_property_changed("is_confirmed", bool(v)))
        self._add_row("已确认:", self.confirmed_check)
        
        self.action_btn = QPushButton("配置行为")
        self.action_btn.clicked.connect(self.action_config_requested.emit)
        self._layout.addWidget(self.action_btn)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.group_edit.setText(self._model.confirm_group)
            self.confirmed_check.setChecked(self._model.is_confirmed)
        finally:
            self._updating = False
