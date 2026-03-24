"""变量系统模块。

本模块实现傻瓜模式的变量管理系统，让用户可以：
1. 定义名字（玩家名、物品名、人物名等）
2. 定义数字（伤害值、血量、密码等）
3. 定义数组（存储多个值）

设计原则：
- 简单易懂：用户无需编程知识即可使用
- 可视化：通过界面操作，无需手写代码
- 配对功能：输入框可以读取/验证变量值
- 通信功能：组件间可以传递信号

使用示例：
    # 创建变量管理器
    var_manager = VariableManager()
    
    # 定义变量
    var_manager.set_variable("玩家名", "张三", VariableType.NAME)
    var_manager.set_variable("血量", 100, VariableType.NUMBER)
    var_manager.set_variable("密码", "123456", VariableType.PASSWORD)
    
    # 获取变量
    name = var_manager.get_variable("玩家名")
    
    # 配对验证
    is_match = var_manager.match_variable("密码", "123456")
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal


class VariableType(Enum):
    """变量类型枚举。
    
    定义变量可以存储的数据类型，方便用户理解和使用。
    
    类型说明：
    - NAME: 名字类型，用于存储玩家名、物品名、人物名等
    - NUMBER: 数字类型，用于存储伤害值、血量、分数等
    - PASSWORD: 密码类型，用于存储需要验证的密码
    - TEXT: 文本类型，用于存储对话、描述等长文本
    - ARRAY: 数组类型，用于存储多个值（如物品列表）
    - BOOLEAN: 布尔类型，用于存储开关状态（是/否）
    """
    NAME = "名字"          # 名字：玩家名、物品名、人物名
    NUMBER = "数字"        # 数字：伤害值、血量、分数
    PASSWORD = "密码"      # 密码：需要验证的密码
    TEXT = "文本"          # 文本：对话、描述、记录
    ARRAY = "数组"         # 数组：物品列表、选项列表
    BOOLEAN = "开关"       # 开关：是/否、开/关


@dataclass
class Variable:
    """变量数据类。
    
    存储单个变量的所有信息。
    
    Attributes:
        name: 变量名称（如"玩家名"、"血量"）
        value: 变量值
        var_type: 变量类型
        description: 变量描述（帮助用户理解用途）
        default_value: 默认值（重置时使用）
        min_value: 最小值（仅数字类型有效）
        max_value: 最大值（仅数字类型有效）
    """
    name: str
    value: Any
    var_type: VariableType
    description: str = ""
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    def __post_init__(self):
        if self.default_value is None:
            self.default_value = self.value
    
    def reset(self):
        """重置变量为默认值。"""
        self.value = self.default_value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于保存）。"""
        return {
            "name": self.name,
            "value": self.value,
            "var_type": self.var_type.value,
            "description": self.description,
            "default_value": self.default_value,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Variable':
        """从字典创建变量。"""
        var_type = VariableType(data.get("var_type", "文本"))
        return cls(
            name=data.get("name", ""),
            value=data.get("value"),
            var_type=var_type,
            description=data.get("description", ""),
            default_value=data.get("default_value"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
        )


class VariableManager(QObject):
    """变量管理器。
    
    管理项目中的所有变量，提供变量的增删改查、配对验证等功能。
    
    功能说明：
    1. 变量管理：创建、读取、更新、删除变量
    2. 配对验证：检查输入值是否与变量匹配
    3. 信号通知：变量变化时发出信号，通知相关组件更新
    
    Signals:
        variable_changed: 变量值改变时发射 (name, new_value)
        variable_added: 新变量添加时发射 (name)
        variable_removed: 变量删除时发射 (name)
        match_success: 配对成功时发射 (name, input_value)
        match_failed: 配对失败时发射 (name, input_value)
    
    使用示例：
        manager = VariableManager()
        
        # 设置变量
        manager.set_variable("玩家名", "李四", VariableType.NAME, "玩家的角色名")
        
        # 获取变量
        name = manager.get_variable("玩家名")
        
        # 配对验证
        if manager.match_variable("密码", user_input):
            print("密码正确！")
    """
    
    variable_changed = Signal(str, object)
    variable_added = Signal(str)
    variable_removed = Signal(str)
    match_success = Signal(str, object)
    match_failed = Signal(str, object)
    
    def __init__(self):
        super().__init__()
        self._variables: Dict[str, Variable] = {}
    
    def set_variable(self, name: str, value: Any, var_type: VariableType = VariableType.TEXT,
                     description: str = "", min_value: Optional[float] = None,
                     max_value: Optional[float] = None) -> None:
        """设置变量值。
        
        如果变量不存在则创建，存在则更新值。
        
        Args:
            name: 变量名称
            value: 变量值
            var_type: 变量类型（默认为文本）
            description: 变量描述
            min_value: 最小值（仅数字类型有效）
            max_value: 最大值（仅数字类型有效）
        
        使用示例：
            manager.set_variable("玩家名", "张三", VariableType.NAME, "玩家的角色名")
            manager.set_variable("血量", 100, VariableType.NUMBER, "玩家当前血量", 0, 999)
        """
        is_new = name not in self._variables
        
        self._variables[name] = Variable(
            name=name,
            value=value,
            var_type=var_type,
            description=description,
            min_value=min_value,
            max_value=max_value,
        )
        
        if is_new:
            self.variable_added.emit(name)
        else:
            self.variable_changed.emit(name, value)
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """获取变量值。
        
        Args:
            name: 变量名称
            default: 变量不存在时的默认返回值
        
        Returns:
            变量值，如果变量不存在则返回 default
        
        使用示例：
            name = manager.get_variable("玩家名", "未知玩家")
        """
        if name in self._variables:
            return self._variables[name].value
        return default
    
    def get_variable_info(self, name: str) -> Optional[Variable]:
        """获取变量完整信息。
        
        Args:
            name: 变量名称
        
        Returns:
            Variable 对象，如果不存在则返回 None
        """
        return self._variables.get(name)
    
    def remove_variable(self, name: str) -> bool:
        """删除变量。
        
        Args:
            name: 变量名称
        
        Returns:
            是否删除成功
        """
        if name in self._variables:
            del self._variables[name]
            self.variable_removed.emit(name)
            return True
        return False
    
    def has_variable(self, name: str) -> bool:
        """检查变量是否存在。"""
        return name in self._variables
    
    def get_all_variables(self) -> List[Variable]:
        """获取所有变量列表。"""
        return list(self._variables.values())
    
    def get_variables_by_type(self, var_type: VariableType) -> List[Variable]:
        """获取指定类型的所有变量。"""
        return [v for v in self._variables.values() if v.var_type == var_type]
    
    def match_variable(self, name: str, value: Any) -> bool:
        """配对验证。
        
        检查输入值是否与变量值匹配。用于密码验证、答案检查等场景。
        
        Args:
            name: 变量名称
            value: 要验证的值
        
        Returns:
            是否匹配成功
        
        使用示例：
            # 验证密码
            if manager.match_variable("密码", user_input):
                print("密码正确！")
            else:
                print("密码错误！")
        """
        if name not in self._variables:
            return False
        
        stored_value = self._variables[name].value
        
        is_match = str(stored_value) == str(value)
        
        if is_match:
            self.match_success.emit(name, value)
        else:
            self.match_failed.emit(name, value)
        
        return is_match
    
    def match_variable_partial(self, name: str, value: Any) -> bool:
        """部分匹配验证。
        
        检查输入值是否包含在变量值中（不区分大小写）。
        用于模糊搜索、关键词匹配等场景。
        """
        if name not in self._variables:
            return False
        
        stored_value = str(self._variables[name].value).lower()
        check_value = str(value).lower()
        
        is_match = check_value in stored_value or stored_value in check_value
        
        if is_match:
            self.match_success.emit(name, value)
        else:
            self.match_failed.emit(name, value)
        
        return is_match
    
    def increment(self, name: str, amount: int = 1) -> bool:
        """增加数字变量的值。
        
        用于血量增加、分数累加等场景。
        
        Args:
            name: 变量名称
            amount: 增加的数量（默认为1）
        
        Returns:
            是否操作成功
        """
        if name not in self._variables:
            return False
        
        var = self._variables[name]
        if var.var_type != VariableType.NUMBER:
            return False
        
        new_value = var.value + amount
        
        if var.max_value is not None:
            new_value = min(new_value, var.max_value)
        
        var.value = new_value
        self.variable_changed.emit(name, new_value)
        return True
    
    def decrement(self, name: str, amount: int = 1) -> bool:
        """减少数字变量的值。
        
        用于血量减少、分数扣除等场景。
        
        Args:
            name: 变量名称
            amount: 减少的数量（默认为1）
        
        Returns:
            是否操作成功
        """
        if name not in self._variables:
            return False
        
        var = self._variables[name]
        if var.var_type != VariableType.NUMBER:
            return False
        
        new_value = var.value - amount
        
        if var.min_value is not None:
            new_value = max(new_value, var.min_value)
        
        var.value = new_value
        self.variable_changed.emit(name, new_value)
        return True
    
    def append_to_array(self, name: str, value: Any) -> bool:
        """向数组变量追加元素。
        
        用于收集物品、记录对话等场景。
        
        Args:
            name: 变量名称
            value: 要追加的值
        
        Returns:
            是否操作成功
        """
        if name not in self._variables:
            return False
        
        var = self._variables[name]
        if var.var_type != VariableType.ARRAY:
            return False
        
        if not isinstance(var.value, list):
            var.value = []
        
        var.value.append(value)
        self.variable_changed.emit(name, var.value)
        return True
    
    def clear_array(self, name: str) -> bool:
        """清空数组变量。
        
        用于重置物品列表、清空记录等场景。
        """
        if name not in self._variables:
            return False
        
        var = self._variables[name]
        if var.var_type != VariableType.ARRAY:
            return False
        
        var.value = []
        self.variable_changed.emit(name, var.value)
        return True
    
    def reset_all(self):
        """重置所有变量为默认值。"""
        for var in self._variables.values():
            var.reset()
            self.variable_changed.emit(var.name, var.value)
    
    def to_dict(self) -> Dict[str, Any]:
        """导出所有变量为字典（用于保存项目）。"""
        return {
            "variables": [v.to_dict() for v in self._variables.values()]
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载变量（用于加载项目）。"""
        self._variables.clear()
        for var_data in data.get("variables", []):
            var = Variable.from_dict(var_data)
            self._variables[var.name] = var


_variable_manager_instance: Optional[VariableManager] = None


def get_variable_manager() -> VariableManager:
    """获取全局变量管理器实例。"""
    global _variable_manager_instance
    if _variable_manager_instance is None:
        _variable_manager_instance = VariableManager()
    return _variable_manager_instance
