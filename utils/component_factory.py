"""组件样式和工厂模块。

本模块提供统一的样式计算和运行时组件创建逻辑，
确保画布绘制和运行时控件显示一致。
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QCheckBox, QComboBox, QListWidget, QGroupBox, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from models.base import ComponentModel, StyleConfig
from models.components import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ProgressBarModel
)


class StyleHelper:
    """样式辅助类。
    
    提供统一的样式计算方法，供画布绘制和运行时控件使用。
    """
    
    @staticmethod
    def get_stylesheet(style: StyleConfig, extra_styles: str = "") -> str:
        """生成样式表字符串。
        
        Args:
            style: 样式配置对象
            extra_styles: 额外的样式字符串
            
        Returns:
            样式表字符串
        """
        if style.use_native_style:
            return ""
        
        style_parts = []
        
        if style.background_color and style.background_color != "transparent":
            style_parts.append(f"background-color: {style.background_color};")
        else:
            style_parts.append("background-color: transparent;")
        
        if style.text_color:
            style_parts.append(f"color: {style.text_color};")
        
        if style.border_color:
            border_width = style.border_width
            if border_width > 0:
                style_parts.append(f"border: {border_width}px solid {style.border_color};")
            else:
                style_parts.append("border: none;")
        
        if style.border_radius > 0:
            style_parts.append(f"border-radius: {style.border_radius}px;")
        
        if style.font_size:
            style_parts.append(f"font-size: {style.font_size}pt;")
        
        if style.font_bold:
            style_parts.append("font-weight: bold;")
        
        if extra_styles:
            style_parts.append(extra_styles)
        
        return "".join(style_parts)
    
    @staticmethod
    def apply_style(widget: QWidget, style: StyleConfig, extra_styles: str = ""):
        """应用样式到控件。
        
        Args:
            widget: 要应用样式的控件
            style: 样式配置对象
            extra_styles: 额外的样式字符串
        """
        if not style.use_native_style:
            stylesheet = StyleHelper.get_stylesheet(style, extra_styles)
            if stylesheet:
                widget.setStyleSheet(stylesheet)
        
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        widget.setFont(font)
    
    @staticmethod
    def get_font(style: StyleConfig) -> QFont:
        """获取字体对象。
        
        Args:
            style: 样式配置对象
            
        Returns:
            QFont 对象
        """
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        return font
    
    @staticmethod
    def is_native_style(style: StyleConfig) -> bool:
        """检查是否使用原生样式。
        
        Args:
            style: 样式配置对象
            
        Returns:
            True 表示使用原生样式，False 表示使用自定义样式
        """
        return style.use_native_style


class ComponentFactory:
    """组件工厂类。
    
    提供统一的运行时组件创建方法。
    """
    
    TITLE_BAR_HEIGHT = 28
    
    @staticmethod
    def create_widget(model: ComponentModel) -> Optional[QWidget]:
        """根据模型创建对应的 Qt 控件（用于运行时）。
        
        Args:
            model: 组件数据模型
            
        Returns:
            创建的 Qt 控件，如果类型不支持则返回 None
        """
        comp_type = model.type
        
        creators = {
            'button': ComponentFactory._create_button,
            'label': ComponentFactory._create_label,
            'input': ComponentFactory._create_input,
            'textarea': ComponentFactory._create_textarea,
            'checkbox': ComponentFactory._create_checkbox,
            'combobox': ComponentFactory._create_combobox,
            'listwidget': ComponentFactory._create_listwidget,
            'groupbox': ComponentFactory._create_groupbox,
            'container': ComponentFactory._create_container,
            'progressbar': ComponentFactory._create_progressbar,
        }
        
        creator = creators.get(comp_type)
        if creator:
            widget = creator(model)
            if widget:
                widget.setProperty("component_id", model.id)
                widget.setProperty("component_type", comp_type)
            return widget
        
        return None
    
    @staticmethod
    def _create_button(model: ButtonModel) -> QPushButton:
        """创建按钮控件。"""
        button = QPushButton()
        button.setText(model.text or "按钮")
        button.resize(model.width, model.height)
        
        alignment = getattr(model, 'alignment', 'center')
        if alignment == 'left':
            extra = "text-align: left; padding-left: 10px;"
        elif alignment == 'right':
            extra = "text-align: right; padding-right: 10px;"
        else:
            extra = "text-align: center;"
        
        StyleHelper.apply_style(button, model.style, extra)
        return button
    
    @staticmethod
    def _create_label(model: LabelModel) -> QLabel:
        """创建标签控件。"""
        label = QLabel()
        label.setText(model.text or "文本")
        label.resize(model.width, model.height)
        
        alignment_map = {
            'left': Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            'center': Qt.AlignmentFlag.AlignCenter,
            'right': Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            'top': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            'bottom': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
        }
        label.setAlignment(alignment_map.get(model.alignment, Qt.AlignmentFlag.AlignCenter))
        label.setWordWrap(model.word_wrap)
        
        extra = ""
        if model.style.background_color == "transparent":
            extra = "background-color: transparent;"
        
        StyleHelper.apply_style(label, model.style, extra)
        
        return label
    
    @staticmethod
    def _create_input(model: InputModel) -> QLineEdit:
        """创建输入框控件。"""
        line_edit = QLineEdit()
        line_edit.setText(model.text or "")
        line_edit.setPlaceholderText(model.placeholder or "")
        line_edit.setMaxLength(model.max_length)
        line_edit.resize(model.width, model.height)
        
        if model.is_password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        StyleHelper.apply_style(line_edit, model.style)
        return line_edit
    
    @staticmethod
    def _create_textarea(model: InputModel) -> QTextEdit:
        """创建多行文本框控件。"""
        text_edit = QTextEdit()
        text_edit.setPlainText(model.text or "")
        text_edit.setPlaceholderText(model.placeholder or "")
        text_edit.resize(model.width, model.height)
        StyleHelper.apply_style(text_edit, model.style)
        return text_edit
    
    @staticmethod
    def _create_checkbox(model: CheckBoxModel) -> QCheckBox:
        """创建复选框控件。"""
        checkbox = QCheckBox()
        checkbox.setText(model.text or "复选框")
        checkbox.setChecked(model.checked)
        checkbox.resize(model.width, model.height)
        StyleHelper.apply_style(checkbox, model.style)
        return checkbox
    
    @staticmethod
    def _create_combobox(model: ComboBoxModel) -> QComboBox:
        """创建下拉框控件。"""
        combo = QComboBox()
        items = model.items or []
        combo.addItems(items)
        if model.current_index >= 0 and model.current_index < len(items):
            combo.setCurrentIndex(model.current_index)
        combo.resize(model.width, model.height)
        StyleHelper.apply_style(combo, model.style)
        return combo
    
    @staticmethod
    def _create_listwidget(model) -> QListWidget:
        """创建列表控件。"""
        list_widget = QListWidget()
        items = getattr(model, 'items', []) or []
        list_widget.addItems(items)
        list_widget.resize(model.width, model.height)
        StyleHelper.apply_style(list_widget, model.style)
        return list_widget
    
    @staticmethod
    def _create_groupbox(model) -> QGroupBox:
        """创建分组框控件。"""
        group_box = QGroupBox()
        group_box.setTitle(model.text or "")
        group_box.resize(model.width, model.height)
        StyleHelper.apply_style(group_box, model.style)
        return group_box
    
    @staticmethod
    def _create_container(model: ContainerModel) -> QWidget:
        """创建容器控件。"""
        from PySide6.QtWidgets import QFrame
        
        container = QFrame()
        container.resize(model.width, model.height)
        
        if model.style.use_native_style:
            container.setFrameStyle(QFrame.Shape.StyledPanel)
        else:
            style = model.style
            bg_color = style.background_color if style.background_color != "transparent" else "#ffffff"
            border_radius = style.border_radius
            
            container.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid #cccccc;
                    border-radius: {border_radius}px;
                }}
            """)
        
        return container
    
    @staticmethod
    def _create_progressbar(model: ProgressBarModel) -> QProgressBar:
        """创建进度条控件。"""
        progressbar = QProgressBar()
        progressbar.resize(model.width, model.height)
        progressbar.setValue(model.value)
        
        if model.show_text:
            progressbar.setFormat("%p%")
        else:
            progressbar.setTextVisible(False)
        
        StyleHelper.apply_style(progressbar, model.style)
        return progressbar
    
    @staticmethod
    def update_widget(widget: QWidget, model: ComponentModel):
        """更新控件属性。
        
        Args:
            widget: 要更新的控件
            model: 新的组件模型
        """
        comp_type = model.type
        
        if comp_type == 'button':
            widget.setText(model.text or "按钮")
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'label':
            widget.setText(model.text or "文本")
            alignment_map = {
                'left': Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                'center': Qt.AlignmentFlag.AlignCenter,
                'right': Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                'top': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                'bottom': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            }
            widget.setAlignment(alignment_map.get(model.alignment, Qt.AlignmentFlag.AlignCenter))
            widget.setWordWrap(model.word_wrap)
            
            extra = ""
            if model.style.background_color == "transparent":
                extra = "background-color: transparent;"
            
            StyleHelper.apply_style(widget, model.style, extra)
        elif comp_type == 'checkbox':
            widget.setText(model.text or "复选框")
            widget.setChecked(model.checked)
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'combobox':
            widget.clear()
            items = model.items or []
            widget.addItems(items)
            if model.current_index >= 0 and model.current_index < len(items):
                widget.setCurrentIndex(model.current_index)
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'progressbar':
            widget.setValue(model.value)
            widget.setTextVisible(model.show_text)
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'input':
            widget.setText(model.text or "")
            widget.setPlaceholderText(model.placeholder or "")
            StyleHelper.apply_style(widget, model.style)
        
        widget.resize(model.width, model.height)


def create_component_widget(model: ComponentModel) -> Optional[QWidget]:
    """便捷函数：创建运行时组件控件。
    
    Args:
        model: 组件数据模型
        
    Returns:
        创建的 Qt 控件
    """
    return ComponentFactory.create_widget(model)


def update_component_widget(widget: QWidget, model: ComponentModel):
    """便捷函数：更新组件控件。
    
    Args:
        widget: 要更新的控件
        model: 新的组件模型
    """
    ComponentFactory.update_widget(widget, model)
