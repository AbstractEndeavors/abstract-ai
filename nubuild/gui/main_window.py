# gui/main_window.py
"""
Top-level QMainWindow that assembles all GUI widgets.

Does not contain any business logic. Receives registry + event_bus,
passes them to child widgets so they can self-register.
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt

from .progress_frame import ProgressFrame, OutputOptionsFrame
from .prompt_tabs import PromptTabsWidget
from .utility_tabs import UtilityTabsWidget


class MainWindow(QMainWindow):
    def __init__(self, registry, event_bus, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Abstract AI Console")
        self.resize(1200, 800)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(10)

        # top: progress + output options
        self.progress_frame = ProgressFrame(
            registry=registry, event_bus=event_bus,
        )
        layout.addWidget(self.progress_frame)

        self.output_options = OutputOptionsFrame(
            registry=registry, event_bus=event_bus,
        )
        layout.addWidget(self.output_options)

        # main split: prompt tabs (left) + utility tabs (right)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.prompt_tabs = PromptTabsWidget(
            registry=registry, event_bus=event_bus,
        )
        splitter.addWidget(self.prompt_tabs)

        self.utility_tabs = UtilityTabsWidget(
            registry=registry, event_bus=event_bus,
        )
        splitter.addWidget(self.utility_tabs)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter)

        self.setCentralWidget(central)

        # status bar
        self.statusBar().showMessage("Ready")
