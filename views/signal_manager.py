"""信号管理面板模块。

本模块实现可视化的信号管理界面，让用户可以：
1. 注册信号连接（源组件 -> 目标组件）
2. 以树状表格形式查看所有信号
3. 配置信号触发条件和动作

设计原则：
- 可视化：像逻辑树一样的树状表格
- 简单易懂：用"注册"而不是"发射"的概念
- 分类显示：按源组件分组显示信号连接

界面布局：
┌─────────────────────────────────────┐
│ 📡 信号管理                          │
├─────────────────────────────────────┤
│ ▼ 输入框 (input001)                  │
│   ├─ 文本改变 → 标签001 (设置文本)    │
│   └─ 值改变 → 变量:玩家名 (保存)      │
│ ▼ 按钮 (button001)                   │
│   └─ 点击 → 窗口002 (打开窗口)        │
├─────────────────────────────────────┤
│ [添加信号] [删除信号] [编辑信号]       │
└─────────────────────────────────────┘
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit, QDialog, QFormLayout,
    QDialogButtonBox, QGroupBox, QSplitter, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from models import (
    SignalType, CommActionType, SignalConnection,
    get_communication_manager, get_variable_manager
)


class SignalEditDialog(QDialog):
    """信号编辑对话框。
    
    用于创建和编辑信号连接。
    
    界面：
    ┌─────────────────────────────────┐
    │ 源组件: [下拉选择]               │
    │ 信号类型: [下拉选择]             │
    │ 目标组件: [下拉选择]             │
    │ 动作类型: [下拉选择]             │
    │ 参数: [输入框]                  │
    │                                 │
    │ [确定] [取消]                   │
    └─────────────────────────────────┘
    """
    
    def __init__(self, components: List[Dict], connection: Optional[SignalConnection] = None, 
                 selected_component_id: str = "", parent=None):
        super().__init__(parent)
        self._components = {c['id']: c for c in components}
        self._connection = connection
        self._selected_component_id = selected_component_id
        self._result = None
        
        self.setWindowTitle("注册信号" if connection is None else "编辑信号")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        
        if connection:
            self._load_connection(connection)
        elif selected_component_id:
            self._select_source_component(selected_component_id)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("信号配置")
        form_layout = QFormLayout(form_group)
        
        self._source_combo = QComboBox()
        for comp_id, comp in self._components.items():
            self._source_combo.addItem(f"{comp.get('name', comp_id)} ({comp_id})", comp_id)
        form_layout.addRow("源组件:", self._source_combo)
        
        self._signal_combo = QComboBox()
        for sig in SignalType:
            self._signal_combo.addItem(sig.value, sig)
        form_layout.addRow("信号类型:", self._signal_combo)
        
        self._target_combo = QComboBox()
        self._target_combo.addItem("-- 选择目标 --", "")
        for comp_id, comp in self._components.items():
            self._target_combo.addItem(f"{comp.get('name', comp_id)} ({comp_id})", comp_id)
        form_layout.addRow("目标组件:", self._target_combo)
        
        self._action_combo = QComboBox()
        for action in CommActionType:
            self._action_combo.addItem(action.value, action)
        form_layout.addRow("动作类型:", self._action_combo)
        
        self._param_edit = QLineEdit()
        self._param_edit.setPlaceholderText("可选参数，如变量名、消息内容等")
        form_layout.addRow("参数:", self._param_edit)
        
        self._var_name_edit = QLineEdit()
        self._var_name_edit.setPlaceholderText("如：玩家名、血量、密码")
        form_layout.addRow("变量名:", self._var_name_edit)
        
        layout.addWidget(form_group)
        
        hint_label = QLabel(
            "💡 提示：\n"
            "• 源组件：发送信号的组件\n"
            "• 信号类型：触发条件（如文本改变、点击）\n"
            "• 目标组件：接收信号的组件\n"
            "• 动作类型：执行的操作（如设置文本、读取变量）"
        )
        hint_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(hint_label)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_connection(self, conn: SignalConnection):
        """加载现有连接数据。"""
        for i in range(self._source_combo.count()):
            if self._source_combo.itemData(i) == conn.source_id:
                self._source_combo.setCurrentIndex(i)
                break
        
        for i in range(self._signal_combo.count()):
            if self._signal_combo.itemData(i) == conn.signal_type:
                self._signal_combo.setCurrentIndex(i)
                break
        
        for i in range(self._target_combo.count()):
            if self._target_combo.itemData(i) == conn.target_id:
                self._target_combo.setCurrentIndex(i)
                break
        
        for i in range(self._action_combo.count()):
            if self._action_combo.itemData(i) == conn.action_type:
                self._action_combo.setCurrentIndex(i)
                break
        
        self._param_edit.setText(conn.action_params.get('param', ''))
        self._var_name_edit.setText(conn.action_params.get('variable_name', ''))
    
    def _select_source_component(self, comp_id: str):
        """选中指定的源组件，并根据组件类型设置默认信号类型。"""
        for i in range(self._source_combo.count()):
            if self._source_combo.itemData(i) == comp_id:
                self._source_combo.setCurrentIndex(i)
                break
        
        comp = self._components.get(comp_id, {})
        comp_type = comp.get('type', '')
        
        if comp_type == 'input':
            for i in range(self._signal_combo.count()):
                if self._signal_combo.itemData(i) == SignalType.TEXT_CHANGED:
                    self._signal_combo.setCurrentIndex(i)
                    break
    
    def _on_accept(self):
        """确认按钮处理。"""
        source_id = self._source_combo.currentData()
        signal_type = self._signal_combo.currentData()
        target_id = self._target_combo.currentData()
        action_type = self._action_combo.currentData()
        
        if not source_id:
            QMessageBox.warning(self, "提示", "请选择源组件")
            return
        
        if not target_id:
            QMessageBox.warning(self, "提示", "请选择目标组件")
            return
        
        action_params = {}
        if self._param_edit.text():
            action_params['param'] = self._param_edit.text()
        if self._var_name_edit.text():
            action_params['variable_name'] = self._var_name_edit.text()
        
        self._result = {
            'source_id': source_id,
            'signal_type': signal_type,
            'target_id': target_id,
            'action_type': action_type,
            'action_params': action_params,
        }
        
        self.accept()
    
    def get_result(self) -> Optional[Dict]:
        return self._result


class SignalManagerPanel(QWidget):
    """信号管理面板。
    
    以树状表格形式显示和管理所有信号连接。
    
    Signals:
        connection_created: 信号连接创建时发射
        connection_removed: 信号连接删除时发射
        connection_updated: 信号连接更新时发射
    """
    
    connection_created = Signal(str)
    connection_removed = Signal(str)
    connection_updated = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._components: List[Dict] = []
        self._comm_manager = get_communication_manager()
        self._selected_component_id: str = ""
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("📡 信号管理")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 12px;
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
            }
        """)
        layout.addWidget(header)
        
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["信号连接", "类型", "状态"])
        self._tree.setColumnWidth(0, 200)
        self._tree.setColumnWidth(1, 100)
        self._tree.setColumnWidth(2, 60)
        self._tree.setAlternatingRowColors(True)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree)
        
        toolbar = QHBoxLayout()
        
        self._add_btn = QPushButton("➕ 注册信号")
        self._add_btn.clicked.connect(self._on_add_signal)
        toolbar.addWidget(self._add_btn)
        
        self._edit_btn = QPushButton("✏️ 编辑")
        self._edit_btn.clicked.connect(self._on_edit_signal)
        toolbar.addWidget(self._edit_btn)
        
        self._delete_btn = QPushButton("🗑️ 删除")
        self._delete_btn.clicked.connect(self._on_delete_signal)
        toolbar.addWidget(self._delete_btn)
        
        toolbar.addStretch()
        
        self._refresh_btn = QPushButton("🔄 刷新")
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)
        
        layout.addLayout(toolbar)
        
        hint = QLabel(
            "💡 双击信号可编辑 | 按源组件分组显示\n"
            "信号注册后，当源组件触发信号时，会自动执行目标动作"
        )
        hint.setStyleSheet("color: #666; font-size: 11px; padding: 8px;")
        layout.addWidget(hint)
    
    def set_components(self, components: List[Dict]):
        """设置组件列表。"""
        self._components = components
        self.refresh()
    
    def set_selected_component(self, comp_id: str):
        """设置当前选中的组件ID。"""
        self._selected_component_id = comp_id
    
    def refresh(self):
        """刷新信号列表。"""
        self._tree.clear()
        
        source_groups: Dict[str, List[SignalConnection]] = {}
        
        for conn in self._comm_manager._connections.values():
            if conn.source_id not in source_groups:
                source_groups[conn.source_id] = []
            source_groups[conn.source_id].append(conn)
        
        for source_id, connections in source_groups.items():
            source_name = source_id
            for comp in self._components:
                if comp['id'] == source_id:
                    source_name = comp.get('name', source_id)
                    break
            
            source_item = QTreeWidgetItem([f"📤 {source_name}", "源组件", ""])
            source_item.setData(0, Qt.ItemDataRole.UserRole, source_id)
            source_item.setExpanded(True)
            self._tree.addTopLevelItem(source_item)
            
            for conn in connections:
                target_name = conn.target_id
                for comp in self._components:
                    if comp['id'] == conn.target_id:
                        target_name = comp.get('name', conn.target_id)
                        break
                
                display_text = f"  {conn.signal_type.value} → {target_name}"
                action_text = conn.action_type.value
                status_text = "✓" if conn.enabled else "✗"
                
                conn_item = QTreeWidgetItem([display_text, action_text, status_text])
                conn_item.setData(0, Qt.ItemDataRole.UserRole, conn.id)
                conn_item.setToolTip(0, f"ID: {conn.id}")
                source_item.addChild(conn_item)
        
        for conn in self._comm_manager._connections.values():
            if conn.source_id not in source_groups:
                other_item = QTreeWidgetItem([f"📤 其他信号", "", ""])
                self._tree.addTopLevelItem(other_item)
    
    def _on_add_signal(self):
        """添加信号。"""
        if not self._components:
            QMessageBox.warning(self, "提示", "请先添加组件")
            return
        
        dialog = SignalEditDialog(
            self._components, 
            selected_component_id=self._selected_component_id,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                conn_id = self._comm_manager.create_connection(
                    source_id=result['source_id'],
                    signal_type=result['signal_type'],
                    target_id=result['target_id'],
                    action_type=result['action_type'],
                    action_params=result['action_params'],
                )
                self.connection_created.emit(conn_id)
                self.refresh()
    
    def _on_edit_signal(self):
        """编辑信号。"""
        current_item = self._tree.currentItem()
        if not current_item:
            return
        
        conn_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not conn_id:
            return
        
        conn = self._comm_manager._connections.get(conn_id)
        if not conn:
            return
        
        dialog = SignalEditDialog(self._components, conn, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            if result:
                conn.source_id = result['source_id']
                conn.signal_type = result['signal_type']
                conn.target_id = result['target_id']
                conn.action_type = result['action_type']
                conn.action_params = result['action_params']
                
                self.connection_updated.emit(conn_id)
                self.refresh()
    
    def _on_delete_signal(self):
        """删除信号。"""
        current_item = self._tree.currentItem()
        if not current_item:
            return
        
        conn_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not conn_id:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个信号连接吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._comm_manager.remove_connection(conn_id)
            self.connection_removed.emit(conn_id)
            self.refresh()
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击项目处理。"""
        conn_id = item.data(0, Qt.ItemDataRole.UserRole)
        if conn_id:
            self._on_edit_signal()
    
    def get_all_connections(self) -> List[SignalConnection]:
        """获取所有信号连接。"""
        return list(self._comm_manager._connections.values())
