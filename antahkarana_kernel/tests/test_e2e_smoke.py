"""
test_e2e_smoke.py - Deterministic end-to-end smoke tests for the Antahkarana Kernel.

Smoke test (test_e2e_kernel_smoke):
  - No LLM required, no network calls, runs in well under 30 s.
  - Seeds Python random from config.json reproducibility.seed (fallback: 42).
  - Instantiates the key modules and exercises the core pipeline.
  - Asserts structural invariants rather than exact values.

Integration test (test_e2e_live_cycle):
  - Skipped unless the env var RUN_INTEGRATION=1 is set.
  - Starts the full AntahkaranaKernel and processes a few inputs.
  - Verifies that a state snapshot file can be written to a temp dir.
  - Does NOT perform real internet ingestion.
"""

import json
import os
import random
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Ensure the kernel package is importable from tests/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ConsciousBuffer import ConsciousBuffer, BroadcastType, ConsciousEvent
from modules.MemoryContinuity import ChittaMemoryDB, InteractionOutcome
from modules.SelfModel import SelfModel
from modules.TrainedStateManager import TrainedStateManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_repro_seed() -> int:
    """Return the configured reproducibility seed (from config.json), or 42."""
    config_path = ROOT / "config.json"
    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        repro = cfg.get("reproducibility", {})
        return int(repro.get("seed", 42))
    except Exception:
        return 42


def _run_pipeline(inputs: list, self_model: SelfModel, memory: ChittaMemoryDB,
                  buffer: ConsciousBuffer) -> list:
    """
    Exercise the core pipeline for each input without requiring ManasBuddhi
    or any LLM:
      1. Record decision in SelfModel
      2. Store memory experience
      3. Broadcast event to ConsciousBuffer
    Returns the list of (decision_id, memory_id) tuples.
    """
    results = []
    for text in inputs:
        decision_id = self_model.record_input_processing(text, decision_type="query")
        memory_id = memory.record_experience(
            interaction_id=decision_id,
            content=text,
            interaction_type="query",
            outcome=InteractionOutcome.SUCCESS,
            success_score=round(random.uniform(0.6, 1.0), 4),
        )
        evt = ConsciousEvent(
            event_id=f"evt_{decision_id}",
            timestamp=time.time(),
            broadcast_type=BroadcastType.DECISION_POINT.value,
            source_module="e2e_smoke_test",
            content={"text": text[:80]},
            priority=0.5,
        )
        buffer.broadcast(evt)
        results.append((decision_id, memory_id))
    return results


# ---------------------------------------------------------------------------
# Fast deterministic smoke test (always runs in CI)
# ---------------------------------------------------------------------------

