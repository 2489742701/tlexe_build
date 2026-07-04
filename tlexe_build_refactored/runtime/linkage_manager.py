"""组件联动管理器模块。

本模块负责解析和执行组件间的联动配置。

## 功能
1. 解析linkages配置
2. 连接源组件信号到目标组件动作
3. 支持模板文本替换

## 使用示例
```python
linkage_manager = LinkageManager(project_model, action_executor)
linkage_manager.setup_linkages()
```
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from models import ProjectModel
    from runtime.action_executor import ActionExecutor

def _log_debug(message: str):
    """调试日志输出。"""
    print(f"[LinkageManager] {message}")
    try:
        from dev_mode.debug_logger import DebugLogger
        DebugLogger.debug(message, "linkage")
    except Exception:
        pass

class LinkageManager(QObject):
    """组件联动管理器。
    
    负责解析和执行组件间的联动配置。
    
    ## 联动配置格式
    ```json
    {
        "source_component": "carousel_1",
        "source_event": "lottery_finished",
        "target_component": "lbl_result",
        "target_action": "set_text",
        "params": {
            "text_template": "恭喜 {winner} 中奖!"
        }
    }
    ```
    
    Signals:
        linkage_triggered: 联动触发信号 (source_id, target_id, action)
    """
    
    linkage_triggered = Signal(str, str, str)
    
    def __init__(self, project_model: 'ProjectModel', action_executor: 'ActionExecutor', parent=None):
        """初始化联动管理器。
        
        Args:
            project_model: 项目数据模型
            action_executor: 动作执行器
            parent: 父对象
        """
        super().__init__(parent)
        self._project_model = project_model
        self._action_executor = action_executor
        self._connections: List[Dict[str, Any]] = []
    
    def setup_linkages(self):
        """设置所有联动配置。
        
        解析项目中的linkages配置，建立组件间的信号连接。
        """
        linkages = self._project_model.linkages
        
        for linkage in linkages:
            self._setup_single_linkage(linkage)
    
    def _setup_single_linkage(self, linkage: Dict[str, Any]):
        """设置单个联动配置。
        
        Args:
            linkage: 联动配置字典
        """
        source_id = linkage.get('source_component')
        source_event = linkage.get('source_event')
        target_id = linkage.get('target_component')
        target_action = linkage.get('target_action')
        params = linkage.get('params', {})
        
        if not all([source_id, source_event, target_id, target_action]):
            missing = [k for k in ['source_component', 'source_event', 'target_component', 'target_action'] 
                      if not locals().get(k.replace('component', '').replace('event', '_event').replace('action', '_action'))]
            _log_debug(f"联动配置不完整，缺少字段: {missing}")
            return
        
        source_component = self._project_model.get_component(source_id)
        target_component = self._project_model.get_component(target_id)
        
        if not source_component or not target_component:
            missing = []
            if not source_component:
                missing.append(f"源组件 {source_id}")
            if not target_component:
                missing.append(f"目标组件 {target_id}")
            _log_debug(f"联动组件不存在: {', '.join(missing)}")
            return
        
        signal = getattr(source_component, source_event, None)
        if not signal or not hasattr(signal, 'connect'):
            _log_debug(f"源组件 {source_id} 不存在信号 {source_event}")
            return
        
        def on_source_event(*args, **kwargs):
            try:
                processed_params = self._process_params(params, args, kwargs, source_component)
                
                self._execute_action(target_component, target_action, processed_params, args, kwargs, source_component)
                
                self.linkage_triggered.emit(source_id, target_id, target_action)
            except Exception as e:
                _log_debug(f"联动执行失败 [{source_id}->{target_id}]: {type(e).__name__}: {e}")
        
        try:
            signal.connect(on_source_event)
            self._connections.append({
                'signal': signal,
                'callback': on_source_event,
                'linkage': linkage
            })
            _log_debug(f"联动已连接: {source_id}.{source_event} -> {target_id}.{target_action}")
        except Exception as e:
            _log_debug(f"联动连接失败 [{source_id}->{target_id}]: {type(e).__name__}: {e}")
    
    def _execute_action(self, target_component, action: str, params: Dict[str, Any], 
                        args: tuple, kwargs: dict, source_component):
        """执行目标组件动作。
        
        支持的动作类型:
        - set_text: 设置文本内容
        - set_image: 设置图片路径
        - set_source: 设置媒体源
        - set_index: 设置索引
        - show: 显示组件
        - hide: 隐藏组件
        - start: 开始播放/轮播
        - stop: 停止播放/轮播
        
        Args:
            target_component: 目标组件
            action: 动作类型
            params: 动作参数
            args: 信号参数
            kwargs: 信号关键字参数
            source_component: 源组件
        """
        if action == 'set_text':
            text = params.get('text_template', '')
            text = self._replace_templates(text, args, kwargs, source_component)
            if hasattr(target_component, 'text'):
                target_component.text = text
        
        elif action == 'set_image':
            image_path = params.get('image_path', '')
            image_path = self._replace_templates(image_path, args, kwargs, source_component)
            if hasattr(target_component, 'image_path'):
                target_component.image_path = image_path
            elif hasattr(target_component, 'source'):
                target_component.source = image_path
        
        elif action == 'set_source':
            source = params.get('source', '')
            source = self._replace_templates(source, args, kwargs, source_component)
            if hasattr(target_component, 'source'):
                target_component.source = source
            elif hasattr(target_component, 'media_source'):
                target_component.media_source = source
        
        elif action == 'set_index':
            index = params.get('index', 0)
            if isinstance(index, str) and index.startswith('{') and index.endswith('}'):
                index = self._replace_templates(index, args, kwargs, source_component)
                try:
                    index = int(index)
                except ValueError:
                    index = 0
            if hasattr(target_component, 'current_index'):
                target_component.current_index = index
        
        elif action == 'show':
            if hasattr(target_component, 'visible'):
                target_component.visible = True
        
        elif action == 'hide':
            if hasattr(target_component, 'visible'):
                target_component.visible = False
        
        elif action == 'start':
            if hasattr(target_component, 'start'):
                target_component.start()
            elif hasattr(target_component, 'play'):
                target_component.play()
            elif hasattr(target_component, 'auto_play'):
                target_component.auto_play = True
        
        elif action == 'stop':
            if hasattr(target_component, 'stop'):
                target_component.stop()
            elif hasattr(target_component, 'pause'):
                target_component.pause()
            elif hasattr(target_component, 'auto_play'):
                target_component.auto_play = False
        
        else:
            action_method = getattr(target_component, action, None)
            if action_method and callable(action_method):
                action_method(**params)
    
    def _process_params(self, params: Dict[str, Any], args: tuple, kwargs: dict, source_component) -> Dict[str, Any]:
        """处理联动参数。
        
        Args:
            params: 原始参数
            args: 信号参数
            kwargs: 信号关键字参数
            source_component: 源组件
            
        Returns:
            处理后的参数字典
        """
        return params.copy()
    
    def _replace_templates(self, template: str, args: tuple, kwargs: dict, source_component) -> str:
        """替换模板占位符。
        
        优先级规则（高到低）:
        1. 信号参数 (args[1]) - 最高优先级，来自信号发射时的参数
        2. 组件属性 - 来自源组件的属性值
        
        支持的占位符:
        - {winner}: 中奖者名称（从image_labels获取）
        - {index}: 中奖索引
        - {image}: 图片路径（优先使用信号参数，否则从images列表获取）
        - {source}: 源路径（仅信号参数）
        - {text}: 文本内容（优先使用信号参数，否则从组件属性获取）
        - {value}: 数值（优先使用信号参数，否则从组件属性获取）
        - {count}: 总数（仅组件属性）
        
        Args:
            template: 模板字符串
            args: 信号参数
            kwargs: 信号关键字参数
            source_component: 源组件
            
        Returns:
            替换后的字符串
        """
        if not template:
            return template
        
        replacements = {}
        
        if args:
            index = args[0] if len(args) >= 1 else None
            second_arg = args[1] if len(args) >= 2 else None
            
            if index is not None:
                replacements['{index}'] = str(index)
                
                try:
                    idx = int(index) if isinstance(index, (int, float, str)) else 0
                    
                    if hasattr(source_component, 'image_labels') and 0 <= idx < len(source_component.image_labels):
                        replacements['{winner}'] = str(source_component.image_labels[idx])
                    elif hasattr(source_component, 'item_labels') and 0 <= idx < len(source_component.item_labels):
                        replacements['{winner}'] = str(source_component.item_labels[idx])
                    
                    if hasattr(source_component, 'images'):
                        if 0 <= idx < len(source_component.images):
                            image_path = str(source_component.images[idx])
                            if '{image}' not in replacements:
                                replacements['{image}'] = image_path
                        
                        replacements['{count}'] = str(len(source_component.images))
                except (ValueError, TypeError):
                    pass
            
            if second_arg is not None:
                replacements['{source}'] = str(second_arg)
                replacements['{text}'] = str(second_arg)
                replacements['{value}'] = str(second_arg)
                replacements['{image}'] = str(second_arg)
        
        if '{text}' not in replacements and hasattr(source_component, 'text'):
            replacements['{text}'] = str(source_component.text)
        
        if '{value}' not in replacements and hasattr(source_component, 'value'):
            replacements['{value}'] = str(source_component.value)
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def clear_linkages(self):
        """清除所有联动连接。"""
        for conn in self._connections:
            try:
                conn['signal'].disconnect(conn['callback'])
            except Exception:
                pass
        
        self._connections.clear()
    
    def add_linkage(self, linkage: Dict[str, Any]):
        """添加新的联动配置。
        
        Args:
            linkage: 联动配置字典
        """
        self._setup_single_linkage(linkage)
        linkages = self._project_model.linkages
        linkages.append(linkage)
        self._project_model.linkages = linkages
    
    def remove_linkage(self, index: int):
        """移除联动配置。
        
        Args:
            index: 联动配置索引
        """
        if 0 <= index < len(self._connections):
            conn = self._connections[index]
            try:
                conn['signal'].disconnect(conn['callback'])
            except Exception:
                pass
            self._connections.pop(index)
            
            linkages = self._project_model.linkages
            if 0 <= index < len(linkages):
                linkages.pop(index)
                self._project_model.linkages = linkages
