# 容器布局引擎 — 编码任务规划

> 基于 spec.md（需求规格）与 design.md（实现方案）生成，聚焦核心功能（布局引擎 + 重叠检测 + 集成），次要功能合并处理。

## 1. 搭建布局引擎包结构与数据模型

- [ ] 创建 `services/layout/` 包目录及 `__init__.py`，导出 LayoutEngine、OverlapDetector 等核心类
- [ ] 实现 `services/layout/data.py`：定义 `LayoutResult`（positions / overlaps / overflow / content_area）和 `OverlapInfo`（source_id / target_id / intersection_rect / avoidance_position）数据类，使用 `@dataclass` + 类型注解
- [ ] 实现 `services/layout/events.py`：定义 `LayoutUpdatedEvent`（container_id + result）和 `OverlapDetectedEvent`（container_id + overlap_ids）事件类
- [ ] 实现 `services/layout/commands.py`：定义 `RelayoutCommand` 撤销/重做命令，包含 execute() 和 undo() 方法，与 UndoManager 集成

**验收标准**：
- `LayoutResult` 和 `OverlapInfo` 可正常实例化并访问全部字段
- `RelayoutCommand.execute()` 正确应用 new_positions，`undo()` 正确回滚 old_positions
- `services/layout/` 包可被外部正常 import

**涉及文件**：`services/layout/__init__.py`、`services/layout/data.py`、`services/layout/events.py`、`services/layout/commands.py`

**依赖**：无

---

## 2. 实现布局策略接口与四种策略

- [ ] 实现 `services/layout/layout_strategy.py`：定义 `LayoutStrategy` 抽象基类，声明 `calculate(children, content_area, spacing) -> Dict[str, Tuple[int,int]]` 接口
- [ ] 实现 `NoneLayoutStrategy`：layout=none 时返回子组件现有位置 `{child.id: (child.x, child.y)}`，不修改任何位置
- [ ] 实现 `VerticalLayoutStrategy`：子组件按添加顺序从上到下排列，首个组件顶部对齐内容区域顶部，后续组件 y = 前一组件.y + 前一组件.height + spacing，所有组件 x 对齐内容区域左侧
- [ ] 实现 `HorizontalLayoutStrategy`：子组件按添加顺序从左到右排列，首个组件左侧对齐内容区域左侧，后续组件 x = 前一组件.x + 前一组件.width + spacing，所有组件 y 对齐内容区域顶部
- [ ] 实现 `GridLayoutStrategy`：列数 = floor((cw + spacing) / (MIN_COLUMN_WIDTH + spacing))，行优先填入网格，换行时 y += row_max_height + spacing
- [ ] 编写单元测试 `tests/test_layout_strategy.py`：覆盖各策略的标准排列计算、边界值（空子组件列表、单组件、零尺寸组件）、验收条件（spec.md 5.1.1 中的 a 条目）

**验收标准**：
- Vertical: padding=10, spacing=5, 两高度50子组件 → 第一个 y=10, 第二个 y=65
- Horizontal: padding=10, spacing=5, 两宽度80子组件 → 第一个 x=10, 第二个 x=95
- Grid: 宽度400, padding=10, spacing=5, 最小列宽120 → 列数=2
- None: 子组件位置保持不变
- 空子组件列表返回空字典

**涉及文件**：`services/layout/layout_strategy.py`、`tests/test_layout_strategy.py`

**依赖**：任务 1

---

## 3. 实现 LayoutEngine 主类

- [ ] 实现 `services/layout/layout_engine.py` 中 `LayoutEngine.__init__`：初始化 project_model、undo_manager、overlap_detector、overlap_avoider、四种策略字典
- [ ] 实现 `relayout(container)` 主流程：验证 layout 合法性（非法值回退 "none" + 警告日志）→ 计算内容区域 → 获取子组件模型 → 策略选择与位置计算 → 溢出检测 → 批量应用位置（blockSignals 防止中间状态）→ 重叠全量检测 → 返回 LayoutResult
- [ ] 实现 `_calc_content_area(container)`：内容区域 = (container.x + padding, container.y + padding, container.width - 2*padding, container.height - 2*padding)
- [ ] 实现 `_get_children_models(container)`：根据 children ID 列表获取子组件模型，跳过不存在（None）的 ID
- [ ] 实现 `_apply_positions(container, children, new_positions)`：批量写入子组件 x/y（blockSignals → 写入 → unblock → 一次性 emit data_changed），注册 UndoManager 撤销命令
- [ ] 实现 `_check_overflow(children, new_positions, content_area)`：检测子组件排列后是否超出内容区域
- [ ] 实现 `move_children_with_parent(container_id, dx, dy)`：父容器拖拽时子组件联动移动，跳过 locked 子组件
- [ ] 编写单元测试 `tests/test_layout_engine.py`：覆盖重排主流程、非法 layout 回退、空子组件、零尺寸组件、联动移动、UndoManager 集成

