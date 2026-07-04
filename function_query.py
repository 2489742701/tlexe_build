"""函数查询工具。

提供简单的接口来查询函数的调用关系，便于AI理解函数之间的互相调用情况。
"""

import json
import os
import time
from typing import Dict, List, Optional, Set, Tuple
from functools import lru_cache


class FunctionQuery:
    """函数查询工具类。"""
    
    def __init__(self, analysis_file: str = None):
        """初始化查询工具。
        
        Args:
            analysis_file: 函数分析结果文件路径，如果为None则自动查找
        """
        if analysis_file is None:
            # 自动查找分析文件
            analysis_file = self._find_analysis_file()
        
        self.data = self._load_analysis(analysis_file)
        self.functions = self.data.get('functions', {})
        self.calls = self.data.get('calls', {})
        self.callers = self.data.get('callers', {})
        
        # 缓存相关属性
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 缓存生存时间（秒）
        
        # 快照文本缓存
        self._snapshot_cache = None
        self._snapshot_timestamp = 0
    
    def _find_analysis_file(self) -> str:
        """自动查找函数分析文件."""
        # 先检查当前目录
        if os.path.exists("function_analysis.json"):
            return "function_analysis.json"
        
        # 检查tlexe_build目录
        if os.path.exists("tlexe_build/function_analysis.json"):
            return "tlexe_build/function_analysis.json"
        
        # 递归查找
        for root, dirs, files in os.walk("."):
            # 跳过缓存目录
            dirs[:] = [d for d in dirs if not d.startswith('__pycache__')]
            
            if "function_analysis.json" in files:
                return os.path.join(root, "function_analysis.json")
        
        # 如果找不到，返回默认路径
        return "function_analysis.json"
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效."""
        if key not in self._cache:
            return False
        
        timestamp = self._cache_timestamps.get(key, 0)
        return (time.time() - timestamp) < self._cache_ttl
    
    def _get_from_cache(self, key: str):
        """从缓存获取值."""
        if self._is_cache_valid(key):
            return self._cache[key]
        return None
    
    def _save_to_cache(self, key: str, value):
        """保存值到缓存."""
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()
    
    def _load_analysis(self, file_path: str) -> Dict:
        """加载函数分析结果."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Analysis file {file_path} not found. Returning empty data.")
            return {'functions': {}, 'calls': {}, 'callers': {}}
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse {file_path}: {e}")
            return {'functions': {}, 'calls': {}, 'callers': {}}
    
    def get_function_info(self, function_name: str) -> Dict:
        """获取函数的完整信息。
        
        Args:
            function_name: 函数名称
            
        Returns:
            包含函数定义、调用的函数、被哪些函数调用的信息
        """
        cache_key = f"func_info_{function_name}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = {
            'name': function_name,
            'definition': self.functions.get(function_name, ''),
            'calls': list(self.calls.get(function_name, set())),
            'called_by': list(self.callers.get(function_name, set()))
        }
        
        self._save_to_cache(cache_key, result)
        return result
    
    def get_called_functions(self, function_name: str) -> List[str]:
        """获取指定函数调用的所有函数。
        
        Args:
            function_name: 函数名称
            
        Returns:
            被调用的函数列表
        """
        cache_key = f"called_funcs_{function_name}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = list(self.calls.get(function_name, set()))
        self._save_to_cache(cache_key, result)
        return result
    
    def get_caller_functions(self, function_name: str) -> List[str]:
        """获取调用指定函数的所有函数。
        
        Args:
            function_name: 函数名称
            
        Returns:
            调用该函数的函数列表
        """
        cache_key = f"caller_funcs_{function_name}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = list(self.callers.get(function_name, set()))
        self._save_to_cache(cache_key, result)
        return result
    
    def function_exists(self, function_name: str) -> bool:
        """检查函数是否存在。
        
        Args:
            function_name: 函数名称
            
        Returns:
            函数是否存在
        """
        cache_key = f"func_exists_{function_name}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = function_name in self.functions
        self._save_to_cache(cache_key, result)
        return result
    
    def list_all_functions(self) -> List[str]:
        """列出所有函数。
        
        Returns:
            所有函数名称列表
        """
        cache_key = "list_all_functions"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = list(self.functions.keys())
        self._save_to_cache(cache_key, result)
        return result
    
    def get_snapshot_text(self, max_functions: int = 50) -> str:
        """获取函数调用关系的快照文本。
        
        Args:
            max_functions: 最大显示函数数量
            
        Returns:
            函数调用关系的文本快照
        """
        cache_key = f"snapshot_{max_functions}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 生成快照文本
        lines = []
        lines.append("=" * 60)
        lines.append("函数调用关系快照")
        lines.append("=" * 60)
        lines.append(f"总函数数量: {len(self.functions)}")
        lines.append(f"总调用关系数量: {sum(len(v) for v in self.calls.values())}")
        lines.append("")
        
        # 按调用数量排序函数
        sorted_functions = sorted(
            self.functions.keys(), 
            key=lambda x: len(self.calls.get(x, set())), 
            reverse=True
        )
        
        lines.append(f"前 {min(max_functions, len(sorted_functions))} 个最活跃的函数 (按调用数量):")
        lines.append("-" * 60)
        
        for i, func_name in enumerate(sorted_functions[:max_functions]):
            calls = self.calls.get(func_name, set())
            callers = self.callers.get(func_name, set())
            definition = self.functions.get(func_name, "")
            
            # 获取函数名（去除类前缀）
            simple_name = func_name.split('.')[-1] if '.' in func_name else func_name
            
            lines.append(f"{i+1:3d}. {simple_name}")
            lines.append(f"     调用: {len(calls)} 个函数")
            lines.append(f"     被调用: {len(callers)} 个函数")
            
            # 显示函数定义的第一行
            if definition:
                first_line = definition.split('\n')[0].strip()
                if len(first_line) > 80:
                    first_line = first_line[:77] + "..."
                lines.append(f"     定义: {first_line}")
            
            # 显示被调用的函数（前3个）
            if calls:
                called_list = list(calls)[:3]
                called_str = ", ".join(called_list)
                if len(calls) > 3:
                    called_str += f" 等共{len(calls)}个"
                lines.append(f"     调用函数: {called_str}")
            
            lines.append("")
        
        # 添加一些统计信息
        lines.append("-" * 60)
        lines.append("统计信息:")
        lines.append(f"  未被调用的函数: {sum(1 for v in self.calls.values() if len(v) == 0)}")
        lines.append(f"  不调用其他函数: {sum(1 for k in self.functions.keys() if len(self.calls.get(k, set())) == 0)}")
        
        # 查找最被调用的函数
        if self.callers:
            most_called = max(self.callers.items(), key=lambda x: len(x[1]))
            lines.append(f"  最被调用的函数: {most_called[0]} ({len(most_called[1])} 次)")
        
        lines.append("=" * 60)
        
        result = "\n".join(lines)
        self._save_to_cache(cache_key, result)
        return result
    
    def get_function_summary(self, function_name: str) -> str:
        """获取单个函数的详细摘要。
        
        Args:
            function_name: 函数名称
            
        Returns:
            函数的详细摘要文本
        """
        cache_key = f"summary_{function_name}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        if not self.function_exists(function_name):
            result = f"函数 '{function_name}' 不存在"
            self._save_to_cache(cache_key, result)
            return result
        
        info = self.get_function_info(function_name)
        lines = []
        lines.append("=" * 60)
        lines.append(f"函数详细信息: {info['name']}")
        lines.append("=" * 60)
        lines.append("")
        
        # 函数定义
        lines.append("函数定义:")
        lines.append("-" * 40)
        definition_lines = info['definition'].split('\n')
        for line in definition_lines[:10]:  # 只显示前10行
            lines.append(line)
        if len(definition_lines) > 10:
            lines.append(f"... 还有 {len(definition_lines) - 10} 行")
        lines.append("")
        
        # 被调用的函数
        lines.append(f"调用的函数 ({len(info['calls'])}):")
        lines.append("-" * 40)
        if info['calls']:
            for i, called in enumerate(sorted(info['calls'])[:20]):
                lines.append(f"  {i+1:2d}. {called}")
            if len(info['calls']) > 20:
                lines.append(f"  ... 还有 {len(info['calls']) - 20} 个函数")
        else:
            lines.append("  (无)")
        lines.append("")
        
        # 调用该函数的函数
        lines.append(f"被以下函数调用 ({len(info['called_by'])}):")
        lines.append("-" * 40)
        if info['called_by']:
            for i, caller in enumerate(sorted(info['called_by'])[:20]):
                lines.append(f"  {i+1:2d}. {caller}")
            if len(info['called_by']) > 20:
                lines.append(f"  ... 还有 {len(info['called_by']) - 20} 个函数")
        else:
            lines.append("  (无)")
        lines.append("")
        
        lines.append("=" * 60)
        
        result = "\n".join(lines)
        self._save_to_cache(cache_key, result)
        return result
    
    def search_functions(self, keyword: str) -> List[str]:
        """搜索包含关键词的函数。
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            包含关键词的函数列表
        """
        keyword = keyword.lower()
        return [name for name in self.functions.keys() if keyword in name.lower()]
    
    def get_call_chain(self, start_function: str, max_depth: int = 3) -> List[List[str]]:
        """获取从起始函数开始的调用链（简化版）。
        
        Args:
            start_function: 起始函数名称
            max_depth: 最大递归深度
            
        Returns:
            调用链列表
        """
        if not self.function_exists(start_function):
            return []
        
        chains = []
        visited = set()
        
        def dfs(current_func: str, path: List[str], depth: int):
            if depth >= max_depth or current_func in visited:
                if len(path) > 1:  # 至少包含起始函数和一个被调用函数
                    chains.append(path.copy())
                return
            
            visited.add(current_func)
            path.append(current_func)
            
            for called_func in self.calls.get(current_func, set()):
                if self.function_exists(called_func):  # 只跟踪存在的函数
                    dfs(called_func, path, depth + 1)
            
            path.pop()
            visited.remove(current_func)
        
        dfs(start_function, [], 0)
        return chains
    
    def print_function_info(self, function_name: str):
        """打印函数信息（便于调试）."""
        info = self.get_function_info(function_name)
        
        print(f"函数: {info['name']}")
        print(f"定义: {info['definition'][:100]}{'...' if len(info['definition']) > 100 else ''}")
        print(f"调用的函数 ({len(info['calls'])}): {', '.join(info['calls'][:5])}{'...' if len(info['calls']) > 5 else ''}")
        print(f"被以下函数调用 ({len(info['called_by'])}): {', '.join(info['called_by'][:5])}{'...' if len(info['called_by']) > 5 else ''}")
        print("-" * 50)