def test_e2e_kernel_smoke():
    """
    Deterministic end-to-end smoke test.

    Invariants checked:
    1. SelfModel processes inputs and increments processed_inputs counter.
    2. ChittaMemoryDB records all experiences and count increases.
    3. ConsciousBuffer receives one event per input.
    4. TrainedStateManager can export memory to a temp dir and files exist.
    """
    seed = _get_repro_seed()
    random.seed(seed)

    # Instantiate modules freshly (no singletons, no side-effects on shared state)
    self_model = SelfModel(identity_name="SmokeTestKernel_e2e")
    memory = ChittaMemoryDB()
    buffer = ConsciousBuffer(max_buffer_size=200)

    initial_memory_count = memory.memory_statistics()["total_memories"]
    initial_processed = self_model.processed_inputs
    initial_coherence = self_model.coherence_score

    test_inputs = [
        "What is the nature of consciousness?",
        "Explain memory continuity in cognitive architectures.",
        "How does self-modeling contribute to coherent reasoning?",
    ]

    results = _run_pipeline(test_inputs, self_model, memory, buffer)

    # --- Invariant 1: SelfModel processed_inputs incremented ---
    assert self_model.processed_inputs == initial_processed + len(test_inputs), (
        f"Expected processed_inputs to increase by {len(test_inputs)}, "
        f"got {self_model.processed_inputs - initial_processed}"
    )

    # --- Invariant 2: Memory record count increased ---
    final_memory_count = memory.memory_statistics()["total_memories"]
    assert final_memory_count == initial_memory_count + len(test_inputs), (
        f"Expected memory count +{len(test_inputs)}, "
        f"got +{final_memory_count - initial_memory_count}"
    )

    # --- Invariant 3: All results have non-empty IDs ---
    for decision_id, memory_id in results:
        assert isinstance(decision_id, str) and decision_id, "decision_id must be a non-empty string"
        assert isinstance(memory_id, str) and memory_id, "memory_id must be a non-empty string"

    # --- Invariant 4: ConsciousBuffer received all events ---
    with buffer.buffer_lock:
        buffered_ids = {e.event_id for e in buffer.event_buffer}
    expected_ids = {f"evt_{did}" for did, _ in results}
    assert expected_ids.issubset(buffered_ids), (
        f"Buffer missing events: {expected_ids - buffered_ids}"
    )

    # --- Invariant 5: TrainedStateManager can export to a temp dir ---
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_kernel_root = Path(tmpdir) / "antahkarana_kernel"
        tmp_kernel_root.mkdir(parents=True)
        tsm = TrainedStateManager(tmp_kernel_root)
        export_result = tsm.export_from_training_run(memory_system=memory)
        assert isinstance(export_result, dict), "export_from_training_run must return a dict"
        assert "files" in export_result, "export result must have a 'files' key"
        for fpath in export_result["files"]:
            assert Path(fpath).exists(), f"Exported file not found: {fpath}"

        # Manifest must exist
        manifest_path = tsm.trained_state_dir / "trained_state_manifest.json"
        assert manifest_path.exists(), "trained_state_manifest.json not created"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert "generated_at" in manifest, "Manifest must contain 'generated_at'"

    # --- Invariant 6: Coherence is still in valid range ---
    assert 0.0 <= self_model.coherence_score <= 1.0, (
        f"coherence_score out of range: {self_model.coherence_score}"
    )

    # --- Invariant 7: Drive signals are in valid range ---
    drives = self_model.compute_drive_signals()
    for key, value in drives.items():
        if key == "computed_at":
            continue
        assert 0.0 <= float(value) <= 1.0, (
            f"Drive signal '{key}' out of [0, 1]: {value}"
        )


# ---------------------------------------------------------------------------
# Optional integration test — skipped unless RUN_INTEGRATION=1
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION") != "1",
    reason="Set RUN_INTEGRATION=1 to run integration tests (requires full kernel startup)",
)
def test_e2e_live_cycle():
    """
    Optional integration test: starts the full AntahkaranaKernel, processes
    a few inputs, and verifies a state snapshot file can be written.

    Does NOT perform real internet ingestion (no Aakaash calls).
    Only runs when RUN_INTEGRATION=1 is set.
    """
    # Import here so the integration test does not affect unit test collection
    from pathlib import Path as _Path

    _KERNEL_ROOT = _Path(__file__).resolve().parent.parent
    if str(_KERNEL_ROOT) not in sys.path:
        sys.path.insert(0, str(_KERNEL_ROOT))

    from AntahkaranaKernel import AntahkaranaKernel

    random.seed(42)

    kernel = AntahkaranaKernel(identity_name="IntegrationTest_Kernel")
    try:
        kernel.startup()

        # Process a small fixed input set
        test_inputs = [
            "Describe your self-model.",
            "What is your current coherence?",
        ]
        outputs = []
        for text in test_inputs:
            out = kernel.process_input(text, input_type="query")
            outputs.append(out)

        # Invariant: each output is a non-empty string
        for i, out in enumerate(outputs):
            assert isinstance(out, str) and len(out) > 0, (
                f"process_input returned empty/non-string for input {i}: {out!r}"
            )

        # Invariant: kernel state counters incremented
        assert kernel.kernel_state["interactions_processed"] >= len(test_inputs), (
            "interactions_processed counter did not increment correctly"
        )

        # Invariant: write a state snapshot to a temp dir (simulating live_engine_state.json)
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "live_engine_state.json"
            snapshot = kernel.self_model.create_state_snapshot()
            state_payload = {
                "written_at": time.time(),
                "identity": kernel.identity_name,
                "coherence_score": snapshot.coherence_score,
                "interactions_processed": kernel.kernel_state["interactions_processed"],
                "thought_cycles": kernel.kernel_state["thought_cycles"],
                "is_running": kernel.kernel_state["is_running"],
            }
            state_file.write_text(json.dumps(state_payload, indent=2), encoding="utf-8")

            assert state_file.exists(), "live_engine_state.json was not written"
            loaded = json.loads(state_file.read_text(encoding="utf-8"))
            assert "coherence_score" in loaded, "State file missing 'coherence_score'"
            assert "interactions_processed" in loaded, "State file missing 'interactions_processed'"

    finally:
        try:
            kernel.shutdown()
        except Exception:
            pass
