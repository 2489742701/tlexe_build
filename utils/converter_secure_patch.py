"""converter.py 安全修复补丁。

本模块提供安全修复后的代码生成函数，
使用 SafeCodeGenerator 转义所有用户输入，防止代码注入。

## 修复说明 (2026-04-02 MCP审查修复)
原 converter.py 使用 f-string 直接拼接用户输入，存在代码注入漏洞。
此补丁提供安全的替代函数。
"""

from typing import Dict, Any, List
from utils.safe_code_generator import SafeCodeGenerator


class SecureCodeTemplates:
    """安全的代码模板生成器。
    
    所有用户输入都通过 SafeCodeGenerator 转义。
    """
    
    @staticmethod
    def create_button(data: Dict[str, Any]) -> List[str]:
        """生成安全的按钮创建代码。"""
        # 安全地转义所有用户输入
        text = SafeCodeGenerator.safe_string(data.get('text', ''))
        x = SafeCodeGenerator.safe_int(data.get('x', 0))
        y = SafeCodeGenerator.safe_int(data.get('y', 0))
        width = SafeCodeGenerator.safe_int(data.get('width', 100))
        height = SafeCodeGenerator.safe_int(data.get('height', 30))
        
        lines = [
            f'btn = QPushButton({text}, parent)',
            f'btn.setGeometry({x}, {y}, {width}, {height})',
        ]
        
        # 安全处理样式
        style = data.get('style', {})
        if style:
            bg_color = SafeCodeGenerator.safe_string(style.get('background_color', '#f0f0f0'))
            text_color = SafeCodeGenerator.safe_string(style.get('text_color', '#000000'))
            border_color = SafeCodeGenerator.safe_string(style.get('border_color', '#cccccc'))
            border_width = SafeCodeGenerator.safe_int(style.get('border_width', 1))
            border_radius = SafeCodeGenerator.safe_int(style.get('border_radius', 4))
            font_size = SafeCodeGenerator.safe_int(style.get('font_size', 12))
            
            lines.append(f'btn.setStyleSheet(f"""')
            lines.append(f'    QPushButton {{')
            lines.append(f'        background-color: {{{bg_color}}};')
            lines.append(f'        color: {{{text_color}}};')
            lines.append(f'        border: {{{border_width}}}px solid {{{border_color}}};')
            lines.append(f'        border-radius: {{{border_radius}}}px;')
            lines.append(f'        font-size: {{{font_size}}}px;')
            lines.append(f'    }}')
            lines.append(f'""")')
        
        return lines
    
    @staticmethod
    def create_label(data: Dict[str, Any]) -> List[str]:
        """生成安全的标签创建代码。"""
        text = SafeCodeGenerator.safe_string(data.get('text', ''))
        x = SafeCodeGenerator.safe_int(data.get('x', 0))
        y = SafeCodeGenerator.safe_int(data.get('y', 0))
        width = SafeCodeGenerator.safe_int(data.get('width', 100))
        height = SafeCodeGenerator.safe_int(data.get('height', 30))
        
        lines = [
            f'lbl = QLabel({text}, parent)',
            f'lbl.setGeometry({x}, {y}, {width}, {height})',
        ]
        
        # 安全处理样式
        style = data.get('style', {})
        if style:
            bg_color = SafeCodeGenerator.safe_string(style.get('background_color', 'transparent'))
            text_color = SafeCodeGenerator.safe_string(style.get('text_color', '#333333'))
            font_size = SafeCodeGenerator.safe_int(style.get('font_size', 12))
            
            lines.append(f'lbl.setStyleSheet(f"""')
            lines.append(f'    QLabel {{')
            lines.append(f'        background-color: {{{bg_color}}};')
            lines.append(f'        color: {{{text_color}}};')
            lines.append(f'        font-size: {{{font_size}}}px;')
            lines.append(f'    }}')
            lines.append(f'""")')
        
        return lines
    
    @staticmethod
    def create_input(data: Dict[str, Any]) -> List[str]:
        """生成安全的输入框创建代码。"""
        x = SafeCodeGenerator.safe_int(data.get('x', 0))
        y = SafeCodeGenerator.safe_int(data.get('y', 0))
        width = SafeCodeGenerator.safe_int(data.get('width', 200))
        height = SafeCodeGenerator.safe_int(data.get('height', 30))
        placeholder = SafeCodeGenerator.safe_string(data.get('placeholder', ''))
        max_length = SafeCodeGenerator.safe_int(data.get('max_length', 32767))
        
        lines = [
            f'inp = QLineEdit(parent)',
            f'inp.setGeometry({x}, {y}, {width}, {height})',
            f'inp.setPlaceholderText({placeholder})',
            f'inp.setMaxLength({max_length})',
        ]
        
        # 安全处理样式
        style = data.get('style', {})
        if style:
            bg_color = SafeCodeGenerator.safe_string(style.get('background_color', '#ffffff'))
            text_color = SafeCodeGenerator.safe_string(style.get('text_color', '#333333'))
            border_color = SafeCodeGenerator.safe_string(style.get('border_color', '#cccccc'))
            border_width = SafeCodeGenerator.safe_int(style.get('border_width', 1))
            
            lines.append(f'inp.setStyleSheet(f"""')
            lines.append(f'    QLineEdit {{')
            lines.append(f'        background-color: {{{bg_color}}};')
            lines.append(f'        color: {{{text_color}}};')
            lines.append(f'        border: {{{border_width}}}px solid {{{border_color}}};')
            lines.append(f'    }}')
            lines.append(f'""")')
        
        return lines


def patch_converter_converter():
    """
    为 converter.py 提供安全修复的 monkey patch。
    
    使用示例:
        from utils.converter_secure_patch import patch_converter_converter
        patch_converter_converter()  # 应用安全补丁
    """
    import utils.converter as converter
    
    # 保存原始方法
    if not hasattr(converter, '_original_generate_component_code'):
        converter._original_generate_component_code = converter.ProjectConverter._generate_component_code
    
    # 替换为安全版本
    converter.ProjectConverter._generate_component_code = _secure_generate_component_code
    
    print("[安全补丁] converter.py 已应用安全修复")


def _secure_generate_component_code(component: Dict[str, Any]) -> List[str]:
    """安全版本的组件代码生成。
    
    使用 SafeCodeGenerator 转义所有用户输入。
    """
    comp_type = component.get('type', '')
    
    if comp_type == 'button':
        return SecureCodeTemplates.create_button(component)
    elif comp_type == 'label':
        return SecureCodeTemplates.create_label(component)
    elif comp_type == 'input':
        return SecureCodeTemplates.create_input(component)
    else:
        # 对于其他类型，返回安全的占位代码
        comp_id = SafeCodeGenerator.safe_string(component.get('id', 'unknown'))
        return [
            f'# 组件 {comp_id} 的安全代码生成尚未实现',
            f'pass',
        ]
