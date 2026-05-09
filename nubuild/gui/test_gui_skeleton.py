#!/usr/bin/env python3
"""
Test that the full GUI skeleton launches, all widgets register into
the registry, and button clicks produce events in the bus.

Uses QApplication but doesn't enter exec() — just constructs and verifies.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # headless

from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)

from abstract_ai.gui.widget_registry import WidgetRegistry
from abstract_ai.gui.event_bus import EventBus
from abstract_ai.gui.main_window import MainWindow

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


print("\n=== GUI construction ===")
registry = WidgetRegistry()
bus = EventBus()
window = MainWindow(registry, bus)

test("window created", window is not None)
test("window title", window.windowTitle() == "Abstract AI Console")
test("registry has keys", len(registry) > 0)

print("\n  Registered %d widget keys." % len(registry))

# check some critical keys exist
critical_keys = [
    "-PROGRESS_TEXT-",
    "-PROGRESS-",
    "-SUBMIT_QUERY-",
    "-CLEAR_CHUNKS-",
    "-RESPONSE-",
    "-INSTRUCTIONS_TEXT-",
    "-ROLE-",
    "-COMPLETION_PERCENTAGE-",
    "-PROMPT_PERCENTAGE-",
    "-TEST_RUN-",
    "-URL-",
]

print("\n=== critical key checks ===")
for key in critical_keys:
    test("key exists: %s" % key, registry.exists(key))

# test read/write round-trip on a text widget
print("\n=== read/write round-trip ===")
registry.write("-PROGRESS_TEXT-", "Testing...")
test("write/read progress text", registry.read("-PROGRESS_TEXT-") == "Testing...")

registry.write("-ROLE-", "Socratic")
test("write/read role combo", registry.read("-ROLE-") == "Socratic")

# test that clicking a button puts an event in the bus
print("\n=== event bus wiring ===")
submit_btn = registry.widget("-SUBMIT_QUERY-")
test("submit button exists", submit_btn is not None)

bus.clear()
submit_btn.click()
events = bus.drain()
test("button click produces event", len(events) >= 1)
test("event key is -SUBMIT_QUERY-",
     any(e["event"] == "-SUBMIT_QUERY-" for e in events))

# test checkbox toggle
print("\n=== checkbox event ===")
bus.clear()
test_run_cb = registry.widget("-TEST_RUN-")
if test_run_cb:
    test_run_cb.setChecked(True)
    events = bus.drain()
    test("checkbox toggle produces event", len(events) >= 1)
    test("checkbox read is True", registry.read("-TEST_RUN-") == True)

# test navigation key format
from abstract_ai.gui.helpers import text_to_key
req_section_back = text_to_key("request SECTION BACK")
test("request section back key registered", registry.exists(req_section_back))

# list all registered keys for inspection
print("\n=== all registered keys ===")
all_keys = sorted(registry.keys())
for k in all_keys:
    print("    %s" % k)

# summary
print("\n" + "=" * 50)
print("PASSED: %d  FAILED: %d" % (passed, failed))
print("Total registered keys: %d" % len(registry))
if failed > 0:
    sys.exit(1)
else:
    print("All tests passed.")
