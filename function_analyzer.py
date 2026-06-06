"""函数调用关系分析工具。

本模块用于分析项目中函数的调用关系，帮助AI理解函数之间的互相调用情况。
"""

import ast
import os
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import json


class FunctionCallAnalyzer:
    """函数调用关系分析器。"""
    
    def __init__(self, root_dir: str):
        """初始化分析器。
        
        Args:
            root_dir: 项目根目录路径
        """
        self.root_dir = root_dir
        self.function_calls: Dict[str, Set[str]] = defaultdict(set)
        self.function_definitions: Dict[str, str] = {}
        self.callers: Dict[str, Set[str]] = defaultdict(set)
        
    def analyze_project(self) -> Dict:
        """分析整个项目的函数调用关系。
        
        Returns:
            包含函数定义和调用关系的字典
        """
        # 遍历所有Python文件
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过缓存目录
            dirs[:] = [d for d in dirs if not d.startswith('__pycache__')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._analyze_file(file_path)
        
        return {
            'functions': dict(self.function_definitions),
            'calls': {k: list(v) for k, v in self.function_calls.items()},
            'callers': {k: list(v) for k, v in self.callers.items()}
        }
    
    def _analyze_file(self, file_path: str):
        """分析单个Python文件。
        
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            analyzer = FunctionVisitor(file_path, self.root_dir)
            analyzer.visit(tree)
            
            # 合并结果
            for func_name, calls in analyzer.function_calls.items():
                self.function_calls[func_name].update(calls)
                for called in calls:
                    self.callers[called].add(func_name)
            
            for func_name, definition in analyzer.function_definitions.items():
                self.function_definitions[func_name] = definition
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def get_function_info(self, function_name: str) -> Dict:
        """获取特定函数的信息。
        
        Args:
            function_name: 函数名称
            
        Returns:
            函数信息字典
        """
        info = {
            'name': function_name,
            'definition': self.function_definitions.get(function_name, ''),
            'calls': list(self.function_calls.get(function_name, set())),
            'called_by': list(self.callers.get(function_name, set()))
        }
        return info
    
    def get_call_chain(self, start_function: str, max_depth: int = 5) -> List[List[str]]:
        """获取从起始函数开始的调用链。
        
        Args:
            start_function: 起始函数名称
            max_depth: 最大递归深度
            
        Returns:
            调用链列表，每个元素是一个函数调用路径
        """
        chains = []
        visited = set()
        
        def dfs(current_func: str, path: List[str], depth: int):
            if depth >= max_depth or current_func in visited:
                if path:
                    chains.append(path.copy())
                return
            
            visited.add(current_func)
            path.append(current_func)
            
            for called_func in self.function_calls.get(current_func, set()):
                dfs(called_func, path, depth + 1)
            
            path.pop()
            visited.remove(current_func)
        
        dfs(start_function, [], 0)
        return chains
    
    def save_analysis(self, output_file: str):
        """保存分析结果到文件。
        
        Args:
            output_file: 输出文件路径
        """
        data = self.analyze_project()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_analysis(self, input_file: str):
        """从文件加载分析结果。
        
        Args:
            input_file: 输入文件路径
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.function_definitions = data.get('functions', {})
        self.function_calls = defaultdict(set, {k: set(v) for k, v in data.get('calls', {}).items()})
        self.callers = defaultdict(set, {k: set(v) for k, v in data.get('callers', {}).items()})


class FunctionVisitor(ast.NodeVisitor):
    """AST访问器，用于提取函数定义和调用。"""
    
    def __init__(self, file_path: str, root_dir: str):
        """初始化访问器。
        
        Args:
            file_path: 当前分析的文件路径
            root_dir: 项目根目录
        """
        self.file_path = file_path
        self.root_dir = root_dir
        self.function_calls: Dict[str, Set[str]] = defaultdict(set)
        self.function_definitions: Dict[str, str] = {}
        self.current_function = None
        self.class_stack = []
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """访问类定义."""
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """访问函数定义."""
        # 构建函数全名
        class_prefix = '.'.join(self.class_stack) if self.class_stack else ''
        if class_prefix:
            func_name = f"{class_prefix}.{node.name}"
        else:
            func_name = node.name
        
        # 保存函数定义
        self.function_definitions[func_name] = ast.get_source_segment(
            open(self.file_path, 'r', encoding='utf-8').read(), node) or f"def {node.name}(...)"
        
        # 进入函数体
        previous_function = self.current_function
        self.current_function = func_name
        self.generic_visit(node)
        self.current_function = previous_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """访问异步函数定义."""
        self.visit_FunctionDef(node)  # 复用同一逻辑
    
    def visit_Call(self, node: ast.Call):
        """访问函数调用."""
        if self.current_function:
            # 提取被调用的函数名
            called_func = self._extract_function_name(node.func)
            if called_func:
                self.function_calls[self.current_function].add(called_func)
        
        self.generic_visit(node)
    
    def _extract_function_name(self, node: ast.AST) -> Optional[str]:
        """从AST节点提取函数名."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # 处理方法调用如 obj.method()
            value_name = self._extract_function_name(node.value)
            if value_name:
                return f"{value_name}.{node.attr}"
            else:
                return node.attr
        elif isinstance(node, ast.Call):
            # 嵌套调用
            return self._extract_function_name(node.func)
        return None


# 便捷函数
def analyze_project(root_dir: str) -> Dict:
    """分析项目并返回函数调用关系。
    
    Args:
        root_dir: 项目根目录
        
    Returns:
        分析结果字典
    """
    analyzer = FunctionCallAnalyzer(root_dir)
    return analyzer.analyze_project()


def get_function_calls(root_dir: str, function_name: str) -> List[str]:
    """获取特定函数调用的函数列表。
    
    Args:
        root_dir: 项目根目录
        function_name: 函数名称
        
    Returns:
        被调用的函数列表
    """
    analyzer = FunctionCallAnalyzer(root_dir)
    analyzer.analyze_project()
    return list(analyzer.function_calls.get(function_name, set()))


def get_function_callers(root_dir: str, function_name: str) -> List[str]:
    """获取调用特定函数的函数列表。
    
    Args:
        root_dir: 项目根目录
        function_name: 函数名称
        
    Returns:
        调用该函数的函数列表
    """
    analyzer = FunctionCallAnalyzer(root_dir)
    analyzer.analyze_project()
    return list(analyzer.callers.get(function_name, set()))


if __name__ == "__main__":
    # 示例用法
    import sys
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "."
    
    print(f"Analyzing project in: {root_dir}")
    result = analyze_project(root_dir)
    
    print(f"Found {len(result['functions'])} functions")
    print(f"Found {sum(len(v) for v in result['calls'].values())} function calls")
    
    # 保存结果
    output_file = os.path.join(root_dir, "function_analysis.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Analysis saved to: {output_file}")