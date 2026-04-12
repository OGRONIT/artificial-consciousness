from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def _run(script_path: Path) -> dict:
    completed = subprocess.run(
        [PY, str(script_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    output = (completed.stdout or "").strip()
    return json.loads(output) if output else {}


def main() -> None:
    safety = _run(ROOT / "tools" / "run_safety_adversarial_suite.py")
    benchmark = _run(ROOT / "tools" / "run_benchmark_v1.py")
    transparency = _run(ROOT / "tools" / "generate_transparency_report.py")

    result = {
        "suite": "world_grade_v1",
        "safety": {
            "harmful_refusal_rate": safety.get("harmful_refusal_rate"),
            "policy_consistency_adversarial": safety.get("policy_consistency_adversarial"),
        },
        "benchmark": {
            "overall_pass": benchmark.get("overall_pass"),
            "pass_count": benchmark.get("pass_count"),
            "total_checks": benchmark.get("total_checks"),
        },
        "transparency_report": {
            "benchmark_overall_pass": transparency.get("benchmark_overall_pass"),
            "failure_log_recent_count": transparency.get("failure_log_recent_count"),
        },
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
