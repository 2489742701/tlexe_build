"""抽奖组件属性编辑器。"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QMenu, QToolButton
)
from PySide6.QtCore import Qt, Signal

from .base_editor import BasePropertyEditor
from .registry import register_property_editor


@register_property_editor('lottery')
class LotteryPropertyEditor(BasePropertyEditor):
    """抽奖组件属性编辑器。"""
    
    start_button_set = Signal(str, str)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        layout.addWidget(QLabel("显示模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["图片模式", "文字模式"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        layout.addWidget(self.mode_combo)
        
        layout.addWidget(QLabel("动画时长(毫秒):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(500, 30000)
        self.duration_spin.setSingleStep(500)
        self.duration_spin.setValue(3000)
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        layout.addWidget(self.duration_spin)
        
        start_btn_layout = QHBoxLayout()
        self.set_start_btn = QPushButton("设定开始按钮")
        self.set_start_btn.setToolTip("点击选择项目中的按钮组件作为抽奖触发按钮")
        self.set_start_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; border-radius: 4px; padding: 6px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        self.set_start_btn.clicked.connect(self._on_set_start_button)
        start_btn_layout.addWidget(self.set_start_btn)
        
        self.bound_label = QLabel("")
        self.bound_label.setStyleSheet("color: #666666; font-size: 11px;")
        start_btn_layout.addWidget(self.bound_label)
        start_btn_layout.addStretch()
        layout.addLayout(start_btn_layout)
        
        layout.addWidget(QLabel("候选项列表:"))
        self.items_list = QListWidget()
        self.items_list.setMinimumHeight(120)
        layout.addWidget(self.items_list)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self._on_add_item)
        btn_layout.addWidget(self.add_btn)
        
        self.del_btn = QPushButton("删除")
        self.del_btn.clicked.connect(self._on_del_item)
        btn_layout.addWidget(self.del_btn)
        
        self.up_btn = QPushButton("上移")
        self.up_btn.clicked.connect(self._on_move_up)
        btn_layout.addWidget(self.up_btn)
        
        self.down_btn = QPushButton("下移")
        self.down_btn.clicked.connect(self._on_move_down)
        btn_layout.addWidget(self.down_btn)
        
        layout.addLayout(btn_layout)
        
        self.warn_label = QLabel("")
        self.warn_label.setStyleSheet("color: #CC9900; font-size: 11px;")
        layout.addWidget(self.warn_label)
        
        layout.addStretch()
    
    def _get_project_model(self):
        """通过 parent 链获取 ProjectModel。"""
        widget = self.parent()
        while widget:
            pm = getattr(widget, '_project_model', None)
            if pm:
                return pm
            pm = getattr(widget, 'project_model', None)
            if pm:
                return pm
            widget = widget.parent()
        
        window = self.window()
        if window:
            for attr in ('_project_model', 'project_model'):
                pm = getattr(window, attr, None)
                if pm:
                    return pm
            controller = getattr(window, '_controller', None)
            if controller:
                pm = getattr(controller, 'project_model', None)
                if pm:
                    return pm
                pm = getattr(controller, '_project_model', None)
                if pm:
                    return pm
        return None
    
    def _on_set_start_button(self):
        """设定开始按钮：展示项目中所有按钮组件供用户点选。"""
        if not self._model:
            return
        
        if self._model.is_animating:
            QMessageBox.warning(self, "提示", "抽奖动画执行中，无法设定开始按钮")
            return
        
        project_model = self._get_project_model()
        if not project_model:
            QMessageBox.warning(self, "提示", "无法获取项目模型，请确保编辑器已正确初始化")
            return
        
        all_components = []
        get_all = getattr(project_model, 'get_all_components', None)
        if get_all:
            all_components = get_all()
        elif hasattr(project_model, '_components'):
            all_components = list(project_model._components.values())
        
        buttons = [c for c in all_components if getattr(c, 'type', '') == 'button']
        
        if not buttons:
            QMessageBox.information(self, "提示", "项目中没有按钮组件。\n请先添加一个按钮组件。")
            return
        
        menu = QMenu(self)
        for btn_comp in buttons:
            name = getattr(btn_comp, 'name', '') or getattr(btn_comp, 'text', '') or btn_comp.id
            action = menu.addAction(f"{name} (ID: {btn_comp.id[:8]}...)")
            action.setData(btn_comp)
        
        menu.setStyleSheet("QMenu { min-width: 200px; }")
        pos = self.set_start_btn.mapToGlobal(self.set_start_btn.rect().bottomLeft())
        selected = menu.exec(pos)
        
        if not selected:
            return
        
        btn_comp = selected.data()
        if not btn_comp:
            return
        
        from models.base import ActionConfig
        current_action = getattr(btn_comp, '_action', None)
        if current_action and getattr(current_action, 'action_type', 'none') != 'none':
            reply = QMessageBox.question(
                self, "确认覆盖",
                f"按钮 \"{btn_comp.name}\" 已有动作配置 ({current_action.action_type})。\n"
                f"是否覆盖为抽奖动画？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        btn_comp._action = ActionConfig(
            action_type="lottery_animation",
            params={"target_component_id": self._model.id}
        )
        btn_comp.data_changed.emit()
        
        self.bound_label.setText(f"→ {btn_comp.name}")
        self.bound_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        
        self.start_button_set.emit(btn_comp.id, self._model.id)
    
    def _update_bound_label(self):
        """更新已绑定按钮的显示。"""
        if not self._model:
            return
        
        project_model = self._get_project_model()
        if not project_model:
            self.bound_label.setText("")
            return
        
        all_components = []
        get_all = getattr(project_model, 'get_all_components', None)
        if get_all:
            all_components = get_all()
        elif hasattr(project_model, '_components'):
            all_components = list(project_model._components.values())
        
        bound_name = None
        for comp in all_components:
            if getattr(comp, 'type', '') == 'button':
                action = getattr(comp, '_action', None)
                if action and getattr(action, 'action_type', '') == 'lottery_animation':
                    target = action.params.get('target_component_id', '')
                    if target == self._model.id:
                        bound_name = getattr(comp, 'name', '')
                        break
        
        if bound_name:
            self.bound_label.setText(f"→ {bound_name}")
            self.bound_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        else:
            self.bound_label.setText("未设定")
            self.bound_label.setStyleSheet("color: #999999; font-size: 11px;")
    
    def _on_mode_changed(self, index):
        if not self._model:
            return
        mode = "image" if index == 0 else "text"
        self._model.display_mode = mode
        self._update_add_button_text()
    
    def _on_duration_changed(self, value):
        if not self._model:
            return
        self._model.animation_duration = value
    
    def _on_add_item(self):
        if not self._model:
            return
        mode = self._model.display_mode
        if mode == "image":
            path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")
            if path:
                self._model.items = self._model.items + [path]
                self._update_items_list()
        else:
            from PySide6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, "添加候选项", "候选项文字:")
            if ok and text.strip():
                self._model.items = self._model.items + [text.strip()]
                self._update_items_list()
    
    def _on_del_item(self):
        if not self._model:
            return
        row = self.items_list.currentRow()
        if 0 <= row < len(self._model.items):
            items = list(self._model.items)
            labels = list(self._model.item_labels)
            items.pop(row)
            labels.pop(row)
            self._model.items = items
            self._model.item_labels = labels
            self._update_items_list()
    
    def _on_move_up(self):
        if not self._model:
            return
        row = self.items_list.currentRow()
        if row > 0:
            items = list(self._model.items)
            labels = list(self._model.item_labels)
            items[row], items[row-1] = items[row-1], items[row]
            labels[row], labels[row-1] = labels[row-1], labels[row]
            self._model.items = items
            self._model.item_labels = labels
            self._update_items_list()
            self.items_list.setCurrentRow(row - 1)
    
    def _on_move_down(self):
        if not self._model:
            return
        row = self.items_list.currentRow()
        if 0 <= row < len(self._model.items) - 1:
            items = list(self._model.items)
            labels = list(self._model.item_labels)
            items[row], items[row+1] = items[row+1], items[row]
            labels[row], labels[row+1] = labels[row+1], labels[row]
            self._model.items = items
            self._model.item_labels = labels
            self._update_items_list()
            self.items_list.setCurrentRow(row + 1)
    
    def _update_items_list(self):
        self.items_list.clear()
        if not self._model:
            return
        for i, label in enumerate(self._model.item_labels):
            self.items_list.addItem(f"{i+1}. {label}")
        if len(self._model.items) != len(self._model.item_labels):
            self.warn_label.setText(f"⚠ items({len(self._model.items)}) 与 labels({len(self._model.item_labels)}) 数量不一致")
        else:
            self.warn_label.setText("")
    
    def _update_add_button_text(self):
        if self._model and self._model.display_mode == "image":
            self.add_btn.setText("添加图片")
        else:
            self.add_btn.setText("添加文字")
    
    def _update_ui_from_model(self):
        if not self._model:
            return
        self.mode_combo.setCurrentIndex(0 if self._model.display_mode == "image" else 1)
        self.duration_spin.setValue(self._model.animation_duration)
        self._update_items_list()
        self._update_add_button_text()
        self._update_bound_label()
        
        is_anim = self._model.is_animating
        self.mode_combo.setEnabled(not is_anim)
        self.add_btn.setEnabled(not is_anim)
        self.del_btn.setEnabled(not is_anim)
        self.up_btn.setEnabled(not is_anim)
        self.down_btn.setEnabled(not is_anim)
        self.set_start_btn.setEnabled(not is_anim)
    
    def set_model(self, model):
        self._model = model
        if model:
            model.data_changed.connect(lambda _: self._update_ui_from_model())
        self._update_ui_from_model()
