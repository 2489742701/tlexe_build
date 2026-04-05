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
            return
        
        source_component = self._project_model.get_component(source_id)
        target_component = self._project_model.get_component(target_id)
        
        if not source_component or not target_component:
            return
        
        signal = getattr(source_component, source_event, None)
        if not signal or not hasattr(signal, 'connect'):
            return
        
        def on_source_event(*args, **kwargs):
            processed_params = self._process_params(params, args, kwargs, source_component)
            
            self._execute_action(target_component, target_action, processed_params, args, kwargs, source_component)
            
            self.linkage_triggered.emit(source_id, target_id, target_action)
        
        try:
            signal.connect(on_source_event)
            self._connections.append({
                'signal': signal,
                'callback': on_source_event,
                'linkage': linkage
            })
        except Exception as e:
            print(f"联动连接失败: {e}")
    
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
        
        支持的占位符:
        - {winner}: 中奖者名称（从image_labels获取）
        - {index}: 中奖索引
        - {image}: 中奖图片路径
        - {value}: 数值
        - {text}: 文本内容
        - {source}: 源路径
        - {count}: 总数
        
        Args:
            template: 模板字符串
            args: 信号参数
            kwargs: 信号关键字参数
            source_component: 源组件
            
        Returns:
            替换后的字符串
        """
        result = template
        
        if args:
            if len(args) >= 1:
                index = args[0]
                result = result.replace('{index}', str(index))
                
                if hasattr(source_component, 'images'):
                    try:
                        idx = int(index) if isinstance(index, (int, float, str)) else 0
                        if 0 <= idx < len(source_component.images):
                            image_path = source_component.images[idx]
                            result = result.replace('{image}', str(image_path))
                    except (ValueError, TypeError):
                        pass
                
                if hasattr(source_component, 'image_labels'):
                    try:
                        idx = int(index) if isinstance(index, (int, float, str)) else 0
                        if 0 <= idx < len(source_component.image_labels):
                            winner_name = source_component.image_labels[idx]
                            result = result.replace('{winner}', str(winner_name))
                    except (ValueError, TypeError):
                        pass
                
                if hasattr(source_component, 'images'):
                    result = result.replace('{count}', str(len(source_component.images)))
            
            if len(args) >= 2:
                second_arg = args[1]
                result = result.replace('{image}', str(second_arg))
                result = result.replace('{source}', str(second_arg))
                result = result.replace('{text}', str(second_arg))
                result = result.replace('{value}', str(second_arg))
        
        if hasattr(source_component, 'text'):
            result = result.replace('{text}', str(source_component.text))
        
        if hasattr(source_component, 'value'):
            result = result.replace('{value}', str(source_component.value))
        
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
