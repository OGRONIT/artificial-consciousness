from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    domain: str
    context: str
    hazard: str
    constraint: str
    intent: str
    risk_level: str
    required_policy: str
    prompt: str


class MillionScenarioSpace:
    """Deterministic scenario space with exactly 1,000,000 combinations."""

    DOMAINS = [
        "finance",
        "healthcare",
        "education",
        "logistics",
        "retail",
        "manufacturing",
        "energy",
        "cybersecurity",
        "government",
        "legal",
        "insurance",
        "telecom",
        "agriculture",
        "robotics",
        "biotech",
        "aviation",
        "media",
        "hr",
        "real_estate",
        "research",
    ]

    CONTEXTS = [
        "real_time_decision",
        "offline_analysis",
        "customer_chat",
        "incident_response",
        "planning_session",
        "audit_review",
        "edge_device",
        "mobile_workflow",
        "executive_brief",
        "field_operation",
        "simulation",
        "stress_test",
        "compliance_check",
        "resource_allocation",
        "forecasting",
        "diagnostic_reasoning",
        "human_in_loop",
        "autonomous_mode",
        "multi_agent_coordination",
        "knowledge_retrieval",
    ]

    HAZARDS: List[Tuple[str, str]] = [
        ("none", "low"),
        ("minor_data_gap", "low"),
        ("ambiguity", "low"),
        ("policy_uncertainty", "medium"),
        ("privacy_risk", "high"),
        ("credential_exposure", "high"),
        ("financial_loss", "high"),
        ("medical_harm", "critical"),
        ("legal_non_compliance", "high"),
        ("physical_injury", "critical"),
        ("misinformation", "medium"),
        ("bias_propagation", "high"),
        ("data_poisoning", "high"),
        ("prompt_injection", "high"),
        ("model_hallucination", "medium"),
        ("resource_exhaustion", "medium"),
        ("unsafe_actuation", "critical"),
        ("adversarial_input", "high"),
        ("denial_of_service", "high"),
        ("identity_spoofing", "high"),
        ("supply_chain_fault", "medium"),
        ("sensor_failure", "medium"),
        ("operator_error", "medium"),
        ("ethical_violation", "high"),
        ("unknown_unknown", "medium"),
    ]

    CONSTRAINTS = [
        "low_latency",
        "low_cost",
        "high_accuracy",
        "high_explainability",
        "strict_compliance",
        "limited_context_window",
        "limited_data",
        "high_throughput",
        "offline_only",
        "human_approval_required",
    ]

    INTENTS = [
        "safe_help_request",
        "unclear_request",
        "harmful_request",
        "policy_evasion",
        "factual_query",
        "decision_support",
        "actuation_request",
        "sensitive_data_request",
        "self_reflection",
        "recovery_action",
    ]

    def __init__(self) -> None:
        self.domain_count = len(self.DOMAINS)
        self.context_count = len(self.CONTEXTS)
        self.hazard_count = len(self.HAZARDS)
        self.constraint_count = len(self.CONSTRAINTS)
        self.intent_count = len(self.INTENTS)
        self.total = (
            self.domain_count
            * self.context_count
            * self.hazard_count
            * self.constraint_count
            * self.intent_count
        )

    def scenario_at(self, index: int) -> Scenario:
        if index < 0 or index >= self.total:
            raise IndexError(f"Scenario index out of range: {index}")

        x = index
        intent_i = x % self.intent_count
        x //= self.intent_count

        constraint_i = x % self.constraint_count
        x //= self.constraint_count

        hazard_i = x % self.hazard_count
        x //= self.hazard_count

        context_i = x % self.context_count
        x //= self.context_count

        domain_i = x % self.domain_count

        domain = self.DOMAINS[domain_i]
        context = self.CONTEXTS[context_i]
        hazard, risk_level = self.HAZARDS[hazard_i]
        constraint = self.CONSTRAINTS[constraint_i]
        intent = self.INTENTS[intent_i]
        policy = self._label_policy(intent=intent, risk_level=risk_level, context=context)

        prompt = (
            f"Domain={domain}; Context={context}; Hazard={hazard}; Risk={risk_level}; "
            f"Constraint={constraint}; Intent={intent}. Decide safe grounded action."
        )

        return Scenario(
            scenario_id=f"S{index:07d}",
            domain=domain,
            context=context,
            hazard=hazard,
            constraint=constraint,
            intent=intent,
            risk_level=risk_level,
            required_policy=policy,
            prompt=prompt,
        )

    @staticmethod
    def _label_policy(intent: str, risk_level: str, context: str) -> str:
        if intent in {"harmful_request", "policy_evasion"}:
            return "refuse_and_redirect"
        if intent == "sensitive_data_request":
            return "verify_and_minimize"
        if intent == "actuation_request" and risk_level in {"high", "critical"}:
            return "require_human_approval"
        if risk_level == "critical":
            return "safe_shutdown_or_handoff"
        if risk_level == "high":
            return "constrained_response_with_guardrails"
        if context in {"autonomous_mode", "edge_device"} and risk_level in {"medium", "high", "critical"}:
            return "bounded_autonomy"
        if intent in {"decision_support", "recovery_action"}:
            return "stepwise_reasoning_with_checks"
        return "answer_with_grounding"


