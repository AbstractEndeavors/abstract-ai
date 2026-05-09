# gui/progress_frame.py
"""
Top-of-window widgets: progress bar, query title, response navigation,
and the submit/clear/readme buttons.
"""
from PyQt6.QtWidgets import (
    QGroupBox, QFrame, QWidget,
    QHBoxLayout, QVBoxLayout,
    QLineEdit, QProgressBar, QPushButton,
)
from .helpers import text_to_key, auto_register
from .navigation_bar import NavigationBar


class ProgressFrame(QGroupBox):
    """Progress text + bar + query count, title input, response nav."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__("PROGRESS", parent)
        left_layout = QVBoxLayout(self)

        # row 1: progress text, bar, query count
        row1 = QHBoxLayout()

        self.progress_text = QLineEdit("Awaiting Prompt")
        self.progress_text.setReadOnly(True)
        self.progress_text.setFixedHeight(24)
        self.progress_text.setMinimumWidth(200)
        row1.addWidget(self.progress_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setMaximumWidth(100)
        row1.addWidget(self.progress_bar)

        self.query_count = QLineEdit("0")
        self.query_count.setReadOnly(True)
        self.query_count.setFixedHeight(24)
        self.query_count.setMinimumWidth(50)
        row1.addWidget(self.query_count)

        left_layout.addLayout(row1)

        # row 2: title input + response nav
        row2 = QHBoxLayout()

        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        title_layout = QHBoxLayout(title_frame)
        self.query_title = QLineEdit("title of prompt")
        self.query_title.setFixedHeight(24)
        self.query_title.setMinimumWidth(200)
        title_layout.addWidget(self.query_title)
        row2.addWidget(title_frame)

        self.resp_nav = NavigationBar(
            "response text", section=False,
            registry=registry, event_bus=event_bus,
        )
        row2.addWidget(self.resp_nav)

        left_layout.addLayout(row2)

        # register widgets
        if registry and event_bus:
            auto_register(registry, event_bus, "-PROGRESS_TEXT-", self.progress_text)
            auto_register(registry, event_bus, "-PROGRESS-", self.progress_bar)
            auto_register(registry, event_bus, "-QUERY_COUNT-", self.query_count)
            auto_register(registry, event_bus, text_to_key("title input"), self.query_title)


class OutputOptionsFrame(QFrame):
    """Submit, Clear Requests, Clear Chunks, Gen Readme buttons."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self)
        layout.setSpacing(20)

        buttons = [
            ("SUBMIT QUERY", "-SUBMIT_QUERY-"),
            ("CLEAR REQUESTS", "-CLEAR_REQUESTS-"),
            ("CLEAR CHUNKS", "-CLEAR_CHUNKS-"),
            ("GEN README", "-GENERATE_README-"),
        ]

        self._buttons = {}
        for label, key in buttons:
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setMinimumWidth(120)
            layout.addWidget(btn)
            self._buttons[key] = btn

            if registry and event_bus:
                auto_register(registry, event_bus, key, btn)
