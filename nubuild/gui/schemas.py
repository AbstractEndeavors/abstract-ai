# schemas.py
"""
Typed data structures for cross-boundary communication.

Every dict or loose list that used to flow between managers is now a
dataclass with named, typed fields. These are importable and testable
without a GUI.
"""
import os
from dataclasses import dataclass, field


# ── Instruction domain ───────────────────────────────────────────────

@dataclass
class InstructionEntry:
    """One section's worth of instruction state (was instruction_data_list[n])."""
    bool_values: dict = field(default_factory=lambda: {"api_response": True})
    text_values: dict = field(default_factory=lambda: {"api_response": "place response to prompt here"})
    text: str = ""


# ── Prompt / chunking domain ────────────────────────────────────────

@dataclass
class PromptState:
    """Snapshot of the prompt/request workspace."""
    request_data_list: list = field(default_factory=lambda: [""])
    prompt_data_list: list = field(default_factory=lambda: [""])
    instruction_data_list: list = field(default_factory=list)
    chunk_type: str = "CODE"
    completion_percentage: int = 50


# ── Display navigation ──────────────────────────────────────────────

@dataclass
class DisplayTracker:
    """Which section/subsection the user is currently viewing."""
    instructions: int = 0
    request: int = 0
    prompt_data: int = 0
    chunk: int = 0
    query: int = 0
    chunk_number: int = 0

    def get(self, key, default=0):
        return getattr(self, key, default)

    def set(self, key, value):
        if hasattr(self, key):
            setattr(self, key, int(value))


# ── Query progress ──────────────────────────────────────────────────

@dataclass
class QueryProgress:
    """Progress of an in-flight query submission."""
    total_chunks: int = 0
    current_chunk: int = 0
    done: bool = False
    status_text: str = "Awaiting Prompt"


# ── API configuration ───────────────────────────────────────────────

@dataclass
class ApiConfig:
    """API connection settings read from the GUI."""
    header: str = ""
    api_key: str = ""
    api_env: str = ""
    endpoint: str = ""


# ── Model configuration ─────────────────────────────────────────────

@dataclass
class ModelConfig:
    """Selected model details."""
    model_name: str = ""
    endpoint: str = ""
    max_tokens: int = 0


# ── Query result ────────────────────────────────────────────────────

@dataclass
class QueryResult:
    """One completed query response, parsed for display."""
    model: str = ""
    title: str = ""
    request: str = ""
    response_content: str = ""
    api_response: str = ""
    file_path: str = ""
    raw_output: dict = field(default_factory=dict)


# ── Event payload ───────────────────────────────────────────────────

@dataclass
class GuiEvent:
    """
    Typed event from the GUI layer to the controller.
    Replaces the old (event, values) tuple from PySimpleGUI's window.read().
    """
    event: str = ""
    payload: dict = field(default_factory=dict)


# ── Instruction key constants ───────────────────────────────────────

INSTRUCTION_KEYS = [
    "instructions",
    "additional_responses",
    "suggestions",
    "abort",
    "database_query",
    "notation",
    "generate_title",
    "additional_instruction",
    "request_chunks",
    "prompt_as_previous",
    "token_adjustment",
]

DEFAULT_INSTRUCTION_BOOLS = {
    "instructions": True,
    "generate_title": True,
    "suggestions": True,
}

# ── GUI key constants (matching the existing -KEY- convention) ──────

API_KEYS = ["header", "api key", "api env"]
MODEL_TYPE_KEYS = ["role", "response type"]
PERCENTAGE_KEYS = ["prompt percentage", "completion percentage"]
FILE_OPTION_KEYS = ["auto chunk title", "reuse chunk data", "append chunks", "scan mode all"]
TEST_OPTION_KEYS = ["test run", "test files", "test file input", "test browse"]
COMPLETION_TOKEN_KEYS = ["completion tokens available", "completion tokens desired", "completion tokens used"]
PROMPT_TOKEN_KEYS = ["prompt tokens available", "prompt tokens desired", "prompt tokens used"]
CHUNK_DATA_KEYS = ["max chunk size", "chunk length", "chunk total"]
ALL_TOKEN_KEYS = COMPLETION_TOKEN_KEYS + PROMPT_TOKEN_KEYS + CHUNK_DATA_KEYS + ["chunk sectioned data"]
