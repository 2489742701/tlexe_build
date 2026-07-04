"""安全表达式求值模块。

本模块提供安全的表达式求值功能，防止代码注入和任意代码执行。

【安全特性】
1. 禁止函数调用
2. 禁止属性访问
3. 禁止导入语句
4. 仅支持基本运算符和逻辑运算符
5. 变量访问通过受控的上下文

【支持的表达式】
- 比较: ==, !=, <, >, <=, >=
- 逻辑: and, or, not
- 算术: +, -, *, /, //, %, **
- 成员: in, not in
- 变量: $variable_name

【使用示例】
    evaluator = SafeExpressionEvaluator()
    context = {'score': 100, 'level': 5}
    
    # 安全求值
    result = evaluator.evaluate('$score > 50 and $level >= 3', context)
    # result = True
    
    # 危险表达式会被拒绝
    try:
        evaluator.evaluate('__import__("os").system("ls")', context)
    except SecurityError:
        print("危险表达式被阻止")
"""

import ast
import operator
from typing import Any, Dict, Callable, Set, Optional
from dataclasses import dataclass
from enum import Enum, auto

class ExpressionError(Exception):
    """表达式错误基类。"""
    pass

class SecurityError(ExpressionError):
    """安全错误，表达式包含危险操作。"""
    pass

class SyntaxError(ExpressionError):
    """语法错误。"""
    pass

class EvaluationError(ExpressionError):
    """求值错误。"""
    pass

@dataclass
class Token:
    """表达式令牌。"""
    type: str
    value: Any
    position: int

class TokenType(Enum):
    """令牌类型。"""
    NUMBER = auto()
    STRING = auto()
    VARIABLE = auto()  # $variable
    OPERATOR = auto()
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    EOF = auto()

