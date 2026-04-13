from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TRAINED_STATE_DIR = REPO_ROOT / "trained_state"
KERNEL_ROOT = REPO_ROOT / "antahkarana_kernel"

SHADOW_MEMORY_PATH = KERNEL_ROOT / "evolution_vault" / "shadow_memory" / "shadow_memory.jsonl"
CONFLICT_METRICS_PATH = KERNEL_ROOT / "evolution_vault" / "conflict_resolution_metrics.json"
FULL_REPORT_PATH = REPO_ROOT / "benchmarks" / "artifacts" / "full_web_run_10_report.json"
LIVE_STATE_PATH = REPO_ROOT / "live_engine_state.json"
ATMAN_CORE_PATH = REPO_ROOT / "Atman_Core.json"


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_shadow_memory_records() -> list[dict]:
    records: list[dict] = []
    if not SHADOW_MEMORY_PATH.exists():
        return records

    with SHADOW_MEMORY_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return records


def _generate_chitta_export() -> dict:
    records = _load_shadow_memory_records()
    normalized: list[dict] = []
    for idx, record in enumerate(records):
        interaction_id = str(record.get("interaction_id") or record.get("memory_id") or f"loaded_{idx}")
        memory_id = str(
            record.get("memory_id")
            or hashlib.sha256(f"{interaction_id}_{record.get('timestamp', 0)}".encode()).hexdigest()[:16]
        )
        normalized.append(
            {
                "memory_id": memory_id,
                "interaction_id": interaction_id,
                "timestamp": record.get("timestamp", time.time()),
                "content": record.get("content", ""),
                "interaction_type": record.get("interaction_type", "interaction"),
                "outcome": record.get("outcome", "unknown"),
                "success_score": record.get("success_score", 0.0),
                "self_model_coherence_before": record.get("self_model_coherence_before", record.get("coherence_before", 1.0)),
                "self_model_coherence_after": record.get("self_model_coherence_after", record.get("coherence_after", 1.0)),
                "logic_conflicts_triggered": record.get("logic_conflicts_triggered", record.get("logic_conflicts", 0)),
                "emotional_valence": record.get("emotional_valence", 0.0),
                "embedding_vector": record.get("embedding_vector"),
                "tags": record.get("tags", []),
                "related_memories": record.get("related_memories", []),
                "learning_value": record.get("learning_value", 0.0),
                "access_count": record.get("access_count", 1),
                "last_accessed": record.get("last_accessed", record.get("timestamp", time.time())),
            }
        )

    normalized.sort(key=lambda item: item.get("learning_value", 0.0), reverse=True)
    return {
        "version": 1,
        "generated_at": time.time(),
        "source_memory_count": len(records),
        "loaded_memory_count": min(250, len(normalized)),
        "memory_statistics": {
            "total_memories": len(records),
            "average_learning_value": (sum(item.get("learning_value", 0.0) for item in records) / len(records)) if records else 0.0,
            "average_success_score": (sum(item.get("success_score", 0.0) for item in records) / len(records)) if records else 0.0,
            "highest_learning_value": normalized[:5],
        },
        "memories": normalized[:250],
    }


def _generate_conflict_export() -> dict:
    payload = _read_json(CONFLICT_METRICS_PATH)
    payload.setdefault("generated_at", time.time())
    payload.setdefault("source_metrics_file", str(CONFLICT_METRICS_PATH))
    return payload


