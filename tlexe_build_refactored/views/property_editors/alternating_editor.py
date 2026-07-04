"""交替变换组件属性编辑器。

支持 text_alternating 和 image_alternating 两种组件类型。
提供类型切换、候选项管理、动画时长配置、开始/停止按钮绑定功能。
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QListWidget,
    QFileDialog, QMessageBox, QMenu, QInputDialog,
    QComboBox,
)
from PySide6.QtCore import Signal

from .base_editor import BasePropertyEditor
from .registry import register_property_editor

FONT_SIZE_PRESETS = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36]

@register_property_editor('alternating')
@register_property_editor('text_alternating')
@register_property_editor('image_alternating')
class AlternatingPropertyEditor(BasePropertyEditor):
    """交替变换组件属性编辑器。"""

    type_switch_requested = Signal(str, str)

    _ACTION_BINDINGS = {
        'start': ('start_alternating', '#4CAF50', '#388E3C', "设定开始按钮", "开始交替变换"),
        'stop':  ('stop_alternating', '#f44336', '#d32f2f', "设定停止按钮", "停止交替变换"),
    }

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("交替类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["文字交替", "图片交替"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_combo)
        type_row.addStretch()
        layout.addLayout(type_row)

        toggle_row = QHBoxLayout()
        toggle_row.addWidget(QLabel("按钮模式:"))
        self.toggle_combo = QComboBox()
        self.toggle_combo.addItems(["同一按钮(开始/停止)", "分开按钮"])
        self.toggle_combo.currentIndexChanged.connect(self._on_toggle_mode_changed)
        toggle_row.addWidget(self.toggle_combo)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)

        layout.addWidget(QLabel("动画时长(毫秒):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(500, 30000)
        self.duration_spin.setSingleStep(500)
        self.duration_spin.setValue(3000)
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        layout.addWidget(self.duration_spin)

        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("字号:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.setEditable(True)
        self.font_size_combo.addItems([str(s) for s in FONT_SIZE_PRESETS])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self._on_font_size_changed)
        font_row.addWidget(self.font_size_combo)
        font_row.addStretch()
        layout.addLayout(font_row)

        self.start_btn_row, self.start_bound_label = self._create_bind_row(layout, 'start')
        self.stop_btn_row, self.stop_bound_label = self._create_bind_row(layout, 'stop')

        layout.addWidget(QLabel("候选项列表:"))
        self.items_list = QListWidget()
        self.items_list.setMinimumHeight(120)
        layout.addWidget(self.items_list)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self._on_add_item)
        self.del_btn = QPushButton("删除")
        self.del_btn.clicked.connect(self._on_del_item)
        self.up_btn = QPushButton("上移")
        self.up_btn.clicked.connect(self._on_move_up)
        self.down_btn = QPushButton("下移")
        self.down_btn.clicked.connect(self._on_move_down)
        for b in (self.add_btn, self.del_btn, self.up_btn, self.down_btn):
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def _on_type_changed(self, index):
        if not self._model:
            return
        new_mode = 'text' if index == 0 else 'image'
        current_mode = getattr(self._model, 'display_mode', 'text')
        if current_mode != new_mode:
            new_type = 'text_alternating' if new_mode == 'text' else 'image_alternating'
            self.type_switch_requested.emit(self._model.id, new_type)

    def _on_toggle_mode_changed(self, index):
        if not self._model:
            return
        mode = 'same' if index == 0 else 'separate'
        self._model.toggle_mode = mode
        self.stop_btn_row.setEnabled(mode == 'separate')
        self.stop_bound_label.setEnabled(mode == 'separate')

    def _on_font_size_changed(self, text):
        if not self._model:
            return
        try:
            size = int(text)
            if 1 <= size <= 200:
                self._model.style.font_size = size
                self._model.data_changed.emit()
        except ValueError:
            pass

    def _create_bind_row(self, layout, key):
        action_type, bg, bg_hover, label_text, _ = self._ACTION_BINDINGS[key]
        row = QHBoxLayout()
        btn = QPushButton(label_text)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {bg}; color: white; border-radius: 4px; padding: 6px; }}"
            f"QPushButton:hover {{ background-color: {bg_hover}; }}"
        )
        btn.clicked.connect(lambda: self._on_bind_button(key))
        row.addWidget(btn)
        bound_label = QLabel("")
        bound_label.setStyleSheet("color: #666666; font-size: 11px;")
        row.addWidget(bound_label)
        row.addStretch()
        layout.addLayout(row)
        return btn, bound_label

    def _get_project_model(self):
        widget = self.parent()
        while widget:
            for attr in ('_project_model', 'project_model'):
                pm = getattr(widget, attr, None)
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
                for attr in ('project_model', '_project_model'):
                    pm = getattr(controller, attr, None)
                    if pm:
                        return pm
        return None

    def _get_all_buttons(self):
        project_model = self._get_project_model()
        if not project_model:
            return []
        get_all = getattr(project_model, 'get_all_components', None)
        all_components = get_all() if get_all else list(getattr(project_model, '_components', {}).values())
        return [c for c in all_components if getattr(c, 'type', '') == 'button']

    def _on_bind_button(self, key):
        if not self._model:
            return
        action_type, _, _, _, confirm_label = self._ACTION_BINDINGS[key]

        if key == 'start' and getattr(self._model, 'is_running', False):
            from views.custom_dialogs import WarningDialog
            WarningDialog.show_warning(self, "提示", "交替变换运行中，无法设定按钮")
            return

        buttons = self._get_all_buttons()
        if not buttons:
            QMessageBox.information(self, "提示", "项目中没有按钮组件。\n请先添加一个按钮组件。")
            return

        menu = QMenu(self)
        for btn_comp in buttons:
            name = getattr(btn_comp, 'name', '') or getattr(btn_comp, 'text', '') or btn_comp.id
            action = menu.addAction(f"{name} (ID: {btn_comp.id[:8]}...)")
            action.setData(btn_comp)
        menu.setStyleSheet("QMenu { min-width: 200px; }")

        trigger_btn = self.start_btn_row if key == 'start' else self.stop_btn_row
        pos = trigger_btn.mapToGlobal(trigger_btn.rect().bottomLeft())
        selected = menu.exec(pos)
        if not selected:
            return

        btn_comp = selected.data()
        if not btn_comp:
            return

        from models.schemas import ActionConfig
        current_action = getattr(btn_comp, '_action', None)
        if current_action and getattr(current_action, 'action_type', 'none') != 'none':
            reply = QMessageBox.question(
                self, "确认覆盖",
                f"按钮 \"{btn_comp.name}\" 已有动作配置 ({current_action.action_type})。\n"
                f"是否覆盖为{confirm_label}？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        btn_comp.action = ActionConfig(
            action_type=action_type,
            params={"target_component_id": self._model.id}
        )

        _, bg, _, _, _ = self._ACTION_BINDINGS[key]
        bound_label = self.start_bound_label if key == 'start' else self.stop_bound_label
        bound_label.setText(f"→ {btn_comp.name}")
        bound_label.setStyleSheet(f"color: {bg}; font-size: 11px; font-weight: bold;")

    def _update_bound_labels(self):
        if not self._model:
            return
        buttons = self._get_all_buttons()
        found = {}
        for comp in buttons:
            action = getattr(comp, '_action', None)
            if not action:
                continue
            at = getattr(action, 'action_type', '')
            target = action.params.get('target_component_id', '')
            if target == self._model.id and at in ('start_alternating', 'stop_alternating'):
                key = 'start' if at == 'start_alternating' else 'stop'
                found[key] = getattr(comp, 'name', '')

        for key, label in (('start', self.start_bound_label), ('stop', self.stop_bound_label)):
            _, bg, _, _, _ = self._ACTION_BINDINGS[key]
            if key in found:
                label.setText(f"→ {found[key]}")
                label.setStyleSheet(f"color: {bg}; font-size: 11px; font-weight: bold;")
            else:
                label.setText("未设定")
                label.setStyleSheet("color: #999999; font-size: 11px;")

    def _on_duration_changed(self, value):
        if self._model:
            self._model.animation_duration = value

    def _on_add_item(self):
        if not self._model:
            return
        if getattr(self._model, 'display_mode', 'text') == 'image':
            path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
            if path:
                self._model.items = self._model.items + [path]
        else:
            text, ok = QInputDialog.getText(self, "添加候选项", "候选项文字:")
            if ok and text.strip():
                self._model.items = self._model.items + [text.strip()]
        self._update_items_list()

    def _on_del_item(self):
        if not self._model:
            return
        row = self.items_list.currentRow()
        if 0 <= row < len(self._model.items):
            items, labels = list(self._model.items), list(self._model.item_labels)
            items.pop(row)
            labels.pop(row)
            self._model.items, self._model.item_labels = items, labels
            self._update_items_list()

    def _swap_items(self, row, other):
        items, labels = list(self._model.items), list(self._model.item_labels)
        items[row], items[other] = items[other], items[row]
        labels[row], labels[other] = labels[other], labels[row]
        self._model.items, self._model.item_labels = items, labels
        self._update_items_list()
        self.items_list.setCurrentRow(other)

    def _on_move_up(self):
        if self._model:
            row = self.items_list.currentRow()
            if row > 0:
                self._swap_items(row, row - 1)

    def _on_move_down(self):
        if self._model:
            row = self.items_list.currentRow()
            if 0 <= row < len(self._model.items) - 1:
                self._swap_items(row, row + 1)

    def _update_items_list(self):
        self.items_list.clear()
        if self._model:
            for i, label in enumerate(self._model.item_labels):
                self.items_list.addItem(f"{i+1}. {label}")

    def _update_ui_from_model(self):
        if not self._model:
            return
        display_mode = getattr(self._model, 'display_mode', 'text')
        self.type_combo.blockSignals(True)
        self.type_combo.setCurrentIndex(0 if display_mode == 'text' else 1)
        self.type_combo.blockSignals(False)

        toggle_mode = getattr(self._model, 'toggle_mode', 'same')
        self.toggle_combo.blockSignals(True)
        self.toggle_combo.setCurrentIndex(0 if toggle_mode == 'same' else 1)
        self.toggle_combo.blockSignals(False)
        self.stop_btn_row.setEnabled(toggle_mode == 'separate')
        self.stop_bound_label.setEnabled(toggle_mode == 'separate')

        self.duration_spin.setValue(self._model.animation_duration)

        font_size = getattr(self._model.style, 'font_size', 12)
        self.font_size_combo.blockSignals(True)
        self.font_size_combo.setCurrentText(str(font_size))
        self.font_size_combo.blockSignals(False)

        self._update_items_list()
        self.add_btn.setText("添加图片" if display_mode == 'image' else "添加文字")
        self._update_bound_labels()
        not_running = not self._model.is_running
        for w in (self.add_btn, self.del_btn, self.up_btn, self.down_btn, self.start_btn_row):
            w.setEnabled(not_running)

    def set_model(self, model):
        if self._model:
            try:
                self._model.data_changed.disconnect(self._update_ui_from_model)
            except RuntimeError:
                pass
        self._model = model
        if model:
            model.data_changed.connect(self._update_ui_from_model)
        self._update_ui_from_model()
