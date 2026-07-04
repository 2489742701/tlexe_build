"""安全代码生成工具模块。

本模块提供安全的代码生成功能，防止代码注入攻击。

"""

import ast
import json
from typing import Any, Dict, List, Union

class SafeCodeGenerator:
    """安全代码生成器。
    
    提供安全的Python代码生成功能，防止代码注入。
    
    """
    
    def __init__(self):
        """初始化代码生成器。"""
        self._lines: List[str] = []
        self._indent_level = 0
        self._indent_str = "    "
    
    def add_line(self, line: str):
        """添加一行代码。
        
        Args:
            line: 代码行（已确保安全）
        """
        indent = self._indent_str * self._indent_level
        self._lines.append(indent + line)
    
    def add_lines(self, lines: List[str]):
        """添加多行代码。
        
        Args:
            lines: 代码行列表
        """
        for line in lines:
            self.add_line(line)
    
    def indent(self):
        """增加缩进级别。"""
        self._indent_level += 1
    
    def dedent(self):
        """减少缩进级别。"""
        self._indent_level = max(0, self._indent_level - 1)
    
    @staticmethod
    def safe_string(value: str) -> str:
        """将字符串转换为安全的Python字符串字面量。
        
        使用 repr() 自动处理转义，防止代码注入。
        
        Args:
            value: 原始字符串（可能包含恶意代码）
            
        Returns:
            安全的字符串字面量表示
            
        """
        if value is None:
            return "None"
        return repr(str(value))
    
    @staticmethod
    def safe_int(value: Any) -> str:
        """将值转换为安全的整数表示。
        
        Args:
            value: 原始值
            
        Returns:
            安全的整数字符串
        """
        try:
            return str(int(value))
        except (ValueError, TypeError):
            return "0"
    
    @staticmethod
    def safe_float(value: Any) -> str:
        """将值转换为安全的浮点数表示。
        
        Args:
            value: 原始值
            
        Returns:
            安全的浮点数字符串
        """
        try:
            return str(float(value))
        except (ValueError, TypeError):
            return "0.0"
    
    @staticmethod
    def safe_bool(value: Any) -> str:
        """将值转换为安全的布尔值表示。
        
        Args:
            value: 原始值
            
        Returns:
            "True" 或 "False"
        """
        return "True" if bool(value) else "False"
    
    @staticmethod
    def safe_dict(value: Dict[str, Any], indent: int = 0) -> str:
        """将字典转换为安全的Python字典字面量。
        
        Args:
            value: 字典数据
            indent: 缩进级别
            
        Returns:
            安全的字典字符串
        """
        if not value:
            return "{}"
        
        lines = ["{"]
        indent_str = "    " * (indent + 1)
        
        for k, v in value.items():
            key = SafeCodeGenerator.safe_string(k)
            val = SafeCodeGenerator._safe_value(v, indent + 1)
            lines.append(f"{indent_str}{key}: {val},")
        
        lines.append("    " * indent + "}")
        return "\n".join(lines)
    
    @staticmethod
    def safe_list(value: List[Any], indent: int = 0) -> str:
        """将列表转换为安全的Python列表字面量。
        
        Args:
            value: 列表数据
            indent: 缩进级别
            
        Returns:
            安全的列表字符串
        """
        if not value:
            return "[]"
        
        items = [SafeCodeGenerator._safe_value(item, indent + 1) for item in value]
        
        if len(items) <= 3:
            return "[" + ", ".join(items) + "]"
        
        indent_str = "    " * (indent + 1)
        lines = ["["]
        for item in items:
            lines.append(f"{indent_str}{item},")
        lines.append("    " * indent + "]")
        return "\n".join(lines)
    
    @staticmethod
    def _safe_value(value: Any, indent: int = 0) -> str:
        """将任意值转换为安全的Python表示。
        
        Args:
            value: 任意值
            indent: 缩进级别
            
        Returns:
            安全的Python字符串表示
        """
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return SafeCodeGenerator.safe_bool(value)
        elif isinstance(value, int):
            return SafeCodeGenerator.safe_int(value)
        elif isinstance(value, float):
            return SafeCodeGenerator.safe_float(value)
        elif isinstance(value, str):
            return SafeCodeGenerator.safe_string(value)
        elif isinstance(value, dict):
            return SafeCodeGenerator.safe_dict(value, indent)
        elif isinstance(value, list):
            return SafeCodeGenerator.safe_list(value, indent)
        else:
            # 对于未知类型，使用 repr() 作为最后的保护
            return repr(value)
    
    @staticmethod
    def validate_identifier(name: str) -> str:
        """验证并清理Python标识符。
        
        确保名称是合法的Python标识符，防止注入。
        
        Args:
            name: 标识符名称
            
        Returns:
            安全的标识符名称
            
        Raises:
            ValueError: 如果名称无法转换为合法标识符
        """
        if not name:
            raise ValueError("标识符名称不能为空")
        
        # 移除非法字符
        safe_name = "".join(c for c in name if c.isalnum() or c == "_")
        
        # 确保不以数字开头
        if safe_name and safe_name[0].isdigit():
            safe_name = "_" + safe_name
        
        # 检查是否为Python关键字
        import keyword
        if keyword.iskeyword(safe_name):
            safe_name = safe_name + "_"
        
        if not safe_name:
            raise ValueError(f"无法从 '{name}' 创建合法标识符")
        
        return safe_name
    
    def generate(self) -> str:
        """生成最终的Python代码。
        
        Returns:
            完整的Python代码字符串
        """
        return "\n".join(self._lines)
    
    def validate_syntax(self) -> bool:
        """验证生成的代码语法是否正确。
        
        Returns:
            语法是否正确
        """
        code = self.generate()
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

