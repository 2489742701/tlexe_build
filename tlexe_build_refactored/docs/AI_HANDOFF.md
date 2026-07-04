# UIDevTool AI Handoff & Architecture Guide

Welcome! If you are an AI assistant reading this, this document contains everything you need to know to immediately start contributing to **UIDevTool**.

## 1. Project Overview
UIDevTool is a desktop UI builder built with **Python (PySide6)**. It allows users to drag and drop components, edit their properties, set up behavioral actions (e.g., clicking a button opens a window), and run the application in a decoupled `runtime/` engine.

## 2. Core Architecture: MVC + Services + Registry

The codebase has undergone a major refactoring to remove tight coupling. It follows a strict **MVC** pattern enhanced with a **Registry Pattern**:

- **Model Layer (`models/`)**: 
  - Pure data representations of components.
  - **CRITICAL**: Models do NOT inherit from PySide6 widgets. They inherit from `ComponentModel` (which inherits from `QObject`).
  - **CRITICAL**: All dynamic properties must be defined using the custom `SignalProperty` descriptor. This automatically generates getters, setters, Qt Signals, and handles JSON serialization.
  - Examples: `ButtonModel`, `WindowModel`, `AlternatingModel`.
  - Simple static schemas (configs) use Pydantic `BaseModel` (e.g., `StyleConfig`, `ActionConfig` in `schemas.py`). Do not mix Pydantic with `QObject`.

- **View Layer (`views/`)**: 
  - The UI of the builder itself. 
  - `Canvas`: Renders the WYSIWYG editor using Qt Graphics Framework.
  - `PropertyPanel`: The right-side panel that edits model properties.
  - **CRITICAL**: The property panel dynamically loads editors for components via `@register_property_editor` (found in `views/property_editors/`).

- **Registry Pattern (`models/registry_init.py` & `component_registry.py`)**:
  - Components are NO LONGER hardcoded in a massive `if/else` block. 
  - Every component has a Model, a Renderer (View), and an Editor. They are tied together dynamically in `models/registry_init.py` using `_r(comp_type, model_class, renderer_class, name, category, desc)`.

- **Runtime Engine (`runtime/` & `renderers/`)**:
  - The `renderers/` directory contains `ComponentRenderer` classes (e.g., `ButtonRenderer`). These are used both by the `Canvas` (in design mode) and the `Runner` (in execution mode).
  - When the user clicks "Run", `runtime/runner.py` reconstructs the UI tree by mapping Models to their Renderers.

## 3. How to Add a New Component (Standard Flow)

If the user asks you to add a new component (e.g., "Add a Slider"):

1. **Create the Model** (`models/components.py`):
   ```python
   class SliderModel(ComponentModel):
       value: int = SignalProperty(50)
       min_val: int = SignalProperty(0)
       max_val: int = SignalProperty(100)
       
       def __init__(self, **kwargs):
           kwargs.setdefault('name', 'Slider')
           super().__init__(comp_type="slider", **kwargs)
   ```
2. **Create the Renderer** (`renderers/component_renderer.py`):
   ```python
   class SliderRenderer(ComponentRenderer):
       def create_widget(self, parent):
           widget = QSlider(Qt.Orientation.Horizontal, parent)
           # Bind model to widget...
           return widget
   ```
3. **Register It** (`models/registry_init.py`):
   ```python
   _r('slider', 'SliderModel', 'SliderRenderer', 'Slider', 'input', 'A sliding input component')
   ```
4. **Create a Property Editor** (`views/property_editors/slider_editor.py`):
   Create a subclass of `BasePropertyEditor` decorated with `@register_property_editor('slider')` to expose `min_val` and `max_val` to the UI.
5. **Add to Toolbox UI** (`views/component_panel.py`):
   Add `"slider": "Slider"` to the `COMPONENT_CATEGORIES` dict so the user can drag it into the canvas.

## 4. Key Systems to Understand

- **SignalProperty (`models/base.py`)**:
  `my_val = SignalProperty(10)` automatically emits `data_changed` when modified. It can take validators and transforms. E.g., `animation_duration: int = SignalProperty(3000, transform=lambda v: max(500, min(30000, int(v))))`.
- **ComponentFactory (`utils/component_factory.py`)**:
  Creates renderers for models. Do not modify this file to add components; it dynamically fetches creators from the Registry.
- **Event Binding (`models/schemas.py` -> `ActionConfig`)**:
  Components can trigger actions. `ActionConfig` holds what happens (e.g., open a window, start animation). Renderers bind these in `_bind_events`.

## 5. Known Quirks & Gotchas
- **Window Resizing**: In runtime, windows should use `.setFixedSize()` if frameless to prevent unexpected maximization.
- **Temporary Projects**: The `AutoSaveService` generates `unsaved_project_xxx.py` in the system Temp dir. The logic in `main.py` explicitly filters these out from the "Recent Projects" list so they do not pollute the welcome screen.
- **Alternating Component**: `TextAlternating` and `ImageAlternating` have been unified into a single `AlternatingModel` (`comp_type="alternating"`). The user can toggle the display mode in the property editor. Legacy types are kept in `registry_init.py` solely for backward compatibility with old save files.

## 6. Roadmap / Future Work
If the user asks for new architectural features, suggest these:
1. **Global Variable Manager / State Tree**: Currently, components communicate directly. A global state tree (Redux-style) would allow components to bind to a global variable (e.g., `{{user_name}}`) and auto-update.
2. **Plugin System**: Allowing users to drop `.py` scripts in a `plugins/` directory that auto-register via `@register_component` without modifying core files.
3. **Node-based Action Editor**: Moving from a linear list of actions to a visual node-based blueprint system for advanced logic.
