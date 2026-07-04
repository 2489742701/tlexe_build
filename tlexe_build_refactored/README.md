# UIDevTool (Refactored)

A powerful, easy-to-use desktop application visual builder. It supports drag-and-drop UI design, property editing, behavior configuration, and real-time execution.

## Architecture Overview

UIDevTool has been fully refactored into a clean, modern **MVC + Services** architecture, driven by Pydantic and PySide6:

- **Model Layer (`models/`)**: 
  All component properties are defined using `SignalProperty`, which provides automated signal emission on changes. Models are pure Pydantic-based objects (`ComponentModel`, `ProjectModel`), ensuring automated serialization to and from JSON (`.itexe` / `.py` formats).
- **View Layer (`views/`)**:
  Manages the PySide6 UI. `Canvas` handles the drag-and-drop workspace, while the `PropertyPanel` relies on isolated component editors (`PropertyEditorRegistry`).
- **Controller Layer (`controllers/`)**:
  The `ProjectController` orchestrates interaction between the UI (Views) and the data (Models), handling commands such as opening projects, selecting components, and applying actions (Undo/Redo).
- **Service Layer (`services/`)**:
  Decoupled services handle `AutoSaveService` (temp file generation), `ExportService`, and component initialization.
- **Component Registry (`component_registry.py`)**:
  All models, renderers, and editors are dynamically registered in `registry_init.py` via the `@register_component` and `@register_property_editor` decorators. This prevents hardcoded dependencies and guarantees loose coupling.

## Key Features

- **20+ Supported Components**: Including Containers, Labels, ProgressBars, Image Carousel, Alternating Playback (combining text and image toggles), Video, and Inputs.
- **Automated Registry & Factory**: Creating a new widget simply involves defining a Model and a Renderer, then registering them. The Factory handles dynamic instantiation.
- **Visual Event Binding**: Bind "Click" behaviors dynamically to UI components, controlling window logic, displaying notifications, and toggling component states.
- **Real-Time Engine (`runtime/`)**: When clicking "Run," the system spawns the `Runner`, injecting models into `ComponentRenderer` to reconstruct the fully functional app.

## Project Structure

```text
tlexe_build_refactored/
├── main.py                     # Entry point
├── models/                     # Data Models & Schemas (Pydantic, SignalProperty)
├── views/                      # UI Views (Canvas, PropertyPanel, Editors)
├── controllers/                # Logic controllers (ProjectController)
├── services/                   # Background services (AutoSave)
├── renderers/                  # View generators for canvas and runtime
├── runtime/                    # Execution engine (Runner, ActionExecutor)
├── utils/                      # Utilities (ComponentFactory, UndoManager)
├── docs/                       # Historic docs and guidelines
└── styles/                     # Qt Stylesheets
```

## Future Development & Roadmap

1. **State Management Enhancement**: 
   Introduce a global Redux-like state tree (`VariableManager`) that components can subscribe to, allowing for dynamic cross-component updates without explicit point-to-point event bindings.
2. **Plugin System**: 
   Implement a `plugins/` directory where developers can drop in a self-contained `.py` file containing a `@register_component` class. UIDevTool will automatically scan and inject it into the component toolbox.
3. **Advanced Visual Logic Editor**:
   Transition the current linear action list into a visual node-based blueprint editor (similar to Unreal Engine's Blueprints).
4. **Layout Engine Upgrades**:
   Add support for Flexbox-like positioning and anchors, allowing designed windows to scale gracefully across different resolutions.
5. **Rich Animations**:
   Expand `AlternatingModel` and other media models with transition effects (fade, slide) managed centrally via Qt Animation Framework.

## How to Run

```bash
python main.py
```
