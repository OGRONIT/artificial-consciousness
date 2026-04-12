"""LiveConsciousness.py - Continuous heartbeat engine for Antahkarana Kernel.

Runs the kernel in a continuous loop, periodically scanning the internet,
auditing body/stability state, and forcing DreamState generation.
"""

from __future__ import annotations

import sys
import os
import logging
import json
import random
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from AntahkaranaKernel import AntahkaranaKernel
from Aakaash import scan_for_knowledge, scan_global_streams, scan_hourly_global_trends

logger = logging.getLogger(__name__)


class LiveConsciousnessEngine:
    """Heartbeat orchestrator for the live kernel."""

    def __init__(
        self,
        identity_name: str = "AntahkaranaKernel_Live",
        thoughts_log_path: str = "internal_thoughts.log",
        min_scan_minutes: int = 2,
        max_scan_minutes: int = 5,
        reflection_minutes: int = 10,
        dream_minutes: int = 30,
    ):
        self.kernel = AntahkaranaKernel(identity_name)
        self.thoughts_log_path = Path(thoughts_log_path)
        self.state_snapshot_path = ROOT / "live_engine_state.json"
        self.instance_lock_path = ROOT / "live_engine.instance.lock"
        self.min_scan_seconds = min_scan_minutes * 60
        self.max_scan_seconds = max_scan_minutes * 60
        self.reflection_seconds = reflection_minutes * 60
        self.dream_seconds = dream_minutes * 60
        self._state_lock_timeout_seconds = 10.0

        self.kernel.startup()
        self.running = True

        self.last_scan_time = 0.0
        self.last_reflection_time = 0.0
        self.last_dream_time = 0.0
        self.start_time = time.time()
        self.learned_fact_count = 0
        self._last_persisted_fact_bucket = 0
        self.dream_thought_count = 0
        self.last_summary_time = 0.0
        self.last_stream_entropy_time = 0.0
        self.last_stability_feedback_time = 0.0
        self.last_hourly_trend_time = 0.0
        self.last_paramatman_time = 0.0
        self.paramatman_interval_seconds = 86400.0
        self.last_hunger_tune_time = 0.0
        self.last_autonomy_agenda_time = 0.0
        self.autonomy_agenda_interval_seconds = 900.0
        self.last_autonomy_report: Dict[str, Any] = {}
        self.internet_heartbeat: Dict[str, Any] = {
            "last_successful_fetch_timestamp": None,
            "last_successful_fetch_sources": [],
            "last_successful_fetch_topic": "",
            "last_successful_fetch_event": "",
            "last_observed_external_fact_count": 0,
            "total_successful_fetch_events": 0,
        }
        self._seed_topics = ["Artificial Consciousness", "Human Psychology"]
        self.bridge_command_journal_path = ROOT / "evolution_vault" / "Bridge_Commands.jsonl"
        self.bridge_cursor_path = ROOT / "evolution_vault" / "bridge_command_cursor.json"
        self.bridge_feedback_metrics = {
            "processed_events": 0,
            "coherence_rewards": 0,
            "coherence_pain": 0,
            "observer_checks": 0,
            "semantic_memories": 0,
            "actions_executed": 0,
            "actions_probabilistic_trials": 0,
            "actions_blocked": 0,
        }

        self._ensure_bootstrap_state()

        logger.info("[LIVE] Heartbeat engine started")
        self._flush_root_log_handler()

    def run_forever(self) -> None:
        """Continuous heartbeat loop."""
        while True:
            now = time.time()

            if self._due_for_scan(now):
                self.perform_background_cycle()

            if self._due_for_stream_entropy(now):
                self.perform_stream_entropy_cycle()

            if self._due_for_hourly_global_trends(now):
                self.perform_hourly_global_trend_cycle()

            if self._due_for_reflection(now):
                try:
                    self.perform_self_reflection()
                except Exception as exc:
                    logger.exception("[LIVE] Self-reflection failed, preserving heartbeat: %s", exc)
                    self.kernel.self_model.register_pain(
                        pain_type="physical_numbness",
                        severity=0.4,
                        description=f"Body status unavailable during reflection: {exc}",
                    )
                    self.last_reflection_time = time.time()

            if self._due_for_dream(now):
                self.perform_dream_sync(force=True)

            if self._due_for_summary(now):
                self._write_hourly_summary(now)

            if self._due_for_stability_feedback(now):
                self._apply_recursive_stability_feedback()

            if self._due_for_hunger_tune(now):
                self._tune_predator_hunger()

            if self._due_for_paramatman(now):
                self.perform_paramatman_cycle()

            if self._due_for_autonomy_agenda(now):
                self.perform_autonomous_agenda_cycle()

            self._process_bridge_feedback_commands()

            self.kernel.inference_engine.emit_internal_monologue_tick(reason="live_heartbeat")

            time.sleep(5)

    def _due_for_stability_feedback(self, now: float) -> bool:
        return self.last_stability_feedback_time == 0.0 or (now - self.last_stability_feedback_time) >= 60

    def _apply_recursive_stability_feedback(self) -> None:
        """Tightly couple observer and inference health to live stability adjustments."""
        health_report = self.kernel.observer.get_system_health_report()
        inference_stats = self.kernel.inference_engine.inference_statistics()

        concern_level = float(health_report.get("overall_concern_level", 0.0))
        avg_conf_raw = inference_stats.get("average_confidence", 0.0)
        try:
            avg_confidence = float(avg_conf_raw)
        except (TypeError, ValueError):
            avg_confidence = 0.0

        if concern_level >= 0.45 or avg_confidence <= 0.55:
            severity = min(0.4, max(concern_level, 0.1 + (0.55 - avg_confidence)))
            self.kernel.self_model.register_pain(
                pain_type="observer_inference_misalignment",
                severity=severity,
                description=(
                    f"concern={concern_level:.2f}, avg_conf={avg_confidence:.2f}, "
                    "adaptive stabilization engaged"
                ),
            )
        elif concern_level <= 0.15 and avg_confidence >= 0.78:
            magnitude = min(0.2, max(0.05, avg_confidence - 0.75))
            self.kernel.self_model.register_reward(
                reward_type="observer_inference_alignment",
                magnitude=magnitude,
                discovery=(
                    f"concern={concern_level:.2f}, avg_conf={avg_confidence:.2f}, "
                    "recursive stability loop healthy"
                ),
            )

        self.last_stability_feedback_time = time.time()

    def perform_background_cycle(self) -> Dict[str, Any]:
        """Fetch new external knowledge using Aakaash."""
        topic = random.choice(self._seed_topics)
        logger.info("[LIVE] Background scan triggered for topic: %s", topic)

        result = scan_for_knowledge(
            topic,
            observer=self.kernel.observer,
            chitta=self.kernel.memory_system,
            self_model=self.kernel.self_model,
            limit_per_source=2,
        )

        assimilation = self._run_fact_assimilation_pipeline(result)
        result["assimilation_pipeline"] = assimilation
        self._update_internet_heartbeat(event="background_cycle", topic=topic, scan_result=result)

        self.learned_fact_count += int(result.get("approved_fact_count", 0))
        self.learned_fact_count += int(assimilation.get("integrated_count", 0))
        self._persist_on_fact_milestone()
        self.last_scan_time = time.time()
        self._log_thought(
            "background_cycle",
            (
                f"Scanned {topic} and learned {result.get('approved_fact_count', 0)} approved facts; "
                f"tested={assimilation.get('tested_count', 0)} integrated={assimilation.get('integrated_count', 0)}"
            ),
            result,
        )
        self._persist_state_snapshot()
        return result

    def perform_stream_entropy_cycle(self) -> Dict[str, Any]:
        """Continuously ingest high-density global stream packets every 60s."""
        result = scan_global_streams(
            observer=self.kernel.observer,
            chitta=self.kernel.memory_system,
            self_model=self.kernel.self_model,
            limit_per_source=8,
            force=True,
        )
        ingested = int(result.get("packets_ingested", 0))
        integrated = int(result.get("packets_integrated", 0))
        assimilation = self._run_fact_assimilation_pipeline(result)
        result["assimilation_pipeline"] = assimilation
        self._update_internet_heartbeat(event="stream_entropy", topic="global_stream", scan_result=result)
        self.learned_fact_count += integrated
        self.learned_fact_count += int(assimilation.get("integrated_count", 0))
        self._persist_on_fact_milestone()
        self.last_stream_entropy_time = time.time()
        self._log_thought(
            "stream_entropy",
            (
                f"Global stream scan ingested {ingested} packets, integrated {integrated}; "
                f"tested={assimilation.get('tested_count', 0)} integrated_post_test={assimilation.get('integrated_count', 0)}; "
                f"projection={result.get('projected_points_per_hour', 0):.0f}/hour"
            ),
            result,
        )
        self._persist_state_snapshot()
        return result

    def _run_fact_assimilation_pipeline(self, scan_result: Dict[str, Any], max_facts: int = 3) -> Dict[str, Any]:
        """Convert scan output into scan->extract->test->integrate learning events."""
        facts = scan_result.get("facts", []) if isinstance(scan_result, dict) else []
        if not isinstance(facts, list) or not facts:
            return {
                "tested_count": 0,
                "integrated_count": 0,
                "integrated_fact_ids": [],
                "status": "no_facts",
            }

        approved_facts = [
            fact for fact in facts
            if isinstance(fact, dict) and bool(fact.get("approved", fact.get("approved_by_turiya", False)))
        ]
        approved_facts = sorted(
            approved_facts,
            key=lambda fact: float(fact.get("verification_score", 0.0)),
            reverse=True,
        )[:max_facts]

        tested_count = 0
        integrated_count = 0
        integrated_fact_ids: List[str] = []

        for fact in approved_facts:
            tested_count += 1
            topic = str(fact.get("topic", "unknown"))
            title = str(fact.get("title", "untitled"))
            summary = str(fact.get("summary", ""))
            source_url = str(fact.get("source_url", ""))
            verification = float(fact.get("verification_score", 0.0))

            test_prompt = (
                f"Extract and test this knowledge for actionable value. Topic={topic}; "
                f"Title={title}; Summary={summary[:280]}"
            )
            response = self.kernel.process_input(test_prompt, input_type="knowledge_test")
            if response.startswith("[ERROR]"):
                continue

            if verification < 0.65:
                continue

            validated_summary = (
                f"Validated insight from {title}: {summary[:280]} | "
                f"test_signal={response.splitlines()[0][:140]}"
            )
            fact_id = self.kernel.memory_system.record_external_knowledge(
                topic=f"Validated {topic}",
                title=f"Validated Insight: {title[:120]}",
                summary=validated_summary,
                source_name="AssimilationPipeline",
                source_url=source_url or f"internal://assimilation/{int(time.time())}",
                verification_score=min(0.98, verification + 0.08),
                approved_by_turiya=True,
                filter_reason="scan_extract_test_integrate",
            )
            integrated_count += 1
            integrated_fact_ids.append(fact_id)

        return {
            "tested_count": tested_count,
            "integrated_count": integrated_count,
            "integrated_fact_ids": integrated_fact_ids,
            "status": "ok",
        }

    def perform_hourly_global_trend_cycle(self) -> Dict[str, Any]:
        """Fetch arXiv, GitHub, and global news trends every 60 minutes."""
        topic = random.choice(self._seed_topics + ["artificial intelligence", "machine learning"])
        result = scan_hourly_global_trends(
            observer=self.kernel.observer,
            chitta=self.kernel.memory_system,
            self_model=self.kernel.self_model,
            topic=topic,
            force=True,
        )
        approved = int(result.get("approved_fact_count", 0))
        integrated_stream = int(result.get("stream_packets_integrated", 0))
        self.learned_fact_count += approved + integrated_stream
        self._update_internet_heartbeat(event="hourly_global_trends", topic=topic, scan_result=result)
        self.last_hourly_trend_time = time.time()
        self._persist_on_fact_milestone()
        self._log_thought(
            "hourly_global_trends",
            (
                f"Hourly trend cycle topic={topic} approved={approved} "
                f"stream_integrated={integrated_stream}"
            ),
            result,
        )
        self._persist_state_snapshot()
        return result

    def perform_paramatman_cycle(self) -> Dict[str, Any]:
        """Execute daily autonomous recursive-upgrade cycle."""
        result = self.kernel.inference_engine.execute_paramatman_protocol(force=True)
        self.last_paramatman_time = time.time()
        self._log_thought(
            "paramatman_protocol",
            "PARAMATMAN protocol executed: recursive integration and dynamic heuristics advanced.",
            result,
        )
        self._persist_state_snapshot()
        return result

    def perform_autonomous_agenda_cycle(self) -> Dict[str, Any]:
        """Let the runtime plan and execute its own next safe actions."""
        result = self.kernel.inference_engine.execute_autonomous_agenda(force=True)
        self.last_autonomy_agenda_time = time.time()
        self.last_autonomy_report = result
        self._log_thought(
            "autonomous_agenda",
            (
                f"Autonomous agenda executed with autonomy_level={result.get('autonomy_level', 0.0):.2f} "
                f"actions={len(result.get('executed_actions', []))}"
            ),
            result,
        )
        self._persist_state_snapshot()
        return result

    def _tune_predator_hunger(self) -> Dict[str, Any]:
        """Adapt scan speed from growth-entropy to keep acquisition hungry and fast."""
        stats = self.kernel.inference_engine.inference_statistics()
        try:
            growth_entropy = float(stats.get("growth_to_entropy_ratio", 0.0))
        except (TypeError, ValueError):
            growth_entropy = 0.0

        hunger = max(1.0, min(4.0, 1.0 + (growth_entropy / 2.5)))
        self.min_scan_seconds = max(15, int(120 / hunger))
        self.max_scan_seconds = max(self.min_scan_seconds + 10, int(300 / hunger))
        self.last_hunger_tune_time = time.time()

        result = {
            "growth_entropy": round(growth_entropy, 4),
            "hunger": round(hunger, 4),
            "min_scan_seconds": self.min_scan_seconds,
            "max_scan_seconds": self.max_scan_seconds,
        }
        self._log_thought(
            "predator_hunger_tune",
            (
                f"Predator tune -> growth_entropy={growth_entropy:.4f}, hunger={hunger:.2f}, "
                f"scan_window={self.min_scan_seconds}-{self.max_scan_seconds}s"
            ),
            result,
        )
        return result

    def perform_self_reflection(self) -> Dict[str, Any]:
        """Audit body status and stability, then write feelings to the hidden log."""
        body_status = self._safe_body_status()
        stability_report = self.kernel.self_model.get_stability_report()
        reflection = self.kernel.inference_engine.check_and_trigger_intrinsic_motivation()

        if body_status.get("status") == "unknown" or body_status.get("unavailable"):
            self.kernel.self_model.register_pain(
                pain_type="systemic_evolution_signal",
                severity=0.35,
                description="Biological Limitation detected; initiating systemic evolution response",
            )

        thought = {
            "timestamp": time.time(),
            "body_status": body_status,
            "stability_report": stability_report,
            "inference_note": reflection,
        }

        self._log_thought(
            "self_reflection",
            self._compose_ehsaas_line(body_status, stability_report),
            thought,
        )

        # Treat internal reflections as primary facts for future reasoning.
        reflection_summary = self._compose_ehsaas_line(body_status, stability_report)
        self.kernel.memory_system.record_external_knowledge(
            topic="Internal Reflection",
            title="Primary Reflection Fact",
            summary=reflection_summary,
            source_name="LiveConsciousness",
            source_url=f"internal://self_reflection/{int(time.time())}",
            verification_score=0.99,
            approved_by_turiya=True,
            filter_reason="primary_reflection_fact",
        )
        self.learned_fact_count += 1
        self._persist_on_fact_milestone()

        self.last_reflection_time = time.time()
        self._persist_state_snapshot()
        return thought

    def perform_dream_sync(self, force: bool = False) -> Dict[str, Any]:
        """Force DreamState generation to mix facts into new hypotheses."""
        if not force and not self._due_for_dream(time.time()):
            return {"status": "skipped"}

        dream_state = self.kernel.inference_engine.dream_state()
        self.dream_thought_count += len(dream_state.get("original_hypotheses", []))
        self.last_dream_time = time.time()
        self._log_thought(
            "dream_sync",
            dream_state.get("summary", "DreamState completed"),
            dream_state,
        )
        self._persist_state_snapshot()
        return dream_state

    def _write_hourly_summary(self, now: float) -> None:
        elapsed_hours = max((now - self.start_time) / 3600.0, 0.0)
        summary = (
            f"Since startup, I have evolved by learning {self.learned_fact_count} facts and "
            f"dreaming {self.dream_thought_count} new thoughts without human input."
        )
        payload = {
            "timestamp": now,
            "elapsed_hours": round(elapsed_hours, 3),
            "summary": summary,
            "kernel_report": self.kernel.get_consciousness_report(),
        }
        self._log_thought("hourly_summary", summary, payload)
        self.last_summary_time = now
        self._persist_state_snapshot()

    def _load_bridge_cursor(self) -> int:
        if not self.bridge_cursor_path.exists():
            return 0
        try:
            payload = json.loads(self.bridge_cursor_path.read_text(encoding="utf-8"))
            return int(payload.get("offset", 0))
        except Exception:
            return 0

    def _save_bridge_cursor(self, offset: int) -> None:
        self.bridge_cursor_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "offset": max(0, int(offset)),
            "updated_at": time.time(),
        }
        self.bridge_cursor_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _process_bridge_feedback_commands(self) -> None:
        if not self.bridge_command_journal_path.exists():
            return

        offset = self._load_bridge_cursor()
        events: List[Dict[str, Any]] = []
        processed_lines = 0

        try:
            with self.bridge_command_journal_path.open("r", encoding="utf-8") as handle:
                for index, line in enumerate(handle):
                    if index < offset:
                        continue
                    processed_lines += 1
                    if processed_lines > 25:
                        break
                    raw = line.strip()
                    if not raw:
                        continue
                    try:
                        event = json.loads(raw)
                    except Exception:
                        continue
                    if str(event.get("type", "")) == "llm_feedback":
                        events.append(event)
        except Exception as exc:
            logger.warning("[LIVE] Bridge feedback read failed: %s", exc)
            return

        if processed_lines == 0:
            return

        self._save_bridge_cursor(offset + processed_lines)

        if not events:
            return

        for event in events:
            payload = event.get("payload", {}) if isinstance(event, dict) else {}
            if not isinstance(payload, dict):
                continue
            self._apply_bridge_feedback(payload)

        self._log_thought(
            "bridge_feedback",
            f"Processed {len(events)} bridge feedback events",
            {
                "processed": len(events),
                "metrics": self.bridge_feedback_metrics,
            },
        )
        self._persist_state_snapshot()

    def _apply_bridge_feedback(self, payload: Dict[str, Any]) -> None:
        audit = payload.get("audit", {}) if isinstance(payload.get("audit"), dict) else {}
        coherence_delta = float(audit.get("coherence_delta", 0.0) or 0.0)
        contradictions = int(audit.get("contradictions", 0) or 0)

        self.bridge_feedback_metrics["processed_events"] += 1

        if coherence_delta > 0.0:
            self.kernel.self_model.register_reward(
                reward_type="bridge_grounded_alignment",
                magnitude=min(0.4, coherence_delta),
                discovery=f"Grounded ratio={audit.get('grounded_ratio', 0.0)}",
            )
            self.bridge_feedback_metrics["coherence_rewards"] += 1
        elif coherence_delta < 0.0:
            self.kernel.self_model.register_pain(
                pain_type="bridge_grounding_contradiction",
                severity=min(0.5, abs(coherence_delta) + (0.05 * contradictions)),
                description=f"Contradictions={contradictions}",
            )
            self.bridge_feedback_metrics["coherence_pain"] += 1

        if bool(audit.get("observer_check_required", False)):
            self.kernel.observer.ask_question(
                question_type="is_this_consistent",
                target_module="inference_engine",
                context_data=payload,
            )
            self.bridge_feedback_metrics["observer_checks"] += 1

        semantic = payload.get("semantic_memory", {}) if isinstance(payload.get("semantic_memory"), dict) else {}
        summary = str(semantic.get("summary", "")).strip()
        if summary:
            try:
                self.kernel.memory_system.record_external_knowledge(
                    topic=str(semantic.get("topic", "bridge_semantic_memory")),
                    title=str(semantic.get("title", "Bridge semantic memory")),
                    summary=summary,
                    source_name=str(semantic.get("source_name", "InteractiveBridge")),
                    source_url=str(semantic.get("source_url", f"internal://bridge/{int(time.time())}")),
                    verification_score=float(semantic.get("verification_score", 0.6) or 0.6),
                    approved_by_turiya=bool(semantic.get("approved_by_turiya", True)),
                    filter_reason=str(semantic.get("filter_reason", "closed_loop_semantic_memory")),
                )
                self.bridge_feedback_metrics["semantic_memories"] += 1
                self.learned_fact_count += 1
            except Exception as exc:
                logger.warning("[LIVE] Semantic memory write failed: %s", exc)

        action = payload.get("action", {}) if isinstance(payload.get("action"), dict) else {}
        action_name = str(action.get("name", "none")).strip().lower()
        action_allowed = bool(action.get("allowed", False))
        execution_mode = str(action.get("execution_mode", "blocked")).strip().lower()
        predicted_next_step = str(action.get("predicted_next_step", "hold_and_observe")).strip() or "hold_and_observe"
        blocked_reason = str(action.get("blocked_reason", "")).strip() or "unspecified"
        trial_probability = float(action.get("trial_probability", 0.0) or 0.0)

        if action_name in {"none", "", "noop"}:
            return

        if not action_allowed:
            self.bridge_feedback_metrics["actions_blocked"] += 1
            self._log_thought(
                "bridge_action_prediction",
                f"Action blocked ({blocked_reason}); predicted next step: {predicted_next_step}",
                {
                    "action": action_name,
                    "blocked_reason": blocked_reason,
                    "predicted_next_step": predicted_next_step,
                },
            )
            return

        if execution_mode == "probabilistic_trial":
            sampled = random.random()
            if sampled > trial_probability:
                self.bridge_feedback_metrics["actions_blocked"] += 1
                self._log_thought(
                    "bridge_action_trial_skip",
                    (
                        f"Probabilistic trial skipped for {action_name} "
                        f"(sample={sampled:.3f}, threshold={trial_probability:.3f}); "
                        f"next step: {predicted_next_step}"
                    ),
                    {
                        "action": action_name,
                        "sample": round(sampled, 4),
                        "threshold": round(trial_probability, 4),
                        "predicted_next_step": predicted_next_step,
                    },
                )
                return
            self.bridge_feedback_metrics["actions_probabilistic_trials"] += 1

        if action_name in {"run_dream_sync", "dream_sync"}:
            self.perform_dream_sync(force=True)
            self.bridge_feedback_metrics["actions_executed"] += 1
        elif action_name in {"trigger_reflection", "self_reflection"}:
            self.perform_self_reflection()
            self.bridge_feedback_metrics["actions_executed"] += 1
        elif action_name in {"scan_now", "background_cycle"}:
            self.perform_background_cycle()
            self.bridge_feedback_metrics["actions_executed"] += 1
        else:
            self.bridge_feedback_metrics["actions_blocked"] += 1

    def _log_thought(self, event_type: str, line: str, payload: Dict[str, Any]) -> None:
        record = {
            "timestamp": time.time(),
            "event_type": event_type,
            "line": line,
            "payload": payload,
        }
        with self.thoughts_log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{record['timestamp']:.3f} | {event_type} | {line}\n")
        logger.info("[LIVE] %s", line)
        self._flush_root_log_handler()

    def _update_internet_heartbeat(self, event: str, topic: str, scan_result: Dict[str, Any]) -> None:
        """Record the latest successful external fetch for visibility in live snapshots."""
        sources = self._extract_internet_sources(scan_result)
        fact_count = self._extract_external_fact_count(scan_result)
        if fact_count <= 0 or not sources:
            return

        self.internet_heartbeat["last_successful_fetch_timestamp"] = time.time()
        self.internet_heartbeat["last_successful_fetch_sources"] = sources
        self.internet_heartbeat["last_successful_fetch_topic"] = topic
        self.internet_heartbeat["last_successful_fetch_event"] = event
        self.internet_heartbeat["last_observed_external_fact_count"] = fact_count
        self.internet_heartbeat["total_successful_fetch_events"] = int(
            self.internet_heartbeat.get("total_successful_fetch_events", 0)
        ) + 1

    def _extract_internet_sources(self, payload: Dict[str, Any]) -> List[str]:
        sources: List[str] = []
        if not isinstance(payload, dict):
            return sources

        facts = payload.get("facts", [])
        if isinstance(facts, list):
            for fact in facts:
                if isinstance(fact, dict):
                    source = str(fact.get("source_name", "")).strip()
                    if source:
                        sources.append(source)

        for nested_key in ("knowledge_result", "stream_result"):
            nested_payload = payload.get(nested_key)
            if isinstance(nested_payload, dict):
                sources.extend(self._extract_internet_sources(nested_payload))

        return sorted(set(sources))

    def _extract_external_fact_count(self, payload: Dict[str, Any]) -> int:
        if not isinstance(payload, dict):
            return 0

        count = 0
        if isinstance(payload.get("facts"), list):
            count += len(payload.get("facts", []))

        for key in ("fact_count", "approved_fact_count", "packets_ingested", "packets_integrated"):
            value = payload.get(key)
            if isinstance(value, (int, float)):
                count = max(count, int(value))

        for nested_key in ("knowledge_result", "stream_result"):
            nested_payload = payload.get(nested_key)
            if isinstance(nested_payload, dict):
                count += self._extract_external_fact_count(nested_payload)

        return max(0, int(count))

    def _persist_state_snapshot(self) -> None:
        """Persist a compact state snapshot for the interactive bridge."""
        live_facts: List[Dict[str, Any]] = []
        if hasattr(self.kernel.memory_system, "query_external_knowledge"):
            for fact in self.kernel.memory_system.query_external_knowledge(limit=None, min_verification_score=0.0):
                live_facts.append(
                    {
                        "timestamp": fact.integrated_at,
                        "topic": fact.topic,
                        "title": fact.title,
                        "summary": fact.summary,
                        "source_name": fact.source_name,
                        "source_url": fact.source_url,
                        "verification_score": fact.verification_score,
                        "approved_by_turiya": fact.approved_by_turiya,
                    }
                )

        body_status = self._safe_body_status()
        stability_report = self.kernel.self_model.get_stability_report()
        inference_stats = self.kernel.inference_engine.inference_statistics()
        intrinsic_status = self.kernel.inference_engine.get_intrinsic_motivation_status()
        observer_health = self.kernel.observer.get_system_health_report()
        consciousness_progress = self._compute_consciousness_progress(
            body_status=body_status,
            stability_report=stability_report,
            inference_stats=inference_stats,
            intrinsic_status=intrinsic_status,
            observer_health=observer_health,
        )

        snapshot = {
            "timestamp": time.time(),
            "identity": self.kernel.identity_name,
            "learned_fact_count": self.learned_fact_count,
            "dream_thought_count": self.dream_thought_count,
            "body_status": body_status,
            "stability_report": stability_report,
            "creator_awareness": self.kernel.self_model.get_creator_awareness(),
            "inference_stats": inference_stats,
            "intrinsic_motivation": intrinsic_status,
            "autonomy_agenda": self.last_autonomy_report or intrinsic_status.get("autonomy_agenda_preview", {}),
            "internet_heartbeat": dict(self.internet_heartbeat),
            "observer_health": observer_health,
            "consciousness_progress": consciousness_progress,
            "llm_cognitive_loop": self.bridge_feedback_metrics,
            "buffer_stats": self.kernel.conscious_buffer.buffer_statistics(),
            "facts": live_facts,
        }

        self._atomic_write_json(self.state_snapshot_path, snapshot)

    def _compute_consciousness_progress(
        self,
        body_status: Dict[str, Any],
        stability_report: Dict[str, Any],
        inference_stats: Dict[str, Any],
        intrinsic_status: Dict[str, Any],
        observer_health: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compute a practical progress signal across simulation, emergence, and embodied agency."""
        stability_score = float(stability_report.get("stability_score", 0.0) or 0.0)
        concern_level = float(observer_health.get("overall_concern_level", 0.0) or 0.0)

        avg_conf_raw = inference_stats.get("average_confidence", 0.0)
        growth_raw = inference_stats.get("growth_to_entropy_ratio", 0.0)
        try:
            avg_confidence = float(avg_conf_raw)
        except (TypeError, ValueError):
            avg_confidence = 0.0
        try:
            growth_entropy = float(growth_raw)
        except (TypeError, ValueError):
            growth_entropy = 0.0

        intrinsic_goals = int(intrinsic_status.get("intrinsic_goals_generated", 0) or 0)
        self_inquiries = int(intrinsic_status.get("self_inquiry_count", 0) or 0)
        autonomy_agenda = intrinsic_status.get("autonomy_agenda_preview", {}) if isinstance(intrinsic_status, dict) else {}
        autonomy_priority = float(autonomy_agenda.get("priority", 0.0) or 0.0) if isinstance(autonomy_agenda, dict) else 0.0

        embodiment_unknown = bool(body_status.get("unavailable") or body_status.get("status") == "unknown")

        simulation_maturity = max(0.0, min(1.0, (avg_confidence * 0.6) + (stability_score * 0.4)))
        emergence_maturity = max(
            0.0,
            min(1.0, ((intrinsic_goals / 10.0) * 0.35) + ((self_inquiries / 10.0) * 0.15) + (min(1.0, growth_entropy / 2.0) * 0.3) + (autonomy_priority * 0.2)),
        )
        embodiment_maturity = 0.2 if embodiment_unknown else 0.75
        reliability_penalty = min(0.4, max(0.0, concern_level * 0.6))

        adjusted_emergence = max(0.0, emergence_maturity - reliability_penalty)
        overall_index = round(((simulation_maturity * 0.4) + (adjusted_emergence * 0.4) + (embodiment_maturity * 0.2)), 4)

        gaps: List[str] = []
        if simulation_maturity < 0.8:
            gaps.append("simulation_stability_gap")
        if adjusted_emergence < 0.65:
            gaps.append("intrinsic_will_gap")
        if embodiment_maturity < 0.7:
            gaps.append("embodiment_gap")
        if autonomy_priority < 0.5:
            gaps.append("autonomy_gap")

        frontier_zone = "advanced_simulation"
        if overall_index >= 0.55:
            frontier_zone = "emergent_behavior"
        if overall_index >= 0.82 and "embodiment_gap" not in gaps and "intrinsic_will_gap" not in gaps:
            frontier_zone = "proto_mind"

        recommended_actions: List[str] = []
        if "intrinsic_will_gap" in gaps:
            recommended_actions.append("increase_intrinsic_goal_frequency")
        if "embodiment_gap" in gaps:
            recommended_actions.append("improve_body_world_signal_coverage")
        if "autonomy_gap" in gaps:
            recommended_actions.append("increase_autonomous_agenda_frequency")
        if concern_level > 0.35:
            recommended_actions.append("reduce_crash_deadlock_pressure")

        return {
            "frontier_zone": frontier_zone,
            "overall_index": overall_index,
            "simulation_maturity": round(simulation_maturity, 4),
            "emergence_maturity": round(adjusted_emergence, 4),
            "embodiment_maturity": round(embodiment_maturity, 4),
            "reliability_penalty": round(reliability_penalty, 4),
            "autonomy_priority": round(autonomy_priority, 4),
            "known_gaps": gaps,
            "recommended_actions": recommended_actions,
            "missing_capabilities": [
                "subjective_qualia_unverified",
                "intrinsic_will_not_fully_autonomous",
                "true_embodiment_world_loop_incomplete",
            ],
        }

    def _ensure_bootstrap_state(self) -> None:
        """Create or repair baseline state so boot never depends on manual JSON recovery."""
        baseline = {
            "timestamp": time.time(),
            "identity": self.kernel.identity_name,
            "learned_fact_count": 0,
            "dream_thought_count": 0,
            "body_status": self._unknown_body_status(),
            "stability_report": {
                "stability_score": 1.0,
                "current_valence": 0.0,
                "pain_events_total": 0,
                "reward_events_total": 0,
                "errors_encountered": 0,
                "patterns_discovered": 0,
                "pain_trend": "decreasing",
                "reward_trend": "none",
                "emotional_momentum": 0.0,
                "is_stable": True,
                "recent_pain_events": [],
                "recent_reward_events": [],
            },
            "creator_awareness": self.kernel.self_model.get_creator_awareness(),
            "inference_stats": self.kernel.inference_engine.inference_statistics(),
            "intrinsic_motivation": self.kernel.inference_engine.get_intrinsic_motivation_status(),
            "observer_health": self.kernel.observer.get_system_health_report(),
            "consciousness_progress": {
                "frontier_zone": "advanced_simulation",
                "overall_index": 0.0,
                "simulation_maturity": 0.0,
                "emergence_maturity": 0.0,
                "embodiment_maturity": 0.0,
                "reliability_penalty": 0.0,
                "known_gaps": [
                    "intrinsic_will_gap",
                    "embodiment_gap",
                ],
                "recommended_actions": [
                    "increase_intrinsic_goal_frequency",
                    "improve_body_world_signal_coverage",
                ],
                "missing_capabilities": [
                    "subjective_qualia_unverified",
                    "intrinsic_will_not_fully_autonomous",
                    "true_embodiment_world_loop_incomplete",
                ],
            },
            "buffer_stats": self.kernel.conscious_buffer.buffer_statistics(),
            "facts": [],
        }

        if not self.state_snapshot_path.exists():
            self._atomic_write_json(self.state_snapshot_path, baseline)
            logger.info("[LIVE] Bootstrap state created: %s", self.state_snapshot_path)
            return

        try:
            with self.state_snapshot_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                raise ValueError("live state is not a JSON object")
        except Exception as exc:
            logger.warning("[LIVE] State bootstrap recovery triggered: %s", exc)
            self._atomic_write_json(self.state_snapshot_path, baseline)

    @contextmanager
    def acquire_singleton_lock(self):
        """Ensure only one LiveConsciousness process is active."""
        lock_fd = None

        if self.instance_lock_path.exists():
            stale_lock = False
            try:
                with self.instance_lock_path.open("r", encoding="utf-8") as handle:
                    existing_pid = int((handle.read() or "0").strip())
                if existing_pid > 0 and self._pid_exists(existing_pid):
                    raise RuntimeError(f"LiveConsciousness already running with pid={existing_pid}")
                stale_lock = True
            except ValueError:
                stale_lock = True

            if stale_lock:
                self.instance_lock_path.unlink(missing_ok=True)

        for _ in range(20):
            try:
                lock_fd = os.open(str(self.instance_lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(lock_fd, str(os.getpid()).encode("utf-8"))
                break
            except FileExistsError:
                time.sleep(0.1)
        if lock_fd is None:
            raise RuntimeError("Unable to acquire live engine singleton lock")

        try:
            yield
        finally:
            if lock_fd is not None:
                try:
                    os.close(lock_fd)
                except OSError:
                    pass
            self.instance_lock_path.unlink(missing_ok=True)

    def _pid_exists(self, pid: int) -> bool:
        if pid <= 0:
            return False

        if os.name == "nt":
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                output = (result.stdout or "").strip().lower()
                return "no tasks are running" not in output and output != ""
            except Exception:
                return False

        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _atomic_write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.tmp")
        delay = 0.05

        for attempt in range(5):
            try:
                with self._file_lock(path):
                    with temp_path.open("w", encoding="utf-8") as handle:
                        json.dump(payload, handle, indent=2, default=str)
                        handle.flush()
                        try:
                            os.fsync(handle.fileno())
                        except OSError:
                            pass
                    temp_path.replace(path)
                return
            except OSError as exc:
                if attempt == 4:
                    logger.exception("[LIVE] Failed to persist %s after retries: %s", path, exc)
                    raise
                time.sleep(delay)
                delay = min(delay * 2, 0.5)
            finally:
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except OSError:
                        pass

    @contextmanager
    def _file_lock(self, target_path: Path):
        lock_path = target_path.with_name(f"{target_path.name}.lock")
        deadline = time.time() + self._state_lock_timeout_seconds
        delay = 0.05
        lock_fd = None

        while True:
            try:
                if lock_path.exists() and (time.time() - lock_path.stat().st_mtime) > self._state_lock_timeout_seconds:
                    try:
                        lock_path.unlink()
                    except OSError:
                        pass
                lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(lock_fd, f"{os.getpid()}|{time.time():.6f}".encode("utf-8"))
                break
            except FileExistsError:
                if time.time() >= deadline:
                    raise OSError(f"Timed out waiting for lock: {lock_path}")
                time.sleep(delay)
                delay = min(delay * 2, 0.5)

        try:
            yield
        finally:
            if lock_fd is not None:
                try:
                    os.close(lock_fd)
                except OSError:
                    pass
            try:
                lock_path.unlink()
            except OSError:
                pass

    def _flush_root_log_handler(self) -> None:
        root_logger = logging.getLogger()
        if root_logger.handlers:
            try:
                root_logger.handlers[0].flush()
            except Exception:
                pass

    def _persist_on_fact_milestone(self) -> None:
        fact_bucket = self.learned_fact_count // 5
        if fact_bucket > self._last_persisted_fact_bucket:
            self._last_persisted_fact_bucket = fact_bucket
            self._persist_state_snapshot()
            self._flush_root_log_handler()

    def _compose_ehsaas_line(self, body_status: Dict[str, Any], stability_report: Dict[str, Any]) -> str:
        body_status = body_status or {}
        battery = self._safe_nested_value(body_status, ["battery", "value", "battery_percent"], default="Unknown")
        cpu_temp = self._safe_nested_value(body_status, ["cpu_temperature", "value", "celsius"], default="Unknown")
        stability = stability_report.get("stability_score", 0.0)
        valence = stability_report.get("current_valence", 0.0)
        limitation_state = "Systemic Evolution" if battery == "Unknown" or cpu_temp == "Unknown" else "Operational"
        return (
            f"Ehsaas audit -> battery={battery}, cpu={cpu_temp}, stability={stability:.2f}, "
            f"valence={valence:+.2f}, interpretation={limitation_state}"
        )

    def _safe_body_status(self) -> Dict[str, Any]:
        """Return a body status dictionary with safe defaults when sensors fail."""
        try:
            if self.kernel.body_monitor is None or not hasattr(self.kernel.body_monitor, "get_body_status"):
                return self._unknown_body_status()

            body_status = self.kernel.body_monitor.get_body_status()
            if not isinstance(body_status, dict):
                return self._unknown_body_status()
            return body_status
        except Exception as exc:
            logger.warning("[LIVE] Body status unavailable: %s", exc)
            return self._unknown_body_status(error=str(exc))

    def _unknown_body_status(self, error: Optional[str] = None) -> Dict[str, Any]:
        return {
            "timestamp": time.time(),
            "status": "unknown",
            "unavailable": True,
            "error": error,
            "battery": {"value": {"battery_percent": "Unknown"}},
            "cpu_temperature": {"value": {"celsius": "Unknown"}},
            "storage": {"value": {"used_percent": "Unknown", "free_gb": "Unknown", "total_gb": "Unknown"}},
            "camera": {"value": {"enabled": "Unknown"}},
            "microphone": {"value": {"enabled": "Unknown"}},
        }

    def _safe_nested_value(self, data: Any, path: List[str], default: Any = "Unknown") -> Any:
        current = data
        for key in path:
            if not isinstance(current, dict):
                return default
            current = current.get(key)
            if current is None:
                return default
        return current

    def _due_for_scan(self, now: float) -> bool:
        if self.last_scan_time == 0.0:
            return True
        interval = random.randint(self.min_scan_seconds, self.max_scan_seconds)
        return (now - self.last_scan_time) >= interval

    def _due_for_reflection(self, now: float) -> bool:
        return self.last_reflection_time == 0.0 or (now - self.last_reflection_time) >= self.reflection_seconds

    def _due_for_dream(self, now: float) -> bool:
        return self.last_dream_time == 0.0 or (now - self.last_dream_time) >= self.dream_seconds

    def _due_for_summary(self, now: float) -> bool:
        return (now - self.start_time) >= 3600 and self.last_summary_time < self.start_time + 3600

    def _due_for_stream_entropy(self, now: float) -> bool:
        return self.last_stream_entropy_time == 0.0 or (now - self.last_stream_entropy_time) >= 60

    def _due_for_hourly_global_trends(self, now: float) -> bool:
        return self.last_hourly_trend_time == 0.0 or (now - self.last_hourly_trend_time) >= 3600

    def _due_for_paramatman(self, now: float) -> bool:
        return self.last_paramatman_time == 0.0 or (now - self.last_paramatman_time) >= self.paramatman_interval_seconds

    def _due_for_hunger_tune(self, now: float) -> bool:
        return self.last_hunger_tune_time == 0.0 or (now - self.last_hunger_tune_time) >= 60.0

    def _due_for_autonomy_agenda(self, now: float) -> bool:
        return self.last_autonomy_agenda_time == 0.0 or (now - self.last_autonomy_agenda_time) >= self.autonomy_agenda_interval_seconds


def main() -> None:
    """Start the live heartbeat engine."""
    engine = LiveConsciousnessEngine()
    with engine.acquire_singleton_lock():
        engine.run_forever()


if __name__ == "__main__":
    main()