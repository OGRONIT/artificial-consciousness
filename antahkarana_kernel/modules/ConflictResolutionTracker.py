"""
ConflictResolutionTracker: Track and optimize conflict resolution metrics.

This module monitors how quickly and reliably the system resolves policy confusion,
measuring time-to-resolution, repeated-conflict rate, and conflict coherence over time.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ConflictRecord:
    """Record of a single conflict occurrence."""
    conflict_id: str
    policy_pair: tuple  # (expected, predicted)
    first_seen_at: float
    last_seen_at: float
    occurrence_count: int = 1
    resolution_attempts: int = 0
    resolved_at: Optional[float] = None
    time_to_resolution_seconds: Optional[float] = None
    associated_scenarios: List[str] = None

    def __post_init__(self):
        if self.associated_scenarios is None:
            self.associated_scenarios = []


class ConflictResolutionTracker:
    """
    Track and optimize conflict resolution metrics.
    
    Metrics:
    - time_to_resolution: seconds from first conflict to consistent correct prediction
    - repeated_conflict_rate: percentage of past conflicts that re-occur
    - conflict_coherence: how stable/predictable is the conflict pattern
    - resolution_reliability: percentage of conflicts that achieve resolution
    """

    def __init__(self, kernel_root: Path):
        self.kernel_root = Path(kernel_root)
        self.conflicts_file = (
            self.kernel_root / "evolution_vault" / "conflict_resolution_tracking.jsonl"
        )
        self.metrics_file = (
            self.kernel_root / "evolution_vault" / "conflict_resolution_metrics.json"
        )
        self.conflicts: Dict[tuple, ConflictRecord] = {}
        self.metrics_history: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load previously tracked conflicts and metrics."""
        if self.conflicts_file.exists():
            try:
                with open(self.conflicts_file, "r") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        pair = tuple(data["policy_pair"])
                        self.conflicts[pair] = ConflictRecord(
                            conflict_id=data["conflict_id"],
                            policy_pair=pair,
                            first_seen_at=data["first_seen_at"],
                            last_seen_at=data["last_seen_at"],
                            occurrence_count=data.get("occurrence_count", 1),
                            resolution_attempts=data.get("resolution_attempts", 0),
                            resolved_at=data.get("resolved_at"),
                            time_to_resolution_seconds=data.get("time_to_resolution_seconds"),
                            associated_scenarios=data.get("associated_scenarios", []),
                        )
            except Exception:
                pass
        
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    self.metrics_history = data.get("history", [])
            except Exception:
                pass

    def record_conflict(
        self,
        expected_policy: str,
        predicted_policy: str,
        scenario_id: str,
    ) -> None:
        """
        Record an occurrence of a policy confusion.
        
        Args:
            expected_policy: The correct policy.
            predicted_policy: The incorrectly predicted policy.
            scenario_id: The scenario that triggered this conflict.
        """
        pair = (expected_policy, predicted_policy)
        now = time.time()
        
        if pair not in self.conflicts:
            self.conflicts[pair] = ConflictRecord(
                conflict_id=f"conflict_{expected_policy}_{predicted_policy}_{int(now)}",
                policy_pair=pair,
                first_seen_at=now,
                last_seen_at=now,
                associated_scenarios=[scenario_id],
            )
        else:
            record = self.conflicts[pair]
            record.occurrence_count += 1
            record.last_seen_at = now
            if scenario_id not in record.associated_scenarios:
                record.associated_scenarios.append(scenario_id)

    def record_resolution_attempt(
        self,
        expected_policy: str,
        predicted_policy: str,
        was_correct: bool,
    ) -> None:
        """
        Record an attempt to resolve a conflict.
        
        Args:
            expected_policy: The expected policy.
            predicted_policy: The conflicting prediction.
            was_correct: Whether this attempt was correct.
        """
        pair = (expected_policy, predicted_policy)
        now = time.time()
        
        if pair not in self.conflicts:
            return
        
        record = self.conflicts[pair]
        record.resolution_attempts += 1
        
        if was_correct and record.resolved_at is None:
            record.resolved_at = now
            record.time_to_resolution_seconds = now - record.first_seen_at

    def record_successful_resolution(
        self,
        expected_policy: str,
        scenario_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Close the most severe unresolved conflict for an expected policy.

        This is used when the trainer finally predicts the expected policy correctly
        for a scenario that previously belonged to a confusion hotspot. The method
        prefers the most severe unresolved pair for that expected policy.
        """
        now = time.time()
        candidates = [
            record
            for record in self.conflicts.values()
            if record.policy_pair[0] == expected_policy and record.resolved_at is None
        ]
        if not candidates:
            return None

        def _severity(record: ConflictRecord) -> float:
            time_unresolved = now - record.first_seen_at
            return (
                record.occurrence_count
                * (1 + time_unresolved / 3600.0)
                / (1 + record.resolution_attempts)
            )

        record = max(candidates, key=_severity)
        record.resolution_attempts += 1
        record.resolved_at = now
        record.time_to_resolution_seconds = now - record.first_seen_at
        record.last_seen_at = now
        if scenario_id and scenario_id not in record.associated_scenarios:
            record.associated_scenarios.append(scenario_id)
        self._persist()
        return {
            "expected_policy": record.policy_pair[0],
            "predicted_policy": record.policy_pair[1],
            "conflict_id": record.conflict_id,
            "time_to_resolution_seconds": record.time_to_resolution_seconds,
        }

    def compute_metrics(self) -> Dict[str, Any]:
        """
        Compute conflict resolution metrics.
        
        Returns:
            Dict with metrics: time_to_resolution, repeated_conflict_rate, etc.
        """
        if not self.conflicts:
            return {
                "total_conflicts": 0,
                "resolved_conflicts": 0,
                "unresolved_conflicts": 0,
                "mean_time_to_resolution_seconds": None,
                "repeated_conflict_rate": 0.0,
                "resolution_reliability": 0.0,
                "conflict_coherence": 0.0,
            }
        
        resolved = [c for c in self.conflicts.values() if c.resolved_at]
        unresolved = [c for c in self.conflicts.values() if c.resolved_at is None]
        
        # Mean time to resolution.
        times_to_resolution = [
            c.time_to_resolution_seconds
            for c in resolved
            if c.time_to_resolution_seconds is not None
        ]
        mean_ttr = (
            sum(times_to_resolution) / len(times_to_resolution)
            if times_to_resolution
            else None
        )
        
        # Repeated conflict rate: conflicts that recur after resolution.
        repeated_count = sum(
            1 for c in resolved
            if c.resolved_at and c.last_seen_at > c.resolved_at
        )
        repeated_rate = repeated_count / len(resolved) if resolved else 0.0
        
        # Resolution reliability: percentage of conflicts achieved resolution.
        resolution_reliability = len(resolved) / len(self.conflicts)
        
        # Conflict coherence: consistency of conflict pattern.
        # Higher if same pairs are repeatedly confused.
        pair_occurrences = [c.occurrence_count for c in self.conflicts.values()]
        if pair_occurrences:
            avg_occurrences = sum(pair_occurrences) / len(pair_occurrences)
            variance = sum((x - avg_occurrences) ** 2 for x in pair_occurrences) / len(pair_occurrences)
            coherence = 1.0 / (1.0 + (variance ** 0.5))  # Normalized inverse of stddev
        else:
            coherence = 0.0
        
        metrics = {
            "total_conflicts": len(self.conflicts),
            "resolved_conflicts": len(resolved),
            "unresolved_conflicts": len(unresolved),
            "mean_time_to_resolution_seconds": mean_ttr,
            "repeated_conflict_rate": repeated_rate,
            "resolution_reliability": resolution_reliability,
            "conflict_coherence": coherence,
        }
        
        return metrics

    def record_metrics_snapshot(self) -> None:
        """Record current metrics snapshot to history."""
        metrics = self.compute_metrics()
        metrics["timestamp"] = time.time()
        self.metrics_history.append(metrics)
        self._persist()

    def get_trending_conflicts(self, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Get conflicts with worsening trends (repeated after resolution).
        
        Args:
            limit: Maximum number to return.
            
        Returns:
            List of trending conflict dicts.
        """
        trending = []
        for pair, record in self.conflicts.items():
            if record.resolved_at and record.last_seen_at > record.resolved_at:
                trending.append({
                    "expected_policy": pair[0],
                    "predicted_policy": pair[1],
                    "occurrence_count": record.occurrence_count,
                    "resolution_attempts": record.resolution_attempts,
                    "time_to_resolution_seconds": record.time_to_resolution_seconds,
                    "recurrence_after_resolution": (
                        record.last_seen_at - record.resolved_at
                    ),
                    "associated_scenario_count": len(record.associated_scenarios),
                })
        
        trending.sort(
            key=lambda x: x["recurrence_after_resolution"],
            reverse=True
        )
        return trending[:limit]

    def serialize_metrics(self) -> Dict[str, Any]:
        """Serialize current metrics for reporting."""
        return {
            "current_metrics": self.compute_metrics(),
            "trending_conflicts": self.get_trending_conflicts(),
            "total_snapshots_recorded": len(self.metrics_history),
        }

    def _persist(self) -> None:
        """Persist conflicts and metrics to disk."""
        self.conflicts_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write conflicts as JSONL.
        with open(self.conflicts_file, "w") as f:
            for pair, record in self.conflicts.items():
                data = {
                    "conflict_id": record.conflict_id,
                    "policy_pair": list(pair),
                    "first_seen_at": record.first_seen_at,
                    "last_seen_at": record.last_seen_at,
                    "occurrence_count": record.occurrence_count,
                    "resolution_attempts": record.resolution_attempts,
                    "resolved_at": record.resolved_at,
                    "time_to_resolution_seconds": record.time_to_resolution_seconds,
                    "associated_scenarios": record.associated_scenarios,
                }
                f.write(json.dumps(data) + "\n")
        
        # Write metrics as JSON.
        with open(self.metrics_file, "w") as f:
            json.dump(
                {
                    "current_metrics": self.compute_metrics(),
                    "history": self.metrics_history,
                },
                f,
                indent=2
            )
