# gui/utility_tabs.py
"""
Right-side utility tabs: SETTINGS, RESPONSES, FILES, QUERY, URLS, FEEDBACK.
"""
from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QScrollArea, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFormLayout, QGroupBox, QFrame,
    QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox,
    QPushButton, QListWidget,
)
from PyQt6.QtCore import Qt
from .helpers import text_to_key, auto_register
from ..schemas import (
    INSTRUCTION_KEYS, DEFAULT_INSTRUCTION_BOOLS,
    API_KEYS, FILE_OPTION_KEYS, TEST_OPTION_KEYS,
)


class SettingsTab(QScrollArea):
    """Model, API, token percentages, instruction bools, test tools, file options."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        widget = QWidget()
        grid = QGridLayout(widget)

        # ── Token Percentage ─────────────────────────────────────────
        token_frame = QGroupBox("Token Percentage")
        token_layout = QGridLayout(token_frame)
        for i, key in enumerate(["prompt percentage", "completion percentage"]):
            label = QLabel(key.title())
            combo = QComboBox()
            combo.addItems([str(n) for n in range(0, 101)])
            combo.setCurrentText("50")
            token_layout.addWidget(label, i, 0)
            token_layout.addWidget(combo, i, 1)
            if registry and event_bus:
                auto_register(registry, event_bus, text_to_key(key), combo)
        grid.addWidget(token_frame, 0, 0, 1, 2)

        # ── API Options ──────────────────────────────────────────────
        api_frame = QGroupBox("API Options")
        api_layout = QFormLayout(api_frame)
        for key in API_KEYS:
            line = QLineEdit()
            api_layout.addRow(key.title() + ":", line)
            if registry and event_bus:
                auto_register(registry, event_bus, text_to_key(key), line)
        grid.addWidget(api_frame, 1, 0, 1, 2)

        # ── Type Options ─────────────────────────────────────────────
        type_frame = QGroupBox("Type Options")
        type_layout = QFormLayout(type_frame)

        self.role_combo = QComboBox()
        roles = [
            "assistant", "Elaborative", "Socratic", "Concise",
            "Friendly/Conversational", "Professional/Formal",
            "Role-Playing", "Teaching", "Debative/Devil's Advocate",
            "Creative/Brainstorming", "Empathetic/Supportive",
        ]
        self.role_combo.addItems(roles)
        type_layout.addRow("Role:", self.role_combo)
        if registry and event_bus:
            auto_register(registry, event_bus, "-ROLE-", self.role_combo)

        self.resp_type_combo = QComboBox()
        self.resp_type_combo.addItems(["instruction", "json", "bash", "text"])
        type_layout.addRow("Response Type:", self.resp_type_combo)
        if registry and event_bus:
            auto_register(registry, event_bus, "-RESPONSE_TYPE-", self.resp_type_combo)

        grid.addWidget(type_frame, 2, 0, 1, 2)

        # ── Model Selection ──────────────────────────────────────────
        model_frame = QGroupBox("Model Selection")
        model_layout = QFormLayout(model_frame)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        model_layout.addRow("Model:", self.model_combo)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("model"), self.model_combo)

        self.endpoint_display = QLineEdit()
        self.endpoint_display.setReadOnly(True)
        model_layout.addRow("Endpoint:", self.endpoint_display)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("endpoint"), self.endpoint_display)

        self.max_tokens_display = QLineEdit()
        self.max_tokens_display.setReadOnly(True)
        model_layout.addRow("Tokens:", self.max_tokens_display)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("max_tokens"), self.max_tokens_display)

        grid.addWidget(model_frame, 3, 0, 1, 2)

        # ── Enable Instructions ──────────────────────────────────────
        instr_frame = QGroupBox("Enable Instructions")
        instr_layout = QGridLayout(instr_frame)
        for idx, key in enumerate(INSTRUCTION_KEYS):
            cb = QCheckBox(key.replace("_", " ").title())
            default = DEFAULT_INSTRUCTION_BOOLS.get(key, False)
            cb.setChecked(default)
            row = idx // 4
            col = idx % 4
            instr_layout.addWidget(cb, row, col)
            if registry and event_bus:
                auto_register(registry, event_bus, text_to_key(key, section="BOOL"), cb)
        grid.addWidget(instr_frame, 4, 0, 1, 2)

        # ── Test Tools ───────────────────────────────────────────────
        test_frame = QGroupBox("Test Tools")
        test_layout = QHBoxLayout(test_frame)
        self.test_run_cb = QCheckBox("Test Run")
        self.test_files_cb = QCheckBox("Test Files")
        self.test_file_input = QLineEdit()
        self.test_browse_btn = QPushButton("Browse")
        test_layout.addWidget(self.test_run_cb)
        test_layout.addWidget(self.test_files_cb)
        test_layout.addWidget(self.test_file_input)
        test_layout.addWidget(self.test_browse_btn)
        if registry and event_bus:
            auto_register(registry, event_bus, "-TEST_RUN-", self.test_run_cb)
            auto_register(registry, event_bus, "-TEST_FILES-", self.test_files_cb)
            auto_register(registry, event_bus, "-TEST_FILE_INPUT-", self.test_file_input)
            auto_register(registry, event_bus, "-TEST_BROWSE-", self.test_browse_btn)
        grid.addWidget(test_frame, 5, 0, 1, 2)

        # ── File Options ─────────────────────────────────────────────
        file_frame = QGroupBox("File Options")
        file_layout = QVBoxLayout(file_frame)
        for key in FILE_OPTION_KEYS:
            cb = QCheckBox(key.replace("_", " ").title())
            file_layout.addWidget(cb)
            if registry and event_bus:
                auto_register(registry, event_bus, text_to_key(key), cb)
        grid.addWidget(file_frame, 6, 0, 1, 2)

        widget.setLayout(grid)
        self.setWidget(widget)
        self.setWidgetResizable(True)


class ResponsesTab(QWidget):
    """Collate, response key selection, file text."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        h = QHBoxLayout()
        self.collate_cb = QCheckBox("Collate Responses")
        self.json_to_string_cb = QCheckBox("JSON to String")
        h.addWidget(self.collate_cb)
        h.addWidget(self.json_to_string_cb)
        layout.addLayout(h)

        if registry and event_bus:
            auto_register(registry, event_bus, "-COLLATE_RESPONSES_BOOL-", self.collate_cb)
            auto_register(registry, event_bus, "-FORMAT_JSON_TO_STRING_RESPONSES-", self.json_to_string_cb)

        key_frame = QGroupBox("Response Key")
        key_layout = QHBoxLayout(key_frame)
        self.response_key_combo = QComboBox()
        key_layout.addWidget(self.response_key_combo)
        layout.addWidget(key_frame)
        if registry and event_bus:
            auto_register(registry, event_bus, "-RESPONSE_KEY_SELECTION_RESPONSES-", self.response_key_combo)

        self.file_text = QTextEdit()
        self.file_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.file_text)
        if registry and event_bus:
            auto_register(registry, event_bus, "-FILE_TEXT_RESPONSES-", self.file_text)