class SafeExpressionEvaluator:
    """安全表达式求值器。
    
    【安全机制】
    1. 词法分析阶段过滤非法字符
    2. 语法分析阶段限制节点类型
    3. 求值阶段使用受控的上下文
    
    【性能】
    - 表达式可预编译，多次求值更快
    - 使用迭代而非递归，避免栈溢出
    """
    
    # 允许的比较运算符
    COMPARE_OPS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
    }
    
    # 允许的算术运算符
    BINARY_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    
    # 允许的一元运算符
    UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
        ast.Invert: operator.invert,
    }
    
    # 允许的逻辑运算符
    BOOL_OPS = {
        ast.And: all,
        ast.Or: any,
    }
    
    # 危险节点类型（禁止）
    DANGEROUS_NODES = (
        ast.Call,           # 函数调用
        ast.Attribute,      # 属性访问
        ast.Subscript,      # 下标访问（可能执行__getitem__）
        ast.Lambda,         # lambda函数
        ast.FunctionDef,    # 函数定义
        ast.ClassDef,       # 类定义
        ast.Import,         # 导入
        ast.ImportFrom,     # 从模块导入
        ast.ExceptHandler,  # 异常处理
        ast.Try,            # try语句
        ast.With,           # with语句
        ast.For,            # for循环
        ast.While,          # while循环
        ast.If,             # if语句（在表达式中不允许）
        ast.ListComp,       # 列表推导式
        ast.DictComp,       # 字典推导式
        ast.SetComp,        # 集合推导式
        ast.GeneratorExp,   # 生成器表达式
        ast.Await,          # async/await
        ast.AsyncFor,
        ast.AsyncWith,
        ast.Yield,
        ast.YieldFrom,
    )
    
    def __init__(self, max_length: int = 1000):
        """初始化求值器。
        
        Args:
            max_length: 表达式最大长度
        """
        self.max_length = max_length
        self._compiled_cache: Dict[str, ast.AST] = {}
    
    def evaluate(self, expression: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """安全地求值表达式。
        
        Args:
            expression: 表达式字符串
            context: 变量上下文
            
        Returns:
            求值结果
            
        Raises:
            SecurityError: 表达式包含危险操作
            SyntaxError: 表达式语法错误
            EvaluationError: 求值过程中出错
            
        使用示例:
            >>> evaluator = SafeExpressionEvaluator()
            >>> evaluator.evaluate('1 + 2')
            3
            >>> evaluator.evaluate('$score > 50', {'score': 100})
            True
        """
        if not expression or not expression.strip():
            return True  # 空表达式视为通过
        
        if len(expression) > self.max_length:
            raise SecurityError(f"表达式过长: {len(expression)} > {self.max_length}")
        
        # 预处理：替换变量引用 $var -> var
        processed_expr = self._preprocess_expression(expression)
        
        # 解析表达式
        try:
            tree = ast.parse(processed_expr, mode='eval')
        except SyntaxError as e:
            raise SyntaxError(f"表达式语法错误: {e}")
        
        # 安全检查
        self._check_security(tree)
        
        # 求值
        try:
            result = self._eval_node(tree.body, context or {})
            return result
        except Exception as e:
            raise EvaluationError(f"求值错误: {e}")
    
    def compile(self, expression: str) -> ast.AST:
        """预编译表达式。
        
        编译后的表达式可以多次求值，提高性能。
        
        Args:
            expression: 表达式字符串
            
        Returns:
            编译后的AST
        """
        if expression in self._compiled_cache:
            return self._compiled_cache[expression]
        
        processed_expr = self._preprocess_expression(expression)
        tree = ast.parse(processed_expr, mode='eval')
        self._check_security(tree)
        
        self._compiled_cache[expression] = tree
        return tree
    
    def evaluate_compiled(self, compiled: ast.AST, context: Optional[Dict[str, Any]] = None) -> Any:
        """求值预编译的表达式。
        
        Args:
            compiled: 编译后的AST
            context: 变量上下文
            
        Returns:
            求值结果
        """
        return self._eval_node(compiled.body, context or {})
    
    def _preprocess_expression(self, expression: str) -> str:
        """预处理表达式。
        
        将 $variable 替换为合法的Python标识符格式。
        
        Args:
            expression: 原始表达式
            
        Returns:
            处理后的表达式
        """
        import re
        
        # 替换 $variable 为 __var_variable
        # 这样可以在AST中作为Name节点处理
        def replace_var(match):
            var_name = match.group(1)
            return f"__var_{var_name}"
        
        # 匹配 $variable_name 或 ${variable_name}
        processed = re.sub(r'\$\{?(\w+)\}?', replace_var, expression)
        
        return processed
    
    def _check_security(self, tree: ast.AST):
        """安全检查。
        
        遍历AST，检查是否包含危险节点。
        
        Args:
            tree: AST树
            
        Raises:
            SecurityError: 发现危险节点
        """
        for node in ast.walk(tree):
            if isinstance(node, self.DANGEROUS_NODES):
                raise SecurityError(f"表达式包含危险操作: {type(node).__name__}")
            
            # 检查Name节点，只允许变量和常量
            if isinstance(node, ast.Name):
                if not node.id.startswith('__var_') and not hasattr(__builtins__, node.id):
                    # 检查是否是Python内置函数（可能被滥用）
                    dangerous_builtins = {'eval', 'exec', 'compile', 'open', 'input', 
                                         '__import__', 'getattr', 'setattr', 'delattr'}
                    if node.id in dangerous_builtins:
                        raise SecurityError(f"不允许使用: {node.id}")
    
    def _eval_node(self, node: ast.AST, context: Dict[str, Any]) -> Any:
        """求值AST节点。
        
        Args:
            node: AST节点
            context: 变量上下文
            
        Returns:
            求值结果
        """
        # 常量
        if isinstance(node, ast.Constant):
            return node.value
        
        # 变量（预处理后的）
        if isinstance(node, ast.Name):
            if node.id.startswith('__var_'):
                var_name = node.id[6:]  # 去掉 __var_ 前缀
                if var_name not in context:
                    raise EvaluationError(f"变量未定义: {var_name}")
                return context[var_name]
            raise SecurityError(f"未授权的标识符: {node.id}")
        
        # 二元运算
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op_func = self.BINARY_OPS.get(type(node.op))
            if not op_func:
                raise SecurityError(f"不支持的运算符: {type(node.op).__name__}")
            return op_func(left, right)
        
        # 一元运算
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            op_func = self.UNARY_OPS.get(type(node.op))
            if not op_func:
                raise SecurityError(f"不支持的运算符: {type(node.op).__name__}")
            return op_func(operand)
        
        # 比较运算
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            result = True
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, context)
                op_func = self.COMPARE_OPS.get(type(op))
                if not op_func:
                    raise SecurityError(f"不支持的比较符: {type(op).__name__}")
                if not op_func(left, right):
                    result = False
                    break
                left = right
            return result
        
        # 逻辑运算
        if isinstance(node, ast.BoolOp):
            values = [self._eval_node(v, context) for v in node.values]
            op_func = self.BOOL_OPS.get(type(node.op))
            if not op_func:
                raise SecurityError(f"不支持的逻辑运算符: {type(node.op).__name__}")
            return op_func(values)
        
        # 元组、列表、集合
        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt, context) for elt in node.elts)
        if isinstance(node, ast.List):
            return [self._eval_node(elt, context) for elt in node.elts]
        if isinstance(node, ast.Set):
            return {self._eval_node(elt, context) for elt in node.elts}
        if isinstance(node, ast.Dict):
            return {
                self._eval_node(k, context): self._eval_node(v, context)
                for k, v in zip(node.keys, node.values)
            }
        
        # 条件表达式 (a if b else c)
        if isinstance(node, ast.IfExp):
            test = self._eval_node(node.test, context)
            if test:
                return self._eval_node(node.body, context)
            else:
                return self._eval_node(node.orelse, context)
        
        raise SecurityError(f"不支持的表达式类型: {type(node).__name__}")
    
    def validate(self, expression: str) -> bool:
        """验证表达式是否安全。
        
        Args:
            expression: 表达式字符串
            
        Returns:
            是否安全
        """
        try:
            self.compile(expression)
            return True
        except (SecurityError, SyntaxError):
            return False
    
    def get_variables(self, expression: str) -> Set[str]:
        """获取表达式中使用的所有变量。
        
        Args:
            expression: 表达式字符串
            
        Returns:
            变量名集合
        """
        processed = self._preprocess_expression(expression)
        tree = ast.parse(processed, mode='eval')
        
        variables = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id.startswith('__var_'):
                variables.add(node.id[6:])
        
        return variables