**验收标准**：
- relayout 对 vertical/horizontal/grid/none 布局正确计算子组件位置
- 非法 layout 值回退为 none，控制台输出警告
- 空子组件容器 relayout 返回空 positions、无 overlaps、overflow=False
- 重排不修改子组件 width/height
- 联动移动后子组件相对父容器偏移量不变

**涉及文件**：`services/layout/layout_engine.py`、`tests/test_layout_engine.py`

**依赖**：任务 1、任务 2

---

## 4. 实现重叠检测器与自动避让

- [ ] 实现 `services/layout/overlap_detector.py` 中 `OverlapDetector.detect(source, siblings)`：检测被拖组件与兄弟组件的 QRectF 交集，零尺寸组件跳过，返回 `List[OverlapInfo]`
- [ ] 实现 `OverlapDetector.detect_all(container, children)`：全量两两检测，返回重叠对列表 `List[Tuple[str,str]]`，用于重排后全量检测
- [ ] 实现 `services/layout/overlap_avoider.py` 中 `OverlapAvoider.avoid(source, overlaps, layout, spacing, container)`：layout=none 时返回空字典；vertical→向下推；horizontal→向右推；grid→向右优先空间不足向下；级联避让深度超 20 输出性能警告日志
- [ ] 编写单元测试 `tests/test_overlap.py`：覆盖 detect 单组件重叠/不重叠/零尺寸、detect_all 全量检测、avoid 各布局方向避让、级联避让、layout=none 不避让

**验收标准**：
- 拖拽组件 A 与 B 矩形有交集 → detect 返回 OverlapInfo（intersection_rect 宽高 > 0）
- 拖拽组件 A 与 B 矩形无交集 → detect 返回空列表
- layout=vertical, B 与 A 重叠 → B 被推到 A 下方 y = A.y + A.height + spacing
- layout=horizontal, B 与 A 重叠 → B 被推到 A 右侧 x = A.x + A.width + spacing
- layout=none 重叠 → avoid 返回空字典
- 级联避让超过 20 个组件 → 输出 warning 日志

**涉及文件**：`services/layout/overlap_detector.py`、`services/layout/overlap_avoider.py`、`tests/test_overlap.py`

**依赖**：任务 1

---

## 5. 实现重叠可视化（OverlapVisualizer）

- [ ] 实现 `services/layout/overlap_visualizer.py` 中 `OverlapVisualizer` 类：定义红色虚线画笔 `QPen(QColor("#FF0000"), 2, Qt.PenStyle.DashLine)`
- [ ] 实现 `show_overlaps(overlap_ids, canvas_view)`：清除不再重叠的指示器 → 为新重叠组件添加红色虚线矩形叠加层（QGraphicsRectItem，ZValue=100 确保最上层）
- [ ] 实现 `clear_overlaps()`：清除所有重叠视觉提示
- [ ] 实现 `_add_overlap_indicator(comp_id, item)` 和 `_remove_overlap_indicator(comp_id)` 内部方法

**验收标准**：
- 重叠组件显示红色虚线边框（线宽 2px、虚线样式）
- 非重叠组件不显示边框
- 调用 clear_overlaps 后所有红色提示消失
- 叠加层 ZValue=100 保证绘制在最上层

**涉及文件**：`services/layout/overlap_visualizer.py`

**依赖**：任务 1

---

## 6. EventBus 扩展与 Presenter 层集成