# 便捷函数
def query_function(function_name: str, analysis_file: str = None) -> Dict:
    """查询单个函数的信息。
    
    Args:
        function_name: 函数名称
        analysis_file: 分析文件路径（可选）
        
    Returns:
        函数信息字典
    """
    query = FunctionQuery(analysis_file)
    return query.get_function_info(function_name)


def get_called_functions(function_name: str, analysis_file: str = None) -> List[str]:
    """获取指定函数调用的所有函数。
    
    Args:
        function_name: 函数名称
        analysis_file: 分析文件路径（可选）
        
    Returns:
        被调用的函数列表
    """
    query = FunctionQuery(analysis_file)
    return query.get_called_functions(function_name)


def get_caller_functions(function_name: str, analysis_file: str = None) -> List[str]:
    """获取调用指定函数的所有函数。
    
    Args:
        function_name: 函数名称
        analysis_file: 分析文件路径（可选）
        
    Returns:
        调用该函数的函数列表
    """
    query = FunctionQuery(analysis_file)
    return query.get_caller_functions(function_name)


if __name__ == "__main__":
    # 示例用法
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python function_query.py <函数名> [分析文件路径] [--snapshot]")
        print("示例: python function_query.py main")
        print("      python function_query.py --snapshot  # 显示快照")
        sys.exit(1)
    
    # 检查是否请求快照
    if sys.argv[1] == "--snapshot":
        analysis_file = sys.argv[2] if len(sys.argv) > 2 else None
        query = FunctionQuery(analysis_file)
        print(query.get_snapshot_text())
        sys.exit(0)
    
    function_name = sys.argv[1]
    analysis_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    query = FunctionQuery(analysis_file)
    query.print_function_info(function_name)