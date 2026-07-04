"""动作节点模块。

本模块实现动作链结构，支持条件分支、循环、序列执行等复杂动作流程。

## 设计理念
采用组合模式（Composite Pattern），将单个动作和动作组合统一抽象为 ActionNode，
支持任意嵌套和组合。

## 支持的动作节点类型
- SimpleAction: 简单动作，执行单一操作
- SequenceAction: 序列动作，依次执行多个动作
- ConditionalAction: 条件动作，if/else 分支
- LoopAction: 循环动作，重复执行
- DelayAction: 延迟动作，等待指定时间
- ParallelAction: 并行动作，同时执行多个动作

## 使用示例
    action_chain = SequenceAction([
        SimpleAction("show_message", {"message": "验证中..."}),
        DelayAction(1000),
        ConditionalAction(
            condition="$密码 == '123456'",
            true_action=SimpleAction("show_component", {"target": "label_success"}),
            false_action=SimpleAction("show_message", {"message": "密码错误！"})
        )
    ])
    
    executor = ActionExecutor(project_model)
    action_chain.execute(executor, var_manager)
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from PySide6.QtCore import QObject

if TYPE_CHECKING:
    from runtime.action_executor import ActionExecutor
    from models.variable_system import VariableManager

from utils.safe_expression import SafeExpressionEvaluator

class ActionNode(ABC):
    """动作节点基类 - 所有动作节点的抽象基类。"""

    @abstractmethod
    def execute(self, executor: 'ActionExecutor', var_manager: 'VariableManager' = None) -> bool:
        """执行动作节点。

        Args:
            executor: 动作执行器
            var_manager: 变量管理器（条件动作需要）

        Returns:
            执行是否成功
        """
        ...

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionNode':
        """从字典反序列化动作节点。"""
        node_type = data.get("type", "simple")

        if node_type == "simple":
            return SimpleAction(
                action_type=data.get("action_type", "none"),
                params=data.get("params", {}),
            )
        elif node_type == "sequence":
            actions = [ActionNode.from_dict(a) for a in data.get("actions", [])]
            return SequenceAction(actions)
        elif node_type == "conditional":
            true_action = None
            false_action = None
            if data.get("true_action"):
                true_action = ActionNode.from_dict(data["true_action"])
            if data.get("false_action"):
                false_action = ActionNode.from_dict(data["false_action"])
            return ConditionalAction(
                condition=data.get("condition", ""),
                true_action=true_action,
                false_action=false_action,
            )
        elif node_type == "loop":
            action = None
            if data.get("action"):
                action = ActionNode.from_dict(data["action"])
            return LoopAction(
                times=data.get("times"),
                action=action,
                condition=data.get("condition"),
            )
        elif node_type == "delay":
            return DelayAction(milliseconds=data.get("milliseconds", 1000))
        elif node_type == "parallel":
            actions = [ActionNode.from_dict(a) for a in data.get("actions", [])]
            return ParallelAction(actions)
        else:
            return SimpleAction(action_type="none")

class SimpleAction(ActionNode):
    """简单动作 - 执行单一操作。"""

    def __init__(self, action_type: str, params: Dict[str, Any] = None):
        self.action_type = action_type
        self.params = params or {}

    def execute(self, executor: 'ActionExecutor', var_manager: 'VariableManager' = None) -> bool:
        from models.schemas import ActionConfig
        action_config = ActionConfig(
            action_type=self.action_type,
            params=self.params,
        )
        return executor.execute(action_config)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "simple",
            "action_type": self.action_type,
            "params": self.params,
        }

class SequenceAction(ActionNode):
    """序列动作 - 依次执行多个动作，任一失败则停止。"""

    def __init__(self, actions: List[ActionNode] = None):
        self.actions = actions or []

    def execute(self, executor: 'ActionExecutor', var_manager: 'VariableManager' = None) -> bool:
        for action in self.actions:
            if not action.execute(executor, var_manager):
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "sequence",
            "actions": [a.to_dict() for a in self.actions],
        }

class ConditionalAction(ActionNode):
    """条件动作 - 根据条件表达式选择执行分支。"""

    def __init__(self, condition: str, true_action: ActionNode = None,
                 false_action: ActionNode = None):
        self.condition = condition
        self.true_action = true_action
        self.false_action = false_action
        self._evaluator = SafeExpressionEvaluator()

    def execute(self, executor: 'ActionExecutor', var_manager: 'VariableManager' = None) -> bool:
        context = {}
        if var_manager:
            for var in var_manager.get_all_variables():
                context[var.name] = var.value

        try:
            result = self._evaluator.evaluate(self.condition, context)
        except Exception:
            result = False

        if result:
            if self.true_action:
                return self.true_action.execute(executor, var_manager)
            return True
        else:
            if self.false_action:
                return self.false_action.execute(executor, var_manager)
            return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "conditional",
            "condition": self.condition,
            "true_action": self.true_action.to_dict() if self.true_action else None,
            "false_action": self.false_action.to_dict() if self.false_action else None,
        }

class LoopAction(ActionNode):
    """循环动作 - 重复执行指定动作。

    支持固定次数循环和条件循环。
    """

    def __init__(self, times: Optional[int] = None, action: ActionNode = None,
                 condition: str = ""):
        self.times = times
        self.action = action
        self.condition = condition
        self._evaluator = SafeExpressionEvaluator()
        self._max_iterations = 1000

    def execute(self, executor: 'ActionExecutor', var_manager: 'VariableManager' = None) -> bool:
        if self.action is None:
            return True

        context = {}
        if var_manager:
            for var in var_manager.get_all_variables():
                context[var.name] = var.value

        if self.times is not None:
            for _ in range(min(self.times, self._max_iterations)):
                if not self.action.execute(executor, var_manager):
                    return False
        elif self.condition:
            iterations = 0
            while iterations < self._max_iterations:
                try:
                    result = self._evaluator.evaluate(self.condition, context)
                except Exception:
                    result = False

                if not result:
                    break

                if not self.action.execute(executor, var_manager):
                    return False

                if var_manager:
                    context = {}
                    for var in var_manager.get_all_variables():
                        context[var.name] = var.value

                iterations += 1
        else:
            return True

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "loop",
            "times": self.times,
            "action": self.action.to_dict() if self.action else None,
            "condition": self.condition,
        }

class DelayAction(ActionNode):
    """延迟动作 - 等待指定时间后继续。"""

    def __init__(self, milliseconds: int = 1000):
        self.delay_ms = milliseconds

    def execute(self, executor: 'ActionExecutor', var_manager: 'VariableManager' = None) -> bool:
        from PySide6.QtCore import QThread
        QThread.msleep(min(self.delay_ms, 10000))
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "delay",
            "milliseconds": self.delay_ms,
        }

class ParallelAction(ActionNode):
    """并行动作 - 同时执行多个动作。"""

    def __init__(self, actions: List[ActionNode] = None):
        self.actions = actions or []

    def execute(self, executor: 'ActionExecutor', var_manager: 'VariableManager' = None) -> bool:
        all_success = True
        for action in self.actions:
            try:
                if not action.execute(executor, var_manager):
                    all_success = False
            except Exception:
                all_success = False
        return all_success

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "parallel",
            "actions": [a.to_dict() for a in self.actions],
        }