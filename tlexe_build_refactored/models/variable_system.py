"""变量系统模块。

Variable 使用 Pydantic VariableSchema，自动获得序列化/验证。
VariableManager 保留 QObject + Signal 用于通知。
"""

from typing import Dict, Any, List, Optional
from PySide6.QtCore import QObject, Signal

from .schemas import VariableSchema, VariableType

class VariableManager(QObject):
    """变量管理器。"""

    variable_changed = Signal(str, object)
    variable_added = Signal(str)
    variable_removed = Signal(str)
    match_success = Signal(str, object)
    match_failed = Signal(str, object)

    def __init__(self):
        super().__init__()
        self._variables: Dict[str, VariableSchema] = {}

    def set_variable(self, name: str, value: Any, var_type: VariableType = VariableType.TEXT,
                      description: str = "", min_value: Optional[float] = None,
                      max_value: Optional[float] = None) -> None:
        is_new = name not in self._variables
        self._variables[name] = VariableSchema(
            name=name, value=value, var_type=var_type,
            description=description, min_value=min_value, max_value=max_value,
        )
        if is_new:
            self.variable_added.emit(name)
        else:
            self.variable_changed.emit(name, value)

    def get_variable(self, name: str, default: Any = None) -> Any:
        if name in self._variables:
            return self._variables[name].value
        return default

    def get_variable_info(self, name: str) -> Optional[VariableSchema]:
        return self._variables.get(name)

    def remove_variable(self, name: str) -> bool:
        if name in self._variables:
            del self._variables[name]
            self.variable_removed.emit(name)
            return True
        return False

    def has_variable(self, name: str) -> bool:
        return name in self._variables

    def get_all_variables(self) -> List[VariableSchema]:
        return list(self._variables.values())

    def get_variables_by_type(self, var_type: VariableType) -> List[VariableSchema]:
        return [v for v in self._variables.values() if v.var_type == var_type]

    def match_variable(self, name: str, value: Any) -> bool:
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
        if name not in self._variables:
            return False
        var = self._variables[name]
        if var.var_type != VariableType.ARRAY:
            return False
        var.value = []
        self.variable_changed.emit(name, var.value)
        return True

    def reset_all(self) -> None:
        for var in self._variables.values():
            var.reset()
            self.variable_changed.emit(var.name, var.value)

    def to_dict(self) -> Dict[str, Any]:
        return {"variables": [v.model_dump() for v in self._variables.values()]}

    def from_dict(self, data: Dict[str, Any]) -> None:
        self._variables.clear()
        for var_data in data.get("variables", []):
            var_data_copy = dict(var_data)
            if "var_type" in var_data_copy:
                try:
                    var_data_copy["var_type"] = VariableType(var_data_copy["var_type"])
                except ValueError:
                    var_data_copy["var_type"] = VariableType.TEXT
            var = VariableSchema.model_validate(var_data_copy)
            self._variables[var.name] = var

_variable_manager_instance: Optional[VariableManager] = None

def get_variable_manager() -> VariableManager:
    global _variable_manager_instance
    if _variable_manager_instance is None:
        _variable_manager_instance = VariableManager()
    return _variable_manager_instance
