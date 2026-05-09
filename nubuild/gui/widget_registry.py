# gui/widget_registry.py
"""
Central lookup for named widgets.

The GUI layer registers widgets at construction time.
The controller layer reads/writes by string key.

This replaces AbstractWindowManager.get_from_value / update_value
with an explicit, inspectable registry. No manager ever imports this
module — only the controller and the GUI layer touch it.
"""
import logging

logger = logging.getLogger(__name__)


class WidgetRegistry:
    """
    String-keyed widget store with pluggable read/write functions.

    Usage (GUI side):
        registry.register("-MY_KEY-", widget,
                          read_func=widget.text,
                          write_func=widget.setText)

    Usage (controller side):
        value = registry.read("-MY_KEY-")
        registry.write("-MY_KEY-", "new value")
    """

    def __init__(self):
        self._widgets = {}          # key -> QWidget reference
        self._read_funcs = {}       # key -> callable() -> value
        self._write_funcs = {}      # key -> callable(value) -> None

    # ── registration (called by GUI layer only) ──────────────────────

    def register(self, key, widget, read_func=None, write_func=None):
        """
        Register a widget under a string key.

        read_func / write_func are callables that know how to get/set
        the widget's value. If omitted, auto_register (in helpers.py)
        should be used instead, which infers them from the widget type.
        """
        if key in self._widgets:
            logger.debug("WidgetRegistry: overwriting key %s", key)
        self._widgets[key] = widget
        if read_func is not None:
            self._read_funcs[key] = read_func
        if write_func is not None:
            self._write_funcs[key] = write_func

    def unregister(self, key):
        """Remove a widget from the registry."""
        self._widgets.pop(key, None)
        self._read_funcs.pop(key, None)
        self._write_funcs.pop(key, None)

    # ── access (called by controller layer) ──────────────────────────

    def read(self, key, default=""):
        """Read the current value of a registered widget by key."""
        func = self._read_funcs.get(key)
        if func is None:
            logger.warning("WidgetRegistry.read: no reader for key '%s'", key)
            return default
        try:
            return func()
        except Exception:
            logger.exception("WidgetRegistry.read failed for key '%s'", key)
            return default

    def write(self, key, value):
        """Write a value to a registered widget by key."""
        func = self._write_funcs.get(key)
        if func is None:
            logger.warning("WidgetRegistry.write: no writer for key '%s'", key)
            return
        try:
            func(value)
        except Exception:
            logger.exception("WidgetRegistry.write failed for key '%s'", key)

    def exists(self, key):
        """Check if a key is registered."""
        return key in self._widgets

    def read_all(self):
        """
        Return a dict of {key: current_value} for every readable widget.
        Equivalent to the old window_mgr.get_values().
        """
        result = {}
        for key in self._read_funcs:
            result[key] = self.read(key)
        return result

    def widget(self, key):
        """
        Direct widget access. Use sparingly — only for type-specific
        operations like update_bar() on a QProgressBar.
        """
        return self._widgets.get(key)

    def keys(self):
        """Return all registered keys."""
        return list(self._widgets.keys())

    def __contains__(self, key):
        return key in self._widgets

    def __len__(self):
        return len(self._widgets)

    def __bool__(self):
        # An empty registry is still a valid registry — always truthy.
        return True

    def __repr__(self):
        return "WidgetRegistry(%d keys)" % len(self._widgets)
