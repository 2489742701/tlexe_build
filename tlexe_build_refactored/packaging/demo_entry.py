"""交替变换演示 - 打包入口脚本（项目数据内嵌）。"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from runtime.runner import Runner

project_data = \
{
    'name': '交替变换演示',
    'windows': [
        {
            'id': 'win_demo',
            'name': '主界面',
            'window_type': 'main',
            'width': 500,
            'height': 420,
            'title': '交替变换演示',
            'components': ['cont', 'title', 'alt', 'btn_toggle', 'result'],
        },
    ],
    'components': [
        {
            'id': 'cont',
            'comp_type': 'container',
            'name': '主容器',
            'x': 10, 'y': 10, 'width': 480, 'height': 400,
            'text': '', 'parent_id': '',
            'style': {'background_color': '#f5f5f5', 'text_color': '#333333', 'border_color': '#cccccc', 'border_width': 1, 'border_radius': 8, 'font_family': 'Microsoft YaHei', 'font_size': 12, 'font_bold': False, 'use_native_style': False},
            'action': {'action_type': 'none', 'params': {}, 'blockly_xml': '', 'python_code': ''},
            'visible': True, 'enabled': True, 'custom_props': {}, 'h_align': 'none', 'v_align': 'none',
            'children': [], 'position_mode': 'center', 'layout': 'none', 'padding': 10, 'spacing': 5,
        },
        {
            'id': 'title',
            'comp_type': 'label',
            'name': '标题',
            'x': 140, 'y': 30, 'width': 220, 'height': 40,
            'text': '交替变换演示', 'parent_id': 'cont',
            'style': {'background_color': 'transparent', 'text_color': '#333333', 'border_color': '#999999', 'border_width': 0, 'border_radius': 0, 'font_family': 'Microsoft YaHei', 'font_size': 22, 'font_bold': True, 'use_native_style': False},
            'action': {'action_type': 'none', 'params': {}, 'blockly_xml': '', 'python_code': ''},
            'visible': True, 'enabled': True, 'custom_props': {}, 'h_align': 'none', 'v_align': 'none',
            'alignment': 'center', 'word_wrap': True, 'auto_size': True,
        },
        {
            'id': 'alt',
            'comp_type': 'text_alternating',
            'name': '交替区',
            'x': 90, 'y': 85, 'width': 300, 'height': 180,
            'text': '', 'parent_id': 'cont',
            'style': {'background_color': '#e8e8e8', 'text_color': '#333333', 'border_color': '#cccccc', 'border_width': 2, 'border_radius': 10, 'font_family': 'Microsoft YaHei', 'font_size': 12, 'font_bold': False, 'use_native_style': False},
            'action': {'action_type': 'none', 'params': {}, 'blockly_xml': '', 'python_code': ''},
            'visible': True, 'enabled': True, 'custom_props': {}, 'h_align': 'none', 'v_align': 'none',
            'items': ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十'],
            'item_labels': ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十'],
            'display_mode': 'text',
            'current_index': 0,
            'animation_duration': 3000,
        },
        {
            'id': 'btn_toggle',
            'comp_type': 'button',
            'name': '开始',
            'x': 175, 'y': 285, 'width': 130, 'height': 40,
            'text': '开始', 'parent_id': 'cont',
            'style': {'background_color': '#4CAF50', 'text_color': '#ffffff', 'border_color': '#388E3C', 'border_width': 0, 'border_radius': 8, 'font_family': 'Microsoft YaHei', 'font_size': 16, 'font_bold': True, 'use_native_style': False},
            'action': {'action_type': 'start_alternating', 'params': {'target_component_id': 'alt', 'action_params': {'duration_ms': 3000}}, 'blockly_xml': '', 'python_code': ''},
            'visible': True, 'enabled': True, 'custom_props': {}, 'h_align': 'none', 'v_align': 'none',
            'target_window_id': '', 'branch_name': '', 'open_mode': 'new_window', 'is_default': False, 'is_cancel': False, 'alignment': 'center',
        },
        {
            'id': 'result',
            'comp_type': 'label',
            'name': '结果',
            'x': 40, 'y': 340, 'width': 420, 'height': 50,
            'text': '点击「开始」启动交替变换', 'parent_id': 'cont',
            'style': {'background_color': 'transparent', 'text_color': '#4CAF50', 'border_color': '#999999', 'border_width': 0, 'border_radius': 0, 'font_family': 'Microsoft YaHei', 'font_size': 20, 'font_bold': True, 'use_native_style': False},
            'action': {'action_type': 'none', 'params': {}, 'blockly_xml': '', 'python_code': ''},
            'visible': True, 'enabled': True, 'custom_props': {}, 'h_align': 'none', 'v_align': 'none',
            'alignment': 'center', 'word_wrap': True, 'auto_size': True,
        },
    ],
    'linkages': [
        {
            'source_component': 'alt',
            'source_event': 'stopped',
            'target_component': 'result',
            'target_action': 'set_text',
            'params': {'text_template': '结果: {value}'},
        },
    ],
    'main_window_id': 'win_demo',
    'current_window_id': 'win_demo',
}

def main():
    app = QApplication(sys.argv)
    runner = Runner()
    runner.run(project_data)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
