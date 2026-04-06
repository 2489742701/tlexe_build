import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

from utils.component_factory import ComponentFactory
from renderers.renderer_factory_v2 import RendererFactoryV2
from views.component_panel import COMPONENT_CATEGORIES

print("=== ComponentFactory ===")
for t in ['button','label','input','textarea','checkbox','combobox',
          'listwidget','groupbox','container','progressbar',
          'hidden_button','image_button','image_carousel','image','video']:
    ok = hasattr(ComponentFactory, '_create_' + t)
    print(f"  {t}: {'OK' if ok else 'MISSING'}")

print("\n=== RendererFactoryV2 ===")
for t in sorted(RendererFactoryV2._registry.keys()):
    print(f"  {t}: OK")

print("\n=== ComponentPanel ===")
for cat, items in COMPONENT_CATEGORIES.items():
    print(f"  {cat}: {list(items.keys())}")