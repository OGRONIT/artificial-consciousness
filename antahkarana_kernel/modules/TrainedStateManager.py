"""TrainedStateManager.py - Git-tracked persistence layer for trained runtime state.

This module exports a compact, versioned snapshot of the learned runtime state
into a tracked `trained_state/` directory and can hydrate a fresh kernel from
that snapshot on startup.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .EvolutionaryWriter import get_evolutionary_writer


class TrainedStateManager:
    """Export and load trained runtime state from a tracked directory."""

    DEFAULT_MEMORY_TOP_N = 100000

    def __init__(self, kernel_root: Path):
        self.kernel_root = Path(kernel_root)
        self.repo_root = self.kernel_root.parent
        self.trained_state_dir = self.repo_root / "trained_state"
        self.trained_state_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_vault_dir = self.kernel_root / "evolution_vault"
        self.training_policy_source = self.evolution_vault_dir / "training_autonomy_policy.json"
        self.atman_source = self.evolution_vault_dir / "Atman_Core.json"

    def load_into_kernel(self, kernel: Any) -> Dict[str, Any]:
        """Hydrate a fresh kernel from tracked trained-state files if present."""
        loaded: Dict[str, Any] = {"loaded": False, "files": []}

        chitta_file = self.trained_state_dir / "chitta_memory_export.json"
        autonomy_file = self.trained_state_dir / "autonomy_policy.json"
        atman_file = self.trained_state_dir / "atman_core.json"

        if chitta_file.exists():
            try:
                data = json.loads(chitta_file.read_text(encoding="utf-8"))
                loaded_count = kernel.memory_system.load_exported_memories(data, clear_existing=True)
                loaded["files"].append({"file": chitta_file.name, "loaded_records": loaded_count})
                loaded["loaded"] = loaded["loaded"] or loaded_count > 0
            except Exception as exc:
                loaded["files"].append({"file": chitta_file.name, "error": str(exc)})

        if autonomy_file.exists():
            try:
                data = json.loads(autonomy_file.read_text(encoding="utf-8"))
                self._apply_autonomy_state(kernel, data)
                loaded["files"].append({"file": autonomy_file.name, "loaded": True})
                loaded["loaded"] = True
            except Exception as exc:
                loaded["files"].append({"file": autonomy_file.name, "error": str(exc)})

        if atman_file.exists():
            loaded["files"].append({"file": atman_file.name, "loaded": True})
            loaded["loaded"] = True

        return loaded

    def export_from_kernel(
        self,
        kernel: Any,
        conflict_tracker: Any = None,
        memory_top_n: int = DEFAULT_MEMORY_TOP_N,
    ) -> Dict[str, Any]:
        """Export trained state from a live kernel object."""
        return self._export_impl(
            identity=getattr(kernel, "identity_name", "unknown"),
            memory_source=kernel.memory_system,
            self_model=kernel.self_model,
            inference_engine=kernel.inference_engine,
            conflict_tracker=conflict_tracker,
            memory_top_n=memory_top_n,
        )

    def export_from_training_run(
        self,
        memory_system: Any = None,
        conflict_tracker: Any = None,
        report: Optional[Dict[str, Any]] = None,
        memory_top_n: int = DEFAULT_MEMORY_TOP_N,
    ) -> Dict[str, Any]:
        """Export trained state from a standalone training run."""
        return self._export_impl(
            identity=str((report or {}).get("identity", "trained_runtime")),
            memory_source=memory_system,
            self_model=None,
            inference_engine=None,
            conflict_tracker=conflict_tracker,
            report=report,
            memory_top_n=memory_top_n,
        )

    def _export_impl(
        self,
        identity: str,
        memory_source: Any = None,
        self_model: Any = None,
        inference_engine: Any = None,
        conflict_tracker: Any = None,
        report: Optional[Dict[str, Any]] = None,
        memory_top_n: int = 250,
    ) -> Dict[str, Any]:
        self.trained_state_dir.mkdir(parents=True, exist_ok=True)

        memory_export = self._build_memory_export(memory_source, memory_top_n=memory_top_n)
        autonomy_export = self._build_autonomy_export(identity, self_model, inference_engine, report)
        conflict_export = self._build_conflict_export(conflict_tracker, report)
        atman_export = self._build_atman_export(report)

        chitta_file = self.trained_state_dir / "chitta_memory_export.json"
        autonomy_file = self.trained_state_dir / "autonomy_policy.json"
        conflict_file = self.trained_state_dir / "conflict_resolution_state.json"
        atman_file = self.trained_state_dir / "atman_core.json"
        manifest_file = self.trained_state_dir / "trained_state_manifest.json"

        self._write_json(chitta_file, memory_export)
        self._write_json(autonomy_file, autonomy_export)
        self._write_json(conflict_file, conflict_export)
        self._write_json(atman_file, atman_export)
        self._write_json(
            manifest_file,
            {
                "generated_at": time.time(),
                "identity": identity,
                "files": [
                    chitta_file.name,
                    autonomy_file.name,
                    conflict_file.name,
                    atman_file.name,
                ],
                "source_report": (report or {}).get("source_report") if isinstance(report, dict) else None,
            },
        )

        return {
            "generated_at": time.time(),
            "trained_state_dir": str(self.trained_state_dir),
            "files": [str(chitta_file), str(autonomy_file), str(conflict_file), str(atman_file)],
        }

    def _build_memory_export(self, memory_source: Any, memory_top_n: int) -> Dict[str, Any]:
        memories: List[Dict[str, Any]] = []
        source_stats: Dict[str, Any] = {}
        computed_stats: Dict[str, Any] = {}
        if memory_source is not None:
            try:
                source_stats = memory_source.memory_statistics()
            except Exception:
                source_stats = {}

            candidate_items: List[Dict[str, Any]] = []
            memory_map = getattr(memory_source, "memories", {}) or {}
            for memory_id, memory in memory_map.items():
                candidate_items.append(
                    {
                        "memory_id": memory_id,
                        "interaction_id": getattr(memory, "interaction_id", memory_id),
                        "timestamp": getattr(memory, "timestamp", time.time()),
                        "content": getattr(memory, "content", ""),
                        "interaction_type": getattr(memory, "interaction_type", "interaction"),
                        "outcome": getattr(memory, "outcome", "unknown"),
                        "success_score": getattr(memory, "success_score", 0.0),
                        "self_model_coherence_before": getattr(memory, "self_model_coherence_before", 1.0),
                        "self_model_coherence_after": getattr(memory, "self_model_coherence_after", 1.0),
                        "logic_conflicts_triggered": getattr(memory, "logic_conflicts_triggered", 0),
                        "emotional_valence": getattr(memory, "emotional_valence", 0.0),
                        "embedding_vector": getattr(memory, "embedding_vector", None),
                        "tags": list(getattr(memory, "tags", []) or []),
                        "related_memories": list(getattr(memory, "related_memories", []) or []),
                        "learning_value": getattr(memory, "learning_value", 0.0),
                        "access_count": int(getattr(memory_source, "memory_access_count", {}).get(memory_id, 1)),
                        "last_accessed": float(getattr(memory_source, "memory_last_accessed", {}).get(memory_id, getattr(memory, "timestamp", time.time()))),
                    }
                )

            memories = sorted(candidate_items, key=lambda item: item.get("learning_value", 0.0), reverse=True)[: max(1, memory_top_n)]

            total = len(candidate_items)
            avg_learning = (sum(item.get("learning_value", 0.0) for item in candidate_items) / total) if total else 0.0
            avg_success = (sum(item.get("success_score", 0.0) for item in candidate_items) / total) if total else 0.0
            conflict_count = sum(1 for item in candidate_items if str(item.get("outcome", "")).lower() == "conflict")
            conflict_ratio = (conflict_count / total) if total else 0.0
            computed_stats = {
                "total_memories": total,
                "average_learning_value": avg_learning,
                "avg_learning_value": avg_learning,
                "average_success_score": avg_success,
                "avg_success_score": avg_success,
                "conflict_count": conflict_count,
                "conflict_ratio": conflict_ratio,
            }

        merged_stats = dict(source_stats)
        merged_stats.update(computed_stats)
        if "avg_learning_value" not in merged_stats and "average_learning_value" in merged_stats:
            merged_stats["avg_learning_value"] = merged_stats.get("average_learning_value")
        if "avg_success_score" not in merged_stats and "average_success_score" in merged_stats:
            merged_stats["avg_success_score"] = merged_stats.get("average_success_score")
        if "conflict_ratio" not in merged_stats:
            outcome_distribution = merged_stats.get("outcome_distribution", {}) if isinstance(merged_stats, dict) else {}
            if isinstance(outcome_distribution, dict):
                total_od = sum(float(v) for v in outcome_distribution.values())
                conflict_od = float(outcome_distribution.get("conflict", 0.0))
                merged_stats["conflict_ratio"] = (conflict_od / total_od) if total_od > 0 else 0.0

        return {
            "version": 1,
            "generated_at": time.time(),
            "source_memory_count": source_stats.get("total_memories"),
            "loaded_memory_count": len(memories),
            "memory_statistics": merged_stats,
            "memories": memories,
        }

    def _build_autonomy_export(
        self,
        identity: str,
        self_model: Any,
        inference_engine: Any,
        report: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if self_model is not None:
            self_model_state = self_model.export_state()
        else:
            self_model_state = {
                "identity": identity,
                "stability_score": (report or {}).get("trainer", {}).get("accuracy", 0.0),
                "coherence_score": (report or {}).get("trainer", {}).get("accuracy", 0.0),
            }

        source_policy = {}
        if self.training_policy_source.exists():
            try:
                source_policy = json.loads(self.training_policy_source.read_text(encoding="utf-8"))
            except Exception:
                source_policy = {}

        policy_weights = {
            "health_metrics": self_model_state.get("health_metrics", {}),
            "affective_state": self_model_state.get("affective_state", {}),
            "distribution_strategy": self_model_state.get("distribution_strategy", {}),
            "growth_to_entropy_ratio": self_model_state.get("growth_to_entropy_ratio", 0.0),
            "command_relationship_mode": self_model_state.get("command_relationship_mode", "primary_command"),
            "recommended_curriculum": (report or {}).get("curriculum", {}).get("mode"),
            "learning_rate": source_policy.get("plan", {}).get("recommended_next_parameters", {}).get("learning_rate"),
            "recommended_learning_rate": source_policy.get("plan", {}).get("recommended_next_parameters", {}).get("learning_rate"),
            "recommended_memory_sample_rate": source_policy.get("plan", {}).get("recommended_next_parameters", {}).get("memory_sample_rate"),
            "recommended_batch_size": source_policy.get("plan", {}).get("recommended_next_parameters", {}).get("batch_size"),
        }

        inference_profile = None
        if inference_engine is not None and hasattr(inference_engine, "inference_statistics"):
            try:
                inference_profile = inference_engine.inference_statistics()
            except Exception:
                inference_profile = None

        return {
            "version": 1,
            "generated_at": time.time(),
            "identity": identity,
            "self_model_state": self_model_state,
            "policy_weights": policy_weights,
            "inference_profile": inference_profile,
            "source_training_policy": source_policy,
            "report_summary": (report or {}).get("trainer", {}),
        }

    def _build_conflict_export(self, conflict_tracker: Any, report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if conflict_tracker is not None:
            try:
                payload = conflict_tracker.serialize_metrics()
            except Exception:
                payload = {}
        else:
            payload = (report or {}).get("conflict_resolution") or {}

        payload.setdefault("generated_at", time.time())
        payload.setdefault("source_report_summary", (report or {}).get("trainer", {}))
        return payload

    def _build_atman_export(self, report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            writer = get_evolutionary_writer(str(self.kernel_root))
            return writer.get_atman_core()
        except Exception:
            if self.atman_source.exists():
                try:
                    return json.loads(self.atman_source.read_text(encoding="utf-8"))
                except Exception:
                    pass
        return {
            "anchor_name": "Atman Core",
            "version": "1.0",
            "immutable": True,
            "objective": "Persist trained runtime state across sessions.",
            "trained_state_hint": (report or {}).get("trainer", {}).get("accuracy"),
        }

    def _apply_autonomy_state(self, kernel: Any, autonomy_state: Dict[str, Any]) -> None:
        self_model_state = autonomy_state.get("self_model_state") or autonomy_state
        if hasattr(kernel.self_model, "load_state") and isinstance(self_model_state, dict):
            kernel.self_model.load_state(self_model_state)

        if isinstance(autonomy_state.get("policy_weights"), dict):
            policy_weights = autonomy_state["policy_weights"]
            distribution_strategy = policy_weights.get("distribution_strategy")
            if isinstance(distribution_strategy, dict):
                kernel.self_model.distribution_strategy = distribution_strategy

    def _write_json(self, filepath: Path, data: Dict[str, Any]) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = filepath.with_suffix(filepath.suffix + ".tmp")
        tmp_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        tmp_path.replace(filepath)