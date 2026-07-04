# 模型层开发文档

> 本文档面向在 `models/` 目录下开发的人员，详细说明架构约定和 API。

## 快速参考

### 新增组件属性

```python
# 在 components.py 的组件类中添加一行即可
class MyModel(ComponentModel):
    my_field: str = SignalProperty("默认值")
```

这一行自动获得：
- `model.my_field` getter
- `model.my_field = "新值"` setter（变更时自动 emit 信号）
- `to_dict()` 自动序列化
- `from_dict(data)` 自动反序列化

### 新增纯数据结构

```python
# 在 schemas.py 中添加 Pydantic 模型
class MyConfig(BaseModel):
    name: str = ""
    value: int = 0
```

自动获得 `model_dump()` / `model_validate()` + 类型验证。

---

## SignalProperty 详解

### 基本用法

```python
# 简单属性
name: str = SignalProperty("")

# 可变默认值（list/dict 必须用 default_factory）
items: list = SignalProperty(default_factory=list)
params: dict = SignalProperty(default_factory=dict)

# 只读属性（如 id）
id: str = SignalProperty("", readonly=True)

# 序列化别名（JSON 中叫 comp_type，Python 中叫 type）
type: str = SignalProperty("", readonly=True, serialize_as="comp_type")
```

### 验证与变换

```python
# validator: 返回 False 则拒绝赋值，属性不变
scale_mode: str = SignalProperty("fit",
    validator=lambda v: v in ['fill', 'fit', 'stretch', 'center', 'tile'])

# transform: 对值做变换后再赋值（如范围钳制、类型转换）
duration: int = SignalProperty(3000,
    transform=lambda v: max(500, min(30000, int(v))))

# validator + transform 可以组合
# transform 先执行，validator 验证变换后的值
```

### 信号控制

```python
# 默认只 emit data_changed
name: str = SignalProperty("")

# 同时 emit 多个信号
width: int = SignalProperty(120, emit=('size_changed', 'data_changed'))

# 带参数的信号（emit_args 映射信号名到参数工厂）
x: int = SignalProperty(0,
    emit=('position_changed', 'data_changed'),
    emit_args={'position_changed': lambda o: (o._x, o._y)})

# 自定义信号名
current_index: int = SignalProperty(0, emit=('current_index_changed', 'data_changed'))
```

### _loading 模式

`from_dict()` 批量加载时设置 `_loading = True`，期间 SignalProperty 不 emit 信号，避免频繁通知。

```python
instance._loading = True
instance._x = 100
instance._y = 200
instance._loading = False
```

---

## Pydantic Schema 详解

### 所有 Schema 列表

| Schema | 用途 | 所在文件 |
|--------|------|----------|
| `StyleConfig` | 组件样式（颜色、字体、边框） | schemas.py |
| `ActionConfig` | 行为配置（动作类型、参数、代码） | schemas.py |
| `ActionDefinition` | 动作定义（类型+显示名+描述） | schemas.py |
| `VariableSchema` | 变量数据（名字/数字/密码等） | schemas.py |
| `BindingConfig` | 变量绑定配置 | schemas.py |
| `ConditionalActionConfig` | 条件动作配置 | schemas.py |
| `SignalConnectionSchema` | 信号连接配置 | schemas.py |
| `CommunicationChannelSchema` | 通信通道 | schemas.py |

### 枚举列表

| 枚举 | 值类型 | 用途 |
|------|--------|------|
| `ActionType` | str | 统一的动作类型（31 种） |
| `WindowType` | str | 窗口类型（main/event） |
| `VariableType` | str | 变量类型（名字/数字/密码等） |
| `SignalType` | str | 通信信号类型 |
| `CommActionType` | str | 通信动作类型 |

### 序列化约定

```python
# Pydantic → dict
data = config.model_dump()

# dict → Pydantic
config = StyleConfig.model_validate(data)

# 枚举序列化为字符串值
# ActionType.OPEN_EVENT → "open_event"
# VariableType.NUMBER → "数字"
```

---

## ComponentModel 基类 API

### 基础属性（所有组件共有）

| 属性 | 类型 | SignalProperty | 说明 |
|------|------|----------------|------|
| id | str | readonly | 组件唯一 ID |
| type | str | readonly, serialize_as="comp_type" | 组件类型 |
| name | str | ✓ | 组件名称 |
| x, y | int | ✓ (position_changed) | 位置 |
| width, height | int | ✓ (size_changed) | 尺寸 |
| text | str | ✓ | 文本内容 |
| parent_id | str | ✓ | 父容器 ID |
| style | StyleConfig | ✓ (style_changed) | 样式配置 |
| action | ActionConfig | ✓ (action_changed) | 行为配置 |
| visible | bool | ✓ | 可见性 |
| enabled | bool | ✓ | 可用性 |
| custom_props | dict | ✓ | 自定义属性 |
| h_align, v_align | str | ✓ | 对齐方式 |

### 方法

| 方法 | 说明 |
|------|------|
| `set_position(x, y)` | 原子设置位置，一次 emit |
| `set_size(w, h)` | 原子设置尺寸，一次 emit |
| `to_dict()` | 序列化为 dict（自动收集子类 SignalProperty） |
| `from_dict(data)` | 从 dict 反序列化 |

### 子类扩展属性自动收集

```python
class ButtonModel(ComponentModel):
    target_window_id: str = SignalProperty("")  # 自动被 to_dict/from_dict 收集

btn = ButtonModel()
d = btn.to_dict()
# d 包含 'target_window_id' 字段

btn2 = ButtonModel.from_dict(d)
# btn2.target_window_id 被自动还原
```

---

## 常见模式

### 组件有子元素列表

```python
class ContainerModel(ComponentModel):
    children: list = SignalProperty(default_factory=list)

    def add_child(self, child_id: str):
        if child_id not in self._children:
            self._children.append(child_id)
            self.data_changed.emit()
```

### 组件有计算属性

```python
class ButtonModel(ComponentModel):
    target_window_id: str = SignalProperty("")

    @property
    def has_branch(self) -> bool:  # 不用 SignalProperty，纯计算
        return bool(self._target_window_id)
```

### 组件有自定义信号

```python
class AlternatingModel(ComponentModel):
    started = Signal()           # Qt 原生信号
    stopped = Signal(int, str)

    items: list = SignalProperty(default_factory=list)
```

### 组件需要特殊初始化默认样式

```python
class LabelModel(ComponentModel):
    def __init__(self, ...):
        super().__init__("label", name, x, y, width, height, text, parent_id)
        self._style.background_color = "transparent"  # 覆盖默认样式
        self._style.border_color = "transparent"
        self._style.border_width = 0
```

---

## 注意事项

1. **list/dict 默认值必须用 `default_factory`**，否则所有实例共享同一对象
2. **Pydantic 和 QObject 不混用** — 需要 Signal 的类继承 QObject，纯数据用 Pydantic
3. **`from_dict` 中直接设置 storage 属性**（`instance._xxx = value`）绕过描述符，不触发信号
4. **`emit_args` 必须用于带参数的信号**（如 `Signal(int, int)`），否则 TypeError
5. **新增枚举值只改 `schemas.py`**，不要在其他文件定义重复枚举