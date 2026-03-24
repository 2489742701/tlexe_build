"""项目控制器模块。

本模块包含项目控制器，负责处理项目的保存、加载、导出等操作。
"""

import json
import os
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QFileDialog, QMessageBox

from models import ProjectModel, ComponentModel, create_component
from views import MainWindow
from utils.undo_manager import UndoManager
from utils.settings import app_settings


def debug_log(category: str, message: str, force: bool = False):
    """调试日志输出。
    
    Args:
        category: 日志类别 (position/component/general)
        message: 日志消息
        force: 是否强制输出（忽略开关设置）
    """
    if not app_settings.debug_verbose and not force:
        return
    
    if category == 'position' and not app_settings.debug_show_position and not force:
        return
    
    if category == 'component' and not app_settings.debug_show_component_details and not force:
        return
    
    print(message)


class ProjectController:
    """项目控制器。
    
    负责处理项目的保存、加载、导出等操作。
    """
    
    def __init__(self, window: MainWindow, project_model: ProjectModel):
        """初始化项目控制器。
        
        Args:
            window: 主窗口视图
            project_model: 项目数据模型
        """
        self.window = window
        self.project_model = project_model
        self._undo_manager = UndoManager()
        self._clipboard: Optional[ComponentModel] = None
        
        self._connect_signals()
        self._load_project_to_view()
    
    def _connect_signals(self):
        """连接信号。"""
        # ==================== 信号连接（入口） ====================
        # 【信号入口】主窗口项目操作信号 -> 控制器槽
        self.window.new_project.connect(self._on_new_project)              # 新建项目请求 -> 创建新项目
        self.window.open_project.connect(self._on_open_project)            # 打开项目请求 -> 打开项目文件
        self.window.save_project.connect(self._on_save_project)            # 保存项目请求 -> 保存项目
        self.window.save_project_as.connect(self._on_save_project_as)      # 另存为请求 -> 另存项目
        self.window.export_project.connect(self._on_export_project)        # 导出请求 -> 导出项目
        self.window.run_project.connect(self._on_run_project)              # 运行请求 -> 运行项目
        self.window.export_to_python.connect(self._on_export_to_python)    # 导出Python请求 -> 导出Python脚本
        self.window.import_from_python.connect(self._on_import_from_python)# 导入Python请求 -> 从Python导入
        
        # 【信号入口】主窗口组件操作信号 -> 控制器槽
        self.window.add_component.connect(self._on_add_component)          # 添加组件请求 -> 添加组件
        self.window.delete_component.connect(self._on_delete_component)    # 删除组件请求 -> 删除组件
        self.window.delete_components.connect(self._on_delete_components)  # 删除多个组件请求 -> 删除多个组件
        self.window.rename_component.connect(self._on_rename_component)    # 重命名组件请求 -> 重命名组件
        
        # 【信号入口】主窗口窗口/事件操作信号 -> 控制器槽
        self.window.window_selected.connect(self._on_window_selected)      # 窗口选中 -> 切换窗口
        self.window.create_event_requested.connect(self._on_create_event)  # 创建事件请求 -> 创建事件
        self.window.delete_window.connect(self._on_delete_window)          # 删除窗口请求 -> 删除窗口
        self.window.rename_window.connect(self._on_rename_window)          # 重命名窗口请求 -> 重命名窗口
        
        # 【信号入口】主窗口选择和属性信号 -> 控制器槽
        self.window.component_selected.connect(self._on_component_selected)    # 组件选中 -> 选中组件
        self.window.property_changed.connect(self._on_property_changed)        # 属性改变 -> 更新属性
        self.window.action_config_requested.connect(self._on_action_config)    # 行为配置请求 -> 配置行为
        
        # 【信号入口】主窗口编辑操作信号 -> 控制器槽
        self.window.undo_requested.connect(self._on_undo)      # 撤销请求 -> 撤销操作
        self.window.redo_requested.connect(self._on_redo)      # 重做请求 -> 重做操作
        self.window.cut_requested.connect(self._on_cut)        # 剪切请求 -> 剪切组件
        self.window.copy_requested.connect(self._on_copy)      # 复制请求 -> 复制组件
        self.window.paste_requested.connect(self._on_paste)    # 粘贴请求 -> 粘贴组件
        
        # 【信号入口】项目模型信号 -> 控制器槽
        self.project_model.component_added.connect(self._on_component_added)          # 组件添加 -> 刷新视图
        self.project_model.component_removed.connect(self._on_component_removed)      # 组件移除 -> 刷新视图
        self.project_model.window_added.connect(self._on_window_added)                # 窗口添加 -> 刷新视图
        self.project_model.current_window_changed.connect(self._on_current_window_changed)  # 当前窗口改变 -> 切换视图
        
        self.window.set_project_model(self.project_model)
    
    def _load_project_to_view(self):
        """加载项目数据到视图。"""
        self.window.set_window_title(self.project_model.name)
        
        if hasattr(self.window, 'logic_tree') and self.window.logic_tree:
            self.window.logic_tree.set_project_model(self.project_model)
        
        if hasattr(self.window, 'designer_view') and self.window.designer_view:
            self.window.designer_view.set_project_model(self.project_model)
            self.window.designer_view.clear()
            
            current_window = self.project_model.current_window
            if current_window:
                self.window.designer_view.set_desktop_size(current_window.width, current_window.height)
                for comp_id in current_window.components:
                    comp = self.project_model.get_component(comp_id)
                    if comp:
                        item = self.window.designer_view.add_component_item(comp)
                        if item:
                            item.moved.connect(self._on_item_moved)
                            item.multi_move_finished.connect(self._on_multi_move_finished)
        
        if hasattr(self.window, 'signal_manager_panel') and self.window.signal_manager_panel:
            components = [comp.to_dict() for comp in self.project_model.get_all_components()]
            self.window.signal_manager_panel.set_components(components)
    
    def _check_unsaved_changes(self) -> bool:
        """检查是否有未保存的修改，如果有则提示用户。
        
        Returns:
            bool: True 表示可以继续操作，False 表示用户取消了操作
        """
        if not self.project_model.is_dirty:
            return True
        
        reply = QMessageBox.question(
            self.window,
            "未保存的修改",
            "当前项目有未保存的修改，是否保存？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._on_save_project()
            return True
        elif reply == QMessageBox.StandardButton.No:
            return True
        else:
            return False
    
    def _on_new_project(self):
        """新建项目。"""
        if not self._check_unsaved_changes():
            return
        
        self.project_model = ProjectModel()
        self._connect_signals()
        self._load_project_to_view()
        self.window.show_status_message("已创建新项目")
    
    def _on_open_project(self, file_path: str):
        """打开项目。"""
        if not self._check_unsaved_changes():
            return
        
        if self.project_model.load_from_file(file_path):
            self._load_project_to_view()
            self.window.show_status_message(f"已打开: {self.project_model.name}")
        else:
            self.window.show_error("打开失败", f"无法打开项目文件: {file_path}")
    
    def _on_save_project(self):
        """保存项目。"""
        if self.project_model.file_path:
            if self.project_model.save_to_file(self.project_model.file_path):
                self.window.show_status_message(f"已保存: {self.project_model.name}")
            else:
                self.window.show_error("保存失败", "无法保存项目文件")
        else:
            self._on_save_project_as("")
    
    def _on_save_project_as(self, file_path: str):
        """另存为项目。"""
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self.window, "保存项目", "", "项目文件 (*.itexe);;所有文件 (*.*)"
            )
        
        if file_path:
            if self.project_model.save_to_file(file_path):
                self.window.show_status_message(f"已保存: {self.project_model.name}")
            else:
                self.window.show_error("保存失败", "无法保存项目文件")
    
    def _on_export_project(self):
        """导出项目。"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.window, "导出项目", "", "Python 文件 (*.py);;所有文件 (*.*)"
        )
        
        if file_path:
            self._on_export_to_python(file_path)
    
    def _on_run_project(self):
        """运行项目。"""
        from runtime.runner import Runner
        
        project_data = self.project_model.to_dict()
        
        print(f"\n{'='*50}")
        print("运行项目 - 组件数据汇总")
        print(f"{'='*50}")
        
        all_components = self.project_model.get_all_components()
        print(f"\n组件总数: {len(all_components)}")
        
        for comp in all_components:
            print(f"\n[{comp.type}] {comp.name}")
            debug_log('position', f"  ID: {comp.id}")
            debug_log('position', f"  位置: ({comp.x}, {comp.y})")
            debug_log('position', f"  大小: ({comp.width}, {comp.height})")
            debug_log('position', f"  父容器ID: {comp.parent_id if hasattr(comp, 'parent_id') and comp.parent_id else '无'}")
            debug_log('component', f"  模型ID: {id(comp)}")
        
        print(f"\n{'='*50}")
        print("开始创建运行窗口")
        print(f"{'='*50}")
        
        runner = Runner()
        runner.run(project_data)
    
    def _on_export_to_python(self, file_path: str):
        """导出为 Python 脚本。
        
        Args:
            file_path: 目标文件路径
        """
        from utils.converter import ProjectConverter
        
        try:
            project_data = self.project_model.to_dict()
            python_code = ProjectConverter.itexe_to_python(project_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            self.window.show_status_message(f"已导出为 Python 脚本: {file_path}")
            QMessageBox.information(self.window, "导出成功", f"项目已成功导出为 Python 脚本：\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self.window, "导出失败", f"导出失败：{e}")
    
    def _on_import_from_python(self, file_path: str):
        """从 Python 脚本导入。
        
        Args:
            file_path: 源文件路径
        """
        from utils.converter import ProjectConverter
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            project_data = ProjectConverter.python_to_itexe(code)
            
            if project_data is None:
                QMessageBox.warning(
                    self.window, 
                    "导入失败", 
                    "无法从该 Python 脚本中提取项目数据。\n\n"
                    "请确保该脚本是由本工具导出的。"
                )
                return
            
            self.project_model.from_dict(project_data)
            self._load_project_to_view()
            
            self.window.show_status_message(f"已从 Python 脚本导入: {file_path}")
            QMessageBox.information(self.window, "导入成功", f"项目已成功从 Python 脚本导入：\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self.window, "导入失败", f"导入失败：{e}")
    
    def _on_add_component(self, comp_type: str, parent_id: str):
        """添加组件。"""
        from utils.settings import app_settings
        
        if not self.project_model.current_window:
            if app_settings.show_create_window_hint:
                self._show_create_window_hint()
            return
        
        comp = create_component(comp_type)
        comp_data = comp.to_dict()
        self.project_model.add_component(comp)
        
        def undo_add(data):
            comp_id = data.get('id')
            if comp_id:
                self.project_model.remove_component(comp_id)
        
        def redo_add(data):
            new_comp = ComponentModel.from_dict(data)
            self.project_model.add_component(new_comp)
        
        self._undo_manager.push(
            action_type='add',
            description=f"添加 {comp.name}",
            undo_data=comp_data,
            redo_data=comp_data,
            undo_callback=undo_add,
            redo_callback=redo_add
        )
        self.window.show_status_message(f"已添加: {comp.name}")
    
    def _show_create_window_hint(self):
        """显示创建窗口提示对话框。"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout
        from utils.settings import app_settings
        
        dialog = QDialog(self.window)
        dialog.setWindowTitle("提示")
        dialog.setFixedSize(400, 180)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        label = QLabel("您可以先创建窗口，否则程序不知道如何排版。\n\n请点击左侧逻辑树中的\"+ 窗口\"按钮创建窗口。")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        dont_show_check = QCheckBox("不再显示此提示")
        layout.addWidget(dont_show_check)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()
        
        if dont_show_check.isChecked():
            app_settings.show_create_window_hint = False
    
    def _on_delete_component(self, comp_id: str):
        """删除组件。"""
        comp = self.project_model.get_component(comp_id)
        if comp:
            comp_data = comp.to_dict()
            if self.project_model.remove_component(comp_id):
                
                def undo_delete(data):
                    new_comp = ComponentModel.from_dict(data)
                    self.project_model.add_component(new_comp)
                
                def redo_delete(data):
                    cid = data.get('id')
                    if cid:
                        self.project_model.remove_component(cid)
                
                self._undo_manager.push(
                    action_type='delete',
                    description=f"删除 {comp.name}",
                    undo_data=comp_data,
                    redo_data=comp_data,
                    undo_callback=undo_delete,
                    redo_callback=redo_delete
                )
                self.window.show_status_message(f"已删除: {comp.name}")
    
    def _on_delete_components(self, comp_ids: list):
        """删除多个组件。"""
        deleted_comps = []
        comp_datas = []
        
        for comp_id in comp_ids:
            comp = self.project_model.get_component(comp_id)
            if comp:
                comp_datas.append(comp.to_dict())
                deleted_comps.append(comp)
        
        if deleted_comps:
            for comp in deleted_comps:
                self.project_model.remove_component(comp.id)
            
            def undo_delete(data_list):
                for data in data_list:
                    new_comp = ComponentModel.from_dict(data)
                    self.project_model.add_component(new_comp)
            
            def redo_delete(data_list):
                for data in data_list:
                    cid = data.get('id')
                    if cid:
                        self.project_model.remove_component(cid)
            
            self._undo_manager.push(
                action_type='delete',
                description=f"删除 {len(deleted_comps)} 个组件",
                undo_data=comp_datas,
                redo_data=comp_datas,
                undo_callback=undo_delete,
                redo_callback=redo_delete
            )
            
            names = ', '.join([comp.name for comp in deleted_comps[:3]])
            if len(deleted_comps) > 3:
                names += f' 等 {len(deleted_comps)} 个组件'
            self.window.show_status_message(f"已删除: {names}")
    
    def _on_rename_component(self, comp_id: str, new_name: str):
        """重命名组件。"""
        comp = self.project_model.get_component(comp_id)
        if comp:
            comp.name = new_name
            self.window.show_status_message(f"已重命名为: {new_name}")
    
    def _on_window_selected(self, window_id: str):
        """选中窗口。"""
        self.project_model.set_current_window(window_id)
    
    def _on_create_event(self, button_id: str):
        """创建事件窗口。"""
        event_id = self.project_model.create_event_for_button(button_id)
        if event_id:
            self.window.show_status_message(f"已创建事件窗口")
    
    def _on_delete_window(self, window_id: str):
        """删除窗口。"""
        if self.project_model.remove_window(window_id):
            self.window.show_status_message("已删除窗口")
    
    def _on_rename_window(self, window_id: str, new_name: str):
        """重命名窗口。"""
        window = self.project_model.get_window(window_id)
        if window:
            window.name = new_name
            self.window.show_status_message(f"窗口已重命名为: {new_name}")
    
    def _on_component_selected(self, comp_id: str):
        """选中组件。"""
        comp = self.project_model.get_component(comp_id)
        if comp:
            self.window.property_panel.set_component(comp)
    
    def _on_property_changed(self, comp_id: str, prop_name: str, new_value):
        """属性改变。"""
        comp = self.project_model.get_component(comp_id)
        if comp:
            if hasattr(comp, prop_name):
                setattr(comp, prop_name, new_value)
    
    def _on_action_config(self, comp_id: str):
        """配置动作。"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
        from views.blockly_editor import BlocklyEditor
        
        comp = self.project_model.get_component(comp_id)
        if not comp:
            return
        
        dialog = QDialog(self.window)
        dialog.setWindowTitle(f"配置行为 - {comp.name}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        editor = BlocklyEditor()
        if hasattr(comp, 'action') and comp.action:
            editor.set_code(comp.action.python_code or "")
            editor.set_xml(comp.action.blockly_xml or "")
        layout.addWidget(editor)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)   # 【信号入口】确定按钮 -> 接受对话框
        button_box.rejected.connect(dialog.reject)   # 【信号入口】取消按钮 -> 拒绝对话框
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            from models.base import ActionConfig
            comp.action = ActionConfig(
                action_type="custom",
                python_code=editor.get_code(),
                blockly_xml=editor.get_xml()
            )
            self.window.show_status_message(f"已更新 {comp.name} 的行为配置")
    
    def _on_undo(self):
        """撤销。"""
        debug_log('general', f"\n{'='*50}", force=True)
        debug_log('general', f"撤销调试", force=True)
        debug_log('general', f"{'='*50}", force=True)
        debug_log('general', f"撤销栈大小: {self._undo_manager.undo_count}")
        debug_log('general', f"可以撤销: {self._undo_manager.can_undo()}")
        
        if self._undo_manager.undo():
            desc = self._undo_manager.get_undo_description()
            self.window.show_status_message(f"撤销: {desc}" if desc else "撤销")
            debug_log('general', f"撤销成功: {desc}")
        else:
            self.window.show_status_message("无法撤销")
            debug_log('general', "撤销失败")
        debug_log('general', f"{'='*50}\n")
    
    def _on_redo(self):
        """重做。"""
        if self._undo_manager.redo():
            desc = self._undo_manager.get_redo_description()
            self.window.show_status_message(f"重做: {desc}" if desc else "重做")
        else:
            self.window.show_status_message("无法重做")
    
    def _restore_component_positions(self, positions: dict):
        """恢复组件位置。"""
        for comp_id, pos_data in positions.items():
            comp = self.project_model.get_component(comp_id)
            if comp:
                x, y = pos_data if isinstance(pos_data, (list, tuple)) else (pos_data.get('x', 0), pos_data.get('y', 0))
                comp.set_position(int(x), int(y))
                item = self.window.designer_view.get_item(comp_id)
                if item:
                    item.setPos(int(x), int(y))
    
    def _on_cut(self):
        """剪切。"""
        self._on_copy()
        selected = self.window.designer_view.get_selected_items()
        if selected:
            self._on_delete_component(selected[0].component_id)
    
    def _on_copy(self):
        """复制。"""
        selected = self.window.designer_view.get_selected_items()
        if selected:
            comp_id = selected[0].component_id
            self._clipboard = self.project_model.get_component(comp_id)
            self.window.show_status_message(f"已复制: {self._clipboard.name if self._clipboard else ''}")
    
    def _on_paste(self):
        """粘贴。"""
        if self._clipboard:
            comp_data = self._clipboard.to_dict()
            comp_data['id'] = ''
            comp_data['x'] += 20
            comp_data['y'] += 20
            comp = ComponentModel.from_dict(comp_data)
            self.project_model.add_component(comp)
            self.window.show_status_message(f"已粘贴: {comp.name}")
    
    def _on_component_added(self, comp_id: str):
        """组件添加后的回调。"""
        comp = self.project_model.get_component(comp_id)
        if comp:
            item = self.window.designer_view.add_component_item(comp)
            if item:
                item.moved.connect(self._on_item_moved)  # 【信号入口】组件移动 -> 记录撤销
                item.multi_move_finished.connect(self._on_multi_move_finished)  # 【信号入口】多选移动完成 -> 记录撤销
    
    def _on_item_moved(self, comp_id: str, new_x: int, new_y: int):
        """组件移动后的回调。
        
        当用户在画布上移动组件时触发此回调。
        更新组件模型位置并记录撤销操作。
        
        Args:
            comp_id: 组件ID
            new_x: 新X坐标
            new_y: 新Y坐标
        """
        debug_log('position', f"\n{'='*50}")
        debug_log('position', f"组件移动调试")
        debug_log('position', f"{'='*50}")
        debug_log('position', f"组件ID: {comp_id}")
        debug_log('position', f"新位置: ({new_x}, {new_y})")
        
        comp = self.project_model.get_component(comp_id)
        if comp:
            old_x, old_y = comp.x, comp.y
            debug_log('position', f"旧位置: ({old_x}, {old_y})")
            debug_log('position', f"位置是否改变: {old_x != new_x or old_y != new_y}")
            
            if old_x != new_x or old_y != new_y:
                comp.set_position(new_x, new_y)
                debug_log('position', "已更新模型位置")
                
                def undo_move(data):
                    """撤销移动操作的回调函数。"""
                    debug_log('position', f"撤销移动: 恢复组件 {data.get('id')} 到位置 ({data.get('old_x')}, {data.get('old_y')})")
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        c.set_position(data.get('old_x', 0), data.get('old_y', 0))
                        item = self.window.designer_view.get_item(data.get('id'))
                        if item:
                            item.setPos(data.get('old_x', 0), data.get('old_y', 0))
                            debug_log('position', "撤销移动: 画布组件位置已更新")
                
                def redo_move(data):
                    """重做移动操作的回调函数。"""
                    debug_log('position', f"重做移动: 移动组件 {data.get('id')} 到位置 ({data.get('new_x')}, {data.get('new_y')})")
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        c.set_position(data.get('new_x', 0), data.get('new_y', 0))
                        item = self.window.designer_view.get_item(data.get('id'))
                        if item:
                            item.setPos(data.get('new_x', 0), data.get('new_y', 0))
                            debug_log('position', "重做移动: 画布组件位置已更新")
                
                self._undo_manager.push(
                    action_type='move',
                    description=f"移动 {comp.name}",
                    undo_data={'id': comp_id, 'old_x': old_x, 'old_y': old_y, 'new_x': new_x, 'new_y': new_y},
                    redo_data={'id': comp_id, 'old_x': old_x, 'old_y': old_y, 'new_x': new_x, 'new_y': new_y},
                    undo_callback=undo_move,
                    redo_callback=redo_move
                )
                debug_log('position', f"已推入撤销栈，当前栈大小: {self._undo_manager.undo_count}")
            else:
                debug_log('position', "位置未改变，不推入撤销栈")
        else:
            debug_log('position', f"未找到组件: {comp_id}")
        debug_log('position', f"{'='*50}\n")
    
    def _on_multi_move_finished(self, positions: dict):
        """多选移动完成后的回调。"""
        debug_log('position', f"\n{'='*50}")
        debug_log('position', "多选移动调试")
        debug_log('position', f"{'='*50}")
        old_positions = positions.get('old', {})
        new_positions = positions.get('new', {})
        
        debug_log('position', f"旧位置: {old_positions}")
        debug_log('position', f"新位置: {new_positions}")
        
        if old_positions and new_positions:
            
            def undo_move(data):
                self._restore_component_positions(data.get('old', {}))
            
            def redo_move(data):
                self._restore_component_positions(data.get('new', {}))
            
            self._undo_manager.push(
                action_type='move',
                description=f"移动 {len(new_positions)} 个组件",
                undo_data={'old': old_positions, 'new': new_positions},
                redo_data={'old': old_positions, 'new': new_positions},
                undo_callback=undo_move,
                redo_callback=redo_move
            )
            debug_log('position', f"已推入撤销栈，当前栈大小: {self._undo_manager.undo_count}")
        else:
            debug_log('position', "位置数据为空，不推入撤销栈")
        debug_log('position', f"{'='*50}\n")
    
    def _on_component_removed(self, comp_id: str):
        """组件移除后的回调。"""
        self.window.designer_view.remove_component_item(comp_id)
    
    def _on_window_added(self, window_id: str):
        """窗口添加后的回调。"""
        window = self.project_model.get_window(window_id)
        if window:
            self.window.show_status_message(f"已添加窗口: {window.name}")
            self.window.logic_tree.refresh()
    
    def _on_current_window_changed(self, window_id: str):
        """当前窗口改变后的回调。"""
        self.window.designer_view.clear()
        
        current_window = self.project_model.get_window(window_id)
        if current_window:
            self.window.designer_view.set_desktop_size(current_window.width, current_window.height)
        
        components = self.project_model.get_components_for_window(window_id)
        for comp in components:
            self.window.designer_view.add_component_item(comp)
