"""首选项对话框模块。

本模块包含应用程序首选项设置对话框的实现。
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QCheckBox, QPushButton, QGroupBox,
    QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal

from utils.settings import app_settings

class PreferencesDialog(QDialog):
    """首选项设置对话框。
    
    提供应用程序各项设置的配置界面。
    
    注意：早期版本使用 settings_changed 信号通知设置变化，
    现已改用 app_settings.add_change_callback() 回调机制。
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("首选项")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """初始化UI。"""
        layout = QVBoxLayout(self)
        
        self._tab_widget = QTabWidget()
        layout.addWidget(self._tab_widget)
        
        general_tab = self._create_general_tab()
        self._tab_widget.addTab(general_tab, "常规")
        
        editor_tab = self._create_editor_tab()
        self._tab_widget.addTab(editor_tab, "编辑器")
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._restore_defaults)
        
        layout.addWidget(button_box)
    
    def _create_general_tab(self) -> QWidget:
        """创建常规设置标签页。"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout(display_group)
        
        self._show_grid_checkbox = QCheckBox("显示网格")
        display_layout.addWidget(self._show_grid_checkbox)
        
        layout.addWidget(display_group)
        
        edit_group = QGroupBox("编辑设置")
        edit_layout = QVBoxLayout(edit_group)
        
        undo_steps_row = QHBoxLayout()
        undo_steps_label = QLabel("撤销最大步数:")
        self._undo_max_steps_spin = QSpinBox()
        self._undo_max_steps_spin.setRange(10, 200)
        self._undo_max_steps_spin.setValue(50)
        self._undo_max_steps_spin.setSuffix(" 步")
        undo_steps_row.addWidget(undo_steps_label)
        undo_steps_row.addWidget(self._undo_max_steps_spin)
        undo_steps_row.addStretch()
        edit_layout.addLayout(undo_steps_row)
        
        undo_steps_hint = QLabel("设置可以撤销的最大操作步数")
        undo_steps_hint.setStyleSheet("color: gray; font-size: 11px; margin-left: 20px;")
        edit_layout.addWidget(undo_steps_hint)
        
        layout.addWidget(edit_group)
        
        layout.addStretch()
        return widget
    
    def _create_editor_tab(self) -> QWidget:
        """创建编辑器设置标签页。"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        handle_group = QGroupBox("手柄设置")
        handle_layout = QVBoxLayout(handle_group)
        
        handle_size_row = QHBoxLayout()
        handle_size_label = QLabel("手柄大小:")
        self._handle_size_spin = QSpinBox()
        self._handle_size_spin.setRange(4, 20)
        self._handle_size_spin.setValue(8)
        self._handle_size_spin.setSuffix(" 像素")
        handle_size_row.addWidget(handle_size_label)
        handle_size_row.addWidget(self._handle_size_spin)
        handle_size_row.addStretch()
        handle_layout.addLayout(handle_size_row)
        
        handle_size_hint = QLabel("调整组件选中时显示的调整手柄方块的大小")
        handle_size_hint.setStyleSheet("color: gray; font-size: 11px; margin-left: 20px;")
        handle_layout.addWidget(handle_size_hint)
        
        tolerance_row = QHBoxLayout()
        tolerance_label = QLabel("点击容差:")
        self._handle_tolerance_spin = QSpinBox()
        self._handle_tolerance_spin.setRange(0, 10)
        self._handle_tolerance_spin.setValue(4)
        self._handle_tolerance_spin.setSuffix(" 像素")
        tolerance_row.addWidget(tolerance_label)
        tolerance_row.addWidget(self._handle_tolerance_spin)
        tolerance_row.addStretch()
        handle_layout.addLayout(tolerance_row)
        
        tolerance_hint = QLabel("增加点击判断范围，使手柄更容易被点击中")
        tolerance_hint.setStyleSheet("color: gray; font-size: 11px; margin-left: 20px;")
        handle_layout.addWidget(tolerance_hint)
        
        layout.addWidget(handle_group)
        
        grid_group = QGroupBox("网格设置")
        grid_layout = QVBoxLayout(grid_group)
        
        grid_size_row = QHBoxLayout()
        grid_size_label = QLabel("网格大小:")
        self._grid_size_spin = QSpinBox()
        self._grid_size_spin.setRange(5, 50)
        self._grid_size_spin.setValue(10)
        self._grid_size_spin.setSuffix(" 像素")
        grid_size_row.addWidget(grid_size_label)
        grid_size_row.addWidget(self._grid_size_spin)
        grid_size_row.addStretch()
        grid_layout.addLayout(grid_size_row)
        
        self._snap_to_grid_checkbox = QCheckBox("对齐到网格")
        grid_layout.addWidget(self._snap_to_grid_checkbox)
        
        layout.addWidget(grid_group)
        
        layout.addStretch()
        return widget
    
    def _load_settings(self):
        """加载当前设置到界面。"""
        self._handle_size_spin.setValue(app_settings.handle_size)
        self._handle_tolerance_spin.setValue(app_settings.handle_click_tolerance)
        self._grid_size_spin.setValue(app_settings.grid_size)
        self._snap_to_grid_checkbox.setChecked(app_settings.snap_to_grid)
        self._show_grid_checkbox.setChecked(app_settings.show_grid)
        self._undo_max_steps_spin.setValue(app_settings.undo_max_steps)
    
    def _apply_settings(self):
        """应用当前设置。"""
        app_settings.handle_size = self._handle_size_spin.value()
        app_settings.handle_click_tolerance = self._handle_tolerance_spin.value()
        app_settings.grid_size = self._grid_size_spin.value()
        app_settings.snap_to_grid = self._snap_to_grid_checkbox.isChecked()
        app_settings.show_grid = self._show_grid_checkbox.isChecked()
        app_settings.undo_max_steps = self._undo_max_steps_spin.value()
    
    def _restore_defaults(self):
        """恢复默认设置。"""
        defaults = app_settings.DEFAULT_SETTINGS
        self._handle_size_spin.setValue(defaults["handle_size"])
        self._handle_tolerance_spin.setValue(defaults["handle_click_tolerance"])
        self._grid_size_spin.setValue(defaults["grid_size"])
        self._snap_to_grid_checkbox.setChecked(defaults["snap_to_grid"])
        self._show_grid_checkbox.setChecked(defaults["show_grid"])
        self._undo_max_steps_spin.setValue(defaults["undo_max_steps"])
    
    def accept(self):
        """确认对话框。"""
        self._apply_settings()
        super().accept()
