#!/usr/bin/env python3
"""
Tests for the foundation layer: schemas, widget_registry, event_bus,
helpers, navigation_controller.

Run with: python test_foundation.py
"""
import sys
import os

# add the parent dir so abstract_ai is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS: %s" % name)
    else:
        failed += 1
        print("  FAIL: %s" % name)


# ── schemas ──────────────────────────────────────────────────────────

print("\n=== schemas ===")
from abstract_ai.schemas import (
    InstructionEntry, PromptState, DisplayTracker, QueryProgress,
    ApiConfig, ModelConfig, QueryResult, GuiEvent,
    INSTRUCTION_KEYS, DEFAULT_INSTRUCTION_BOOLS,
)

ie = InstructionEntry()
test("InstructionEntry defaults", ie.bool_values == {"api_response": True})
test("InstructionEntry text defaults", "api_response" in ie.text_values)
test("InstructionEntry text empty", ie.text == "")

ps = PromptState()
test("PromptState defaults", ps.request_data_list == [""])
test("PromptState chunk_type", ps.chunk_type == "CODE")
test("PromptState completion_percentage", ps.completion_percentage == 50)

dt = DisplayTracker()
test("DisplayTracker get", dt.get("request") == 0)
dt.set("request", 5)
test("DisplayTracker set", dt.request == 5)
test("DisplayTracker get after set", dt.get("request") == 5)

qp = QueryProgress()
test("QueryProgress defaults", qp.done == False and qp.status_text == "Awaiting Prompt")

test("INSTRUCTION_KEYS length", len(INSTRUCTION_KEYS) == 11)
test("DEFAULT_INSTRUCTION_BOOLS has instructions", DEFAULT_INSTRUCTION_BOOLS["instructions"] == True)

ge = GuiEvent(event="-TEST-", payload={"foo": "bar"})
test("GuiEvent fields", ge.event == "-TEST-" and ge.payload["foo"] == "bar")


# ── widget_registry ──────────────────────────────────────────────────

print("\n=== widget_registry ===")
from abstract_ai.gui.widget_registry import WidgetRegistry

reg = WidgetRegistry()
test("empty registry", len(reg) == 0)

# simulate a widget with read/write
_store = {"value": "hello"}
reg.register("-TEST_KEY-", object(),
             read_func=lambda: _store["value"],
             write_func=lambda v: _store.__setitem__("value", v))

test("registry read", reg.read("-TEST_KEY-") == "hello")
reg.write("-TEST_KEY-", "world")
test("registry write", _store["value"] == "world")
test("registry read after write", reg.read("-TEST_KEY-") == "world")
test("registry exists", reg.exists("-TEST_KEY-"))
test("registry not exists", not reg.exists("-NOPE-"))
test("registry read default", reg.read("-NOPE-", default="fallback") == "fallback")
test("registry contains", "-TEST_KEY-" in reg)
test("registry len", len(reg) == 1)

all_vals = reg.read_all()
test("registry read_all", all_vals == {"-TEST_KEY-": "world"})

reg.unregister("-TEST_KEY-")
test("registry unregister", len(reg) == 0)


# ── event_bus ────────────────────────────────────────────────────────

print("\n=== event_bus ===")
from abstract_ai.gui.event_bus import EventBus

bus = EventBus()
test("bus starts empty", bus.pending() == 0)

bus.emit("-CLICK-", x=10, y=20)
bus.emit("-SUBMIT-")
test("bus has 2 events", bus.pending() == 2)

items = bus.drain()
test("bus drain returns 2", len(items) == 2)
test("bus drain event 0", items[0]["event"] == "-CLICK-" and items[0]["x"] == 10)
test("bus drain event 1", items[1]["event"] == "-SUBMIT-")
test("bus empty after drain", bus.pending() == 0)
test("bus drain empty", bus.drain() == [])

bus.emit("-A-")
bus.emit("-B-")
cleared = bus.clear()
test("bus clear returns count", cleared == 2)
test("bus empty after clear", bus.pending() == 0)


# ── helpers ──────────────────────────────────────────────────────────

print("\n=== helpers ===")
from abstract_ai.gui.helpers import text_to_key, get_nav_keys

test("text_to_key basic", text_to_key("prompt_data") == "-PROMPT_DATA-")
test("text_to_key with section", text_to_key("instructions", "BOOL") == "-INSTRUCTIONS_BOOL-")
test("text_to_key spaces", text_to_key("chunk title", "url") == "-CHUNK_TITLE_URL-")
test("text_to_key no section", text_to_key("request") == "-REQUEST-")

bk, nk, fk = get_nav_keys("request", section=True)
test("nav keys section", bk == "-REQUEST_SECTION_BACK-")
test("nav keys section number", nk == "-REQUEST_SECTION_NUMBER-")
test("nav keys section forward", fk == "-REQUEST_SECTION_FORWARD-")

bk2, nk2, fk2 = get_nav_keys("chunk", section=False)
test("nav keys item", bk2 == "-CHUNK_BACK-")
test("nav keys item forward", fk2 == "-CHUNK_FORWARD-")


# ── navigation_controller ───────────────────────────────────────────

print("\n=== navigation_controller ===")
from abstract_ai.controllers.navigation_controller import NavigationController

nc = NavigationController()

test("navigate forward from 0", nc.navigate("forward", 0, 5) == 1)
test("navigate forward at max", nc.navigate("forward", 5, 5) == 5)
test("navigate back from 3", nc.navigate("back", 3, 5) == 2)
test("navigate back from 0", nc.navigate("back", 0, 5) == 0)
test("navigate unknown", nc.navigate("sideways", 3, 5) == 3)

test("clamp low", nc.clamp(-1, 5) == 0)
test("clamp high", nc.clamp(10, 5) == 5)
test("clamp valid", nc.clamp(3, 5) == 3)

test("get_list_max empty", nc.get_list_max([]) == 0)
test("get_list_max 3 items", nc.get_list_max([1, 2, 3]) == 2)

d, l, dr = nc.parse_nav_event("-REQUEST_SECTION_BACK-")
test("parse section back", (d, l, dr) == ("request", "section", "back"))

d, l, dr = nc.parse_nav_event("-CHUNK_FORWARD-")
test("parse item forward", (d, l, dr) == ("chunk", "item", "forward"))

d, l, dr = nc.parse_nav_event("-QUERY_SECTION_FORWARD-")
test("parse query section forward", (d, l, dr) == ("query", "section", "forward"))

d, l, dr = nc.parse_nav_event("-RESPONSE_TEXT_BACK-")
test("parse response_text back", (d, l, dr) == ("response_text", "item", "back"))

d, l, dr = nc.parse_nav_event("-NOT_AN_EVENT-")
test("parse non-nav event", d is None)

d, l, dr = nc.parse_nav_event("plain_string")
test("parse plain string", d is None)


# ── summary ──────────────────────────────────────────────────────────

print("\n" + "=" * 50)
print("PASSED: %d  FAILED: %d" % (passed, failed))
if failed > 0:
    sys.exit(1)
else:
    print("All tests passed.")
