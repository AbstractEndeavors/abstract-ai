# gui/helpers.py
"""
GUI helper utilities.

- text_to_key(): the key-naming convention shared across the whole app
- auto_register(): infers read/write functions from widget type and
  registers into the WidgetRegistry + connects signals to the EventBus
"""
import logging

logger = logging.getLogger(__name__)


def text_to_key(text, section=""):
    """
    Convert a human-readable label to the -KEY- format used throughout
    the app for widget identification.

    Examples:
        text_to_key("prompt_data")          -> "-PROMPT_DATA-"
        text_to_key("instructions", "BOOL") -> "-INSTRUCTIONS_BOOL-"
        text_to_key("chunk title", "url")   -> "-CHUNK_TITLE_URL-"
    """
    upper = text.upper().replace(" ", "_")
    if section:
        upper = upper + "_" + section.upper()
    return "-" + upper + "-"


def auto_register(registry, event_bus, key, widget):
    """
    Infer read/write functions from the PyQt6 widget type, register into
    the WidgetRegistry, and connect the appropriate change signal to
    the EventBus.

    Supported widget types:
        QLineEdit, QTextEdit, QPlainTextEdit, QCheckBox, QComboBox,
        QProgressBar, QListWidget, QPushButton

    For QPushButton, only the clicked signal is wired (no read/write —
    buttons are fire-and-forget).
    """
    # late imports so this module can be imported without PyQt6 installed
    # (useful for testing schemas/bus/registry in isolation)
    from PyQt6.QtWidgets import (
        QLineEdit, QTextEdit, QPlainTextEdit,
        QCheckBox, QComboBox, QProgressBar,
        QListWidget, QPushButton,
    )

    if isinstance(widget, QLineEdit):
        registry.register(
            key, widget,
            read_func=widget.text,
            write_func=widget.setText,
        )
        widget.textChanged.connect(lambda _text: event_bus.emit(key))

    elif isinstance(widget, QTextEdit):
        registry.register(
            key, widget,
            read_func=widget.toPlainText,
            write_func=widget.setPlainText,
        )
        # textChanged fires on every keystroke; that's fine for the bus
        widget.textChanged.connect(lambda: event_bus.emit(key))

    elif isinstance(widget, QPlainTextEdit):
        registry.register(
            key, widget,
            read_func=widget.toPlainText,
            write_func=widget.setPlainText,
        )
        widget.textChanged.connect(lambda: event_bus.emit(key))

    elif isinstance(widget, QCheckBox):
        registry.register(
            key, widget,
            read_func=widget.isChecked,
            write_func=widget.setChecked,
        )
        widget.toggled.connect(lambda _checked: event_bus.emit(key))

    elif isinstance(widget, QComboBox):
        registry.register(
            key, widget,
            read_func=widget.currentText,
            write_func=lambda v: widget.setCurrentText(str(v)),
        )
        widget.currentTextChanged.connect(lambda _text: event_bus.emit(key))

    elif isinstance(widget, QProgressBar):
        registry.register(
            key, widget,
            read_func=widget.value,
            write_func=widget.setValue,
        )
        # no signal — progress bars are write-only from the controller

    elif isinstance(widget, QListWidget):
        registry.register(
            key, widget,
            read_func=_list_widget_read(widget),
            write_func=_list_widget_write(widget),
        )
        widget.currentItemChanged.connect(lambda _cur, _prev: event_bus.emit(key))

    elif isinstance(widget, QPushButton):
        # buttons have no read/write value — just wire the click signal
        registry.register(key, widget, read_func=lambda: None, write_func=lambda v: None)
        widget.clicked.connect(lambda: event_bus.emit(key))

    else:
        logger.warning(
            "auto_register: unsupported widget type %s for key '%s'",
            type(widget).__name__, key,
        )


def _list_widget_read(widget):
    """Return a callable that reads all items from a QListWidget."""
    def _read():
        items = []
        for i in range(widget.count()):
            item = widget.item(i)
            if item is not None:
                items.append(item.text())
        return items
    return _read


def _list_widget_write(widget):
    """Return a callable that replaces all items in a QListWidget."""
    def _write(values):
        widget.clear()
        if isinstance(values, (list, tuple)):
            widget.addItems([str(v) for v in values])
        elif isinstance(values, str):
            widget.addItem(values)
    return _write


# ── Navigation helpers ───────────────────────────────────────────────

def get_nav_keys(name, section=True):
    """
    Return the back/number/forward key tuple for a navigation bar.

    If section=True:  "-NAME SECTION BACK-", "-NAME SECTION NUMBER-", "-NAME SECTION FORWARD-"
    If section=False: "-NAME BACK-",         "-NAME NUMBER-",         "-NAME FORWARD-"
    """
    insert = "%s %s" % (name, "SECTION " if section else "")
    insert = insert.strip()
    back_key = text_to_key(insert + " back")
    number_key = text_to_key(insert + " number")
    forward_key = text_to_key(insert + " forward")
    return back_key, number_key, forward_key
