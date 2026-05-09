# controller.py
"""
AppController: the single orchestrator.

Owns all managers and sub-controllers. Drains the event bus. Routes events.
This is the only class that knows about both the registry and the managers.

Replaces the monolithic GptManager class and its monkey-patched methods.
"""
import os
import asyncio
import logging
import threading

from .schemas import (
    DisplayTracker, InstructionEntry, PromptState,
    INSTRUCTION_KEYS, DEFAULT_INSTRUCTION_BOOLS,
)
from .gui.helpers import text_to_key
from .controllers.navigation_controller import NavigationController
from .controllers.instruction_controller import InstructionController
from .controllers.prompt_controller import PromptController
from .controllers.response_controller import ResponseController
from .controllers.url_controller import UrlController
from .controllers.test_controller import TestController

logger = logging.getLogger(__name__)


class AppController:
    """
    Central event router and dependency wirer.

    All managers are instantiated here with explicit dependencies.
    All sub-controllers receive only what they need.
    The tick() method is called by a QTimer to drain the event bus.
    """

    def __init__(self, registry, event_bus):
        self.registry = registry
        self.bus = event_bus

        # ── core managers (pure logic, no GUI) ───────────────────────
        # These are lazy-imported to avoid circular deps and to allow
        # the controller to be tested with mocks.
        self.instruction_mgr = None
        self.model_mgr = None
        self.api_mgr = None
        self.prompt_mgr = None
        self.response_mgr = None
        self.history_mgr = None

        # ── sub-controllers ──────────────────────────────────────────
        self.navigation = NavigationController()
        self.instructions = None
        self.prompts = None
        self.responses = None
        self.urls = None
        self.tests = None

        # ── state ────────────────────────────────────────────────────
        self.tracker = DisplayTracker()
        self.instruction_data_list = []
        self.loop = None  # asyncio event loop, set by main.py

        self._initialized = False

    def initialize(self):
        """
        Create all managers and sub-controllers.
        Called after the GUI is built and the registry is populated.
        """
        if self._initialized:
            return

        # import managers
        from abstract_ai import (
            ApiManager, ModelManager, PromptManager,
            InstructionManager, ResponseManager,
        )
        from abstract_utilities import HistoryManager

        self.instruction_mgr = InstructionManager()
        self.model_mgr = ModelManager(default_selection=True)
        self.api_mgr = ApiManager()
        self.history_mgr = HistoryManager()

        # instruction data bootstrap
        self.instruction_data_list = [
            {
                "bool_values": {"api_response": True},
                "text_values": {"api_response": "place response to prompt here"},
                "text": "",
            }
        ]

        self.prompt_mgr = PromptManager(
            instruction_mgr=self.instruction_mgr,
            model_mgr=self.model_mgr,
            instruction_data=self.instruction_data_list,
        )
        self.response_mgr = ResponseManager(
            prompt_mgr=self.prompt_mgr,
            api_mgr=self.api_mgr,
        )

        # sub-controllers
        self.instructions = InstructionController(
            self.instruction_mgr, self.prompt_mgr,
            self.registry, INSTRUCTION_KEYS,
        )
        self.prompts = PromptController(
            self.prompt_mgr, self.registry, self.history_mgr,
        )
        self.responses = ResponseController(
            self.response_mgr, self.prompt_mgr,
            self.api_mgr, self.registry,
        )
        self.urls = UrlController(self.registry)
        self.tests = TestController(self.registry)

        # initial sync
        self._sync_model_to_gui()
        self.instructions.restore_defaults()
        self._sync_instructions()

        self._initialized = True
        logger.info("AppController initialized.")

    # ── event routing (called by QTimer) ─────────────────────────────

    def tick(self):
        """Drain the event bus and route each event to its handler."""
        if not self._initialized:
            return

        for item in self.bus.drain():
            event = item.get("event", "")
            if not event:
                continue
            try:
                self._route(event, item)
            except Exception:
                logger.exception("Error handling event: %s", event)

    def _route(self, event, item):
        """Route a single event to the appropriate handler."""
        # explicit event map
        handler = self._EVENT_MAP.get(event)
        if handler:
            getattr(self, handler)(item)
            return

        # instruction bool toggle
        if self.instructions and self.instructions.is_instruction_event(event):
            self._on_instruction_change(item)
            return

        # navigation events (back/forward)
        domain, level, direction = self.navigation.parse_nav_event(event)
        if domain is not None:
            self._on_navigate(domain, level, direction)
            return

        # URL events
        if self.urls and self.urls.handle_event(event):
            return

        # test events
        if self.tests and self.tests.handle_event(event):
            return

        # fallthrough — some events (like text changes) don't need handling
        logger.debug("Unhandled event: %s", event)

    _EVENT_MAP = {
        "-SUBMIT_QUERY-":              "_on_submit",
        "-CLEAR_REQUESTS-":            "_on_clear_requests",
        "-CLEAR_CHUNKS-":              "_on_clear_chunks",
        "-GENERATE_README-":           "_on_gen_readme",
        "-COLLATE_RESPONSES_BOOL-":    "_on_collate",
        "-RESPONSE_TEXT_BACK-":        "_on_response_nav_back",
        "-RESPONSE_TEXT_FORWARD-":     "_on_response_nav_forward",
        "-COMPLETION_PERCENTAGE-":     "_on_token_pct",
        "-PROMPT_PERCENTAGE-":         "_on_token_pct",
        "-ADD_QUERY-":                 "_on_add_query",
        "-UNDO_CHUNKS-":              "_on_undo_chunks",
        "-REDO_CHUNKS-":              "_on_redo_chunks",
    }

    # ── submit ───────────────────────────────────────────────────────

    def _on_submit(self, item):
        if self.responses.submission_in_progress:
            return

        # update all managers before submitting
        self._sync_all()

        # calculate total chunks for progress
        dists = self.prompts.chunk_token_distributions
        total = sum(len(d) for d in dists) if dists else 0
        self.responses.progress.total_chunks = total

        # run async
        test_mode = self.tests.test_mode
        test_path = self.tests.test_file_path

        if self.loop:
            future = asyncio.run_coroutine_threadsafe(
                self.responses.submit(test_mode=test_mode, test_path=test_path),
                self.loop,
            )
            future.add_done_callback(self._on_submit_done)

    def _on_submit_done(self, future):
        try:
            future.result()
        except Exception:
            logger.exception("Async submit failed")
        # post-submit: update progress display, delegate feedback
        self.responses.update_progress_display()
        if self.responses.last_result.api_response:
            self.instructions.delegate_response_feedback(
                self.responses.last_result.api_response
            )
        # clear chunk data if reuse is off
        reuse = self.registry.read("-REUSE_CHUNK_DATA-", default=False)
        if not reuse:
            section = self.tracker.prompt_data
            self.prompts.update_prompt_data(section, "")

    # ── clear ────────────────────────────────────────────────────────

    def _on_clear_requests(self, item):
        self.prompts.state.request_data_list = [""]
        self.prompts.sync_request_display(0)
        self.tracker.request = 0

    def _on_clear_chunks(self, item):
        section = self.tracker.prompt_data
        self.prompts.clear_chunks(section)

    # ── instructions ─────────────────────────────────────────────────

    def _on_instruction_change(self, item):
        section = self.tracker.request
        self.instruction_data_list = self.instructions.sync_from_gui(
            section, self.instruction_data_list,
        )
        self._refresh_query_display()

    def _sync_instructions(self):
        section = self.tracker.request
        self.instruction_data_list = self.instructions.sync_from_gui(
            section, self.instruction_data_list,
        )

    # ── navigation ───────────────────────────────────────────────────

    def _on_navigate(self, domain, level, direction):
        if level == "section":
            # navigate the section index for this domain
            current = self.tracker.get(domain, 0)
            ref = self._get_section_reference(domain)
            max_idx = self.navigation.get_list_max(ref)
            new_idx = self.navigation.navigate(direction, current, max_idx)
            self.tracker.set(domain, new_idx)

            # reset sub-item to 0
            self.tracker.chunk_number = 0

            # sync all related displays
            self._sync_section_displays()

        elif level == "item":
            # navigate the chunk/sub-item within the current section
            section_idx = self.tracker.get(domain, 0)
            ref = self._get_item_reference(domain, section_idx)
            max_idx = self.navigation.get_list_max(ref)
            current = self.tracker.chunk_number
            new_idx = self.navigation.navigate(direction, current, max_idx)
            self.tracker.chunk_number = new_idx

            self._sync_section_displays()

    def _get_section_reference(self, domain):
        """Get the list that section navigation indexes into."""
        refs = {
            "request": self.prompts.state.request_data_list,
            "prompt_data": self.prompts.state.prompt_data_list,
            "instructions": self.prompts.state.prompt_data_list,
            "chunk": self.prompts.chunk_token_distributions,
            "query": self.prompts.chunk_token_distributions,
        }
        return refs.get(domain, [])

    def _get_item_reference(self, domain, section_idx):
        """Get the sub-list that item navigation indexes into."""
        if domain in ("chunk", "query"):
            dists = self.prompts.chunk_token_distributions
            if dists and 0 <= section_idx < len(dists):
                return dists[section_idx]
        return []

    def _sync_section_displays(self):
        """After navigation, refresh all affected displays."""
        section = self.tracker.request
        self.prompts.sync_request_display(section)
        self.prompts.sync_prompt_display(section)
        self.instructions.sync_to_gui(
            min(section, len(self.instruction_data_list) - 1),
            self.instruction_data_list,
        )
        self.prompts.sync_chunk_info(
            self.tracker.query, self.tracker.chunk_number,
        )
        self.prompts.sync_query_display(
            self.tracker.query, self.tracker.chunk_number,
        )

        # write navigation numbers back to registry
        for domain in ("request", "prompt_data", "instructions", "chunk", "query"):
            num_key = text_to_key("%s section number" % domain)
            self.registry.write(num_key, str(self.tracker.get(domain, 0)))
        self.registry.write(
            text_to_key("chunk number"),
            str(self.tracker.chunk_number),
        )

    # ── token percentages ────────────────────────────────────────────

    def _on_token_pct(self, item):
        event = item.get("event", "")
        self.prompts.sync_percentages(event)
        self.prompts.recalculate(self.instruction_data_list, self.tracker)
        self._refresh_query_display()

    # ── response navigation ──────────────────────────────────────────

    def _on_response_nav_back(self, item):
        self.responses.navigate("back")

    def _on_response_nav_forward(self, item):
        self.responses.navigate("forward")

    # ── collation ────────────────────────────────────────────────────

    def _on_collate(self, item):
        enabled = self.registry.read("-COLLATE_RESPONSES_BOOL-", default=False)
        if enabled:
            files = self.registry.read("-FILES_LIST_RESPONSES-", default=[])
            if files:
                self.responses.collate_responses(files)

    # ── undo/redo ────────────────────────────────────────────────────

    def _on_undo_chunks(self, item):
        self.prompts.undo_chunks()
        self.prompts.sync_prompt_display(self.tracker.prompt_data)

    def _on_redo_chunks(self, item):
        self.prompts.redo_chunks()
        self.prompts.sync_prompt_display(self.tracker.prompt_data)

    # ── add query ────────────────────────────────────────────────────

    def _on_add_query(self, item):
        self.instruction_data_list = self.prompts.fill_lists(
            self.instruction_data_list
        )
        self._refresh_query_display()

    # ── gen readme ───────────────────────────────────────────────────

    def _on_gen_readme(self, item):
        # placeholder — the readme generation window is a separate concern
        logger.info("GEN README requested (not yet implemented in new arch)")

    # ── sync helpers ─────────────────────────────────────────────────

    def _sync_all(self):
        """Full refresh of all managers from current GUI state."""
        self._sync_model()
        self._sync_api()
        self._sync_instructions()
        self.prompts.recalculate(self.instruction_data_list, self.tracker)
        self.responses.rebuild_response_mgr()

    def _sync_model(self):
        """Read model selection from registry, update ModelManager."""
        from abstract_ai import ModelManager
        model_name = self.registry.read(text_to_key("model"), default="")
        self.model_mgr = ModelManager(input_model_name=model_name)
        self._sync_model_to_gui()

    def _sync_model_to_gui(self):
        """Write model info into registry."""
        if self.model_mgr:
            self.registry.write(text_to_key("model"), self.model_mgr.selected_model_name)
            self.registry.write(text_to_key("endpoint"), self.model_mgr.selected_endpoint)
            self.registry.write(text_to_key("max_tokens"), str(self.model_mgr.selected_max_tokens))

    def _sync_api(self):
        """Read API settings from registry, update ApiManager."""
        from abstract_ai import ApiManager
        header = self.registry.read(text_to_key("header"), default="")
        api_env = self.registry.read(text_to_key("api_env"), default="")
        api_key = self.registry.read(text_to_key("api_key"), default="")
        endpoint = self.model_mgr.selected_endpoint if self.model_mgr else ""
        self.api_mgr = ApiManager(
            header=header, api_env=api_env,
            api_key=api_key, endpoint=endpoint,
        )

    def _refresh_query_display(self):
        """Recalculate and sync query/chunk displays."""
        self.prompts.recalculate(self.instruction_data_list, self.tracker)
        section = self.tracker.query
        chunk = self.tracker.chunk_number
        self.prompts.sync_chunk_info(section, chunk)
        self.prompts.sync_query_display(section, chunk)