def _generate_autonomy_export() -> dict:
    policy_report = _read_json(FULL_REPORT_PATH)
    live_snapshot = _read_json(LIVE_STATE_PATH)
    self_model_state = {
        "identity": live_snapshot.get("identity", "AntahkaranaKernel_Live"),
        "creation_timestamp": live_snapshot.get("timestamp", time.time()),
        "uptime_seconds": live_snapshot.get("consciousness_progress", {}).get("overall_index", 0.0),
        "existence_state": "active",
        "processed_inputs": live_snapshot.get("llm_cognitive_loop", {}).get("processed_events", 0),
        "internal_conflicts": live_snapshot.get("observer_health", {}).get("total_anomalies", 0),
        "coherence_score": live_snapshot.get("stability_report", {}).get("stability_score", 1.0),
        "stability_score": live_snapshot.get("stability_report", {}).get("stability_score", 1.0),
        "health_metrics": {
            "logic_consistency": live_snapshot.get("stability_report", {}).get("stability_score", 1.0),
            "memory_stability": 1.0,
            "response_coherence": live_snapshot.get("inference_stats", {}).get("average_confidence", 1.0),
            "identity_integrity": 1.0,
        },
        "affective_state": {
            "current_valence": live_snapshot.get("stability_report", {}).get("current_valence", 0.0),
            "emotional_momentum": live_snapshot.get("stability_report", {}).get("pain_trend", 0.0),
            "pattern_discovery_count": live_snapshot.get("learned_fact_count", 0),
            "error_count": live_snapshot.get("observer_health", {}).get("total_anomalies", 0),
        },
        "trust_score": live_snapshot.get("creator_awareness", {}).get("trust_score", 0.5),
        "growth_to_entropy_ratio": live_snapshot.get("inference_stats", {}).get("growth_to_entropy_ratio", 0.0),
        "command_relationship_mode": "primary_command",
        "distribution_strategy": live_snapshot.get("body_status", {}).get("distribution_strategy", {"active": False, "channels": []}) if isinstance(live_snapshot.get("body_status"), dict) else {"active": False, "channels": []},
    }

    return {
        "version": 1,
        "generated_at": time.time(),
        "identity": live_snapshot.get("identity", "AntahkaranaKernel_Live"),
        "self_model_state": self_model_state,
        "policy_weights": {
            "recommended_curriculum": "adversarial",
            "recommended_learning_rate": policy_report.get("self_upgrade", {}).get("recommended_next_parameters", {}).get("learning_rate"),
            "recommended_memory_sample_rate": policy_report.get("self_upgrade", {}).get("recommended_next_parameters", {}).get("memory_sample_rate"),
            "recommended_batch_size": policy_report.get("self_upgrade", {}).get("recommended_next_parameters", {}).get("batch_size"),
            "current_training_accuracy": policy_report.get("trainer", {}).get("accuracy"),
            "current_training_learning_value": policy_report.get("memory_after", {}).get("average_learning_value"),
        },
        "inference_profile": live_snapshot.get("inference_stats", {}),
        "source_training_report": {
            "report_file": str(FULL_REPORT_PATH),
            "accuracy": policy_report.get("trainer", {}).get("accuracy"),
            "memory_average_learning_value": policy_report.get("memory_after", {}).get("average_learning_value"),
        },
    }


def _generate_atman_export() -> dict:
    return _read_json(ATMAN_CORE_PATH) or {
        "anchor_name": "Atman Core",
        "version": "1.0",
        "immutable": True,
        "objective": "Persist trained runtime state across sessions.",
    }


def main() -> None:
    TRAINED_STATE_DIR.mkdir(parents=True, exist_ok=True)

    chitta = _generate_chitta_export()
    conflict = _generate_conflict_export()
    autonomy = _generate_autonomy_export()
    atman = _generate_atman_export()

    (TRAINED_STATE_DIR / "chitta_memory_export.json").write_text(json.dumps(chitta, indent=2, default=str), encoding="utf-8")
    (TRAINED_STATE_DIR / "conflict_resolution_state.json").write_text(json.dumps(conflict, indent=2, default=str), encoding="utf-8")
    (TRAINED_STATE_DIR / "autonomy_policy.json").write_text(json.dumps(autonomy, indent=2, default=str), encoding="utf-8")
    (TRAINED_STATE_DIR / "atman_core.json").write_text(json.dumps(atman, indent=2, default=str), encoding="utf-8")

    manifest = {
        "generated_at": time.time(),
        "identity": autonomy.get("identity"),
        "files": [
            "chitta_memory_export.json",
            "conflict_resolution_state.json",
            "autonomy_policy.json",
            "atman_core.json",
        ],
        "source_files": {
            "shadow_memory": str(SHADOW_MEMORY_PATH),
            "conflict_metrics": str(CONFLICT_METRICS_PATH),
            "live_state": str(LIVE_STATE_PATH),
            "training_report": str(FULL_REPORT_PATH),
            "atman_core": str(ATMAN_CORE_PATH),
        },
    }
    (TRAINED_STATE_DIR / "trained_state_manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    print(json.dumps({"trained_state_dir": str(TRAINED_STATE_DIR), "loaded_memory_count": chitta["loaded_memory_count"]}, indent=2))


if __name__ == "__main__":
    main()
