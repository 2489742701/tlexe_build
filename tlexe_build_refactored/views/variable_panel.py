"""变量管理面板。

提供可视化界面管理项目变量，包括设置玩家名和其他变量。
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QInputDialog, QFrame
)
from PySide6.QtCore import Qt, Signal

from models.variable_system import VariableManager, get_variable_manager
from models.schemas import VariableType

class VariablePanel(QWidget):
    """变量管理面板。
    
    Signals:
        variable_changed: 变量改变时发射 (name, value)
    """
    
    variable_changed = Signal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._var_manager = get_variable_manager()
        self._var_manager.variable_changed.connect(self._on_variable_changed)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        header = QLabel("Variable Manager")
        header.setStyleSheet("font-size: 13px; font-weight: bold; color: #555; padding: 4px 0;")
        layout.addWidget(header)
        
        name_section = QFrame()
        name_section.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        name_layout = QVBoxLayout(name_section)
        name_layout.setSpacing(8)
        
        name_label = QLabel("Player Name / Player name:")
        name_label.setStyleSheet("font-weight: bold; color: #333;")
        name_layout.addWidget(name_label)
        
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Enter player name...")
        self._name_edit.setText(self._var_manager.get_variable("player_name", ""))
        self._name_edit.textChanged.connect(self._on_name_changed)
        name_layout.addWidget(self._name_edit)
        
        layout.addWidget(name_section)
        
        vars_label = QLabel("All Variables / All variables:")
        vars_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; margin-top: 5px;")
        layout.addWidget(vars_label)
        
        self._vars_list = QListWidget()
        self._vars_list.itemDoubleClicked.connect(self._on_var_double_clicked)
        layout.addWidget(self._vars_list, 1)
        
        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)
        
        add_btn = QPushButton("[+] Add")
        add_btn.setFixedHeight(28)
        add_btn.clicked.connect(self._on_add_variable)
        toolbar.addWidget(add_btn)
        
        del_btn = QPushButton("[-] Delete")
        del_btn.setFixedHeight(28)
        del_btn.clicked.connect(self._on_delete_variable)
        toolbar.addWidget(del_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self._refresh_list()
    
    def _on_name_changed(self, text: str):
        """处理玩家名改变。"""
        self._var_manager.set_variable(
            "player_name",
            text,
            VariableType.NAME,
            "Player name"
        )
        self.variable_changed.emit("player_name", text)
    
    def _on_variable_changed(self, name: str, value: object):
        """处理变量改变。"""
        if name == "player_name":
            if self._name_edit.text() != value:
                self._name_edit.setText(str(value))
        self._refresh_list()
        self.variable_changed.emit(name, value)
    
    def _refresh_list(self):
        """刷新变量列表。"""
        self._vars_list.clear()
        for var in self._var_manager.get_all_variables():
            if var.name == "player_name":
                continue
            item_text = f"{var.name}: {var.value} ({var.var_type.value})"
            self._vars_list.addItem(item_text)
    
    def _on_add_variable(self):
        """添加新变量。"""
        name, ok = QInputDialog.getText(self, "Add Variable", "Variable name:")
        if not ok or not name:
            return
        
        if self._var_manager.has_variable(name):
            from views.custom_dialogs import WarningDialog
            WarningDialog.show_warning(self, "提示", "变量已存在！")
            return
        
        value, ok = QInputDialog.getText(self, "Add Variable", "Variable value:")
        if not ok:
            return
        
        self._var_manager.set_variable(name, value, VariableType.TEXT)
        self._refresh_list()
    
    def _on_delete_variable(self):
        """删除选中变量。"""
        current = self._vars_list.currentItem()
        if not current:
            return
        
        item_text = current.text()
        var_name = item_text.split(":")[0].strip()
        
        reply = QMessageBox.question(
            self, "Delete Variable",
            f"Delete variable '{var_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._var_manager.remove_variable(var_name)
            self._refresh_list()
    
    def _on_var_double_clicked(self, item: QListWidgetItem):
        """编辑变量。"""
        item_text = item.text()
        var_name = item_text.split(":")[0].strip()
        var_info = self._var_manager.get_variable_info(var_name)
        
        if not var_info:
            return
        
        new_value, ok = QInputDialog.getText(
            self, "Edit Variable",
            f"New value for '{var_name}':",
            text=str(var_info.value)
        )
        
        if ok:
            self._var_manager.set_variable(var_name, new_value, var_info.var_type)
            self._refresh_list()

def get_player_name() -> str:
    """获取当前玩家名。
    
    这是一个便捷函数，可以在项目任何地方调用。
    
    Returns:
        当前设置的玩家名，如果没有设置则返回空字符串
    """
    return get_variable_manager().get_variable("player_name", "")

def set_player_name(name: str):
    """设置玩家名。
    
    这是一个便捷函数，可以在项目任何地方调用。
    
    Args:
        name: 要设置的玩家名
    """
    get_variable_manager().set_variable(
        "player_name",
        name,
        VariableType.NAME,
        "Player name"
    )

def get_variable(name: str, default=None):
    """获取变量值。
    
    这是一个便捷函数，可以在项目任何地方调用。
    
    Args:
        name: 变量名称
        default: 变量不存在时的默认值
    
    Returns:
        变量值
    """
    return get_variable_manager().get_variable(name, default)

def set_variable(name: str, value, var_type: VariableType = VariableType.TEXT):
    """设置变量值。
    
    这是一个便捷函数，可以在项目任何地方调用。
    
    Args:
        name: 变量名称
        value: 变量值
        var_type: 变量类型
    """
    get_variable_manager().set_variable(name, value, var_type)