class FilesTab(QWidget):
    """File browser, chunk/response data buttons, file text."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title_h = QHBoxLayout()
        self.chunk_title = QLineEdit()
        title_h.addWidget(QLabel("Chunk Title:"))
        title_h.addWidget(self.chunk_title)
        layout.addLayout(title_h)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("-CHUNK_TITLE-", section="files"), self.chunk_title)

        btn_h = QHBoxLayout()
        self.chunk_btn = QPushButton("CHUNK_DATA")
        self.response_btn = QPushButton("RESPONSE_DATA")
        btn_h.addWidget(self.chunk_btn)
        btn_h.addWidget(self.response_btn)
        layout.addLayout(btn_h)
        if registry and event_bus:
            auto_register(registry, event_bus, "-ADD_FILE_TO_CHUNK_FILES-", self.chunk_btn)
            auto_register(registry, event_bus, "-ADD_FILE_TO_RESPONSE_FILES-", self.response_btn)

        self.file_text = QTextEdit()
        self.file_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.file_text)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("-FILE_TEXT-", section="files"), self.file_text)


class QueryDbTab(QWidget):
    """Database query tab."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        h = QHBoxLayout()
        self.db_query_cb = QCheckBox("Database Query")
        self.perform_cb = QCheckBox("Perform Query")
        h.addWidget(self.db_query_cb)
        h.addWidget(self.perform_cb)
        layout.addLayout(h)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("database query bool", section="database"), self.db_query_cb)

        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        table_layout = QHBoxLayout(table_frame)
        self.table_combo = QComboBox()
        table_layout.addWidget(QLabel("Table:"))
        table_layout.addWidget(self.table_combo)
        layout.addWidget(table_frame)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("table configuration", section="database"), self.table_combo)

        btn_h = QHBoxLayout()
        self.chunk_btn = QPushButton("CHUNK_DATA")
        self.response_btn = QPushButton("RESPONSE_DATA")
        btn_h.addWidget(self.chunk_btn)
        btn_h.addWidget(self.response_btn)
        layout.addLayout(btn_h)

        self.file_text = QTextEdit()
        self.file_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.file_text)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("-FILE_TEXT-", section="database"), self.file_text)


