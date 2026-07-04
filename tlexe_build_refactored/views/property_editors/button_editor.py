"""按钮组件属性编辑器。"""

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QWidget
from .base_editor import BasePropertyEditor
from .registry import register_property_editor

@register_property_editor('button')
class ButtonEditor(BasePropertyEditor):
    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)
        
        self.default_check = QCheckBox()
        self.default_check.stateChanged.connect(lambda v: self._on_property_changed("is_default", bool(v)))
        self._add_row("默认按钮:", self.default_check)
        
        self.cancel_check = QCheckBox()
        self.cancel_check.stateChanged.connect(lambda v: self._on_property_changed("is_cancel", bool(v)))
        self._add_row("取消按钮:", self.cancel_check)
        
        self.align_combo = QComboBox()
        self.align_combo.addItems(["左对齐", "居中", "右对齐"])
        self.align_combo.currentIndexChanged.connect(lambda i: self._on_property_changed("alignment", ["left", "center", "right"][i]))
        self.align_combo.setFixedWidth(100)
        self._add_row("对齐:", self.align_combo)
        
        # 正常动作区域
        self.normal_action_widget = QWidget()
        normal_layout = QVBoxLayout(self.normal_action_widget)
        normal_layout.setContentsMargins(0, 0, 0, 0)
        normal_layout.setSpacing(10)
        
        branch_layout = QHBoxLayout()
        branch_layout.setSpacing(14)
        branch_label_title = QLabel("分支:")
        branch_label_title.setFixedWidth(70)
        branch_label_title.setStyleSheet("color: #555;")
        branch_layout.addWidget(branch_label_title)
        self.branch_label = QLabel("无")
        self.branch_label.setStyleSheet("color: #666;")
        branch_layout.addWidget(self.branch_label)
        branch_layout.addStretch()
        normal_layout.addLayout(branch_layout)
        
        self.action_btn = QPushButton("配置行为")
        self.action_btn.clicked.connect(self.action_config_requested.emit)
        normal_layout.addWidget(self.action_btn)
        
        self._event_btn = None
        self._layout.addWidget(self.normal_action_widget)
        
        # 延伸组件提示区域
        self.extension_widget = QWidget()
        ext_layout = QVBoxLayout(self.extension_widget)
        ext_layout.setContentsMargins(0, 0, 0, 0)
        ext_layout.setSpacing(10)
        
        self.extension_warning_label = QLabel()
        self.extension_warning_label.setWordWrap(True)
        self.extension_warning_label.setStyleSheet("color: #e6a23c; font-size: 12px; font-weight: bold; padding: 5px; border: 1px solid #faecd8; background-color: #fdf6ec; border-radius: 4px;")
        ext_layout.addWidget(self.extension_warning_label)
        
        self.unbind_btn = QPushButton("解除关联")
        self.unbind_btn.setStyleSheet("QPushButton{background-color:#f56c6c;color:white;border-radius:4px;padding:6px;font-weight:bold;} QPushButton:hover{background-color:#f78989;}")
        self.unbind_btn.clicked.connect(self._on_unbind_clicked)
        ext_layout.addWidget(self.unbind_btn)
        
        self._layout.addWidget(self.extension_widget)
        self.extension_widget.hide()
        
    def _add_row(self, label_text, widget):
        from PySide6.QtWidgets import QWidget
        layout = QHBoxLayout()
        layout.setSpacing(14)
        label = QLabel(label_text)
        label.setFixedWidth(70)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.addStretch()
        self._layout.addLayout(layout)
        
    def _update_ui_from_model(self):
        self._updating = True
        try:
            self.default_check.setChecked(self._model.is_default)
            self.cancel_check.setChecked(self._model.is_cancel)
            self.align_combo.setCurrentIndex({"left": 0, "center": 1, "right": 2}.get(self._model.alignment, 1))
            
            action_type = ""
            if hasattr(self._model, 'action') and self._model.action:
                action_type = self._model.action.action_type
                
            is_extension = action_type in ['start_alternating', 'stop_alternating', 'lottery_animation']
            
            if is_extension:
                self.normal_action_widget.hide()
                self.extension_widget.show()
                target_id = self._model.action.params.get('target_component_id', '未知组件')
                action_name = "开始" if "start" in action_type else ("停止" if "stop" in action_type else "抽奖触发")
                self.extension_warning_label.setText(f"⚠️ 此组件目前作为 [{target_id}] 的 {action_name}触发器 延伸产物被绑定。")
            else:
                self.extension_widget.hide()
                self.normal_action_widget.show()
                self.branch_label.setText(self._model.branch_name or "无")
                
                if self._event_btn:
                    self._event_btn.deleteLater()
                    self._event_btn = None
                    
                if self._model.has_branch:
                    self._event_btn = QPushButton("跳转到事件")
                    self._event_btn.clicked.connect(lambda: self.goto_event_requested.emit(self._model.target_window_id))
                else:
                    self._event_btn = QPushButton("创建事件分支")
                    self._event_btn.clicked.connect(lambda: self.create_event_requested.emit(self._model.id))
                
                self.normal_action_widget.layout().insertWidget(1, self._event_btn)
        finally:
            self._updating = False

    def _on_unbind_clicked(self):
        if not self._model or not self._model.action:
            return
        target_id = self._model.action.params.get('target_component_id', '')
        action_type = self._model.action.action_type
        self.unbind_extension_requested.emit(self._model.id, target_id, action_type)

