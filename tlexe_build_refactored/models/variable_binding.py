"""变量绑定模块。

BindingConfig/ConditionalActionConfig 使用 Pydantic，自动序列化。
VariableBinding/BindingManager 保留 QObject + Signal。
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from .schemas import BindingConfig, ConditionalActionConfig

if TYPE_CHECKING:
    from .variable_system import VariableManager
    from .base import ComponentModel

from utils.safe_expression import SafeExpressionEvaluator

class VariableBinding(QObject):
    """变量绑定 - 建立变量和组件属性的联系。"""

    binding_triggered = Signal(str, str, object)
    binding_error = Signal(str, str, str)

    def __init__(self, variable_manager: 'VariableManager',
                 var_name: str, component_model: 'ComponentModel',
                 property_name: str = "text",
                 bidirectional: bool = False,
                 parent=None):
        super().__init__(parent)
        self._var_manager = variable_manager
        self._var_name = var_name
        self._component = component_model
        self._property_name = property_name
        self._bidirectional = bidirectional
        self._active = True
        self._updating = False
        self._var_manager.variable_changed.connect(self._on_variable_changed)
        if self._bidirectional:
            self._component.data_changed.connect(self._on_component_changed)
        current_value = self._var_manager.get_variable(self._var_name)
        if current_value is not None:
            self._apply_to_component(current_value)

    @property
    def var_name(self) -> str:
        return self._var_name

    @property
    def component_id(self) -> str:
        return self._component.id

    @property
    def property_name(self) -> str:
        return self._property_name

    @property
    def bidirectional(self) -> bool:
        return self._bidirectional

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value

    def _on_variable_changed(self, name: str, new_value: Any) -> None:
        if not self._active or name != self._var_name:
            return
        self._apply_to_component(new_value)

    def _on_component_changed(self) -> None:
        if not self._active or not self._bidirectional or self._updating:
            return
        new_value = getattr(self._component, self._property_name, None)
        if new_value is not None:
            self._updating = True
            try:
                self._var_manager.set_variable(self._var_name, new_value)
                self.binding_triggered.emit(self._var_name, self._component.id, new_value)
            except Exception as e:
                self.binding_error.emit(self._var_name, self._component.id, str(e))
            finally:
                self._updating = False

    def _apply_to_component(self, value: Any) -> None:
        self._updating = True
        try:
            if hasattr(self._component, self._property_name):
                setattr(self._component, self._property_name, value)
                self.binding_triggered.emit(self._var_name, self._component.id, value)
        except Exception as e:
            self.binding_error.emit(self._var_name, self._component.id, str(e))
        finally:
            self._updating = False

    def disconnect(self) -> None:
        self._active = False
        try:
            self._var_manager.variable_changed.disconnect(self._on_variable_changed)
        except TypeError:
            pass
        if self._bidirectional:
            try:
                self._component.data_changed.disconnect(self._on_component_changed)
            except TypeError:
                pass

    def to_config(self) -> BindingConfig:
        return BindingConfig(
            component_id=self._component.id,
            variable_name=self._var_name,
            component_property=self._property_name,
            bidirectional=self._bidirectional,
        )

class BindingManager(QObject):
    """绑定管理器。"""

    binding_added = Signal(str, str)
    binding_removed = Signal(str, str)
    conditional_action_added = Signal(str)

    def __init__(self, variable_manager: 'VariableManager', parent=None):
        super().__init__(parent)
        self._var_manager = variable_manager
        self._bindings: Dict[str, VariableBinding] = {}
        self._conditional_actions: List[ConditionalActionConfig] = []
        self._evaluator = SafeExpressionEvaluator()

    def add_binding(self, component_model: 'ComponentModel',
                    var_name: str, property_name: str = "text",
                    bidirectional: bool = False) -> VariableBinding:
        key = f"{component_model.id}:{var_name}:{property_name}"
        if key in self._bindings:
            return self._bindings[key]
        binding = VariableBinding(
            variable_manager=self._var_manager,
            var_name=var_name, component_model=component_model,
            property_name=property_name, bidirectional=bidirectional,
        )
        self._bindings[key] = binding
        self.binding_added.emit(var_name, component_model.id)
        return binding

    def remove_binding(self, component_id: str, var_name: str, property_name: str = "text") -> None:
        key = f"{component_id}:{var_name}:{property_name}"
        if key in self._bindings:
            self._bindings[key].disconnect()
            del self._bindings[key]
            self.binding_removed.emit(var_name, component_id)

    def remove_bindings_for_component(self, component_id: str) -> None:
        keys_to_remove = [k for k in self._bindings if k.startswith(f"{component_id}:")]
        for key in keys_to_remove:
            self._bindings[key].disconnect()
            del self._bindings[key]

    def remove_bindings_for_variable(self, var_name: str) -> None:
        keys_to_remove = [k for k in self._bindings if f":{var_name}:" in k]
        for key in keys_to_remove:
            self._bindings[key].disconnect()
            del self._bindings[key]

    def add_conditional_action(self, condition: str,
                                true_action: Dict[str, Any],
                                false_action: Dict[str, Any] = None) -> ConditionalActionConfig:
        config = ConditionalActionConfig(condition=condition, true_action=true_action, false_action=false_action or {})
        self._conditional_actions.append(config)
        self.conditional_action_added.emit(condition)
        return config

    def evaluate_condition(self, condition: str) -> bool:
        context = {var.name: var.value for var in self._var_manager.get_all_variables()}
        return self._evaluator.evaluate(condition, context)

    def execute_conditional_actions(self) -> None:
        for action_config in self._conditional_actions:
            try:
                if self.evaluate_condition(action_config.condition):
                    self._execute_action(action_config.true_action)
                elif action_config.false_action:
                    self._execute_action(action_config.false_action)
            except Exception:
                pass

    def _execute_action(self, action: Dict[str, Any]) -> None:
        action_type = action.get("action_type", "none")
        if action_type == "set_variable":
            var_name = action.get("variable_name", "")
            var_value = action.get("variable_value")
            if var_name:
                self._var_manager.set_variable(var_name, var_value)

    def get_all_bindings(self) -> List[VariableBinding]:
        return list(self._bindings.values())

    def get_bindings_for_component(self, component_id: str) -> List[VariableBinding]:
        return [b for b in self._bindings.values() if b.component_id == component_id]

    def get_bindings_for_variable(self, var_name: str) -> List[VariableBinding]:
        return [b for b in self._bindings.values() if b.var_name == var_name]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bindings": [b.to_config().model_dump() for b in self._bindings.values()],
            "conditional_actions": [a.model_dump() for a in self._conditional_actions],
        }

    def from_dict(self, data: Dict[str, Any], component_lookup: Dict[str, 'ComponentModel']) -> None:
        for key in list(self._bindings.keys()):
            self._bindings[key].disconnect()
        self._bindings.clear()
        self._conditional_actions.clear()
        for binding_data in data.get("bindings", []):
            config = BindingConfig.model_validate(binding_data)
            component = component_lookup.get(config.component_id)
            if component:
                self.add_binding(component_model=component, var_name=config.variable_name,
                                property_name=config.component_property, bidirectional=config.bidirectional)
        for action_data in data.get("conditional_actions", []):
            config = ConditionalActionConfig.model_validate(action_data)
            self._conditional_actions.append(config)

    def clear(self) -> None:
        for key in list(self._bindings.keys()):
            self._bindings[key].disconnect()
        self._bindings.clear()
        self._conditional_actions.clear()
