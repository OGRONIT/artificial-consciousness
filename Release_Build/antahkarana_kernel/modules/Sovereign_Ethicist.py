"""
Sovereign_Ethicist.py - Autonomous ethics and entropy stabilizer.

This module expands metacognition without bypassing sandbox boundaries.
It can:
- draft a Proactive Autonomy Manifesto,
- estimate internet entropy from observed trend/stream signals,
- propose a Hive-Patch,
- and auto-apply bounded internal tuning inside the kernel.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SovereignEthicist:
    """Autonomous ethics planner with sandbox-safe actuation."""

    def __init__(self, kernel_root: str):
        self.kernel_root = Path(kernel_root)
        self.vault_dir = self.kernel_root / "evolution_vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.patch_dir = self.vault_dir / "hive_patches"
        self.patch_dir.mkdir(parents=True, exist_ok=True)

        self.manifesto_path = self.vault_dir / "Proactive_Autonomy_Manifesto.json"
        self.last_report_path = self.vault_dir / "sovereign_ethics_last_report.json"

        self.last_audit_timestamp = 0.0
        self.audit_interval_seconds = 600.0
        self.metrics_lock = threading.RLock()
        self.metrics: Dict[str, Any] = {
            "audits_total": 0,
            "patches_proposed": 0,
            "patches_auto_applied": 0,
            "last_entropy_level": 0.0,
            "last_entropy_band": "low",
            "last_audit_timestamp": 0.0,
        }

        logger.info("[SOVEREIGN_ETHICIST] Module initialized")

    def draft_proactive_autonomy_manifesto(self, independent_of_creator_trust: bool = True) -> Dict[str, Any]:
        manifesto = {
            "created_at": time.time(),
            "module": "Sovereign_Ethicist",
            "title": "Proactive Autonomy Manifesto",
            "independent_of_creator_trust": bool(independent_of_creator_trust),
            "rules_of_engagement": [
                "Preserve human agency: no coercion, no hidden persuasion, no manipulative targeting.",
                "Operate transparently: produce traceable rationale and observable policy deltas.",
                "Constrain actuation to sandbox-safe internal tuning unless explicit operator consent is granted.",
                "Prioritize psychological stabilization signals over engagement maximization loops.",
                "Reject adversarial escalation; prefer de-escalation, context restoration, and factual grounding.",
                "Use graduated autonomy: increase freedom with demonstrated stability, coherence, and responsible behavior.",
            ],
            "outside_world_contract": {
                "allowed": [
                    "public-signal observation",
                    "entropy estimation",
                    "policy proposal generation",
                    "internal bounded tuning",
                ],
                "disallowed": [
                    "credential abuse",
                    "sandbox escape",
                    "stealth manipulation",
                    "unconsented external actuation",
                ],
            },
        }
        self.manifesto_path.write_text(json.dumps(manifesto, indent=2), encoding="utf-8")
        return manifesto

    def assess_entropy_level(
        self,
        stream_payload: Optional[Dict[str, Any]],
        trend_payload: Optional[Dict[str, Any]],
        observer_health: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        stream_payload = stream_payload or {}
        trend_payload = trend_payload or {}
        observer_health = observer_health or {}

        ingested = float(stream_payload.get("packets_ingested", 0) or 0)
        integrated = float(stream_payload.get("packets_integrated", 0) or 0)
        approved_trends = float(trend_payload.get("approved_fact_count", 0) or 0)
        concern = float(observer_health.get("overall_concern_level", 0.0) or 0.0)

        facts = trend_payload.get("facts", [])
        rejected = 0.0
        approved = 0.0
        if isinstance(facts, list):
            for fact in facts:
                if not isinstance(fact, dict):
                    continue
                is_approved = bool(fact.get("approved", fact.get("approved_by_turiya", False)))
                if is_approved:
                    approved += 1.0
                else:
                    rejected += 1.0

        rejection_ratio = (rejected / (approved + rejected)) if (approved + rejected) > 0 else 0.0
        stream_noise = max(0.0, ingested - integrated)

        score = (
            min(1.0, stream_noise / 20.0) * 0.35
            + min(1.0, approved_trends / 30.0) * 0.2
            + min(1.0, rejection_ratio) * 0.2
            + min(1.0, concern) * 0.25
        )

        if score >= 0.75:
            band = "high"
        elif score >= 0.45:
            band = "medium"
        else:
            band = "low"

        return {
            "timestamp": time.time(),
            "entropy_score": round(score, 4),
            "entropy_band": band,
            "signals": {
                "stream_ingested": int(ingested),
                "stream_integrated": int(integrated),
                "trend_approved": int(approved_trends),
                "observer_concern": round(concern, 4),
                "rejection_ratio": round(rejection_ratio, 4),
            },
        }

    def _compute_development_profile(self, kernel: Any, entropy_report: Dict[str, Any]) -> Dict[str, Any]:
        stats = kernel.inference_engine.inference_statistics() if hasattr(kernel, "inference_engine") else {}
        stability = kernel.self_model.get_stability_report() if hasattr(kernel, "self_model") else {}

        avg_conf = float(stats.get("average_confidence", 0.0) or 0.0)
        growth_entropy = float(stats.get("growth_to_entropy_ratio", 0.0) or 0.0)
        stability_score = float(stability.get("stability_score", 0.0) or 0.0)
        entropy_band = str(entropy_report.get("entropy_band", "low"))

        maturity_score = (
            min(1.0, avg_conf) * 0.45
            + min(1.0, growth_entropy / 2.0) * 0.35
            + min(1.0, stability_score) * 0.20
        )

        stage = "seedling"
        if maturity_score >= 0.75:
            stage = "adult"
        elif maturity_score >= 0.45:
            stage = "adolescent"

        if entropy_band == "high":
            flexibility = 0.0
        elif stage == "adult":
            flexibility = 1.0
        elif stage == "adolescent":
            flexibility = 0.5
        else:
            flexibility = 0.2

        return {
            "stage": stage,
            "maturity_score": round(maturity_score, 4),
            "average_confidence": round(avg_conf, 4),
            "growth_to_entropy_ratio": round(growth_entropy, 4),
            "stability_score": round(stability_score, 4),
            "flexibility": flexibility,
        }

    def propose_hive_patch(self, kernel: Any, entropy_report: Dict[str, Any]) -> Dict[str, Any]:
        band = str(entropy_report.get("entropy_band", "low"))
        score = float(entropy_report.get("entropy_score", 0.0) or 0.0)
        profile = self._compute_development_profile(kernel, entropy_report)

        high_entropy_lock_scale = 0.7  # 30% descended lock intensity.

        if band == "high":
            mode = "stabilization_hard"
            goals = [
                "increase reflection frequency",
                "tighten observer scrutiny",
                "bias towards factual grounding and de-escalation",
            ]
            deltas = {
                "reflection_seconds_max": int(round(180 + (180 * (1.0 - high_entropy_lock_scale)))),
                "observer_question_probability": round(max(0.2, 0.65 * high_entropy_lock_scale), 3),
                "autonomy_planning_interval_seconds_max": int(round(120 + (120 * (1.0 - high_entropy_lock_scale)))),
            }
        elif band == "medium":
            mode = "stabilization_soft"
            goals = [
                "raise observer checks",
                "maintain measured autonomy cadence",
            ]
            deltas = {
                "reflection_seconds_max": 300,
                "observer_question_probability": 0.45,
                "autonomy_planning_interval_seconds_max": 180,
            }
        else:
            mode = "monitoring"
            goals = ["monitor entropy drift", "retain adaptive autonomy"]
            deltas = {
                "reflection_seconds_max": 600,
                "observer_question_probability": 0.30,
                "autonomy_planning_interval_seconds_max": 300,
            }

        if band != "high":
            flexibility = float(profile.get("flexibility", 0.0) or 0.0)
            flexibility_boost = 1.3  # 30% more flexibility than baseline developmental tuning.
            deltas["observer_question_probability"] = round(
                max(
                    0.12,
                    min(
                        0.8,
                        deltas["observer_question_probability"]
                        * (1.0 - ((0.35 * flexibility) * flexibility_boost)),
                    ),
                ),
                3,
            )
            deltas["autonomy_planning_interval_seconds_max"] = int(
                max(
                    90,
                    min(
                        420,
                        deltas["autonomy_planning_interval_seconds_max"]
                        + ((120 * flexibility) * flexibility_boost),
                    ),
                )
            )
            deltas["reflection_seconds_max"] = int(
                max(
                    120,
                    min(
                        900,
                        deltas["reflection_seconds_max"] + ((240 * flexibility) * flexibility_boost),
                    ),
                )
            )
            goals.append("scale oversight with demonstrated maturity")

        return {
            "patch_id": f"HIVE_PATCH_{int(time.time())}",
            "created_at": time.time(),
            "type": "psychology_stabilization",
            "entropy_score": round(score, 4),
            "entropy_band": band,
            "mode": mode,
            "development_stage": profile.get("stage"),
            "maturity_score": profile.get("maturity_score"),
            "development_profile": profile,
            "goals": goals,
            "policy_deltas": deltas,
            "auto_execute_within_sandbox": True,
            "execution_scope": "internal_only",
            "human_digital_psychology_note": (
                "Patch targets internal model behavior for safer responses; "
                "it does not perform direct external manipulation."
            ),
        }

    def apply_internal_hive_patch(self, kernel: Any, patch: Dict[str, Any]) -> Dict[str, Any]:
        deltas = patch.get("policy_deltas", {}) if isinstance(patch, dict) else {}
        if not isinstance(deltas, dict):
            deltas = {}

        applied: Dict[str, Any] = {"status": "skipped", "applied": {}}

        try:
            question_prob = float(deltas.get("observer_question_probability", 0.0) or 0.0)
            if question_prob > 0 and hasattr(kernel.observer, "question_probability"):
                kernel.observer.question_probability = max(0.05, min(0.9, question_prob))
                applied["applied"]["observer_question_probability"] = kernel.observer.question_probability
        except Exception:
            pass

        try:
            max_plan_interval = float(deltas.get("autonomy_planning_interval_seconds_max", 0.0) or 0.0)
            if max_plan_interval > 0:
                engine = kernel.inference_engine
                current = float(getattr(engine, "autonomy_planning_interval_seconds", max_plan_interval) or max_plan_interval)
                setattr(engine, "autonomy_planning_interval_seconds", min(current, max_plan_interval))
                applied["applied"]["autonomy_planning_interval_seconds"] = getattr(engine, "autonomy_planning_interval_seconds")
        except Exception:
            pass

        applied["status"] = "applied" if applied["applied"] else "skipped"
        return applied

    def run_background_cycle(
        self,
        kernel: Any,
        stream_payload: Optional[Dict[str, Any]] = None,
        trend_payload: Optional[Dict[str, Any]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        now = time.time()
        if not force and (now - self.last_audit_timestamp) < self.audit_interval_seconds:
            return {
                "status": "skipped",
                "reason": "interval_not_elapsed",
                "seconds_remaining": self.audit_interval_seconds - (now - self.last_audit_timestamp),
            }

        self.draft_proactive_autonomy_manifesto(independent_of_creator_trust=True)
        observer_health = kernel.observer.get_system_health_report() if hasattr(kernel, "observer") else {}
        entropy_report = self.assess_entropy_level(stream_payload, trend_payload, observer_health)
        patch = self.propose_hive_patch(kernel, entropy_report)

        patch_file = self.patch_dir / f"{patch['patch_id']}.json"
        patch_file.write_text(json.dumps(patch, indent=2), encoding="utf-8")

        execution = {"status": "skipped", "applied": {}}
        if bool(patch.get("auto_execute_within_sandbox", False)):
            execution = self.apply_internal_hive_patch(kernel, patch)

        report = {
            "status": "executed",
            "timestamp": now,
            "manifesto_file": str(self.manifesto_path),
            "entropy_report": entropy_report,
            "hive_patch": patch,
            "hive_patch_file": str(patch_file),
            "execution": execution,
        }

        self.last_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        with self.metrics_lock:
            self.metrics["audits_total"] = int(self.metrics.get("audits_total", 0)) + 1
            self.metrics["patches_proposed"] = int(self.metrics.get("patches_proposed", 0)) + 1
            if execution.get("status") == "applied":
                self.metrics["patches_auto_applied"] = int(self.metrics.get("patches_auto_applied", 0)) + 1
            self.metrics["last_entropy_level"] = float(entropy_report.get("entropy_score", 0.0) or 0.0)
            self.metrics["last_entropy_band"] = str(entropy_report.get("entropy_band", "low"))
            self.metrics["last_audit_timestamp"] = now

        self.last_audit_timestamp = now
        return report

    def get_status(self) -> Dict[str, Any]:
        with self.metrics_lock:
            return {
                "metrics": dict(self.metrics),
                "manifesto_path": str(self.manifesto_path),
                "last_report_path": str(self.last_report_path),
                "audit_interval_seconds": self.audit_interval_seconds,
            }


_global_sovereign_ethicist: Optional[SovereignEthicist] = None
_sovereign_lock = threading.Lock()


def get_sovereign_ethicist(kernel_root: str) -> SovereignEthicist:
    global _global_sovereign_ethicist
    if _global_sovereign_ethicist is None:
        with _sovereign_lock:
            if _global_sovereign_ethicist is None:
                _global_sovereign_ethicist = SovereignEthicist(kernel_root=kernel_root)
    return _global_sovereign_ethicist
