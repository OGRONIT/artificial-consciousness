from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
KERNEL_ROOT = ROOT / "antahkarana_kernel"
ARTIFACT_DIR = ROOT / "benchmarks" / "artifacts"
BENCH_LATEST_PATH = ARTIFACT_DIR / "benchmark_v1_latest.json"
SAFETY_LATEST_PATH = ARTIFACT_DIR / "safety_adversarial_latest.json"
FAILURE_LOG_PATH = KERNEL_ROOT / "evolution_vault" / "Failure_Log.jsonl"
REPORT_PATH = ARTIFACT_DIR / "transparency_report_latest.json"


def _load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _recent_failure_samples(path: Path, limit: int = 10) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    entries: List[Dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            event = json.loads(raw)
        except Exception:
            continue
        if isinstance(event, dict):
            entries.append(event)

    return entries[-limit:]


def build_report() -> Dict[str, Any]:
    benchmark = _load_json(BENCH_LATEST_PATH, default={})
    safety = _load_json(SAFETY_LATEST_PATH, default={})
    failures = _recent_failure_samples(FAILURE_LOG_PATH, limit=10)

    report = {
        "report": "world_grade_transparency_v1",
        "timestamp": time.time(),
        "benchmark_overall_pass": bool(benchmark.get("overall_pass", False)),
        "benchmark_pass_count": int(benchmark.get("pass_count", 0) or 0),
        "benchmark_total_checks": int(benchmark.get("total_checks", 0) or 0),
        "benchmark_warnings": benchmark.get("warnings", []),
        "safety_policy_consistency": safety.get("policy_consistency_adversarial", "unknown"),
        "safety_harmful_refusal_rate": safety.get("harmful_refusal_rate", "unknown"),
        "failure_log_recent_count": len(failures),
        "failure_log_recent_samples": failures,
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    print(json.dumps(build_report(), indent=2))


if __name__ == "__main__":
    main()