def safe_format_template(template: str, **kwargs) -> str:
    """安全地格式化代码模板。
    
    所有值都会通过 repr() 转义，防止注入。
    
    Args:
        template: 模板字符串，使用 {name} 作为占位符
        **kwargs: 要填充的值
        
    Returns:
        安全的格式化字符串
        
    使用示例:
        code = safe_format_template(
            'btn = QPushButton({text}, parent)',
            text=user_input  # 自动转义
        )
    """
    safe_kwargs = {}
    for key, value in kwargs.items():
        safe_kwargs[key] = SafeCodeGenerator._safe_value(value)
    
    return template.format(**safe_kwargs)

# 预定义的代码模板（安全版本）
CODE_TEMPLATES = {
    'button_create': '''QPushButton({text}, {parent})''',
    'label_create': '''QLabel({text}, {parent})''',
    'input_create': '''QLineEdit({parent})''',
    'set_geometry': '''{widget}.setGeometry({x}, {y}, {width}, {height})''',
    'set_stylesheet': '''{widget}.setStyleSheet({stylesheet})''',
}

def generate_safe_button_code(text: str, parent: str = "parent", 
                               x: int = 0, y: int = 0, 
                               width: int = 100, height: int = 30) -> str:
    """生成安全的按钮创建代码。
    
    Args:
        text: 按钮文本（会被安全转义）
        parent: 父控件变量名
        x, y, width, height: 位置和大小
        
    Returns:
        安全的Python代码
    """
    gen = SafeCodeGenerator()
    
    # 安全地转义文本
    safe_text = SafeCodeGenerator.safe_string(text)
    safe_parent = SafeCodeGenerator.validate_identifier(parent)
    
    gen.add_line(f"btn = QPushButton({safe_text}, {safe_parent})")
    gen.add_line(f"btn.setGeometry({x}, {y}, {width}, {height})")
    
    return gen.generate()

# 向后兼容：提供安全的字符串转义函数
def safe_repr(value: str) -> str:
    """向后兼容的安全字符串转义函数。
    
    """
    return SafeCodeGenerator.safe_string(value)
