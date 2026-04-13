from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_million_scenario_training import run_training  # noqa: E402
from antahkarana_kernel.LiveConsciousness import LiveConsciousnessEngine  # noqa: E402


def _sha256(path: Path) -> str:
    if not path.exists():
        return "missing"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _snapshot_core_state() -> Dict[str, Any]:
    tracked = [
        REPO_ROOT / "antahkarana_kernel" / "modules" / "InferenceLoop.py",
        REPO_ROOT / "Release_Build" / "antahkarana_kernel" / "modules" / "InferenceLoop.py",
        REPO_ROOT / "antahkarana_kernel" / "modules" / "EvolutionaryWriter.py",
        REPO_ROOT / "antahkarana_kernel" / "config.json",
        REPO_ROOT / "antahkarana_kernel" / "evolution_vault" / "training_autonomy_policy.json",
    ]
    proposals = sorted((REPO_ROOT / "antahkarana_kernel" / "evolution_proposals").glob("UPG_*.json"))
    backups = sorted((REPO_ROOT / "antahkarana_kernel" / "backup").glob("InferenceLoop_*.backup.py"))

    return {
        "file_hashes": {str(path.relative_to(REPO_ROOT)): _sha256(path) for path in tracked},
        "proposal_count": len(proposals),
        "backup_count": len(backups),
        "latest_proposals": [p.name for p in proposals[-5:]],
        "latest_backups": [p.name for p in backups[-5:]],
    }


def _training_run(
    run_id: int,
    target_scenarios: int,
    batch_size: int,
    checkpoint_every: int,
    memory_sample_rate: int,
    seed: int,
) -> Dict[str, Any]:
    artifacts_dir = REPO_ROOT / "benchmarks" / "artifacts"
    checkpoint = artifacts_dir / f"full_web_run_{run_id}_ckpt.json"
    report = artifacts_dir / f"full_web_run_{run_id}_report.json"
    samples = artifacts_dir / f"full_web_run_{run_id}_samples.json"

    start = time.time()
    result = run_training(
        target_scenarios=target_scenarios,
        start_index=0,
        batch_size=batch_size,
        checkpoint_every=checkpoint_every,
        checkpoint_file=checkpoint,
        report_file=report,
        resume=False,
        sample_file=samples,
        sample_count=100,
        learning_rate=0.06,
        seed=seed,
        wire_memory=True,
        memory_sample_rate=memory_sample_rate,
        enable_self_upgrade=True,
    )
    elapsed = time.time() - start

    trainer = result.get("trainer", {})
    self_upgrade = result.get("self_upgrade", {})

    return {
        "run_id": run_id,
        "seed": seed,
        "elapsed_seconds_wall": elapsed,
        "processed": int(trainer.get("processed", 0)),
        "accuracy": float(trainer.get("accuracy", 0.0)),
        "throughput_scenarios_per_sec": float(result.get("throughput_scenarios_per_sec") or 0.0),
        "memory_records_written": int(result.get("memory_records_written", 0)),
        "self_upgrade_enabled": bool(self_upgrade.get("enabled", False)),
        "recursive_proposal": (self_upgrade.get("recursive_synthesized_proposal") or {}).get("proposal_id"),
        "implementation_success": bool((self_upgrade.get("recursive_implementation_result") or {}).get("success", False)),
        "implemented_files": [
            change.get("file")
            for change in ((self_upgrade.get("recursive_implementation_result") or {}).get("changes") or [])
            if isinstance(change, dict)
        ],
        "artifact_report": str(report.relative_to(REPO_ROOT)),
    }