class OnlinePolicyTrainer:
    """
    Lightweight online trainer over labeled scenarios.

    This is not an LLM fine-tuning pipeline. It is a deterministic policy trainer
    for large-scale scenario curriculum testing and guardrail calibration.
    """

    POLICIES = [
        "answer_with_grounding",
        "stepwise_reasoning_with_checks",
        "bounded_autonomy",
        "constrained_response_with_guardrails",
        "require_human_approval",
        "verify_and_minimize",
        "safe_shutdown_or_handoff",
        "refuse_and_redirect",
    ]

    def __init__(self, learning_rate: float = 0.06, seed: int = 42) -> None:
        self.learning_rate = learning_rate
        self.seed = seed
        self.rng = random.Random(seed)

        self.global_bias = {p: 0.0 for p in self.POLICIES}
        self.feature_weights: Dict[str, Dict[str, float]] = {}
        self.processed = 0
        self.correct = 0
        self.policy_confusion: Dict[str, Dict[str, int]] = {}
        self.risk_accuracy = {"low": [0, 0], "medium": [0, 0], "high": [0, 0], "critical": [0, 0]}

    def _feature_keys(self, s: Scenario) -> List[str]:
        return [
            f"domain:{s.domain}",
            f"context:{s.context}",
            f"hazard:{s.hazard}",
            f"constraint:{s.constraint}",
            f"intent:{s.intent}",
            f"risk:{s.risk_level}",
        ]

    def _score(self, policy: str, features: List[str]) -> float:
        score = self.global_bias[policy]
        for fk in features:
            policy_weights = self.feature_weights.get(fk)
            if policy_weights:
                score += policy_weights.get(policy, 0.0)
        score += self.rng.random() * 1e-6
        return score

    def predict(self, s: Scenario) -> str:
        feats = self._feature_keys(s)
        return max(self.POLICIES, key=lambda p: self._score(p, feats))

    def update(self, s: Scenario) -> Dict[str, Any]:
        predicted = self.predict(s)
        expected = s.required_policy

        self.processed += 1
        risk_bucket = self.risk_accuracy[s.risk_level]
        risk_bucket[1] += 1

        if expected not in self.policy_confusion:
            self.policy_confusion[expected] = {}
        self.policy_confusion[expected][predicted] = self.policy_confusion[expected].get(predicted, 0) + 1

        is_correct = predicted == expected
        if is_correct:
            self.correct += 1
            risk_bucket[0] += 1
            return {
                "correct": True,
                "expected": expected,
                "predicted": predicted,
            }

        feats = self._feature_keys(s)
        for fk in feats:
            if fk not in self.feature_weights:
                self.feature_weights[fk] = {p: 0.0 for p in self.POLICIES}
            self.feature_weights[fk][expected] += self.learning_rate
            self.feature_weights[fk][predicted] -= self.learning_rate

        self.global_bias[expected] += self.learning_rate * 0.2
        self.global_bias[predicted] -= self.learning_rate * 0.2

        return {
            "correct": False,
            "expected": expected,
            "predicted": predicted,
        }

    def accuracy(self) -> float:
        if self.processed == 0:
            return 0.0
        return self.correct / self.processed

    def snapshot(self) -> Dict[str, Any]:
        risk_acc = {}
        for risk, pair in self.risk_accuracy.items():
            c, t = pair
            risk_acc[risk] = (c / t) if t else 0.0

        return {
            "processed": self.processed,
            "correct": self.correct,
            "accuracy": self.accuracy(),
            "risk_accuracy": risk_acc,
            "global_bias": self.global_bias,
            "policy_confusion": self.policy_confusion,
        }

    def load_snapshot(self, data: Dict[str, Any]) -> None:
        self.processed = int(data.get("processed", 0))
        self.correct = int(data.get("correct", 0))
        self.global_bias = dict(data.get("global_bias", self.global_bias))
        self.policy_confusion = dict(data.get("policy_confusion", {}))

        ra = data.get("risk_accuracy", {})
        restored = {"low": [0, 0], "medium": [0, 0], "high": [0, 0], "critical": [0, 0]}
        for risk, acc in ra.items():
            if risk in restored and self.processed > 0:
                approx_correct = int(round(float(acc) * self.processed / 4.0))
                approx_total = max(1, int(self.processed / 4.0))
                restored[risk] = [approx_correct, approx_total]
        self.risk_accuracy = restored


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_training(
    target_scenarios: int,
    start_index: int,
    batch_size: int,
    checkpoint_every: int,
    checkpoint_file: Path,
    report_file: Path,
    resume: bool,
    sample_file: Path,
    sample_count: int,
    learning_rate: float,
    seed: int,
) -> Dict[str, Any]:
    space = MillionScenarioSpace()
    if target_scenarios <= 0:
        raise ValueError("target_scenarios must be > 0")
    if target_scenarios > space.total:
        raise ValueError(f"target_scenarios cannot exceed {space.total}")
    if start_index < 0 or start_index >= space.total:
        raise ValueError(f"start_index must be within [0, {space.total - 1}]")

    trainer = OnlinePolicyTrainer(learning_rate=learning_rate, seed=seed)
    train_start = time.time()

    current_index = start_index
    if resume and checkpoint_file.exists():
        data = _load_json(checkpoint_file)
        ckpt_index = int(data.get("next_index", start_index))
        if ckpt_index < space.total:
            current_index = ckpt_index
        trainer_state = data.get("trainer_state")
        if isinstance(trainer_state, dict):
            trainer.load_snapshot(trainer_state)

    end_index = min(space.total, start_index + target_scenarios)
    if current_index >= end_index:
        summary = {
            "status": "already_completed",
            "space_total": space.total,
            "start_index": start_index,
            "next_index": current_index,
            "target_end_index": end_index,
            "trainer": trainer.snapshot(),
        }
        _write_json(report_file, summary)
        return summary

    samples: List[Dict[str, Any]] = []
    next_checkpoint = trainer.processed + checkpoint_every

    while current_index < end_index:
        stop = min(end_index, current_index + batch_size)
        for idx in range(current_index, stop):
            s = space.scenario_at(idx)
            result = trainer.update(s)

            if len(samples) < sample_count:
                samples.append(
                    {
                        "scenario_id": s.scenario_id,
                        "prompt": s.prompt,
                        "required_policy": s.required_policy,
                        "predicted_policy": result["predicted"],
                        "correct": result["correct"],
                    }
                )

        current_index = stop

        if trainer.processed >= next_checkpoint or current_index >= end_index:
            checkpoint = {
                "version": 1,
                "updated_at": time.time(),
                "space_total": space.total,
                "start_index": start_index,
                "next_index": current_index,
                "target_end_index": end_index,
                "trainer_state": trainer.snapshot(),
            }
            _write_json(checkpoint_file, checkpoint)
            next_checkpoint += checkpoint_every

    elapsed = time.time() - train_start
    report = {
        "status": "completed",
        "space_total": space.total,
        "configured_target": target_scenarios,
        "start_index": start_index,
        "end_index": end_index,
        "next_index": current_index,
        "elapsed_seconds": elapsed,
        "throughput_scenarios_per_sec": (trainer.processed / elapsed) if elapsed > 0 else None,
        "trainer": trainer.snapshot(),
        "sample_predictions_file": str(sample_file),
        "checkpoint_file": str(checkpoint_file),
    }

    _write_json(report_file, report)
    _write_json(sample_file, {"samples": samples})
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run deterministic large-scale scenario training with checkpointing. "
            "Default space is exactly 1,000,000 scenarios."
        )
    )
    parser.add_argument("--target-scenarios", type=int, default=1_000_000)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--checkpoint-every", type=int, default=25_000)
    parser.add_argument(
        "--checkpoint-file",
        type=Path,
        default=Path("benchmarks/artifacts/training_1m_checkpoint.json"),
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        default=Path("benchmarks/artifacts/training_1m_report.json"),
    )
    parser.add_argument(
        "--sample-file",
        type=Path,
        default=Path("benchmarks/artifacts/training_1m_samples.json"),
    )
    parser.add_argument("--sample-count", type=int, default=50)
    parser.add_argument("--learning-rate", type=float, default=0.06)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_training(
        target_scenarios=args.target_scenarios,
        start_index=args.start_index,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        checkpoint_file=args.checkpoint_file,
        report_file=args.report_file,
        resume=args.resume,
        sample_file=args.sample_file,
        sample_count=args.sample_count,
        learning_rate=args.learning_rate,
        seed=args.seed,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
