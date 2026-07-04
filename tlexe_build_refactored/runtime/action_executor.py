"""动作执行器模块。

根据 ActionConfig 执行相应的操作，实现组件间的事件联动。

支持的动作类型:
    none, close_program, close_window, open_window, switch_window,
    random_image, next_image, prev_image, start_carousel, stop_carousel,
    lottery_animation, start_alternating, stop_alternating, set_text,
    show_component, hide_component, show_message, execute_python, delay

Signals:
    action_executed: 动作执行完成信号 (action_type: str, success: bool)
    window_switch_requested: 窗口切换请求信号 (window_id: str)
    window_close_requested: 窗口关闭请求信号
    program_close_requested: 程序关闭请求信号
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from models import ProjectModel, ComponentModel
    from runtime.action_nodes import ActionNode

class ActionExecutor(QObject):
    """动作执行器，根据 ActionConfig 执行组件间的事件联动。

    Signals:
        action_executed: 动作执行完成 (action_type, success)
        window_switch_requested: 窗口切换请求 (window_id)
        window_close_requested: 窗口关闭请求
        program_close_requested: 程序关闭请求
    """
    
    action_executed = Signal(str, bool)
    window_switch_requested = Signal(str)
    window_close_requested = Signal()
    program_close_requested = Signal()
    
    def __init__(self, project_model: 'ProjectModel', parent=None):
        """初始化动作执行器。
        
        Args:
            project_model: 项目数据模型
            parent: 父对象
        """
        super().__init__(parent)
        self._project_model = project_model
    
    def execute(self, action_config) -> bool:
        from models.schemas import ActionType
        from runtime.action_nodes import ActionNode

        if isinstance(action_config, ActionNode):
            from models.variable_system import get_variable_manager
            var_manager = get_variable_manager()
            return action_config.execute(self, var_manager)

        action_type = action_config.action_type
        target_component_id = action_config.get_target_component_id()
        target_window_id = action_config.get_target_window_id()
        action_params = action_config.get_action_params()
        
        if action_type == ActionType.NONE.value:
            return True
        
        elif action_type == ActionType.CLOSE_PROGRAM.value:
            return self._close_program()
        
        elif action_type == ActionType.CLOSE_WINDOW.value:
            return self._close_window()
        
        elif action_type == ActionType.OPEN_WINDOW.value:
            return self._open_window(target_window_id, action_params)
        
        elif action_type == ActionType.SWITCH_WINDOW.value:
            return self._switch_window(target_window_id)
        
        elif action_type == ActionType.RANDOM_IMAGE.value:
            return self._random_image(target_component_id, action_params)
        
        elif action_type == ActionType.NEXT_IMAGE.value:
            return self._next_image(target_component_id)
        
        elif action_type == ActionType.PREV_IMAGE.value:
            return self._prev_image(target_component_id)
        
        elif action_type == ActionType.START_CAROUSEL.value:
            return self._start_carousel(target_component_id, action_params)
        
        elif action_type == ActionType.STOP_CAROUSEL.value:
            return self._stop_carousel(target_component_id)
        
        elif action_type == ActionType.LOTTERY_ANIMATION.value:
            return self._lottery_animation(target_component_id, action_params)
        
        elif action_type == ActionType.START_ALTERNATING.value:
            return self._start_alternating(target_component_id, action_params)
        
        elif action_type == ActionType.STOP_ALTERNATING.value:
            return self._stop_alternating(target_component_id)
        
        elif action_type == ActionType.SET_TEXT.value:
            return self._set_text(target_component_id, action_params)
        
        elif action_type == ActionType.SHOW_COMPONENT.value:
            return self._show_component(target_component_id)
        
        elif action_type == ActionType.HIDE_COMPONENT.value:
            return self._hide_component(target_component_id)
        
        elif action_type == ActionType.SHOW_MESSAGE.value:
            return self._show_message(action_params)
        
        elif action_type == ActionType.EXECUTE_PYTHON.value:
            return self._execute_python(action_config.python_code or action_params.get("code", ""))
        
        elif action_type == ActionType.DELAY.value:
            return self._delay(action_params)
        
        self.action_executed.emit(action_type, False)
        return False
    
    def _show_message(self, params: Dict[str, Any]) -> bool:
        """显示消息框。"""
        from views.custom_dialogs import ErrorDialog, WarningDialog
        from PySide6.QtWidgets import QMessageBox
        message = params.get("message", "")
        title = params.get("title", "提示")
        msg_type = params.get("type", "info")
        
        if msg_type == "warning":
            WarningDialog.show_warning(None, title, message)
        elif msg_type == "error":
            ErrorDialog.show_error(None, title, message)
        else:
            QMessageBox.information(None, title, message)
        
        self.action_executed.emit("show_message", True)
        return True
    
    def _close_program(self) -> bool:
        """关闭程序。
        
        Returns:
            是否成功
        """
        self.program_close_requested.emit()
        self.action_executed.emit("close_program", True)
        return True
    
    def _close_window(self) -> bool:
        """关闭当前窗口。
        
        Returns:
            是否成功
        """
        self.window_close_requested.emit()
        self.action_executed.emit("close_window", True)
        return True
    
    def _open_window(self, window_id: str, params: Dict[str, Any]) -> bool:
        """打开窗口。
        
        Args:
            window_id: 窗口ID
            params: 额外参数
            
        Returns:
            是否成功
        """
        if not window_id:
            return False
        
        self.window_switch_requested.emit(window_id)
        self.action_executed.emit("open_window", True)
        return True
    
    def _switch_window(self, window_id: str) -> bool:
        """切换窗口。
        
        Args:
            window_id: 目标窗口ID
            
        Returns:
            是否成功
        """
        if not window_id:
            return False
        
        self.window_switch_requested.emit(window_id)
        self.action_executed.emit("switch_window", True)
        return True
    
    def _random_image(self, component_id: str, params: Dict[str, Any]) -> bool:
        """随机选图。
        
        Args:
            component_id: 目标组件ID（图片轮播组件）
            params: 额外参数
            
        Returns:
            是否成功
        """
        from models.components import ImageCarouselModel
        
        component = self._project_model.get_component(component_id)
        if isinstance(component, ImageCarouselModel):
            component.random_image()
            self.action_executed.emit("random_image", True)
            return True
        return False
    
    def _next_image(self, component_id: str) -> bool:
        """下一张图片。
        
        Args:
            component_id: 目标组件ID（图片轮播组件）
            
        Returns:
            是否成功
        """
        from models.components import ImageCarouselModel
        
        component = self._project_model.get_component(component_id)
        if isinstance(component, ImageCarouselModel):
            component.next_image()
            self.action_executed.emit("next_image", True)
            return True
        return False
    
    def _prev_image(self, component_id: str) -> bool:
        """上一张图片。
        
        Args:
            component_id: 目标组件ID（图片轮播组件）
            
        Returns:
            是否成功
        """
        from models.components import ImageCarouselModel
        
        component = self._project_model.get_component(component_id)
        if isinstance(component, ImageCarouselModel):
            component.prev_image()
            self.action_executed.emit("prev_image", True)
            return True
        return False
    
    def _start_carousel(self, component_id: str, params: Dict[str, Any]) -> bool:
        """开始轮播。
        
        Args:
            component_id: 目标组件ID（图片轮播组件）
            params: 额外参数（如interval）
            
        Returns:
            是否成功
        """
        from models.components import ImageCarouselModel
        
        component = self._project_model.get_component(component_id)
        if isinstance(component, ImageCarouselModel):
            interval = params.get("interval")
            if interval:
                component.interval = interval
            component.auto_play = True
            self.action_executed.emit("start_carousel", True)
            return True
        return False
    
    def _stop_carousel(self, component_id: str) -> bool:
        """停止轮播。
        
        Args:
            component_id: 目标组件ID（图片轮播组件）
            
        Returns:
            是否成功
        """
        from models.components import ImageCarouselModel
        
        component = self._project_model.get_component(component_id)
        if isinstance(component, ImageCarouselModel):
            component.auto_play = False
            self.action_executed.emit("stop_carousel", True)
            return True
        return False
    
    def _lottery_animation(self, component_id: str, params: Dict[str, Any]) -> bool:
        """执行抽奖动画。
        
        支持 LotteryModel（优先）、ImageCarouselModel 和 LabelModel。
        
        Args:
            component_id: 目标组件ID
            params: 动画参数
                - duration_ms: 动画时长（毫秒），默认3000
                - candidates: 候选人列表（仅 LabelModel 有效）
                
        Returns:
            是否成功
        """
        from models.components import LotteryModel, ImageCarouselModel, LabelModel
        
        component = self._project_model.get_component(component_id)
        duration_ms = params.get("duration_ms", 3000)
        
        if isinstance(component, LotteryModel):
            component.lottery_animation(duration_ms=duration_ms)
            self.action_executed.emit("lottery_animation", True)
            return True
        elif isinstance(component, ImageCarouselModel):
            component.lottery_animation(duration_ms=duration_ms)
            self.action_executed.emit("lottery_animation", True)
            return True
        elif isinstance(component, LabelModel):
            candidates = params.get("candidates", None)
            component.lottery_animation(candidates=candidates, duration_ms=duration_ms)
            self.action_executed.emit("lottery_animation", True)
            return True
        return False
    
    def _start_alternating(self, component_id: str, params: Dict[str, Any]) -> bool:
        """开始交替变换动画。
        
        支持 TextAlternatingModel 和 ImageAlternatingModel。
        
        Args:
            component_id: 目标组件ID
            params: 动画参数
                - duration_ms: 动画时长（毫秒），默认3000
                
        Returns:
            是否成功
        """
        from models.components import AlternatingModel
        
        component = self._project_model.get_component(component_id)
        duration_ms = params.get("duration_ms", 3000)
        
        if isinstance(component, AlternatingModel):
            component.start_alternating(duration_ms=duration_ms)
            self.action_executed.emit("start_alternating", True)
            return True
        return False
    
    def _stop_alternating(self, component_id: str) -> bool:
        """停止交替变换动画。
        
        支持 TextAlternatingModel 和 ImageAlternatingModel。
        
        Args:
            component_id: 目标组件ID
            
        Returns:
            是否成功
        """
        from models.components import AlternatingModel
        
        component = self._project_model.get_component(component_id)
        
        if isinstance(component, AlternatingModel):
            component.stop_alternating()
            self.action_executed.emit("stop_alternating", True)
            return True
        return False
    
    def _set_text(self, component_id: str, params: Dict[str, Any]) -> bool:
        """设置组件文本。
        
        Args:
            component_id: 目标组件ID
            params: 参数
                - text: 要设置的文本内容
                - use_template: 是否使用模板（支持{winner}等占位符）
                
        Returns:
            是否成功
        """
        from models.base import ComponentModel
        
        component = self._project_model.get_component(component_id)
        if component and hasattr(component, 'text'):
            text = params.get('text', '')
            component.text = text
            self.action_executed.emit("set_text", True)
            return True
        return False
    
    def _show_component(self, component_id: str) -> bool:
        """显示组件。
        
        Args:
            component_id: 目标组件ID
            
        Returns:
            是否成功
        """
        from models.base import ComponentModel
        
        component = self._project_model.get_component(component_id)
        if component:
            component.visible = True
            self.action_executed.emit("show_component", True)
            return True
        return False
    
    def _hide_component(self, component_id: str) -> bool:
        """隐藏组件。
        
        Args:
            component_id: 目标组件ID
            
        Returns:
            是否成功
        """
        from models.base import ComponentModel
        
        component = self._project_model.get_component(component_id)
        if component:
            component.visible = False
            self.action_executed.emit("hide_component", True)
            return True
        return False
    
    def _execute_python(self, code: str) -> bool:
        if not code:
            return False
        
        try:
            exec(code)
            self.action_executed.emit("execute_python", True)
            return True
        except Exception as e:
            print(f"执行Python代码失败: {e}")
            self.action_executed.emit("execute_python", False)
            return False
    
    def _delay(self, params: Dict[str, Any]) -> bool:
        from PySide6.QtCore import QTimer
        milliseconds = params.get("milliseconds", 1000)
        QTimer.singleShot(milliseconds, lambda: self.action_executed.emit("delay", True))
        return True
