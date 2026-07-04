"""多媒体组件属性编辑器。

包含 Image, Video, ImageCarousel, HiddenButton, ImageButton 等组件的属性编辑器。
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
    QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QFileDialog
)
from .base_editor import BasePropertyEditor
from .registry import register_property_editor

class BaseMediaEditor(BasePropertyEditor):
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

@register_property_editor('image')
class ImageEditor(BaseMediaEditor):
    def _setup_specific_ui(self):
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setFixedWidth(50)
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.browse_btn)
        self._add_row("图片路径:", path_layout)
        
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["自适应(fit)", "填充(fill)", "拉伸(stretch)", "居中(center)"])
        self.scale_combo.currentIndexChanged.connect(self._on_scale_changed)
        self.scale_combo.setFixedWidth(100)
        self._add_row("缩放模式:", self.scale_combo)
        
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 100)
        self.radius_spin.valueChanged.connect(lambda v: self._on_property_changed("border_radius", v))
        self._add_row("圆角:", self.radius_spin)
        
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setSingleStep(0.1)
        self.opacity_spin.valueChanged.connect(lambda v: self._on_property_changed("opacity", v))
        self._add_row("不透明度:", self.opacity_spin)
        
        self.hover_check = QCheckBox()
        self.hover_check.stateChanged.connect(lambda v: self._on_property_changed("hover_effect", bool(v)))
        self._add_row("悬停效果:", self.hover_check)
        
    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            self._on_property_changed("image_path", path)
            self.path_edit.setText(path)
            
    def _on_scale_changed(self, index):
        modes = ['fit', 'fill', 'stretch', 'center']
        if 0 <= index < len(modes):
            self._on_property_changed("scale_mode", modes[index])

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.path_edit.setText(self._model.image_path)
            modes = {'fit': 0, 'fill': 1, 'stretch': 2, 'center': 3}
            self.scale_combo.setCurrentIndex(modes.get(self._model.scale_mode, 0))
            self.radius_spin.setValue(self._model.border_radius)
            self.opacity_spin.setValue(self._model.opacity)
            self.hover_check.setChecked(self._model.hover_effect)
        finally:
            self._updating = False

@register_property_editor('video')
class VideoEditor(BaseMediaEditor):
    def _setup_specific_ui(self):
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setFixedWidth(50)
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.browse_btn)
        self._add_row("视频路径:", path_layout)
        
        self.auto_play_check = QCheckBox()
        self.auto_play_check.stateChanged.connect(lambda v: self._on_property_changed("auto_play", bool(v)))
        self._add_row("自动播放:", self.auto_play_check)
        
        self.loop_check = QCheckBox()
        self.loop_check.stateChanged.connect(lambda v: self._on_property_changed("loop", bool(v)))
        self._add_row("循环播放:", self.loop_check)
        
        self.muted_check = QCheckBox()
        self.muted_check.stateChanged.connect(lambda v: self._on_property_changed("muted", bool(v)))
        self._add_row("静音:", self.muted_check)
        
        self.controls_check = QCheckBox()
        self.controls_check.stateChanged.connect(lambda v: self._on_property_changed("controls", bool(v)))
        self._add_row("显示控制条:", self.controls_check)
        
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.0, 1.0)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.valueChanged.connect(lambda v: self._on_property_changed("volume", v))
        self._add_row("音量:", self.volume_spin)

    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择视频", "", "Videos (*.mp4 *.avi *.mkv *.mov)")
        if path:
            self._on_property_changed("video_path", path)
            self.path_edit.setText(path)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.path_edit.setText(self._model.video_path)
            self.auto_play_check.setChecked(self._model.auto_play)
            self.loop_check.setChecked(self._model.loop)
            self.muted_check.setChecked(self._model.muted)
            self.controls_check.setChecked(self._model.controls)
            self.volume_spin.setValue(self._model.volume)
        finally:
            self._updating = False

@register_property_editor('hidden_button')
class HiddenButtonEditor(BaseMediaEditor):
    def _setup_specific_ui(self):
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
            self.branch_label.setText(self._model.branch_name or "无")
            if self._event_btn:
                self._event_btn.deleteLater()
                self._event_btn = None
                
            if getattr(self._model, 'has_branch', False):
                self._event_btn = QPushButton("跳转到事件")
                self._event_btn.clicked.connect(lambda: self.parent().goto_event_requested.emit(self._model.target_window_id))
            else:
                self._event_btn = QPushButton("创建事件分支")
                self._event_btn.clicked.connect(lambda: self.parent().create_event_requested.emit(self._model.id))
            self._layout.insertWidget(self._layout.count() - 1, self._event_btn)
        finally:
            self._updating = False

@register_property_editor('image_button')
class ImageButtonEditor(BaseMediaEditor):
    def _setup_specific_ui(self):
        self._add_image_row("默认图片:", "normal_image")
        self._add_image_row("悬停图片:", "hover_image")
        self._add_image_row("按下图片:", "pressed_image")
        
        self.branch_label = QLabel("无")
        self.branch_label.setStyleSheet("color: #666;")
        self._add_row("分支:", self.branch_label)
        
        self.action_btn = QPushButton("配置行为")
        self.action_btn.clicked.connect(self.action_config_requested.emit)
        self._layout.addWidget(self.action_btn)
        self._event_btn = None

    def _add_image_row(self, label_text, property_name):
        layout = QHBoxLayout()
        edit = QLineEdit()
        edit.setReadOnly(True)
        setattr(self, f"{property_name}_edit", edit)
        layout.addWidget(edit)
        
        btn = QPushButton("浏览")
        btn.setFixedWidth(50)
        btn.clicked.connect(lambda: self._on_browse_image(property_name))
        layout.addWidget(btn)
        self._add_row(label_text, layout)

    def _on_browse_image(self, property_name):
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            self._on_property_changed(property_name, path)
            getattr(self, f"{property_name}_edit").setText(path)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.normal_image_edit.setText(getattr(self._model, 'normal_image', ''))
            self.hover_image_edit.setText(getattr(self._model, 'hover_image', ''))
            self.pressed_image_edit.setText(getattr(self._model, 'pressed_image', ''))
            self.branch_label.setText(getattr(self._model, 'branch_name', '') or "无")
            
            if self._event_btn:
                self._event_btn.deleteLater()
                self._event_btn = None
                
            if getattr(self._model, 'has_branch', False):
                self._event_btn = QPushButton("跳转到事件")
                self._event_btn.clicked.connect(lambda: self.parent().goto_event_requested.emit(self._model.target_window_id))
            else:
                self._event_btn = QPushButton("创建事件分支")
                self._event_btn.clicked.connect(lambda: self.parent().create_event_requested.emit(self._model.id))
            self._layout.insertWidget(self._layout.count() - 1, self._event_btn)
        finally:
            self._updating = False

@register_property_editor('image_carousel')
class ImageCarouselEditor(BaseMediaEditor):
    def _setup_specific_ui(self):
        self.auto_play_check = QCheckBox()
        self.auto_play_check.stateChanged.connect(lambda v: self._on_property_changed("auto_play", bool(v)))
        self._add_row("自动播放:", self.auto_play_check)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(500, 10000)
        self.interval_spin.setSingleStep(500)
        self.interval_spin.valueChanged.connect(lambda v: self._on_property_changed("interval", v))
        self._add_row("切换间隔(ms):", self.interval_spin)

    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.auto_play_check.setChecked(getattr(self._model, 'auto_play', False))
            self.interval_spin.setValue(getattr(self._model, 'interval', 3000))
        finally:
            self._updating = False