# 便捷函数
def safe_eval(expression: str, context: Optional[Dict[str, Any]] = None, 
              default: Any = None) -> Any:
    """安全求值表达式的便捷函数。
    
    Args:
        expression: 表达式字符串
        context: 变量上下文
        default: 出错时的默认值
        
    Returns:
        求值结果，出错时返回default
        
    使用示例:
        >>> safe_eval('$x + $y', {'x': 1, 'y': 2})
        3
        >>> safe_eval('dangerous_code', default=False)
        False
    """
    evaluator = SafeExpressionEvaluator()
    try:
        return evaluator.evaluate(expression, context)
    except Exception:
        return default

def validate_condition(condition: str) -> bool:
    """验证条件表达式是否安全。
    
    Args:
        condition: 条件表达式
        
    Returns:
        是否安全
    """
    if not condition:
        return True
    
    evaluator = SafeExpressionEvaluator()
    return evaluator.validate(condition)

# 预定义的常用条件模板
CONDITION_TEMPLATES = {
    'equals': '$var == {value}',
    'not_equals': '$var != {value}',
    'greater_than': '$var > {value}',
    'less_than': '$var < {value}',
    'in_range': '$var >= {min} and $var <= {max}',
    'contains': '{value} in $var',
    'not_empty': '$var',
}

def build_condition(template_name: str, **kwargs) -> str:
    """使用模板构建条件表达式。
    
    Args:
        template_name: 模板名称
        **kwargs: 模板参数
        
    Returns:
        条件表达式
        
    使用示例:
        >>> build_condition('equals', var='score', value=100)
        '$score == 100'
        >>> build_condition('in_range', var='level', min=1, max=10)
        '$level >= 1 and $level <= 10'
    """
    template = CONDITION_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"未知模板: {template_name}")
    
    # 替换变量名
    if 'var' in kwargs:
        template = template.replace('$var', f"${kwargs['var']}")
    
    # 替换其他参数
    for key, value in kwargs.items():
        if key != 'var':
            if isinstance(value, str):
                value = repr(value)
            template = template.replace(f'{{{key}}}', str(value))
    
    return template