- [ ] 修改 `eventbus/event_bus.py`：新增 `layout_updated = Signal(LayoutUpdatedEvent)` 和 `overlap_detected = Signal(OverlapDetectedEvent)` 信号
- [ ] 修改 `presenters/canvas_presenter.py`：创建 LayoutEngine 实例（需 project_model 和 undo_manager），存储为实例属性
- [ ] 在 `CanvasPresenter._connect_component_signals()` 中增加对 `ContainerModel.data_changed` 的监听，当容器 layout/padding/spacing 属性变更时调用 `LayoutEngine.relayout(container)`
- [ ] 在子组件增删事件处理（`_on_component_added` / `_on_component_removed`）中增加逻辑：获取父容器，若 layout != "none" 则触发 `LayoutEngine.relayout()`
- [ ] LayoutEngine.relayout 完成后通过 EventBus 发布 `LayoutUpdatedEvent`

**验收标准**：
- EventBus 新增信号可正常 emit 和 connect
- 修改容器 layout 属性 → 自动触发布局重排 → 子组件位置更新
- 新增/删除子组件 → 父容器 layout != "none" 时自动重排
- 重排完成后 EventBus 发出 layout_updated 事件

**涉及文件**：`eventbus/event_bus.py`、`presenters/canvas_presenter.py`

**依赖**：任务 3、任务 4

---

## 7. Controller 层集成（拖拽结束 + resize 重排）

- [ ] 修改 `controllers/canvas_controller_v2.py` 的 `on_drag_end` 方法末尾：获取被拖组件的父容器 → `OverlapDetector.detect(source, siblings)` → 若 overlaps 非空且 auto_avoid_enabled → `OverlapAvoider.avoid()` → `LayoutEngine._apply_positions()` → `OverlapVisualizer.clear_overlaps()`
- [ ] 修改 `on_resize_end` 方法：检测被 resize 对象是否为容器且 layout != "none" → 调用 `LayoutEngine.relayout(container)`
- [ ] 确保拖拽结束后的重叠检测和避让逻辑不影响原有拖拽放置功能

**验收标准**：
- 拖拽组件到与兄弟组件重叠位置后释放 → 触发重叠检测
- 自动避让开启时，重叠组件被推到最近空位
- 自动避让关闭时，仅显示重叠提示不移动组件
- 容器 resize 结束且 layout != "none" → 子组件自动重排
- 容器 resize 且 layout = "none" → 子组件位置不变

**涉及文件**：`controllers/canvas_controller_v2.py`

**依赖**：任务 3、任务 4、任务 5、任务 6

---

## 8. View 层集成（实时重叠检测 + 父容器拖拽联动）

- [ ] 修改 `views/canvas.py` 中 `ComponentGraphicsItem.mouseMoveEvent` 拖拽分支：增加实时调用 `OverlapDetector.detect(dragged_comp, siblings)` → `OverlapVisualizer.show_overlaps(overlap_ids, canvas_view)`
- [ ] 修改 `ComponentGraphicsItem.mouseMoveEvent`：当拖拽对象是容器时，计算移动增量 (dx, dy)，调用 `LayoutEngine.move_children_with_parent(container_id, dx, dy)`
- [ ] 修改 `ComponentGraphicsItem.mouseReleaseEvent` 的 resize 结束分支：当 model.type == "container" 且 layout != "none" 时，触发 `LayoutEngine.relayout(container)`
- [ ] 确保 OverlapVisualizer 的叠加层在组件 paint 中正确绘制，不被组件自身内容遮挡

**验收标准**：
- 拖拽组件过程中实时显示/消除重叠红色虚线边框
- 拖拽父容器 → 子组件跟随移动（相对偏移量不变）
- 拖拽结束后重叠提示消除
- 容器 resize 结束 → layout != "none" 时子组件重排
- locked 子组件不参与联动移动

**涉及文件**：`views/canvas.py`

**依赖**：任务 5、任务 6、任务 7

---

## 9. Grid 布局增强与容器 Resize 响应式处理（次要功能合并）

- [ ] 验证 `GridLayoutStrategy` 的列数自动计算逻辑：确保容器宽度变化时列数正确更新，行优先填入正确
- [ ] 实现容器 resize 时的溢出检测与处理策略：溢出标记（overflow=True）→ 提供滚动选项（垂直溢出纵向滚动，水平溢出横向滚动）→ 可选缩放选项（缩放比例低于 0.3 时回退为滚动）
- [ ] 在 `ContainerRenderer.render` 中增加溢出状态下的视觉提示绘制（溢出边框/滚动条占位）
- [ ] 确保 layout=none 时容器 resize 不触发子组件重排（spec.md 5.3.1 规则 4）

