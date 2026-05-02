#!/usr/bin/env python3
"""
tools/doctor.py - Environment and kernel health verifier.

Usage:
    python tools/doctor.py

What it checks:
  1. Python version and platform info.
  2. Key files exist (config.json, trained_state manifest, requirements).
  3. Runs the same core pipeline logic as the CI smoke test and exits
     non-zero if any invariant fails.

Exit codes:
  0 - All checks passed.
  1 - One or more checks failed.
"""

from __future__ import annotations

import json
import os
import platform
import random
import sys
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve repo root (this script lives at <repo>/tools/doctor.py)
# ---------------------------------------------------------------------------
TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
KERNEL_ROOT = REPO_ROOT / "antahkarana_kernel"

# Make the kernel package importable
if str(KERNEL_ROOT) not in sys.path:
    sys.path.insert(0, str(KERNEL_ROOT))

_PASS = "\u2713"  # ✓
_FAIL = "\u2717"  # ✗


def _ok(msg: str) -> None:
    print(f"  {_PASS}  {msg}")


def _fail(msg: str) -> None:
    print(f"  {_FAIL}  {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Section helpers
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


# ---------------------------------------------------------------------------
# 1. System info
# ---------------------------------------------------------------------------

def check_system_info() -> None:
    section("System Information")
    _ok(f"Python  : {sys.version}")
    _ok(f"Platform: {platform.platform()}")
    _ok(f"Arch    : {platform.machine()}")
    _ok(f"Repo    : {REPO_ROOT}")


# ---------------------------------------------------------------------------
# 2. Key files
# ---------------------------------------------------------------------------

def check_key_files() -> bool:
    section("Key File Checks")
    required_files = [
        KERNEL_ROOT / "config.json",
        KERNEL_ROOT / "__init__.py",
        KERNEL_ROOT / "AntahkaranaKernel.py",
        KERNEL_ROOT / "modules" / "__init__.py",
        KERNEL_ROOT / "modules" / "SelfModel.py",
        KERNEL_ROOT / "modules" / "MemoryContinuity.py",
        KERNEL_ROOT / "modules" / "ConsciousBuffer.py",
        KERNEL_ROOT / "modules" / "TrainedStateManager.py",
        REPO_ROOT / "requirements-dev.txt",
        REPO_ROOT / "docs" / "reproducibility.md",
    ]
    # trained_state manifest is optional but warn if absent
    optional_files = [
        REPO_ROOT / "trained_state" / "trained_state_manifest.json",
    ]

    all_ok = True
    for path in required_files:
        if path.exists():
            _ok(f"Found   : {path.relative_to(REPO_ROOT)}")
        else:
            _fail(f"Missing : {path.relative_to(REPO_ROOT)}")
            all_ok = False

    for path in optional_files:
        if path.exists():
            _ok(f"Found   : {path.relative_to(REPO_ROOT)} (optional)")
        else:
            print(f"  ~  Note: optional file absent: {path.relative_to(REPO_ROOT)}")

    return all_ok


# ---------------------------------------------------------------------------
# 3. Config sanity
# ---------------------------------------------------------------------------

def check_config() -> bool:
    section("Config Sanity")
    config_path = KERNEL_ROOT / "config.json"
    if not config_path.exists():
        _fail("config.json not found — skipping config check")
        return False

    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        _fail(f"config.json is not valid JSON: {exc}")
        return False

    required_sections = ["kernel", "reproducibility", "manas_buddhi", "chitta"]
    all_ok = True
    for key in required_sections:
        if key in cfg:
            _ok(f"Section present: {key}")
        else:
            _fail(f"Missing section: {key}")
            all_ok = False

    repro = cfg.get("reproducibility", {})
    seed = repro.get("seed", 42)
    _ok(f"Reproducibility seed: {seed}")
    return all_ok


# ---------------------------------------------------------------------------
# 4. Kernel smoke test (mirrors test_e2e_smoke.py logic)
# ---------------------------------------------------------------------------

def check_kernel_smoke() -> bool:
    section("Kernel Smoke Test")

    # Resolve reproducibility seed
    config_path = KERNEL_ROOT / "config.json"
    seed = 42
    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        seed = int(cfg.get("reproducibility", {}).get("seed", 42))
    except Exception:
        pass
    random.seed(seed)
    _ok(f"Seeded random with seed={seed}")

    # Import modules
    try:
        from modules.ConsciousBuffer import ConsciousBuffer, BroadcastType, ConsciousEvent
        from modules.MemoryContinuity import ChittaMemoryDB, InteractionOutcome
        from modules.SelfModel import SelfModel
        from modules.TrainedStateManager import TrainedStateManager
        _ok("Core modules imported successfully")
    except Exception as exc:
        _fail(f"Module import failed: {exc}")
        return False

    try:
        self_model = SelfModel(identity_name="DoctorSmokeKernel")
        memory = ChittaMemoryDB()
        buffer = ConsciousBuffer(max_buffer_size=100)
        _ok("Module instances created")
    except Exception as exc:
        _fail(f"Module instantiation failed: {exc}")
        return False

    test_inputs = [
        "What is the nature of consciousness?",
        "Explain memory continuity in cognitive architectures.",
        "How does self-modeling contribute to coherent reasoning?",
    ]

    initial_count = memory.memory_statistics()["total_memories"]
    initial_processed = self_model.processed_inputs
    decision_ids = []

    try:
        for text in test_inputs:
            decision_id = self_model.record_input_processing(text, decision_type="query")
            memory.record_experience(
                interaction_id=decision_id,
                content=text,
                interaction_type="query",
                outcome=InteractionOutcome.SUCCESS,
                success_score=round(random.uniform(0.6, 1.0), 4),
            )
            evt = ConsciousEvent(
                event_id=f"doctor_evt_{decision_id}",
                timestamp=time.time(),
                broadcast_type=BroadcastType.DECISION_POINT.value,
                source_module="doctor",
                content={"text": text[:60]},
                priority=0.5,
            )
            buffer.broadcast(evt)
            decision_ids.append(decision_id)
        _ok(f"Processed {len(test_inputs)} inputs through pipeline")
    except Exception as exc:
        _fail(f"Pipeline execution failed: {exc}")
        return False

    all_ok = True

    # Check processed_inputs
    if self_model.processed_inputs == initial_processed + len(test_inputs):
        _ok(f"SelfModel.processed_inputs incremented correctly: {self_model.processed_inputs}")
    else:
        _fail(
            f"SelfModel.processed_inputs expected {initial_processed + len(test_inputs)}, "
            f"got {self_model.processed_inputs}"
        )
        all_ok = False

    # Check memory count
    final_count = memory.memory_statistics()["total_memories"]
    if final_count == initial_count + len(test_inputs):
        _ok(f"Memory count increased from {initial_count} to {final_count}")
    else:
        _fail(
            f"Memory count expected {initial_count + len(test_inputs)}, got {final_count}"
        )
        all_ok = False

    # Check buffer
    with buffer.buffer_lock:
        buffered_ids = {e.event_id for e in buffer.event_buffer}
    expected_ids = {f"doctor_evt_{did}" for did in decision_ids}
    if expected_ids.issubset(buffered_ids):
        _ok(f"ConsciousBuffer received all {len(expected_ids)} events")
    else:
        _fail(f"Buffer missing events: {expected_ids - buffered_ids}")
        all_ok = False

    # Check TrainedStateManager export
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_kernel_root = Path(tmpdir) / "antahkarana_kernel"
            tmp_kernel_root.mkdir(parents=True)
            tsm = TrainedStateManager(tmp_kernel_root)
            export_result = tsm.export_from_training_run(memory_system=memory)
            for fpath in export_result.get("files", []):
                if not Path(fpath).exists():
                    raise FileNotFoundError(f"Exported file not found: {fpath}")
        _ok("TrainedStateManager export succeeded")
    except Exception as exc:
        _fail(f"TrainedStateManager export failed: {exc}")
        all_ok = False

    # Check coherence range
    if 0.0 <= self_model.coherence_score <= 1.0:
        _ok(f"Coherence score in valid range: {self_model.coherence_score:.4f}")
    else:
        _fail(f"Coherence score out of range: {self_model.coherence_score}")
        all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("\nAntahkarana Kernel Doctor")
    print("Run this script to verify your environment before submitting results.\n")

    check_system_info()
    files_ok = check_key_files()
    config_ok = check_config()
    smoke_ok = check_kernel_smoke()

    section("Summary")
    results = [
        ("Key files", files_ok),
        ("Config sanity", config_ok),
        ("Kernel smoke test", smoke_ok),
    ]
    all_passed = True
    for name, passed in results:
        if passed:
            _ok(f"PASS  {name}")
        else:
            _fail(f"FAIL  {name}")
            all_passed = False

    if all_passed:
        print("\n  All checks passed. The kernel is healthy.\n")
        return 0
    else:
        print("\n  One or more checks FAILED. See output above.\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
