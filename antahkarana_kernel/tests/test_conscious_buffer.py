"""
Tests for ConsciousBuffer (Global Workspace Theory) module.
Validates event enqueue/dequeue semantics and buffer size limiting.
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ConsciousBuffer import ConsciousBuffer, ConsciousEvent, BroadcastType


def make_event(event_id: str = "evt_1", priority: float = 0.5) -> ConsciousEvent:
    return ConsciousEvent(
        event_id=event_id,
        timestamp=time.time(),
        broadcast_type=BroadcastType.STATE_UPDATE.value,
        source_module="test_module",
        content={"value": "test"},
        priority=priority,
    )


def test_broadcast_stores_event():
    buf = ConsciousBuffer(max_buffer_size=100)
    evt = make_event("e1")
    buf.broadcast(evt)
    with buf.buffer_lock:
        ids = [e.event_id for e in buf.event_buffer]
    assert "e1" in ids


def test_buffer_size_limit_enforced():
    """Buffer should not grow beyond max_buffer_size."""
    max_size = 5
    buf = ConsciousBuffer(max_buffer_size=max_size)
    for i in range(max_size + 3):
        buf.broadcast(make_event(f"evt_{i}"))
    with buf.buffer_lock:
        assert len(buf.event_buffer) <= max_size


def test_high_priority_sets_conscious_focus():
    buf = ConsciousBuffer(max_buffer_size=100)
    evt = make_event("high_prio", priority=0.9)
    buf.broadcast(evt)
    with buf.focus_lock:
        focus = dict(buf.conscious_focus)
    assert focus.get("focused_event_id") == "high_prio"


def test_low_priority_does_not_override_focus():
    buf = ConsciousBuffer(max_buffer_size=100)
    high = make_event("high", priority=0.9)
    buf.broadcast(high)
    low = make_event("low", priority=0.3)
    buf.broadcast(low)
    with buf.focus_lock:
        focus = dict(buf.conscious_focus)
    # Low priority should not have replaced the focus
    assert focus.get("focused_event_id") != "low"


def test_module_registration():
    buf = ConsciousBuffer(max_buffer_size=100)
    buf.register_module("test_module")
    with buf.modules_lock:
        assert "test_module" in buf.modules


def test_metrics_updated_after_broadcast():
    buf = ConsciousBuffer(max_buffer_size=100)
    buf.broadcast(make_event("metrics_evt"))
    with buf.metrics_lock:
        assert buf.integration_metrics["total_events_processed"] >= 1


def test_event_index_populated():
    buf = ConsciousBuffer(max_buffer_size=100)
    evt = make_event("idx_evt")
    buf.broadcast(evt)
    with buf.index_lock:
        assert "idx_evt" in buf.event_index_by_module.get("test_module", [])