class UrlsTab(QWidget):
    """URL input, list, fetch buttons, text area."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        url_h = QHBoxLayout()
        self.url_input = QLineEdit()
        self.add_url_btn = QPushButton("Add URL")
        url_h.addWidget(self.url_input)
        url_h.addWidget(self.add_url_btn)
        layout.addLayout(url_h)
        if registry and event_bus:
            auto_register(registry, event_bus, "-URL-", self.url_input)

        self.url_listbox = QListWidget()
        layout.addWidget(self.url_listbox)
        if registry and event_bus:
            auto_register(registry, event_bus, "-URL_LIST-", self.url_listbox)

        btn_h = QHBoxLayout()
        self.get_soup_btn = QPushButton("GET SOUP")
        self.get_source_btn = QPushButton("GET SOURCE")
        self.chunk_btn = QPushButton("CHUNK_DATA")
        btn_h.addWidget(self.get_soup_btn)
        btn_h.addWidget(self.get_source_btn)
        btn_h.addWidget(self.chunk_btn)
        layout.addLayout(btn_h)
        if registry and event_bus:
            auto_register(registry, event_bus, "-GET_SOUP-", self.get_soup_btn)
            auto_register(registry, event_bus, "-GET_SOURCE_CODE-", self.get_source_btn)
            auto_register(registry, event_bus, "-ADD_URL_TO_CHUNK-", self.chunk_btn)

        title_h = QHBoxLayout()
        self.chunk_title = QLineEdit()
        title_h.addWidget(QLabel("Chunk Title:"))
        title_h.addWidget(self.chunk_title)
        layout.addLayout(title_h)
        if registry and event_bus:
            auto_register(registry, event_bus, text_to_key("-CHUNK_TITLE-", section="url"), self.chunk_title)

        self.url_text = QTextEdit()
        self.url_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.url_text)
        if registry and event_bus:
            auto_register(registry, event_bus, "-URL_TEXT-", self.url_text)


class FeedbackTab(QWidget):
    """Response display + feedback fields for each instruction key."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # main response
        resp_frame = QGroupBox("Response")
        resp_layout = QVBoxLayout(resp_frame)
        self.response_edit = QTextEdit()
        self.response_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        resp_layout.addWidget(self.response_edit)
        layout.addWidget(resp_frame)
        if registry and event_bus:
            auto_register(registry, event_bus, "-RESPONSE-", self.response_edit)

        # feedback fields
        feedback_fields = [
            "request_chunks", "abort", "additional_responses",
            "suggestions", "notation", "other",
        ]
        self._feedback_widgets = {}
        for f in feedback_fields:
            frame = QGroupBox(f.replace("_", " ").title())
            flayout = QVBoxLayout(frame)
            fb_key = text_to_key(f, section="feedback")

            if f in ("request_chunks", "abort", "additional_responses"):
                w = QLineEdit()
            else:
                w = QTextEdit()
                w.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

            flayout.addWidget(w)
            layout.addWidget(frame)
            self._feedback_widgets[f] = w

            if registry and event_bus:
                auto_register(registry, event_bus, fb_key, w)


class UtilityTabsWidget(QTabWidget):
    """Container for all utility-side tabs."""

    def __init__(self, registry=None, event_bus=None, parent=None):
        super().__init__(parent)

        self.settings_tab = SettingsTab(registry=registry, event_bus=event_bus)
        self.addTab(self.settings_tab, "SETTINGS")

        self.responses_tab = ResponsesTab(registry=registry, event_bus=event_bus)
        self.addTab(self.responses_tab, "RESPONSES")

        self.files_tab = FilesTab(registry=registry, event_bus=event_bus)
        self.addTab(self.files_tab, "FILES")

        self.query_tab = QueryDbTab(registry=registry, event_bus=event_bus)
        self.addTab(self.query_tab, "QUERY")

        self.urls_tab = UrlsTab(registry=registry, event_bus=event_bus)
        self.addTab(self.urls_tab, "URLS")

        self.feedback_tab = FeedbackTab(registry=registry, event_bus=event_bus)
        self.addTab(self.feedback_tab, "FEEDBACK")
