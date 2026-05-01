"""
Tests for MemoryContinuity (ChittaMemoryDB) module.
Validates experience recording, retrieval, external facts, and export/import.
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.MemoryContinuity import ChittaMemoryDB, InteractionOutcome


def make_db() -> ChittaMemoryDB:
    return ChittaMemoryDB()


def test_record_and_retrieve_experience():
    db = make_db()
    mid = db.record_experience(
        content="test input",
        interaction_type="test",
        outcome=InteractionOutcome.SUCCESS,
        success_score=0.9,
    )
    assert isinstance(mid, str)
    retrieved = db.retrieve_memory(mid)
    assert retrieved is not None
    assert retrieved.content == "test input"
    assert retrieved.outcome == InteractionOutcome.SUCCESS.value


def test_multiple_experiences_stored():
    db = make_db()
    ids = []
    for i in range(5):
        mid = db.record_experience(content=f"item {i}", success_score=0.5)
        ids.append(mid)
    assert len(ids) == 5
    # All unique
    assert len(set(ids)) == 5


def test_retrieve_nonexistent_memory_returns_none():
    db = make_db()
    assert db.retrieve_memory("nonexistent_id_xyz") is None


def test_memory_statistics_returns_dict():
    db = make_db()
    db.record_experience(content="hello", success_score=0.7)
    stats = db.memory_statistics()
    assert isinstance(stats, dict)
    assert "total_memories" in stats


def test_add_and_retrieve_external_fact():
    db = make_db()
    fact_id = db.record_external_knowledge(
        topic="test_topic",
        title="Test Title",
        summary="A test fact.",
        source_name="TestSource",
        source_url="https://example.com",
        verification_score=0.9,
        approved_by_turiya=True,
        filter_reason="passed",
    )
    assert isinstance(fact_id, str)
    # Query back the fact
    results = db.query_external_knowledge(topic="test_topic")
    assert len(results) >= 1
    fact = results[0]
    assert fact.topic == "test_topic"
    assert fact.title == "Test Title"


def test_recent_memories_retrieval():
    db = make_db()
    for i in range(3):
        db.record_experience(content=f"recent {i}", success_score=0.5)
    recent = db.retrieve_recent_experiences(limit=3)
    assert len(recent) <= 3


def test_export_import_roundtrip():
    db = make_db()
    db.record_experience(content="exportable content", success_score=0.8,
                         outcome=InteractionOutcome.SUCCESS)
    from modules.TrainedStateManager import TrainedStateManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir) / "antahkarana_kernel"
        tmp_root.mkdir()
        tsm = TrainedStateManager(tmp_root)
        export = tsm._build_memory_export(db, memory_top_n=10)
        assert isinstance(export, dict)
        memories_list = export.get("memories", [])
        assert len(memories_list) >= 1
        # Reimport
        db2 = make_db()
        loaded_count = db2.load_exported_memories(export, clear_existing=True)
        assert loaded_count >= 1
