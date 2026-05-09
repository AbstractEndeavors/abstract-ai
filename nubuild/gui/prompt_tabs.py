# gui/prompt_tabs.py
"""
Left-side prompt tabs: REQUEST, PROMPT DATA, CHUNKS, QUERY, INSTRUCTIONS.
"""
from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QGroupBox,
    QTextEdit, QCheckBox, QGridLayout,
)
from PyQt6.QtCore import Qt
from .helpers import text_to_key, auto_register
from .navigation_bar import NavigationBar
from ..schemas import INSTRUCTION_KEYS


class PromptTab(QWidget):
    """
    A tab with optional section/sub-section navigation and a multiline
    text area.

    Args:
        title: domain name (e.g. "request", "prompt_data", "chunks", "query")
        with_subsection: if True, adds a second (item-level) nav bar
    """

    def __init__(self, title, with_subsection=False,
                 registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # section navigation
        layout.addWidget(NavigationBar(
            title, section=True, registry=registry, event_bus=event_bus,
        ))

        if with_subsection:
            layout.addWidget(NavigationBar(
                title, section=False, registry=registry, event_bus=event_bus,
            ))

        # data frame
        frame = QGroupBox("%s DATA" % title.upper())
        frame_layout = QVBoxLayout(frame)
        self.text_edit = QTextEdit()
        self.text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        frame_layout.addWidget(self.text_edit)
        layout.addWidget(frame)

        # figure out the key for this text area
        if title.lower() in ("request",):
            key = text_to_key("request")
        elif title.lower() in ("prompt_data", "prompt data"):
            key = text_to_key("prompt_data data")
        elif title.lower() in ("chunks",):
            key = text_to_key("chunk sectioned data")
        elif title.lower() in ("query",):
            key = text_to_key("query")
        else:
            key = text_to_key(title)

        if registry and event_bus:
            auto_register(registry, event_bus, key, self.text_edit)


class InstructionsTab(QWidget):
    """
    INSTRUCTIONS tab: section nav, main instructions text area,
    and a grid of instruction bool checkboxes.
    """

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # section navigation
        layout.addWidget(NavigationBar(
            "instructions", section=True,
            registry=registry, event_bus=event_bus,
        ))

        # main instructions frame
        frame = QGroupBox("INSTRUCTIONS")
        frame_layout = QVBoxLayout(frame)

        # assembled instructions display
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setObjectName("-INSTRUCTIONS_TEXT-")
        self.instructions_edit.setPlaceholderText("Assembled instructions will appear here")
        frame_layout.addWidget(self.instructions_edit)

        if registry and event_bus:
            auto_register(registry, event_bus, "-INSTRUCTIONS_TEXT-", self.instructions_edit)

        # instruction bool checkboxes (excluding "instructions" which is in settings)
        sub_widget = QWidget()
        sub_layout = QGridLayout(sub_widget)

        display_keys = [k for k in INSTRUCTION_KEYS if k != "instructions"]
        self._checkboxes = {}

        for idx, key in enumerate(display_keys):
            cb = QCheckBox(key.replace("_", " ").title())
            bool_key = text_to_key(key, section="BOOL")
            row = idx // 2
            col = idx % 2
            sub_layout.addWidget(cb, row, col)
            self._checkboxes[key] = cb

            if registry and event_bus:
                auto_register(registry, event_bus, bool_key, cb)

        frame_layout.addWidget(sub_widget)
        layout.addWidget(frame)


class PromptTabsWidget(QTabWidget):
    """Container for all prompt-side tabs."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)

        self.request_tab = PromptTab(
            "request", with_subsection=False,
            registry=registry, event_bus=event_bus,
        )
        self.addTab(self.request_tab, "REQUEST")

        self.prompt_data_tab = PromptTab(
            "prompt_data", with_subsection=False,
            registry=registry, event_bus=event_bus,
        )
        self.addTab(self.prompt_data_tab, "PROMPT DATA")

        self.chunks_tab = PromptTab(
            "chunks", with_subsection=True,
            registry=registry, event_bus=event_bus,
        )
        self.addTab(self.chunks_tab, "CHUNKS")

        self.query_tab = PromptTab(
            "query", with_subsection=True,
            registry=registry, event_bus=event_bus,
        )
        self.addTab(self.query_tab, "QUERY")

        self.instructions_tab = InstructionsTab(
            registry=registry, event_bus=event_bus,
        )
        self.addTab(self.instructions_tab, "INSTRUCTIONS")
