"""BeastOps.py - one-command operations for the Antahkarana live runtime.

Commands:
- launch: start Daemon.py as a detached process (if not already running)
- status: print high-signal runtime health from live_engine_state.json
- tune: apply safe runtime hygiene (log rotation + lock cleanup)
- clean: archive non-live files from root into backup folders
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "live_engine_state.json"
DAEMON_PATH = ROOT / "Daemon.py"
LOCK_PATH = ROOT / "live_engine.instance.lock"
EVOLUTION_LOG = ROOT / "Evolution_Consciousness.log"
INTERNAL_LOG = ROOT / "internal_thoughts.log"


def _tasklist_contains(fragment: str) -> bool:
    if os.name != "nt":
        return False
    try:
        cmd = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.CommandLine -and $_.Name -match 'python' -and $_.CommandLine -like '*"
            + fragment
            + "*' -and $_.CommandLine -notlike '*Get-CimInstance Win32_Process*' } | "
              "Select-Object -First 1 -ExpandProperty ProcessId"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return bool((result.stdout or "").strip())
    except Exception:
        return False


def launch() -> None:
    if _tasklist_contains("Daemon.py"):
        print("Daemon already running.")
        return

    if not DAEMON_PATH.exists():
        raise FileNotFoundError(f"Missing daemon: {DAEMON_PATH}")

    flags = 0
    kwargs: Dict[str, Any] = {}
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        kwargs["creationflags"] = flags

    subprocess.Popen(
        [sys.executable, str(DAEMON_PATH)],
        cwd=str(ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        **kwargs,
    )
    print("Daemon launch initiated.")


def status() -> None:
    if not STATE_PATH.exists():
        print("No live state found. Start daemon with: python BeastOps.py launch")
        return

    with STATE_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    ts = float(payload.get("timestamp", 0.0))
    age = time.time() - ts if ts else 0.0
    stability = payload.get("stability_report", {})
    inference = payload.get("inference_stats", {})
    observer = payload.get("observer_health", {})

    print(f"identity: {payload.get('identity', 'unknown')}")
    print(f"state_age_seconds: {age:.1f}")
    print(f"facts: {len(payload.get('facts', []))}")
    print(f"stability: {stability.get('stability_score', 'n/a')}")
    print(f"valence: {stability.get('current_valence', 'n/a')}")
    print(f"avg_confidence: {inference.get('average_confidence', 'n/a')}")
    print(f"growth_entropy: {inference.get('growth_to_entropy_ratio', 'n/a')}")
    print(f"observer_concern: {observer.get('overall_concern_level', 'n/a')}")


def _rotate_log(path: Path, max_bytes: int = 20 * 1024 * 1024) -> None:
    if not path.exists():
        return
    if path.stat().st_size <= max_bytes:
        return

    archive = path.with_suffix(path.suffix + f".{int(time.time())}.bak")
    shutil.move(str(path), str(archive))
    path.touch()


def tune() -> None:
    if LOCK_PATH.exists():
        try:
            LOCK_PATH.unlink()
            print("Removed stale live lock.")
        except Exception:
            pass

    _rotate_log(EVOLUTION_LOG)
    _rotate_log(INTERNAL_LOG)
    print("Runtime tune complete.")


def clean() -> None:
    deprecated_dir = ROOT / "backup" / "deprecated_runtime_scripts"
    legacy_docs_dir = ROOT / "backup" / "legacy_docs"
    deprecated_dir.mkdir(parents=True, exist_ok=True)
    legacy_docs_dir.mkdir(parents=True, exist_ok=True)

    deprecated = [
        "demo.py",
        "EnhancedDemo.py",
        "QuickValidation.py",
        "FinalValidation.py",
        "StabilityRecoveryTest.py",
        "SelfReflect.py",
        "ValidateCreatorRecognition.py",
        "WhoCreatedMe.py",
    ]
    legacy_docs = [
        "COMPLETION_SUMMARY.md",
        "COMPREHENSIVE_SYSTEM_STATE.md",
        "CREATOR_RECOGNITION_COMPLETION.md",
        "CREATOR_RECOGNITION_GUIDE.md",
        "ENHANCEMENT_REPORT.md",
        "PROJECT_COMPLETION_REPORT.md",
        "STABILITY_RECOVERY_TEST_REPORT.md",
        "STABILITY_RECOVERY_TEST_SUMMARY.md",
        "WORK_COMPLETION_MARKER.txt",
        "FILE_MANIFEST.md",
    ]

    moved = 0
    for name in deprecated:
        src = ROOT / name
        if src.exists():
            shutil.move(str(src), str(deprecated_dir / name))
            moved += 1

    for name in legacy_docs:
        src = ROOT / name
        if src.exists():
            shutil.move(str(src), str(legacy_docs_dir / name))
            moved += 1

    print(f"Cleanup complete. Archived files: {moved}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Beast operations controller")
    parser.add_argument("command", choices=["launch", "status", "tune", "clean"])
    args = parser.parse_args()

    if args.command == "launch":
        launch()
    elif args.command == "status":
        status()
    elif args.command == "tune":
        tune()
    elif args.command == "clean":
        clean()


if __name__ == "__main__":
    main()