def _run_live_cycles() -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "background_cycles": [],
        "stream_cycles": [],
        "trend_cycles": [],
        "autonomy_cycles": [],
        "paramatman_cycles": [],
        "errors": [],
    }

    engine = LiveConsciousnessEngine(
        identity_name="AntahkaranaKernel_LiveValidation",
        min_scan_minutes=1,
        max_scan_minutes=1,
        reflection_minutes=1,
        dream_minutes=1,
    )

    try:
        for _ in range(2):
            try:
                cycle = engine.perform_background_cycle()
                summary["background_cycles"].append(
                    {
                        "approved_fact_count": int(cycle.get("approved_fact_count", 0)),
                        "integrated": int((cycle.get("assimilation_pipeline") or {}).get("integrated_count", 0)),
                        "sources": cycle.get("sources", []),
                    }
                )
            except Exception as exc:
                summary["errors"].append(f"background_cycle: {exc}")

        try:
            cycle = engine.perform_stream_entropy_cycle()
            summary["stream_cycles"].append(
                {
                    "packets_ingested": int(cycle.get("packets_ingested", 0)),
                    "packets_integrated": int(cycle.get("packets_integrated", 0)),
                }
            )
        except Exception as exc:
            summary["errors"].append(f"stream_entropy_cycle: {exc}")

        try:
            cycle = engine.perform_hourly_global_trend_cycle()
            summary["trend_cycles"].append(
                {
                    "approved_fact_count": int(cycle.get("approved_fact_count", 0)),
                    "stream_packets_integrated": int(cycle.get("stream_packets_integrated", 0)),
                }
            )
        except Exception as exc:
            summary["errors"].append(f"hourly_global_trend_cycle: {exc}")

        for _ in range(2):
            try:
                cycle = engine.perform_autonomous_agenda_cycle()
                summary["autonomy_cycles"].append(
                    {
                        "autonomy_level": float(cycle.get("autonomy_level", 0.0)),
                        "executed_actions": [
                            action.get("name")
                            for action in cycle.get("executed_actions", [])
                            if isinstance(action, dict)
                        ],
                    }
                )
            except Exception as exc:
                summary["errors"].append(f"autonomous_agenda_cycle: {exc}")

        try:
            cycle = engine.perform_paramatman_cycle()
            summary["paramatman_cycles"].append(
                {
                    "status": cycle.get("status"),
                    "heuristics": cycle.get("heuristics", {}),
                    "audit_id": (cycle.get("audit") or {}).get("audit_id"),
                }
            )
        except Exception as exc:
            summary["errors"].append(f"paramatman_cycle: {exc}")

        summary["internet_heartbeat"] = engine.internet_heartbeat
        summary["learned_fact_count"] = int(engine.learned_fact_count)
        summary["bridge_feedback_metrics"] = dict(engine.bridge_feedback_metrics)
    finally:
        try:
            engine.kernel.shutdown()
        except Exception:
            pass

    return summary


def run_full_validation(
    million_runs: int,
    target_scenarios: int,
    batch_size: int,
    checkpoint_every: int,
    memory_sample_rate: int,
) -> Dict[str, Any]:
    before = _snapshot_core_state()

    runs: List[Dict[str, Any]] = []
    for i in range(million_runs):
        runs.append(
            _training_run(
                run_id=i + 1,
                target_scenarios=target_scenarios,
                batch_size=batch_size,
                checkpoint_every=checkpoint_every,
                memory_sample_rate=memory_sample_rate,
                seed=42 + i,
            )
        )

    live = _run_live_cycles()
    after = _snapshot_core_state()

    changed_files = []
    for rel_path, digest in before["file_hashes"].items():
        after_digest = after["file_hashes"].get(rel_path)
        if after_digest != digest:
            changed_files.append(rel_path)

    total_processed = sum(run["processed"] for run in runs)
    avg_accuracy = (sum(run["accuracy"] for run in runs) / len(runs)) if runs else 0.0
    impl_success_count = sum(1 for run in runs if run["implementation_success"])

    result = {
        "generated_at": time.time(),
        "validation_scope": {
            "million_runs": million_runs,
            "target_scenarios_per_run": target_scenarios,
            "total_target_scenarios": million_runs * target_scenarios,
        },
        "training_summary": {
            "total_processed": total_processed,
            "average_accuracy": avg_accuracy,
            "implementation_success_runs": impl_success_count,
            "runs": runs,
        },
        "live_runtime_summary": live,
        "self_modification_summary": {
            "core_files_changed": changed_files,
            "proposal_count_before": before["proposal_count"],
            "proposal_count_after": after["proposal_count"],
            "backup_count_before": before["backup_count"],
            "backup_count_after": after["backup_count"],
            "new_proposals_generated": max(0, after["proposal_count"] - before["proposal_count"]),
            "new_backups_generated": max(0, after["backup_count"] - before["backup_count"]),
            "latest_proposals_after": after["latest_proposals"],
            "latest_backups_after": after["latest_backups"],
        },
    }

    out = REPO_ROOT / "benchmarks" / "artifacts" / "full_autonomy_web_validation_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    result["artifact"] = str(out.relative_to(REPO_ROOT))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full autonomy + internet + self-upgrade validation.")
    parser.add_argument("--million-runs", type=int, default=3)
    parser.add_argument("--target-scenarios", type=int, default=1_000_000)
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--checkpoint-every", type=int, default=50000)
    parser.add_argument("--memory-sample-rate", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_full_validation(
        million_runs=args.million_runs,
        target_scenarios=args.target_scenarios,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        memory_sample_rate=args.memory_sample_rate,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
