"""组件树视图模块。

本模块包含组件层级结构树的实现。
支持组件选择、重命名、删除、添加等操作。
"""

from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QAbstractItemView,
    QMenu, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem

from models import ProjectModel, ComponentModel

class ComponentTreeView(QWidget):
    # 选中组件信号，用于通知外部选中状态变化
    component_selected = Signal(str)
    
    # 多选组件信号
    components_selected = Signal(list)

    # 双击组件信号，通常用于打开编辑器
    component_double_clicked = Signal(str)

    # 删除请求信号，由外部处理实际删除逻辑
    delete_requested = Signal(str)
    
    # 批量删除请求信号
    delete_multiple_requested = Signal(list)

    # 重命名请求信号，由外部处理实际重命名逻辑
    rename_requested = Signal(str, str)

    # 添加组件请求信号，由外部处理实际添加逻辑
    add_component_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_model: Optional[ProjectModel] = None
        self._tree_model: Optional[QStandardItemModel] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tree_view = QTreeView()
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # 设置扩展选择模式，支持 Ctrl/Shift 多选
        self._tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        self._tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tree_view.setDragEnabled(True)
        self._tree_view.setAcceptDrops(True)
        self._tree_view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self._tree_view.clicked.connect(self._on_item_clicked)
        self._tree_view.doubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self._tree_view)

    def set_project_model(self, model: ProjectModel):
        self._project_model = model
        self._tree_model = QStandardItemModel()
        self._tree_view.setModel(self._tree_model)
        self._refresh_tree()
        model.component_added.connect(self._on_component_added)
        model.component_removed.connect(self._on_component_removed)

    def _refresh_tree(self):
        if self._tree_model is None or self._project_model is None:
            return
        self._tree_model.clear()
        root_item = self._tree_model.invisibleRootItem()
        for comp in self._project_model.get_all_components():
            item = self._create_tree_item(comp)
            root_item.appendRow(item)

    def _create_tree_item(self, comp: ComponentModel) -> QStandardItem:
        display_text = f"{comp.name} ({comp.type})"
        item = QStandardItem(display_text)
        item.setData(comp.id, Qt.ItemDataRole.UserRole)
        item.setEditable(False)
        return item

    def _on_component_added(self, comp: ComponentModel):
        if self._tree_model is None:
            return
        item = self._create_tree_item(comp)
        self._tree_model.appendRow(item)

    def _on_component_removed(self, comp_id: str):
        if self._tree_model is None:
            return
        items = self._tree_model.findItems("", Qt.MatchFlag.MatchContains)
        for item in items:
            if item.data(Qt.ItemDataRole.UserRole) == comp_id:
                self._tree_model.removeRow(item.row())
                break

    def _on_item_clicked(self, index: QModelIndex):
        comp_id = self._get_comp_id_from_index(index)
        if not comp_id:
            return
            
        selected_ids = self.get_selected_component_ids()
        
        if len(selected_ids) == 1:
            self.component_selected.emit(comp_id)
        elif len(selected_ids) > 1:
            self.components_selected.emit(selected_ids)

    def _on_item_double_clicked(self, index: QModelIndex):
        comp_id = self._get_comp_id_from_index(index)
        if comp_id:
            self.component_double_clicked.emit(comp_id)

    def _get_comp_id_from_index(self, index: QModelIndex) -> Optional[str]:
        if self._tree_model is None:
            return None
        item = self._tree_model.itemFromIndex(index)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def _show_context_menu(self, pos):
        index = self._tree_view.indexAt(pos)
        comp_id = self._get_comp_id_from_index(index)
        menu = QMenu(self)
        selected_ids = self.get_selected_component_ids()

        if len(selected_ids) > 1:
            delete_action = menu.addAction(f"删除选中的 {len(selected_ids)} 个组件")
            delete_action.triggered.connect(lambda: self._on_delete_multiple(selected_ids))
            menu.addSeparator()

        if comp_id:
            rename_action = menu.addAction("重命名")
            rename_action.triggered.connect(lambda: self._on_rename(comp_id))

            if len(selected_ids) <= 1:
                delete_action = menu.addAction("删除")
                delete_action.triggered.connect(lambda: self._on_delete(comp_id))
        else:
            add_button_action = menu.addAction("添加按钮")
            add_button_action.triggered.connect(lambda: self._on_add_component("button", ""))
            add_label_action = menu.addAction("添加标签")
            add_label_action.triggered.connect(lambda: self._on_add_component("label", ""))
            add_input_action = menu.addAction("添加输入框")
            add_input_action.triggered.connect(lambda: self._on_add_component("input", ""))
            add_container_action = menu.addAction("添加容器")
            add_container_action.triggered.connect(lambda: self._on_add_component("container", ""))
            menu.addSeparator()
            add_checkbox_action = menu.addAction("添加复选框")
            add_checkbox_action.triggered.connect(lambda: self._on_add_component("checkbox", ""))
            add_combobox_action = menu.addAction("添加下拉框")
            add_combobox_action.triggered.connect(lambda: self._on_add_component("combobox", ""))
            add_progressbar_action = menu.addAction("添加进度条")
            add_progressbar_action.triggered.connect(lambda: self._on_add_component("progressbar", ""))

        menu.exec(self._tree_view.viewport().mapToGlobal(pos))

    def _on_rename(self, comp_id: str):
        if self._project_model is None:
            return
        comp = self._project_model.get_component(comp_id)
        if comp is None:
            return
        new_name, ok = QInputDialog.getText(
            self, "重命名", "请输入新名称:",
            text=comp.name
        )
        if ok and new_name:
            self.rename_requested.emit(comp_id, new_name)

    def _on_delete(self, comp_id: str):
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个组件吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(comp_id)
    
    def _on_delete_multiple(self, comp_ids: List[str]):
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(comp_ids)} 个组件吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_multiple_requested.emit(comp_ids)

    def _on_add_component(self, comp_type: str, parent_id: str):
        self.add_component_requested.emit(comp_type, parent_id)

    def select_component(self, comp_id: str):
        if self._tree_model is None:
            return
        items = self._tree_model.findItems("", Qt.MatchFlag.MatchContains)
        for item in items:
            if item.data(Qt.ItemDataRole.UserRole) == comp_id:
                index = item.index()
                self._tree_view.setCurrentIndex(index)
                break

    def clear_selection(self):
        self._tree_view.clearSelection()

    def get_selected_component_id(self) -> Optional[str]:
        indexes = self._tree_view.selectedIndexes()
        if indexes:
            return self._get_comp_id_from_index(indexes[0])
        return None
    
    def get_selected_component_ids(self) -> List[str]:
        indexes = self._tree_view.selectedIndexes()
        result = []
        for index in indexes:
            comp_id = self._get_comp_id_from_index(index)
            if comp_id and comp_id not in result:
                result.append(comp_id)
        return result
