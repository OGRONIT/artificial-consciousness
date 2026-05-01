"""
Tests for TrainedStateManager — load/export roundtrip using temp dirs.
"""
import sys
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.TrainedStateManager import TrainedStateManager
from modules.MemoryContinuity import ChittaMemoryDB, InteractionOutcome


def make_tsm(tmp_root: Path) -> TrainedStateManager:
    kernel_root = tmp_root / "antahkarana_kernel"
    kernel_root.mkdir(parents=True, exist_ok=True)
    return TrainedStateManager(kernel_root)


def test_export_creates_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        tsm = make_tsm(Path(tmpdir))
        db = ChittaMemoryDB()
        db.record_experience(content="hello", success_score=0.7,
                             outcome=InteractionOutcome.SUCCESS)

        result = tsm.export_from_training_run(memory_system=db)
        assert isinstance(result, dict)
        assert "files" in result
        for fpath in result["files"]:
            assert Path(fpath).exists(), f"Expected file not found: {fpath}"


def test_export_memory_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        tsm = make_tsm(Path(tmpdir))
        db = ChittaMemoryDB()
        db.record_experience(content="unique content xyz", success_score=0.6,
                             outcome=InteractionOutcome.SUCCESS)

        result = tsm.export_from_training_run(memory_system=db)
        # Read chitta memory export and verify content is there
        chitta_file = tsm.trained_state_dir / "chitta_memory_export.json"
        data = json.loads(chitta_file.read_text(encoding="utf-8"))
        memories = data.get("memories", [])
        contents = [m.get("content", "") for m in memories]
        assert any("unique content xyz" in c for c in contents)


def test_import_restores_memories():
    with tempfile.TemporaryDirectory() as tmpdir:
        tsm = make_tsm(Path(tmpdir))
        db = ChittaMemoryDB()
        db.record_experience(content="import test", success_score=0.8)

        tsm.export_from_training_run(memory_system=db)

        # Now load into a fresh DB via load_exported_memories
        chitta_file = tsm.trained_state_dir / "chitta_memory_export.json"
        data = json.loads(chitta_file.read_text(encoding="utf-8"))
        db2 = ChittaMemoryDB()
        loaded = db2.load_exported_memories(data, clear_existing=True)
        assert loaded >= 1


def test_manifest_file_created():
    with tempfile.TemporaryDirectory() as tmpdir:
        tsm = make_tsm(Path(tmpdir))
        tsm.export_from_training_run()
        manifest = tsm.trained_state_dir / "trained_state_manifest.json"
        assert manifest.exists()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert "generated_at" in data


def test_export_with_empty_db():
    """Export should succeed even with an empty memory system."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tsm = make_tsm(Path(tmpdir))
        result = tsm.export_from_training_run(memory_system=ChittaMemoryDB())
        assert isinstance(result, dict)
