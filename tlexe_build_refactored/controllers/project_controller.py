"""项目控制器模块。

负责处理项目的保存、加载、导出、运行等操作，以及组件的增删改查。

架构说明:
    本控制器采用渐进式迁移策略，同时支持：
    1. 旧的信号连接方式（保持兼容）
    2. 新的 EventBus + Presenter 架构

    迁移完成后，旧代码将逐步被移除。

命名约定:
    - 槽方法：_on_{信号名}（_on_new_project, _on_add_component）
    - 私有方法：_{动词}_{名词}（_add_single_component, _check_button_conflict）
    - 撤销回调：undo_{动作}/redo_{动作}（undo_add, redo_add）
"""

import json
import os
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QFileDialog, QMessageBox

from models import ProjectModel, ComponentModel, create_component
from models.component_registry import ComponentRegistry
from views import MainWindow
from utils.undo_manager import UndoManager
from utils.settings import app_settings

from presenters import CanvasPresenter

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
    
    try:
        from dev_mode.debug_logger import DebugLogger
        DebugLogger.debug(f"[{category}] {message}", "editor")
    except Exception:
        pass

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
        self._runner = None
        
        self._canvas_presenter: Optional[CanvasPresenter] = None
        
        self._connect_signals()
        self._init_canvas_presenter()
        self._load_project_to_view()
    
    def _init_canvas_presenter(self):
        """初始化画布Presenter。
        
        创建CanvasPresenter实例，管理画布视图与组件模型的交互。
        Presenter通过EventBus实现模块间解耦通信。
        """
        if hasattr(self.window, 'designer_view') and self.window.designer_view:
            self._canvas_presenter = CanvasPresenter(
                canvas_view=self.window.designer_view,
                project_model=self.project_model
            )
            debug_log('component', f"[架构迁移] CanvasPresenter已初始化")
    
    def _connect_signals(self):
        """连接信号。"""
        # ==================== 信号连接（入口） ====================
        # 【信号入口】主窗口项目操作信号 -> 控制器槽
        self.window.new_project.connect(self._on_new_project)              # 新建项目请求 -> 创建新项目
        self.window.open_project.connect(self._on_open_project)            # 打开项目请求 -> 打开项目文件
        self.window.save_project.connect(self._on_save_project)            # 保存项目请求 -> 保存项目
        self.window.save_project_as.connect(self._on_save_project_as)      # 另存为请求 -> 另存项目
        self.window.export_project.connect(self._on_export_project)        # 导出请求 -> 导出项目
        self.window.run_project.connect(self._on_run_project)              # 运行请求 -> 运行完整项目
        self.window.run_from_current.connect(self._on_run_from_current)    # 从当前窗口运行 -> 从当前窗口运行
        self.window.export_to_python.connect(self._on_export_to_python)    # 导出Python请求 -> 导出Python脚本
        self.window.import_from_python.connect(self._on_import_from_python)# 导入Python请求 -> 从Python导入
        self.window.export_to_exe.connect(self._on_export_to_exe)          # 导出EXE请求 -> 导出为可执行文件
        
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
        self.window.unbind_extension_requested.connect(self._on_unbind_extension)  # 解除绑定请求 -> 解除绑定
        
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
                self.window.designer_view.update_window_size(current_window.width, current_window.height, current_window.frameless)
                for comp_id in current_window.components:
                    comp = self.project_model.get_component(comp_id)
                    if comp:
                        item = self.window.designer_view.add_component_item(comp)
                        if item:
                            item.moved.connect(self._on_item_moved)
                            item.multi_move_finished.connect(self._on_multi_move_finished)
                            item.resized.connect(self._on_item_resized)
        
        if hasattr(self.window, 'signal_manager_panel') and self.window.signal_manager_panel:
            components = [comp.to_dict() for comp in self.project_model.get_all_components()]
            self.window.signal_manager_panel.set_components(components)
        
        self.project_model.mark_clean()
    
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
                self.window, "保存项目", "", "项目文件 (*.py);;旧格式 (*.itexe);;所有文件 (*.*)"
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
        """运行完整项目（从主窗口开始）。"""
        from runtime.runner import Runner
        
        project_data = self.project_model.to_dict()
        
        print(f"\n{'='*50}")
        print("运行完整项目 - 组件数据汇总")
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
        
        self._runner = Runner()
        self._runner.run(project_data)
    
    def _on_run_from_current(self):
        """从当前窗口运行项目。"""
        from runtime.runner import Runner
        
        current_window_id = self.project_model.current_window_id
        if not current_window_id:
            self.window.show_status_message("没有当前窗口，无法运行")
            return
        
        project_data = self.project_model.to_dict()
        project_data['main_window_id'] = current_window_id
        
        print(f"\n{'='*50}")
        print(f"从当前窗口运行 - {current_window_id}")
        print(f"{'='*50}")
        
        self._runner = Runner()
        self._runner.run(project_data)
    
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
            from views.custom_dialogs import ErrorDialog
            ErrorDialog.show_error(self.window, "导出失败", f"导出失败：{e}")
    
    def _on_export_to_exe(self):
        """导出为可执行文件。"""
        from views.export_dialog import ExportDialog
        
        project_data = self.project_model.to_dict()
        
        source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        dialog = ExportDialog(project_data, source_dir, self.window)
        dialog.exec()
    
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
                from views.custom_dialogs import WarningDialog
                WarningDialog.show_warning(
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
            from views.custom_dialogs import ErrorDialog
            ErrorDialog.show_error(self.window, "导入失败", f"导入失败：{e}")
    
    def _on_add_component(self, comp_type: str, parent_id: str):
        """添加组件。"""
        from utils.settings import app_settings
        from models import TechComponentManager
        
        if not self.project_model.current_window:
            if app_settings.show_create_window_hint:
                self._show_create_window_hint()
            return
        
        tech_templates = TechComponentManager.get_available_templates()
        if comp_type in tech_templates:
            self._add_tech_component(comp_type, parent_id)
        else:
            self._add_single_component(comp_type, parent_id)
    
    def _add_single_component(self, comp_type: str, parent_id: str):
        """添加单个组件。"""
        if comp_type in ('button', 'confirm_button'):
            if not self._check_button_conflict(comp_type):
                return
        
        comp = create_component(comp_type)
        if parent_id:
            comp.parent_id = parent_id
        
        comp_data = comp.to_dict()
        self.project_model.add_component(comp)
        
        def undo_add(data):
            comp_id = data.get('id')
            if comp_id:
                self.project_model.remove_component(comp_id)
        
        def redo_add(data):
            comp_cls = ComponentRegistry.get_model_class(data.get('type') or data.get('comp_type', 'label'))
            new_comp = (comp_cls or ComponentModel).from_dict(data)
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
    
    def _add_tech_component(self, template_id: str, parent_id: str):
        """添加技术类控件组件。"""
        from models import TechComponentManager
        
        try:
            components = TechComponentManager.create_tech_component(
                template_id,
                parent_id=parent_id,
                offset_x=50,
                offset_y=50
            )
            
            comp_data_list = []
            for comp in components:
                if parent_id:
                    comp.parent_id = parent_id
                self.project_model.add_component(comp)
                comp_data_list.append(comp.to_dict())
            
            def undo_add_tech(data_list):
                for data in data_list:
                    comp_id = data.get('id')
                    if comp_id:
                        self.project_model.remove_component(comp_id)
            
            def redo_add_tech(data_list):
                for data in data_list:
                    comp_cls = ComponentRegistry.get_model_class(data.get('type') or data.get('comp_type', 'label'))
                    new_comp = (comp_cls or ComponentModel).from_dict(data)
                    self.project_model.add_component(new_comp)
            
            template_info = TechComponentManager.get_template_info(template_id)
            display_name = template_info.get('display_name', template_id)
            
            self._undo_manager.push(
                action_type='add',
                description=f"添加技术类控件: {display_name}",
                undo_data=comp_data_list,
                redo_data=comp_data_list,
                undo_callback=undo_add_tech,
                redo_callback=redo_add_tech
            )
            
            self.window.show_status_message(f"已添加技术类控件: {display_name} ({len(components)}个组件)")
            
        except Exception as e:
            self.window.show_status_message(f"添加技术类控件失败: {str(e)}")
    
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
                    comp_cls = ComponentRegistry.get_model_class(data.get('type') or data.get('comp_type', 'label'))
                    new_comp = comp_cls.from_dict(data) if comp_cls else ComponentModel.from_dict(data)
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
                    comp_cls = ComponentRegistry.get_model_class(data.get('type') or data.get('comp_type', 'label'))
                    new_comp = comp_cls.from_dict(data) if comp_cls else ComponentModel.from_dict(data)
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
            old_name = comp.name
            if old_name == new_name:
                return
            
            comp.name = new_name
            
            def undo_rename(data):
                c = self.project_model.get_component(data.get('id'))
                if c:
                    c.name = data.get('old_name')
            
            def redo_rename(data):
                c = self.project_model.get_component(data.get('id'))
                if c:
                    c.name = data.get('new_name')
            
            self._undo_manager.push(
                action_type='rename',
                description=f"重命名 {old_name} 为 {new_name}",
                undo_data={'id': comp_id, 'old_name': old_name, 'new_name': new_name},
                redo_data={'id': comp_id, 'old_name': old_name, 'new_name': new_name},
                undo_callback=undo_rename,
                redo_callback=redo_rename
            )
            
            self.window.show_status_message(f"已重命名为: {new_name}")
    
    def _on_window_selected(self, window_id: str):
        """选中窗口。"""
        self.project_model.set_current_window(window_id)
        self.window.logic_tree.select_window(window_id)
    
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
            old_name = window.name
            if old_name == new_name:
                return
            
            window.name = new_name
            
            def undo_rename(data):
                w = self.project_model.get_window(data.get('id'))
                if w:
                    w.name = data.get('old_name')
            
            def redo_rename(data):
                w = self.project_model.get_window(data.get('id'))
                if w:
                    w.name = data.get('new_name')
            
            self._undo_manager.push(
                action_type='rename_window',
                description=f"重命名窗口 {old_name} 为 {new_name}",
                undo_data={'id': window_id, 'old_name': old_name, 'new_name': new_name},
                redo_data={'id': window_id, 'old_name': old_name, 'new_name': new_name},
                undo_callback=undo_rename,
                redo_callback=redo_rename
            )
            
            self.window.show_status_message(f"窗口已重命名为: {new_name}")
    
    def _on_component_selected(self, comp_id: str):
        """选中组件。"""
        comp = self.project_model.get_component(comp_id)
        if comp:
            self.window.property_panel.set_component(comp)
            self.window.logic_tree.select_component(comp_id)
            if hasattr(self.window, 'signal_manager_panel') and self.window.signal_manager_panel:
                self.window.signal_manager_panel.set_selected_component(comp_id)
    
    def _on_property_changed(self, comp_id: str, prop_name: str, old_value, new_value):
        """属性改变。
        
        Args:
            comp_id: 组件ID
            prop_name: 属性名称
            old_value: 旧值
            new_value: 新值
        """
        comp = self.project_model.get_component(comp_id)
        if not comp:
            # Handle window properties
            if comp_id == "" and self.project_model.current_window:
                cw = self.project_model.current_window
                if prop_name in ("width", "height", "frameless"):
                    self.window.designer_view.update_window_size(cw.width, cw.height, cw.frameless)
            return
        
        if prop_name.startswith("style."):
            style_prop = prop_name.split(".")[1]
            
            def undo_style_change(data):
                c = self.project_model.get_component(data.get('id'))
                if c:
                    setattr(c.style, data.get('prop'), data.get('old_value'))
                    c.style_changed.emit()
                    c.data_changed.emit()
            
            def redo_style_change(data):
                c = self.project_model.get_component(data.get('id'))
                if c:
                    setattr(c.style, data.get('prop'), data.get('new_value'))
                    c.style_changed.emit()
                    c.data_changed.emit()
            
            self._undo_manager.push(
                action_type='style_change',
                description=f"修改 {comp.name} 样式.{style_prop}",
                undo_data={'id': comp_id, 'prop': style_prop, 'old_value': old_value, 'new_value': new_value},
                redo_data={'id': comp_id, 'prop': style_prop, 'old_value': old_value, 'new_value': new_value},
                undo_callback=undo_style_change,
                redo_callback=redo_style_change
            )
        else:
            if prop_name in ["x", "y"]:
                def undo_position_change(data):
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        if data.get('prop') == 'x':
                            c.x = data.get('old_value')
                        else:
                            c.y = data.get('old_value')
                        item = self.window.designer_view.get_item(data.get('id'))
                        if item:
                            item.setPos(c.x, c.y)
                
                def redo_position_change(data):
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        if data.get('prop') == 'x':
                            c.x = data.get('new_value')
                        else:
                            c.y = data.get('new_value')
                        item = self.window.designer_view.get_item(data.get('id'))
                        if item:
                            item.setPos(c.x, c.y)
                
                self._undo_manager.push(
                    action_type='property_change',
                    description=f"修改 {comp.name} {prop_name}",
                    undo_data={'id': comp_id, 'prop': prop_name, 'old_value': old_value, 'new_value': new_value},
                    redo_data={'id': comp_id, 'prop': prop_name, 'old_value': old_value, 'new_value': new_value},
                    undo_callback=undo_position_change,
                    redo_callback=redo_position_change
                )
            elif prop_name in ["width", "height"]:
                def undo_size_change(data):
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        if data.get('prop') == 'width':
                            c.width = data.get('old_value')
                        else:
                            c.height = data.get('old_value')
                        item = self.window.designer_view.get_item(data.get('id'))
                        if item:
                            item.update()
                
                def redo_size_change(data):
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        if data.get('prop') == 'width':
                            c.width = data.get('new_value')
                        else:
                            c.height = data.get('new_value')
                        item = self.window.designer_view.get_item(data.get('id'))
                        if item:
                            item.update()
                
                self._undo_manager.push(
                    action_type='property_change',
                    description=f"修改 {comp.name} {prop_name}",
                    undo_data={'id': comp_id, 'prop': prop_name, 'old_value': old_value, 'new_value': new_value},
                    redo_data={'id': comp_id, 'prop': prop_name, 'old_value': old_value, 'new_value': new_value},
                    undo_callback=undo_size_change,
                    redo_callback=redo_size_change
                )
            else:
                def undo_prop_change(data):
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        setattr(c, data.get('prop'), data.get('old_value'))
                        c.data_changed.emit()
                
                def redo_prop_change(data):
                    c = self.project_model.get_component(data.get('id'))
                    if c:
                        setattr(c, data.get('prop'), data.get('new_value'))
                        c.data_changed.emit()
                
                self._undo_manager.push(
                    action_type='property_change',
                    description=f"修改 {comp.name} {prop_name}",
                    undo_data={'id': comp_id, 'prop': prop_name, 'old_value': old_value, 'new_value': new_value},
                    redo_data={'id': comp_id, 'prop': prop_name, 'old_value': old_value, 'new_value': new_value},
                    undo_callback=undo_prop_change,
                    redo_callback=redo_prop_change
                )
            
            if comp.type == "container" and prop_name in ["width", "height"]:
                current_window = self.project_model.current_window
                if current_window:
                    container_comp = None
                    for cid in current_window.components:
                        c = self.project_model.get_component(cid)
                        if c and c.type == "container":
                            container_comp = c
                            break
                    
                    if container_comp and container_comp.id == comp_id:
                        if prop_name == "width":
                            current_window.width = new_value
                        elif prop_name == "height":
                            current_window.height = new_value
                        
                        self.window.designer_view.update_window_size(
                            current_window.width, current_window.height
                        )
    
    def _check_button_conflict(self, comp_type: str) -> bool:
        """检测确认按钮与普通按钮同窗冲突。
        
        Returns:
            True 允许添加, False 取消添加
        """
        current_window = self.project_model.current_window
        if not current_window:
            return True
        
        has_button = False
        has_confirm = False
        for cid in current_window.components:
            c = self.project_model.get_component(cid)
            if c:
                if c.type == 'button':
                    has_button = True
                elif c.type == 'confirm_button':
                    has_confirm = True
        
        will_conflict = (
            (comp_type == 'confirm_button' and has_button) or
            (comp_type == 'button' and has_confirm)
        )
        
        if will_conflict:
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.warning(
                self.window, "按钮类型冲突",
                "当前窗口已有普通按钮。\n\n"
                "普通按钮和确认按钮在同一窗口中可能产生交互冲突：\n"
                "普通按钮点击立即执行动作，确认按钮需要全部按下才执行。\n\n"
                "确定要继续添加吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            ) if comp_type == 'confirm_button' else QMessageBox.warning(
                self.window, "按钮类型冲突",
                "当前窗口已有确认按钮。\n\n"
                "普通按钮和确认按钮在同一窗口中可能产生交互冲突：\n"
                "普通按钮点击立即执行动作，确认按钮需要全部按下才执行。\n\n"
                "确定要继续添加吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes
        
        return True
    
    def _on_action_config(self, comp_id: str):
        """配置动作 — 先选目标组件，再根据目标类型选动作。"""
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox,
            QComboBox, QLabel, QSpinBox, QGroupBox, QFormLayout, QRadioButton, QButtonGroup
        )
        
        comp = self.project_model.get_component(comp_id)
        if not comp:
            return
        
        current_window_id = self.project_model.current_window_id
        current_window = self.project_model.get_window(current_window_id)
        
        dialog = QDialog(self.window)
        dialog.setWindowTitle(f"配置行为 - {comp.name}")
        dialog.setMinimumSize(420, 300)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        scope_group = QButtonGroup(dialog)
        scope_this = QRadioButton("本窗体")
        scope_all = QRadioButton("全部窗体")
        scope_this.setChecked(True)
        scope_group.addButton(scope_this)
        scope_group.addButton(scope_all)
        scope_layout = QHBoxLayout()
        scope_layout.addWidget(scope_this)
        scope_layout.addWidget(scope_all)
        form.addRow("作用范围:", scope_layout)
        
        target_combo = QComboBox()
        target_combo.addItem("-- 选择目标组件 --", "")
        
        action_combo = QComboBox()
        action_combo.addItem("-- 请先选择目标组件 --", "none")
        action_combo.setEnabled(False)
        
        duration_spin = QSpinBox()
        duration_spin.setRange(500, 30000)
        duration_spin.setSingleStep(500)
        duration_spin.setValue(3000)
        duration_spin.setSuffix(" ms")
        duration_spin.setEnabled(False)
        
        current_action = getattr(comp, 'action', None)
        
        def refresh_targets():
            target_combo.clear()
            target_combo.addItem("-- 选择目标组件 --", "")
            if scope_this.isChecked() and current_window:
                comp_ids = current_window.components
                components = [self.project_model.get_component(cid) for cid in comp_ids]
            else:
                components = self.project_model.get_all_components()
            for c in components:
                if c and c.id != comp_id:
                    target_combo.addItem(f"{c.name} ({c.type})", c.id)
            
            if current_action and current_action.params:
                target_id = current_action.params.get("target_component_id", "")
                if target_id:
                    for i in range(target_combo.count()):
                        if target_combo.itemData(i) == target_id:
                            target_combo.setCurrentIndex(i)
                            break
        
        def get_available_actions(target_comp_type: str) -> list:
            always = [
                ("无动作", "none"),
                ("关闭窗口", "close_window"),
                ("关闭程序", "close_program"),
                ("打开窗口", "open_window"),
            ]
            target_specific = []
            if target_comp_type in ('text_alternating', 'image_alternating'):
                target_specific = [
                    ("开始交替变换", "start_alternating"),
                    ("停止交替变换", "stop_alternating"),
                ]
            elif target_comp_type in ('lottery', 'image_carousel'):
                target_specific = [
                    ("抽奖动画", "lottery_animation"),
                    ("随机图片", "random_image"),
                    ("下一张图片", "next_image"),
                    ("上一张图片", "prev_image"),
                    ("开始轮播", "start_carousel"),
                    ("停止轮播", "stop_carousel"),
                ]

            elif target_comp_type == 'image':
                target_specific = [
                    ("随机图片", "random_image"),
                ]
            
            general = [
                ("设置文本", "set_text"),
                ("显示组件", "show_component"),
                ("隐藏组件", "hide_component"),
            ]
            return always + target_specific + general
        
        def on_target_changed():
            target_id = target_combo.currentData()
            action_combo.clear()
            
            if not target_id:
                action_combo.addItem("-- 请先选择目标组件 --", "none")
                action_combo.setEnabled(False)
                duration_spin.setEnabled(False)
                return
            
            target_comp = self.project_model.get_component(target_id)
            target_type = target_comp.type if target_comp else ""
            
            actions = get_available_actions(target_type)
            for display_name, action_type in actions:
                action_combo.addItem(display_name, action_type)
            
            action_combo.setEnabled(True)
            
            if current_action and current_action.action_type:
                for i in range(action_combo.count()):
                    if action_combo.itemData(i) == current_action.action_type:
                        action_combo.setCurrentIndex(i)
                        break
            
            on_action_changed()
        
        def on_action_changed():
            action_type = action_combo.currentData()
            needs_duration = {"start_alternating", "lottery_animation"}
            duration_spin.setEnabled(action_type in needs_duration)
        
        refresh_targets()
        scope_this.toggled.connect(lambda: refresh_targets())
        target_combo.currentIndexChanged.connect(on_target_changed)
        action_combo.currentIndexChanged.connect(on_action_changed)
        
        form.addRow("目标组件:", target_combo)
        form.addRow("动作类型:", action_combo)
        form.addRow("动画时长:", duration_spin)
        
        layout.addLayout(form)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            from models.schemas import ActionConfig
            
            action_type = action_combo.currentData()
            target_id = target_combo.currentData()
            duration = duration_spin.value()
            
            params = {}
            if target_id:
                params["target_component_id"] = target_id
            needs_duration = {"start_alternating", "lottery_animation"}
            if action_type in needs_duration:
                params["action_params"] = {"duration_ms": duration}
            
            comp.action = ActionConfig(
                action_type=action_type,
                params=params
            )
            
            self.project_model.mark_dirty()
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
            comp_cls = ComponentRegistry.get_model_class(comp_data.get('type') or comp_data.get('comp_type', 'label'))
            comp = (comp_cls or ComponentModel).from_dict(comp_data)
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
                item.resized.connect(self._on_item_resized)  # 【信号入口】组件调整大小 -> 同步窗口尺寸
    
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
    
    def _on_item_resized(self, resize_data: dict):
        """组件调整大小后的回调。
        
        当组件调整大小时，记录撤销操作并同步更新窗口模型和画布桌面大小。
        
        Args:
            resize_data: 包含调整前后尺寸和位置的字典
        """
        comp_id = resize_data.get('id')
        old_width = resize_data.get('old_width', 0)
        old_height = resize_data.get('old_height', 0)
        old_x = resize_data.get('old_x', 0)
        old_y = resize_data.get('old_y', 0)
        new_width = resize_data.get('new_width', 0)
        new_height = resize_data.get('new_height', 0)
        new_x = resize_data.get('new_x', 0)
        new_y = resize_data.get('new_y', 0)
        
        comp = self.project_model.get_component(comp_id)
        if not comp:
            return
        
        def undo_resize(data):
            """撤销调整大小操作的回调函数。"""
            c = self.project_model.get_component(data.get('id'))
            if c:
                c.width = data.get('old_width', 100)
                c.height = data.get('old_height', 100)
                c.x = data.get('old_x', 0)
                c.y = data.get('old_y', 0)
                item = self.window.designer_view.get_item(data.get('id'))
                if item:
                    item.setPos(data.get('old_x', 0), data.get('old_y', 0))
                    item.update()
        
        def redo_resize(data):
            """重做调整大小操作的回调函数。"""
            c = self.project_model.get_component(data.get('id'))
            if c:
                c.width = data.get('new_width', 100)
                c.height = data.get('new_height', 100)
                c.x = data.get('new_x', 0)
                c.y = data.get('new_y', 0)
                item = self.window.designer_view.get_item(data.get('id'))
                if item:
                    item.setPos(data.get('new_x', 0), data.get('new_y', 0))
                    item.update()
        
        self._undo_manager.push(
            action_type='resize',
            description=f"调整 {comp.name} 大小",
            undo_data=resize_data,
            redo_data=resize_data,
            undo_callback=undo_resize,
            redo_callback=redo_resize
        )
        
        if comp.type == "container":
            current_window = self.project_model.current_window
            if current_window:
                container_comp = None
                for cid in current_window.components:
                    c = self.project_model.get_component(cid)
                    if c and c.type == "container":
                        container_comp = c
                        break
                
                if container_comp and container_comp.id == comp_id:
                    self.window.designer_view.update_window_size(new_width, new_height, current_window.frameless)
    
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
            desktop_w = current_window.width
            desktop_h = current_window.height
            for cid in current_window.components:
                c = self.project_model.get_component(cid)
                if c and c.type == "container":
                    desktop_w = c.width
                    desktop_h = c.height
                    break
            self.window.designer_view.update_window_size(desktop_w, desktop_h, False)
        
        components = self.project_model.get_components_for_window(window_id)
        for comp in components:
            item = self.window.designer_view.add_component_item(comp)
            if item:
                item.resized.connect(self._on_item_resized)

    def _on_unbind_extension(self, comp_id: str, target_id: str, action_type: str):
        """处理解除延伸组件绑定请求。
        
        Args:
            comp_id: 触发器组件ID (如按钮)
            target_id: 目标组件ID (如交替变换组件)
            action_type: 动作类型 (如 start_alternating)
        """
        trigger_comp = self.project_model.get_component(comp_id)
        target_comp = self.project_model.get_component(target_id)
        
        if not trigger_comp:
            return
            
        # 1. 重置触发器组件的动作
        from models.schemas import ActionConfig, ActionType
        trigger_comp.action = ActionConfig(action_type=ActionType.NONE.value)
        
        # 2. 从目标组件中移除绑定
        if target_comp:
            if action_type == 'start_alternating':
                if hasattr(target_comp, 'start_btn_id'):
                    target_comp.start_btn_id = ""
            elif action_type == 'stop_alternating':
                if hasattr(target_comp, 'stop_btn_id'):
                    target_comp.stop_btn_id = ""
            elif action_type == 'lottery_animation':
                if hasattr(target_comp, 'start_btn_id'):
                    target_comp.start_btn_id = ""
            # 发射目标组件修改信号
            target_comp.data_changed.emit()
            
        # 发射触发器修改信号
        trigger_comp.data_changed.emit()
        self.project_model.mark_dirty()
        
        # 刷新当前的属性面板视图 (这会重新触发UI构建)
        if self.window.property_panel._current_model and self.window.property_panel._current_model.id == comp_id:
            self.window.property_panel.set_component(trigger_comp)
