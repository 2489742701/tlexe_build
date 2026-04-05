"""画布控制器模块。

本模块包含画布控制器，负责处理画布上的所有交互逻辑，
包括组件选择、拖拽、调整大小、对齐等。

## 修复说明 (2026-04-02)
【问题】画布交互逻辑散落在 views/canvas.py 的 ComponentGraphicsItem 中，
导致 ComponentGraphicsItem 成为"上帝类"，同时控制器层单薄。

【解决方案】创建 CanvasController，将所有画布交互逻辑从视图中分离，
实现真正的 MVC 架构。

【收益】
1. ComponentGraphicsItem 只负责渲染和事件转发，不再处理业务逻辑
2. 画布交互逻辑集中，便于维护和测试
3. 支持实现复杂的交互功能（对齐、分布、多选等）
4. 控制器可以访问 ProjectModel，实现数据和视图的同步
"""

from typing import Optional, Dict, List, Tuple
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtWidgets import QGraphicsItem

from models import ComponentModel, ProjectModel
from utils.undo_manager import UndoManager


class CanvasController:
    """画布控制器。
    
    负责处理画布上的所有交互逻辑，包括组件选择、拖拽、调整大小等。
    
    Attributes:
        _canvas_view: 画布视图引用
        _project_model: 项目数据模型
        _undo_manager: 撤销管理器
        _selected_items: 当前选中的组件列表
        _drag_state: 拖拽状态
        _resize_state: 调整大小状态
        
    Signals:
        component_selected: 组件被选中时发射 (comp_id)
        components_moved: 组件移动完成时发射 (comp_ids, delta)
        component_resized: 组件大小改变时发射 (comp_id, new_rect)
        
    ## 修复说明 (2026-04-02)
    此类是新创建的，用于解决 canvas.py 中 ComponentGraphicsItem 职责过多的问题。
    将原本散落在视图中的交互逻辑抽取到这里，实现真正的 MVC 架构。
    """
    
    component_selected = Signal(str)
    components_moved = Signal(list, QPointF)
    component_resized = Signal(str, QRectF)
    selection_changed = Signal(list)  # 选中的组件ID列表
    
    def __init__(self, canvas_view, project_model: ProjectModel, undo_manager: UndoManager):
        """初始化画布控制器。
        
        Args:
            canvas_view: 画布视图引用
            project_model: 项目数据模型
            undo_manager: 撤销管理器
        """
        self._canvas_view = canvas_view
        self._project_model = project_model
        self._undo_manager = undo_manager
        
        # 选择状态
        self._selected_items: List[QGraphicsItem] = []
        self._is_multi_selecting = False
        
        # 拖拽状态
        self._drag_state = {
            'is_dragging': False,
            'start_pos': QPointF(),
            'items_start_positions': {}  # item -> QPointF
        }
        
        # 调整大小状态
        self._resize_state = {
            'is_resizing': False,
            'handle': -1,
            'start_pos': QPointF(),
            'start_rect': QRectF(),
            'item': None
        }
        
        # 对齐辅助线
        self._show_alignment_guides = True
        self._alignment_threshold = 5  # 像素
    
    # ==================== 选择管理 ====================
    
    def on_item_clicked(self, item, modifiers: Qt.KeyboardModifier):
        """处理组件点击事件。
        
        Args:
            item: 被点击的图形项
            modifiers: 键盘修饰键状态（Ctrl、Shift等）
            
        ## 修复说明 (2026-04-02)
        从 ComponentGraphicsItem.mousePressEvent 中抽取，集中处理选择逻辑。
        """
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+点击：切换选择状态
            self._toggle_item_selection(item)
        elif modifiers & Qt.KeyboardModifier.ShiftModifier:
            # Shift+点击：添加到选择
            self._add_item_to_selection(item)
        else:
            # 普通点击：单选
            self._select_single_item(item)
    
    def _select_single_item(self, item):
        """单选组件。"""
        # 清除之前的选择
        for selected in self._selected_items:
            selected.setSelected(False)
        
        self._selected_items = [item]
        item.setSelected(True)
        
        comp_id = item.model.id if hasattr(item, 'model') else None
        if comp_id:
            self.component_selected.emit(comp_id)
            self.selection_changed.emit([comp_id])
    
    def _add_item_to_selection(self, item):
        """添加组件到选择。"""
        if item not in self._selected_items:
            self._selected_items.append(item)
            item.setSelected(True)
            
            comp_ids = [i.model.id for i in self._selected_items if hasattr(i, 'model')]
            self.selection_changed.emit(comp_ids)
    
    def _toggle_item_selection(self, item):
        """切换组件选择状态。"""
        if item in self._selected_items:
            self._selected_items.remove(item)
            item.setSelected(False)
        else:
            self._selected_items.append(item)
            item.setSelected(True)
        
        comp_ids = [i.model.id for i in self._selected_items if hasattr(i, 'model')]
        self.selection_changed.emit(comp_ids)
    
    def clear_selection(self):
        """清除所有选择。"""
        for item in self._selected_items:
            item.setSelected(False)
        self._selected_items = []
        self.selection_changed.emit([])
    
    def get_selected_items(self) -> List[QGraphicsItem]:
        """获取当前选中的组件列表。"""
        return self._selected_items.copy()
    
    # ==================== 拖拽管理 ====================
    
    def on_drag_start(self, item, pos: QPointF):
        """开始拖拽。
        
        Args:
            item: 被拖拽的组件
            pos: 鼠标位置
            
        ## 修复说明 (2026-04-02)
        从 ComponentGraphicsItem.mousePressEvent 中抽取，集中处理拖拽逻辑。
        """
        self._drag_state['is_dragging'] = True
        self._drag_state['start_pos'] = pos
        self._drag_state['items_start_positions'] = {}
        
        # 记录所有选中组件的起始位置
        for selected_item in self._selected_items:
            self._drag_state['items_start_positions'][selected_item] = selected_item.pos()
    
    def on_drag_move(self, delta: QPointF):
        """拖拽移动中。
        
        Args:
            delta: 鼠标移动的增量
        """
        if not self._drag_state['is_dragging']:
            return
        
        # 移动所有选中的组件
        for item, start_pos in self._drag_state['items_start_positions'].items():
            new_pos = start_pos + delta
            
            # 应用网格对齐
            if self._canvas_view and hasattr(self._canvas_view, 'snap_to_grid'):
                new_pos = self._canvas_view.snap_to_grid(new_pos)
            
            item.setPos(new_pos)
        
        # 更新对齐辅助线
        if self._show_alignment_guides:
            self._update_alignment_guides()
    
    def on_drag_end(self):
        """拖拽结束。"""
        if not self._drag_state['is_dragging']:
            return
        
        # 计算实际移动的增量
        moved_items = []
        deltas = []
        
        for item, start_pos in self._drag_state['items_start_positions'].items():
            end_pos = item.pos()
            delta = end_pos - start_pos
            
            if delta.x() != 0 or delta.y() != 0:
                moved_items.append(item)
                deltas.append(delta)
                
                # 更新模型数据
                if hasattr(item, 'model'):
                    item.model.x = int(end_pos.x())
                    item.model.y = int(end_pos.y())
        
        # 发射移动完成信号
        if moved_items:
            comp_ids = [i.model.id for i in moved_items if hasattr(i, 'model')]
            # 使用第一个组件的增量作为代表
            self.components_moved.emit(comp_ids, deltas[0] if deltas else QPointF())
        
        # 清除对齐辅助线
        self._clear_alignment_guides()
        
        # 重置拖拽状态
        self._drag_state['is_dragging'] = False
        self._drag_state['items_start_positions'] = {}
    
    def _update_alignment_guides(self):
        """更新对齐辅助线。"""
        # TODO: 实现对齐辅助线显示
        pass
    
    def _clear_alignment_guides(self):
        """清除对齐辅助线。"""
        # TODO: 实现对齐辅助线清除
        pass
    
    # ==================== 调整大小管理 ====================
    
    def on_resize_start(self, item, handle: int, pos: QPointF):
        """开始调整大小。
        
        Args:
            item: 被调整大小的组件
            handle: 调整手柄索引（0-7）
            pos: 鼠标位置
            
        ## 修复说明 (2026-04-02)
        从 ComponentGraphicsItem.mousePressEvent 中抽取，集中处理调整大小逻辑。
        """
        self._resize_state['is_resizing'] = True
        self._resize_state['handle'] = handle
        self._resize_state['start_pos'] = pos
        self._resize_state['start_rect'] = item.boundingRect()
        self._resize_state['item'] = item
    
    def on_resize_move(self, pos: QPointF):
        """调整大小移动中。
        
        Args:
            pos: 当前鼠标位置
        """
        if not self._resize_state['is_resizing']:
            return
        
        handle = self._resize_state['handle']
        start_rect = self._resize_state['start_rect']
        delta = pos - self._resize_state['start_pos']
        
        # 根据手柄计算新的矩形
        new_rect = self._calculate_resize_rect(start_rect, handle, delta)
        
        # 应用最小尺寸限制
        min_size = 20
        if new_rect.width() < min_size:
            new_rect.setWidth(min_size)
        if new_rect.height() < min_size:
            new_rect.setHeight(min_size)
        
        # 更新组件大小
        item = self._resize_state['item']
        if hasattr(item, 'set_rect'):
            item.set_rect(new_rect)
    
    def _calculate_resize_rect(self, start_rect: QRectF, handle: int, delta: QPointF) -> QRectF:
        """计算调整大小后的矩形。
        
        Args:
            start_rect: 起始矩形
            handle: 调整手柄索引
            delta: 鼠标移动增量
            
        Returns:
            新的矩形
        """
        new_rect = QRectF(start_rect)
        
        # 手柄索引：0=左上, 1=上中, 2=右上, 3=右中, 4=右下, 5=下中, 6=左下, 7=左中
        if handle in [0, 1, 2]:  # 上边
            new_rect.setTop(start_rect.top() + delta.y())
        if handle in [2, 3, 4]:  # 右边
            new_rect.setRight(start_rect.right() + delta.x())
        if handle in [4, 5, 6]:  # 下边
            new_rect.setBottom(start_rect.bottom() + delta.y())
        if handle in [6, 7, 0]:  # 左边
            new_rect.setLeft(start_rect.left() + delta.x())
        
        return new_rect
    
    def on_resize_end(self):
        """调整大小结束。"""
        if not self._resize_state['is_resizing']:
            return
        
        item = self._resize_state['item']
        new_rect = item.boundingRect()
        
        # 更新模型数据
        if hasattr(item, 'model'):
            item.model.width = int(new_rect.width())
            item.model.height = int(new_rect.height())
            item.model.x = int(item.pos().x())
            item.model.y = int(item.pos().y())
            
            # 发射调整大小完成信号
            self.component_resized.emit(item.model.id, new_rect)
        
        # 重置调整大小状态
        self._resize_state['is_resizing'] = False
        self._resize_state['item'] = None
    
    # ==================== 对齐和分布 ====================
    
    def align_selected(self, alignment: str):
        """对齐选中的组件。
        
        Args:
            alignment: 对齐方式 ('left', 'center', 'right', 'top', 'middle', 'bottom')
        """
        if len(self._selected_items) < 2:
            return
        
        # 获取边界矩形
        rects = [item.sceneBoundingRect() for item in self._selected_items]
        
        if alignment == 'left':
            target_x = min(r.left() for r in rects)
            for item in self._selected_items:
                item.setX(target_x)
        elif alignment == 'center':
            center_x = sum(r.center().x() for r in rects) / len(rects)
            for item in self._selected_items:
                item.setX(center_x - item.boundingRect().width() / 2)
        elif alignment == 'right':
            target_x = max(r.right() for r in rects)
            for item in self._selected_items:
                item.setX(target_x - item.boundingRect().width())
        elif alignment == 'top':
            target_y = min(r.top() for r in rects)
            for item in self._selected_items:
                item.setY(target_y)
        elif alignment == 'middle':
            center_y = sum(r.center().y() for r in rects) / len(rects)
            for item in self._selected_items:
                item.setY(center_y - item.boundingRect().height() / 2)
        elif alignment == 'bottom':
            target_y = max(r.bottom() for r in rects)
            for item in self._selected_items:
                item.setY(target_y - item.boundingRect().height())
    
    def distribute_selected(self, direction: str):
        """分布选中的组件。
        
        Args:
            direction: 分布方向 ('horizontal', 'vertical')
        """
        if len(self._selected_items) < 3:
            return
        
        if direction == 'horizontal':
            # 按 X 坐标排序
            items = sorted(self._selected_items, key=lambda i: i.x())
            left = items[0].x()
            right = items[-1].x()
            total_width = right - left
            spacing = total_width / (len(items) - 1)
            
            for i, item in enumerate(items):
                item.setX(left + spacing * i)
        
        elif direction == 'vertical':
            # 按 Y 坐标排序
            items = sorted(self._selected_items, key=lambda i: i.y())
            top = items[0].y()
            bottom = items[-1].y()
            total_height = bottom - top
            spacing = total_height / (len(items) - 1)
            
            for i, item in enumerate(items):
                item.setY(top + spacing * i)
