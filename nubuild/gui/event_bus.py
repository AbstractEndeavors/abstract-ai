# gui/event_bus.py
"""
One-way event channel: GUI -> Controller.

The GUI layer calls bus.emit(event_name, **payload).
The controller drains the queue on a QTimer tick.

This replaces the PySimpleGUI event loop (while True: event, values = window.read())
with a decoupled queue that the controller polls at a fixed interval.
"""
import queue
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Thread-safe event queue.

    GUI widgets push events with .emit(). The AppController calls .drain()
    on a QTimer to consume all pending events in one batch.
    """

    def __init__(self):
        self._queue = queue.Queue()

    def emit(self, event, **kwargs):
        """
        Push an event into the queue.

        Args:
            event: The event key string (e.g. "-SUBMIT_QUERY-", "-INSTRUCTIONS_BOOL-").
            **kwargs: Additional payload data attached to the event.
        """
        item = {"event": event}
        if kwargs:
            item.update(kwargs)
        self._queue.put(item)
        logger.debug("EventBus.emit: %s", event)

    def drain(self):
        """
        Consume and return all pending events without blocking.

        Returns:
            list[dict]: Each dict has at minimum an "event" key.
        """
        items = []
        while True:
            try:
                items.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return items

    def pending(self):
        """Return the approximate number of pending events."""
        return self._queue.qsize()

    def clear(self):
        """Discard all pending events."""
        discarded = 0
        while True:
            try:
                self._queue.get_nowait()
                discarded += 1
            except queue.Empty:
                break
        if discarded:
            logger.debug("EventBus.clear: discarded %d events", discarded)
        return discarded
