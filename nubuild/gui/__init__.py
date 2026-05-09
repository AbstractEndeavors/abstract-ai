# gui/__init__.py
from .widget_registry import WidgetRegistry
from .event_bus import EventBus
from .helpers import text_to_key, auto_register, get_nav_keys

# MainWindow and widget modules are not imported here to avoid
# requiring PyQt6 at import time. Import them directly when needed:
#   from abstract_ai.gui.main_window import MainWindow
