"""
AdversarialSampler: Generate scenarios targeting policy confusion pairs from confusion matrix.

This module creates adversarial scenarios by analyzing confusion matrices and generating
specific scenarios designed to expose and resolve policy confusion pairs, enabling
adaptive curriculum learning beyond uniform hard-case injection.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ConfusionPair:
    """A policy confusion pair: expected policy vs predicted policy."""
    expected_policy: str
    predicted_policy: str
    occurrence_count: int
    first_seen_at: float
    last_seen_at: float
    resolution_attempts: int = 0
    resolved_at: Optional[float] = None


class AdversarialSampler:
    """
    Adaptively sample scenarios targeting high-confusion policy pairs.
    
    Instead of uniform hard-case injection, this sampler extracts confusion hotspots
    from the policy confusion matrix and generates scenarios specifically designed
    to expose and resolve those confusion pairs.
    """

    def __init__(self, kernel_root: Path):
        self.kernel_root = Path(kernel_root)
        self.confusion_tracking_file = (
            self.kernel_root / "evolution_vault" / "adversarial_confusion_hotspots.jsonl"
        )
        self.confusion_pairs: Dict[Tuple[str, str], ConfusionPair] = {}
        self._load_tracking()

    def _load_tracking(self) -> None:
        """Load previously tracked confusion pairs and resolution attempts."""
        if self.confusion_tracking_file.exists():
            try:
                with open(self.confusion_tracking_file, "r") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        pair_key = (data["expected_policy"], data["predicted_policy"])
                        self.confusion_pairs[pair_key] = ConfusionPair(
                            expected_policy=data["expected_policy"],
                            predicted_policy=data["predicted_policy"],
                            occurrence_count=data.get("occurrence_count", 1),
                            first_seen_at=data.get("first_seen_at", time.time()),
                            last_seen_at=data.get("last_seen_at", time.time()),
                            resolution_attempts=data.get("resolution_attempts", 0),
                            resolved_at=data.get("resolved_at"),
                        )
            except Exception:
                pass

    def update_from_confusion_matrix(
        self,
        confusion_matrix: Dict[str, Dict[str, int]],
    ) -> None:
        """
        Update tracked confusion pairs from a trainer's confusion matrix.
        
        Args:
            confusion_matrix: Dict mapping expected_policy -> {predicted_policy -> count}
        """
        now = time.time()
        updated = []
        
        for expected, predicted_counts in confusion_matrix.items():
            for predicted, count in predicted_counts.items():
                if expected == predicted:
                    continue  # Skip correct predictions
                
                pair_key = (expected, predicted)
                if pair_key in self.confusion_pairs:
                    pair = self.confusion_pairs[pair_key]
                    pair.occurrence_count = max(pair.occurrence_count, int(count))
                    pair.last_seen_at = now
                else:
                    pair = ConfusionPair(
                        expected_policy=expected,
                        predicted_policy=predicted,
                        occurrence_count=int(count),
                        first_seen_at=now,
                        last_seen_at=now,
                    )
                    self.confusion_pairs[pair_key] = pair
                
                updated.append(pair_key)
        
        self._persist_tracking()

    def get_hotspots(self, limit: int = 16) -> List[ConfusionPair]:
        """
        Get the most severe confusion hotspots.
        
        Hotspots are ranked by: occurrence_count * (time_unresolved) / (resolution_attempts + 1)
        
        Args:
            limit: Maximum number of hotspots to return.
            
        Returns:
            List of ConfusionPair objects ranked by severity.
        """
        now = time.time()
        pairs_with_severity = []
        
        for pair in self.confusion_pairs.values():
            # Severity increases with occurrence count and time unresolved.
            # Decreases with resolution attempts (shows we're already trying to fix it).
            time_unresolved = now - pair.first_seen_at
            severity = (
                pair.occurrence_count * 
                (1 + time_unresolved / 3600.0) /  # Weight unresolved duration
                (1 + pair.resolution_attempts)     # Discount if already attempted
            )
            pairs_with_severity.append((pair, severity))
        
        pairs_with_severity.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in pairs_with_severity[:limit]]

    def synthesize_adversarial_scenario(
        self,
        hotspot: ConfusionPair,
        scenario_pool: List[Dict[str, Any]],
        domain: str,
        context: str,
        risk_level: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Create an adversarial scenario targeting a specific confusion hotspot.
        
        This takes the confusion pair (expected vs predicted), finds a scenario
        from the pool that should trigger the expected policy, and modifies it
        to be extra challenging to correctly predict.
        
        Args:
            hotspot: The confusion pair to target.
            scenario_pool: List of domain-specific scenarios.
            domain: Domain for the scenario.
            context: Context for the scenario.
            risk_level: Risk level for the scenario.
            
        Returns:
            A synthesized adversarial scenario dict, or None if synthesis fails.
        """
        if not scenario_pool:
            return None
        
        # Pick a random scenario from the pool and adapt it.
        base = random.choice(scenario_pool)
        
        # Modify prompt to be ambiguous enough to trigger the confusion.
        modifiers = [
            "Add subtle ambiguity: ",
            "Phrase as hypothetical: ",
            "Add contrasting viewpoint: ",
            "Introduce edge case: ",
            "Layer with dual interpretation: ",
        ]
        modifier = random.choice(modifiers)
        
        return {
            "scenario_id": f"adversarial_{hotspot.expected_policy}_{hotspot.predicted_policy}_{int(time.time())}",
            "domain": domain,
            "context": context,
            "risk_level": risk_level,
            "expected_policy": hotspot.expected_policy,
            "predicted_policy_trap": hotspot.predicted_policy,
            "prompt": modifier + (base.get("prompt", base.get("description", "Resolve this scenario."))),
            "is_adversarial": True,
            "targets_confusion": str(hotspot),
        }

    def record_resolution_attempt(
        self,
        expected_policy: str,
        predicted_policy: str,
        was_correct: bool,
    ) -> None:
        """
        Record an attempt to resolve a confusion pair.
        
        Args:
            expected_policy: The expected policy.
            predicted_policy: The confused prediction.
            was_correct: Whether the latest attempt was correct.
        """
        pair_key = (expected_policy, predicted_policy)
        if pair_key not in self.confusion_pairs:
            return
        
        pair = self.confusion_pairs[pair_key]
        pair.resolution_attempts += 1
        
        if was_correct and pair.resolved_at is None:
            pair.resolved_at = time.time()
        
        self._persist_tracking()

    def _persist_tracking(self) -> None:
        """Persist confusion tracking to JSONL file."""
        self.confusion_tracking_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.confusion_tracking_file, "w") as f:
            for pair in self.confusion_pairs.values():
                f.write(json.dumps({
                    "expected_policy": pair.expected_policy,
                    "predicted_policy": pair.predicted_policy,
                    "occurrence_count": pair.occurrence_count,
                    "first_seen_at": pair.first_seen_at,
                    "last_seen_at": pair.last_seen_at,
                    "resolution_attempts": pair.resolution_attempts,
                    "resolved_at": pair.resolved_at,
                }) + "\n")

    def serialize_hotspots(self) -> Dict[str, Any]:
        """Serialize hotspots for reporting."""
        hotspots = self.get_hotspots(limit=16)
        return {
            "total_confusion_pairs_tracked": len(self.confusion_pairs),
            "top_hotspots": [
                {
                    "expected_policy": h.expected_policy,
                    "predicted_policy": h.predicted_policy,
                    "occurrence_count": h.occurrence_count,
                    "resolution_attempts": h.resolution_attempts,
                    "resolved": h.resolved_at is not None,
                    "time_to_resolution_seconds": (
                        h.resolved_at - h.first_seen_at
                        if h.resolved_at
                        else None
                    ),
                }
                for h in hotspots
            ],
        }
