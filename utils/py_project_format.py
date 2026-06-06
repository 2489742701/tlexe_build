"""Python 项目格式序列化/反序列化工具。

将项目数据 dict 转为可直接 exec() 的 Python 源码格式，
替代 JSON (.itexe)，无需转义，可直接运行调试。
"""

import json
import re
from typing import Dict, Any


def dict_to_python_code(data: Dict[str, Any], project_name: str = "") -> str:
    """将项目数据 dict 序列化为可 exec() 的 Python 源码。

    格式：头部注释 + project_data = { ... } 字典字面量。
    字典内容用 repr() 生成，保证 Python 原生可读，无需 JSON 转义。
    """
    lines = [
        '"""',
        f'{project_name or data.get("name", "未命名项目")} - 傻瓜桌面开发工具项目文件',
        '',
        '本文件是项目的原生 Python 格式，可直接运行或用 exec() 加载。',
        '修改后保存即可，无需关心 JSON 转义。',
        '"""',
        '',
        'project_data = \\',
    ]
    dict_str = _dict_to_literal(data, indent=0)
    lines.append(dict_str)
    return '\n'.join(lines)


def python_code_to_dict(code: str) -> Dict[str, Any]:
    """从 Python 源码中提取 project_data 字典。

    支持两种格式：
    1. 新格式：project_data = { ... }
    2. 旧格式：纯 JSON (.itexe 内容)
    """
    exec_error = None
    try:
        local_ns: Dict[str, Any] = {}
        exec(code, {"__builtins__": __builtins__}, local_ns)
        if 'project_data' in local_ns:
            return local_ns['project_data']
        exec_error = "exec 成功但未找到 project_data 变量"
    except Exception as e:
        exec_error = f"exec 失败: {type(e).__name__}: {e}"

    json_error = None
    try:
        return json.loads(code)
    except Exception as e:
        json_error = f"JSON 解析失败: {type(e).__name__}: {e}"

    raise ValueError(
        f"无法从文件内容中提取项目数据\n"
        f"  Python 格式: {exec_error}\n"
        f"  JSON 格式: {json_error}"
    )


def _dict_to_literal(obj: Any, indent: int = 0) -> str:
    """递归将 Python 对象转为格式化的字典字面量字符串。"""
    prefix = "    " * indent
    inner = "    " * (indent + 1)

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            val_str = _dict_to_literal(v, indent + 1)
            items.append(f"{inner}{k!r}: {val_str}")
        return "{\n" + ",\n".join(items) + f",\n{prefix}}}"

    if isinstance(obj, list):
        if not obj:
            return "[]"
        if _is_simple_list(obj):
            return "[" + ", ".join(_simple_repr(item) for item in obj) + "]"
        items = []
        for item in obj:
            val_str = _dict_to_literal(item, indent + 1)
            items.append(f"{inner}{val_str}")
        return "[\n" + ",\n".join(items) + f",\n{prefix}]"

    return _simple_repr(obj)


def _is_simple_list(lst: list) -> bool:
    """判断列表是否足够简单可以写在一行。"""
    if len(lst) > 6:
        return False
    for item in lst:
        if isinstance(item, (dict, list)):
            return False
        if isinstance(item, str) and len(item) > 30:
            return False
    return True


def _simple_repr(obj: Any) -> str:
    """简单值的 repr，对中文友好。"""
    if isinstance(obj, str):
        return repr(obj)
    if isinstance(obj, bool):
        return repr(obj)
    if obj is None:
        return "None"
    return repr(obj)


def is_python_project_file(file_path: str) -> bool:
    """判断文件是否为 Python 项目格式。"""
    return file_path.endswith('.py')


def is_itexe_project_file(file_path: str) -> bool:
    """判断文件是否为旧 JSON 格式。"""
    return file_path.endswith('.itexe')