**验收标准**：
- Grid 布局容器宽度从 400 缩小到 300 → 列数重新计算，子组件按新列数重排
- 子组件总高度超过容器内容区域 → overflow=True，提供滚动选项
- 缩放比例低于 0.3 → 不缩放，改为滚动
- layout=none 容器 resize → 子组件位置不变

**涉及文件**：`services/layout/layout_engine.py`、`renderers/container_renderer.py`

**依赖**：任务 3、任务 8

---

## 10. 运行时集成（Runner 布局计算）

- [ ] 修改 `runtime/runner.py` 的 `_calculate_relative_position` 方法：当容器 layout != "none" 时，调用 `LayoutEngine.relayout()` 计算子组件位置，而非直接使用组件 x/y 属性
- [ ] 确保运行时模式下父容器拖拽不触发子组件联动（联动仅限编辑器），运行时由布局引擎控制位置
- [ ] 验证运行时布局计算与编辑器布局计算结果一致

**验收标准**：
- 运行时容器 layout=vertical → 子组件按垂直布局正确排列
- 运行时拖拽父容器 → 子组件由布局引擎重排决定位置，不直接跟随
- 运行时布局计算结果与编辑器 relayout 结果一致

**涉及文件**：`runtime/runner.py`

**依赖**：任务 6、任务 8

---

## 11. 向后兼容与 ContainerModel 属性信号增强

- [ ] 修改 `models/components.py` 中 `ContainerModel`：确保 layout 默认值为 "none"、padding 默认值为 10、spacing 默认值为 5，升级后保持不变
- [ ] 在 ContainerModel 的 layout / padding / spacing setter 中增加 `layout_changed` 细粒度信号发射，使属性变更能精确触发布局重排（而非仅依赖粗粒度 data_changed）
- [ ] 验证已有项目加载后容器行为不变：layout=none 时子组件保持绝对定位，padding/spacing 保持原值

**验收标准**：
- 新建 ContainerModel → layout="none", padding=10, spacing=5
- 修改 layout 属性 → layout_changed 信号正确发射
- 已有项目（layout 默认 "none"）升级后子组件位置不变

**涉及文件**：`models/components.py`

**依赖**：任务 6

---

## 12. 端到端验证与集成测试

- [ ] 编写端到端测试 `tests/test_layout_e2e.py`：验证垂直/水平/网格/绝对定位布局的完整交互流程
- [ ] 验证拖拽过程中实时重叠检测和红色虚线边框显示/消除
- [ ] 验证拖拽结束后自动避让和级联避让的正确性
- [ ] 验证容器 resize 触发子组件重排和溢出处理
- [ ] 验证父容器拖拽时子组件联动移动
- [ ] 验证撤销/重做功能：重排操作可 undo/redo，位置正确回滚
- [ ] 验证已有项目向后兼容性
- [ ] 性能测试：100 个子组件重排 ≤ 16ms，重叠检测 ≤ 8ms

**验收标准**：
- 所有布局模式交互流程正确
- 实时重叠检测响应 ≤ 8ms
- 重排计算 ≤ 16ms（100 子组件）
- 撤销/重做功能正常
- 向后兼容无破坏

**涉及文件**：`tests/test_layout_e2e.py`、`tests/test_layout_strategy.py`、`tests/test_layout_engine.py`、`tests/test_overlap.py`

**依赖**：任务 1-11 全部完成

---

## 任务依赖关系图

```
任务 1 (包结构+数据模型)
  ├─→ 任务 2 (布局策略)
  ├─→ 任务 4 (重叠检测+避让)
  └─→ 任务 5 (重叠可视化)

任务 2 ──→ 任务 3 (LayoutEngine 主类)
任务 3 + 任务 4 ──→ 任务 6 (EventBus + Presenter 集成)
任务 3 + 任务 4 + 任务 5 + 任务 6 ──→ 任务 7 (Controller 集成)
任务 5 + 任务 6 + 任务 7 ──→ 任务 8 (View 集成)
任务 3 + 任务 8 ──→ 任务 9 (Grid增强+Resize响应式)
任务 6 + 任务 8 ──→ 任务 10 (运行时集成)
任务 6 ──→ 任务 11 (向后兼容+信号增强)
任务 1-11 ──→ 任务 12 (端到端验证)
```

## 推荐执行顺序

1 → 2 → 4 → 5 → 3 → 6 → 11 → 7 → 8 → 9 → 10 → 12
