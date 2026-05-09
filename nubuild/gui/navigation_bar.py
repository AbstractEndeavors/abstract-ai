# gui/navigation_bar.py
"""
Reusable navigation bar widget: [<-] [number] [->]

Registers its three widgets into the registry and connects signals
to the event bus.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QSpacerItem, QSizePolicy
from .helpers import text_to_key, auto_register


class NavigationBar(QWidget):
    """
    Args:
        name: domain name (e.g. "request", "chunk", "query")
        section: if True, keys are "-NAME SECTION BACK-" etc.
                 if False, keys are "-NAME BACK-" etc.
        registry: WidgetRegistry
        event_bus: EventBus
    """

    def __init__(self, name, section=True, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        insert = "%s %s" % (name, "SECTION " if section else "")
        insert = insert.strip()

        back_key = text_to_key(insert + " BACK")
        number_key = text_to_key(insert + " NUMBER")
        forward_key = text_to_key(insert + " FORWARD")

        # spacer left
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.back_btn = QPushButton("<-")
        self.back_btn.setFixedHeight(24)
        layout.addWidget(self.back_btn)

        self.number_edit = QLineEdit("0")
        self.number_edit.setFixedWidth(40)
        self.number_edit.setFixedHeight(24)
        layout.addWidget(self.number_edit)

        self.forward_btn = QPushButton("->")
        self.forward_btn.setFixedHeight(24)
        layout.addWidget(self.forward_btn)

        # spacer right
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # register + wire
        if registry and event_bus:
            auto_register(registry, event_bus, back_key, self.back_btn)
            auto_register(registry, event_bus, number_key, self.number_edit)
            auto_register(registry, event_bus, forward_key, self.forward_btn)
