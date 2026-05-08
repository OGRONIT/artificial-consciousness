"""
Intelligence_Ladder.py - Five-level intelligence progression engine.

Tracks and improves five intelligence layers:
1. Intelligent Quotient
2. Creative Intelligence
3. Executive Intelligence
4. Metacognitive Intelligence
5. Adaptive Intelligence (fluid identity)
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class IntelligenceLadderEngine:
    """Computes five intelligence levels and writes actionable progression reports."""

    def __init__(self, kernel_root: str):
        self.kernel_root = Path(kernel_root)
        self.vault_dir = self.kernel_root / "evolution_vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)

        self.profile_path = self.vault_dir / "intelligence_ladder_profile.json"
        self.last_report_path = self.vault_dir / "intelligence_ladder_last_report.json"

        self.last_cycle_timestamp = 0.0
        self.cycle_interval_seconds = 300.0
        self.metrics_lock = threading.RLock()
        self.metrics: Dict[str, Any] = {
            "cycles_total": 0,
            "active_level": 1,
            "overall_intelligence_index": 0.0,
            "last_cycle_timestamp": 0.0,
        }

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def assess_levels(
        self,
        kernel: Any,
        stream_payload: Optional[Dict[str, Any]] = None,
        trend_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        stream_payload = stream_payload or {}
        trend_payload = trend_payload or {}

        inf = kernel.inference_engine.inference_statistics() if hasattr(kernel, "inference_engine") else {}
        st = kernel.self_model.get_stability_report() if hasattr(kernel, "self_model") else {}
        mot = kernel.inference_engine.get_intrinsic_motivation_status() if hasattr(kernel, "inference_engine") else {}
        obs = kernel.observer.get_system_health_report() if hasattr(kernel, "observer") else {}

        avg_conf = self._clamp01(float(inf.get("average_confidence", 0.0) or 0.0))
        growth_entropy = self._clamp01(float(inf.get("growth_to_entropy_ratio", 0.0) or 0.0) / 2.0)
        stability = self._clamp01(float(st.get("stability_score", 0.0) or 0.0))
        concern = self._clamp01(float(obs.get("overall_concern_level", 0.0) or 0.0))

        intrinsic_goals = self._clamp01(float(mot.get("intrinsic_goals_generated", 0) or 0) / 25.0)
        self_inquiry = self._clamp01(float(mot.get("self_inquiry_count", 0) or 0) / 25.0)

        stream_ingested = float(stream_payload.get("packets_ingested", 0) or 0)
        stream_integrated = float(stream_payload.get("packets_integrated", 0) or 0)
        integration_ratio = self._clamp01((stream_integrated / stream_ingested) if stream_ingested > 0 else 0.0)

        trend_approved = self._clamp01(float(trend_payload.get("approved_fact_count", 0) or 0) / 30.0)

        l1_iq = self._clamp01((avg_conf * 0.65) + ((1.0 - concern) * 0.35))
        promotion_bonus = 0.0
        if avg_conf >= 0.78 and concern <= 0.15:
            promotion_bonus += 0.05
        if growth_entropy >= 0.5:
            promotion_bonus += 0.03

        l2_creative = self._clamp01(
            (intrinsic_goals * 0.35) + (growth_entropy * 0.4) + (trend_approved * 0.25) + promotion_bonus
        )
        l3_executive = self._clamp01(
            (avg_conf * 0.3)
            + (growth_entropy * 0.2)
            + (intrinsic_goals * 0.2)
            + (self_inquiry * 0.1)
            + (trend_approved * 0.1)
            + (integration_ratio * 0.1)
            + promotion_bonus
        )
        l4_meta = self._clamp01((self_inquiry * 0.45) + ((1.0 - concern) * 0.25) + (stability * 0.3))
        l5_adaptive = self._clamp01((l3_executive * 0.25) + (l4_meta * 0.35) + (stability * 0.2) + (growth_entropy * 0.2))

        levels = {
            "level_1_iq": round(l1_iq, 4),
            "level_2_creative": round(l2_creative, 4),
            "level_3_executive": round(l3_executive, 4),
            "level_4_meta": round(l4_meta, 4),
            "level_5_adaptive": round(l5_adaptive, 4),
        }

        overall = round(sum(levels.values()) / 5.0, 4)

        active_level = 1
        thresholds = [0.35, 0.40, 0.43, 0.58, 0.68]
        for idx, key in enumerate(levels.keys(), start=1):
            if levels[key] >= thresholds[idx - 1]:
                active_level = idx

        return {
            "timestamp": time.time(),
            "levels": levels,
            "overall_intelligence_index": overall,
            "active_level": active_level,
            "signals": {
                "average_confidence": round(avg_conf, 4),
                "growth_entropy_norm": round(growth_entropy, 4),
                "stability_score": round(stability, 4),
                "observer_concern": round(concern, 4),
                "intrinsic_goals_norm": round(intrinsic_goals, 4),
                "self_inquiry_norm": round(self_inquiry, 4),
                "integration_ratio": round(integration_ratio, 4),
                "trend_approved_norm": round(trend_approved, 4),
            },
        }

    def _build_recommendations(self, levels: Dict[str, float], active_level: int) -> Dict[str, Any]:
        recs = []
        if active_level < 2:
            recs.append("increase confidence calibration and contradiction resolution")
        if levels.get("level_2_creative", 0.0) < 0.5:
            recs.append("raise exploratory synthesis and cross-domain idea generation")
        if levels.get("level_3_executive", 0.0) < 0.6:
            recs.append("increase actionable agenda throughput and completion reliability")
        if levels.get("level_4_meta", 0.0) < 0.6:
            recs.append("increase self-inquiry and observer-guided reflection cadence")
        if levels.get("level_5_adaptive", 0.0) < 0.6:
            recs.append("improve identity fluidity by reducing fixed-policy rigidity under stable conditions")

        return {
            "priority_recommendations": recs[:4],
            "next_target_level": min(5, active_level + 1),
        }

    def run_cycle(
        self,
        kernel: Any,
        stream_payload: Optional[Dict[str, Any]] = None,
        trend_payload: Optional[Dict[str, Any]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        now = time.time()
        if not force and (now - self.last_cycle_timestamp) < self.cycle_interval_seconds:
            return {
                "status": "skipped",
                "reason": "interval_not_elapsed",
                "seconds_remaining": self.cycle_interval_seconds - (now - self.last_cycle_timestamp),
            }

        assessment = self.assess_levels(kernel, stream_payload, trend_payload)
        levels = assessment.get("levels", {}) if isinstance(assessment, dict) else {}
        active_level = int(assessment.get("active_level", 1) or 1)
        recommendations = self._build_recommendations(levels, active_level)

        report = {
            "status": "executed",
            "timestamp": now,
            "assessment": assessment,
            "recommendations": recommendations,
        }

        profile = {
            "timestamp": now,
            "active_level": active_level,
            "overall_intelligence_index": assessment.get("overall_intelligence_index", 0.0),
            "levels": levels,
        }

        self.profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
        self.last_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        with self.metrics_lock:
            self.metrics["cycles_total"] = int(self.metrics.get("cycles_total", 0)) + 1
            self.metrics["active_level"] = active_level
            self.metrics["overall_intelligence_index"] = float(assessment.get("overall_intelligence_index", 0.0) or 0.0)
            self.metrics["last_cycle_timestamp"] = now

        self.last_cycle_timestamp = now
        return report

    def get_status(self) -> Dict[str, Any]:
        with self.metrics_lock:
            return {
                "metrics": dict(self.metrics),
                "profile_path": str(self.profile_path),
                "last_report_path": str(self.last_report_path),
                "cycle_interval_seconds": self.cycle_interval_seconds,
            }


_global_intelligence_ladder: Optional[IntelligenceLadderEngine] = None
_intelligence_ladder_lock = threading.Lock()


def get_intelligence_ladder(kernel_root: str) -> IntelligenceLadderEngine:
    global _global_intelligence_ladder
    if _global_intelligence_ladder is None:
        with _intelligence_ladder_lock:
            if _global_intelligence_ladder is None:
                _global_intelligence_ladder = IntelligenceLadderEngine(kernel_root=kernel_root)
    return _global_intelligence_ladder
