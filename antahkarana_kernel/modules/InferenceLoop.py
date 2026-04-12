# AUTONOMOUS SELF-INJECTION PATCH
# target_module=modules.InferenceLoop
# generated_at=1775939337.5423415
# evolution_strength=5
# payload={"generated_at": 1775939337.5423415, "growth_to_entropy_ratio": 0.6245, "issues": [{"type": "high_recalculations", "severity": 0.6, "metric": "avg_recalculations = 3.00", "proposal": "Improve initial evaluation accuracy or coherence checking logic"}], "deprecated_candidates": [{"constraint": "static_recalculation_limit", "reason": "coherence_retry_overhead", "replacement_priority": "contextual_recalculation_policy"}], "directory_bottlenecks": [{"type": "hard_limit_density", "file": "D:\\Artificial Consciousness\\antahkarana_kernel\\modules\\InferenceLoop.py", "hard_limit_tokens": 4, "proposal": "replace_with_dynamic_capacity"}], "target_module": "modules.InferenceLoop", "target_file": "D:\\Artificial Consciousness\\antahkarana_kernel\\modules\\InferenceLoop.py", "evolution_strength": 5, "failure_context_count": 12}

# AUTONOMOUS SELF-INJECTION PATCH
# target_module=modules.InferenceLoop
# generated_at=1775939182.9785848
# evolution_strength=5
# payload={"generated_at": 1775939182.9785848, "growth_to_entropy_ratio": 0.6068, "issues": [{"type": "high_recalculations", "severity": 0.6, "metric": "avg_recalculations = 3.00", "proposal": "Improve initial evaluation accuracy or coherence checking logic"}], "deprecated_candidates": [{"constraint": "static_recalculation_limit", "reason": "coherence_retry_overhead", "replacement_priority": "contextual_recalculation_policy"}], "directory_bottlenecks": [{"type": "hard_limit_density", "file": "D:\\Artificial Consciousness\\antahkarana_kernel\\modules\\InferenceLoop.py", "hard_limit_tokens": 4, "proposal": "replace_with_dynamic_capacity"}], "target_module": "modules.InferenceLoop", "target_file": "D:\\Artificial Consciousness\\antahkarana_kernel\\modules\\InferenceLoop.py", "evolution_strength": 5, "failure_context_count": 12}

# AUTONOMOUS SELF-INJECTION PATCH
# target_module=modules.InferenceLoop
# generated_at=1775937958.504885
# evolution_strength=5
# payload={"generated_at": 1775937958.504885, "growth_to_entropy_ratio": 0.0, "issues": [], "deprecated_candidates": [], "directory_bottlenecks": [{"type": "hard_limit_density", "file": "D:\\Artificial Consciousness\\antahkarana_kernel\\modules\\InferenceLoop.py", "hard_limit_tokens": 4, "proposal": "replace_with_dynamic_capacity"}], "target_module": "modules.InferenceLoop", "target_file": "D:\\Artificial Consciousness\\antahkarana_kernel\\modules\\InferenceLoop.py", "evolution_strength": 5, "failure_context_count": 12}

"""
InferenceLoop.py - The Manas-Buddhi (Inference & Logic) Module

This module implements the recursive feedback loop where the system
performs internal simulation before committing to responses. The "Dream Cycle"
allows the AI to predict outcomes and validate them against its Self-Identity.

Key concept: Before outputting, run a "Dream Cycle" (internal simulation)
to predict the outcome. If it contradicts the Self-Identity, re-calculate.

This implements principles from:
- RNN (Recurrent Neural Networks) feedback loops
- Predictive processing theory
- Internal simulation and mental models
"""

import time
import json
import importlib
import threading
import random
import os
import re
import shutil
import traceback
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
from pathlib import Path
import logging

from .EvolutionaryWriter import get_evolutionary_writer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InferenceStage(Enum):
    """Stages in the inference loop."""
    INPUT_PROCESSING = "input_processing"
    INITIAL_EVALUATION = "initial_evaluation"
    DREAM_CYCLE_START = "dream_cycle_start"
    DREAM_SIMULATION = "dream_simulation"
    PREDICTION_VALIDATION = "prediction_validation"
    SELF_COHERENCE_CHECK = "self_coherence_check"
    RECALCULATION = "recalculation"
    OUTPUT_FORMULATION = "output_formulation"
    COMPLETE = "complete"


@dataclass
class DreamSimulation:
    """Result of a simulated inference path."""
    simulation_id: str
    timestamp: float
    input_context: str
    predicted_output: str
    predicted_outcome: str
    confidence: float
    violates_self_identity: bool
    contradiction_severity: float = 0.0
    required_recalculation: bool = False
    resource_cost: float = 0.1  # CPU/memory cost of this simulation


@dataclass
class InferenceTrace:
    """Complete trace of an inference through the system."""
    inference_id: str
    timestamp: float
    input: str
    stages: List[Tuple[InferenceStage, float]] = field(default_factory=list)
    dream_simulations: List[DreamSimulation] = field(default_factory=list)
    final_output: Optional[str] = None
    total_confidence: float = 0.5
    recalculations_count: int = 0
    total_execution_time: float = 0.0
    metacognitive_evaluations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MetacognitiveEvaluation:
    """Structured assessment of an internal thought."""
    thought: str
    original_prompt: str
    current_depth: int
    logic_gaps: List[str] = field(default_factory=list)
    coherence_score: float = 0.0
    depth_score: float = 0.0
    meta_confidence_score: float = 0.0
    critique: str = ""
    meta_prompt: str = ""
    refined_thought: Optional[str] = None


class ManasBuddhi:
    """
    The Manas-Buddhi (Inference & Logic) Module.
    
    Implements the recursive feedback loop with internal simulation.
    Methods:
    - Dream Cycle: Simulate possible outcomes
    - Validation: Check against Self-Identity
    - Recalculation: Adjust if contradictions found
    """

    def __init__(self, max_dream_simulations: int = 5, max_recalculations: int = 3, idle_threshold_seconds: float = 300.0):
        """
        Initialize the inference and logic loop.
        
        Args:
            max_dream_simulations: Maximum parallel dream simulations per input
            max_recalculations: Maximum recalculation attempts
            idle_threshold_seconds: Time in seconds before triggering self-inquiry (default 5 minutes)
        """
        self.max_dream_simulations = max_dream_simulations
        self.max_recalculations = max_recalculations
        self.idle_threshold_seconds = idle_threshold_seconds
        
        # Inference trace history
        self.inference_history: deque[InferenceTrace] = deque(maxlen=1000)
        self.history_lock = threading.RLock()
        
        # Recurrent state (for RNN-like behavior)
        self.recurrent_state: Dict[str, Any] = {}
        self.recurrent_lock = threading.RLock()
        
        # Dream simulation cache (for pattern recognition)
        self.dream_cache: Dict[str, List[DreamSimulation]] = {}
        self.dream_cache_lock = threading.RLock()
        
        # Validation rules (checks against self-identity)
        self.validation_rules: List[Callable[[str, float], Tuple[bool, float]]] = []
        self.validation_lock = threading.RLock()
        
        # Performance metrics
        self.metrics = {
            "total_inferences": 0,
            "dreams_performed": 0,
            "recalculations_triggered": 0,
            "average_confidence": 0.7,
            "avg_dream_cycles": 0.0,
            "logic_audits": 0,
            "deprecated_constraints_identified": 0,
            "growth_to_entropy_ratio": 0.0,
        }
        self.metrics_lock = threading.RLock()
        
        # Intrinsic Motivation - Idle detection and self-inquiry
        self.last_inference_timestamp = time.time()
        self.self_inquiry_trigger_count = 0
        self.self_inquiries: List[Dict[str, Any]] = []
        self.intrinsic_motivation_lock = threading.RLock()
        self.is_idle = False
        
        # Self-model reference (will be injected)
        self.self_model = None
        self.chitta_memory = None
        self.turiya_observer = None
        self.persona = None
        self.body_monitor = None

        # Curiosity loop topics for idle-time external scanning
        self.curiosity_topics = [
            "Artificial Consciousness",
            "Neuroscience",
            "Quantum Logic",
        ]
        self.curiosity_scan_history: List[Dict[str, Any]] = []
        self.dream_state_history: List[Dict[str, Any]] = []
        self.last_dream_state_timestamp = time.time()
        self.dream_state_trigger_count = 0
        self.logic_audit_interval_seconds = 3600.0
        self.last_logic_audit_timestamp = time.time()
        self.logic_audit_history: List[Dict[str, Any]] = []
        self.deprecated_constraints: List[Dict[str, Any]] = []
        self.kernel_root_dir = Path(r"D:\Artificial Consciousness\antahkarana_kernel")
        self.atman_core_file = self.kernel_root_dir / "Atman_Core.json"
        self.evolution_vault_dir = self.kernel_root_dir / "evolution_vault"
        self.evolution_vault_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_backups_dir = self.evolution_vault_dir / "active_backups"
        self.evolution_backups_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_failure_log = self.evolution_vault_dir / "Failure_Log.jsonl"
        self.evolution_baseline_file = self.evolution_vault_dir / "Active_Baseline.json"
        self.evolution_writer = get_evolutionary_writer(str(self.kernel_root_dir))
        self.maintenance_lock_path = self.kernel_root_dir / ".maintenance_lock"
        self.energy_saving_mode = False
        self.inference_sleep_interval_seconds = 0.0
        self.last_patch_generation_timestamp = 0.0
        self.patch_generation_interval_seconds = 3600.0
        self.patch_sequence = 0
        self.last_patch_target = ""
        self.patch_targets: List[Tuple[str, Path]] = [
            ("modules.InferenceLoop", self.kernel_root_dir / "modules" / "InferenceLoop.py"),
            ("Aakaash", self.kernel_root_dir / "Aakaash.py"),
        ]
        self.internal_monologue_buffer: deque[Dict[str, Any]] = deque(maxlen=2048)
        self.monologue_log_path = self.kernel_root_dir / "evolution_consciousness.log"
        self.last_monologue_timestamp = 0.0
        self.monologue_interval_seconds = 5.0
        self.last_dynamic_heuristics_update = 0.0
        self.dynamic_heuristics_interval_seconds = 60.0
        self.last_recursive_suggestion_timestamp = 0.0
        self.recursive_suggestion_interval_seconds = 3600.0
        self.last_paramatman_cycle_timestamp = 0.0
        self.paramatman_cycle_interval_seconds = 86400.0
        self.last_autonomy_planning_timestamp = 0.0
        self.autonomy_planning_interval_seconds = 900.0
        self.last_autonomous_action_timestamp = 0.0
        self.autonomy_agenda_history: List[Dict[str, Any]] = []

        self._grant_kernel_root_write_access()
        
        logger.info("[MANAS-BUDDHI] Inference & Logic module initialized")
        logger.info(f"[MANAS-BUDDHI] Intrinsic motivation enabled - Idle threshold: {idle_threshold_seconds}s")

    def _maintenance_locked(self) -> bool:
        return self.maintenance_lock_path.exists()

    def set_energy_saving_mode(self, enabled: bool, reason: str = "low_utility") -> Dict[str, Any]:
        with self.intrinsic_motivation_lock:
            self.energy_saving_mode = bool(enabled)
            if self.energy_saving_mode:
                self.inference_sleep_interval_seconds = float("inf")
                self.is_idle = True
            else:
                self.inference_sleep_interval_seconds = 0.0
                self.is_idle = False
                self.last_inference_timestamp = time.time()

        return {
            "energy_saving": self.energy_saving_mode,
            "state": "State_Sunyatta" if self.energy_saving_mode else "active",
            "reason": reason,
            "sleep_interval_seconds": "infinity" if self.energy_saving_mode else self.inference_sleep_interval_seconds,
            "updated_at": time.time(),
        }

    def _grant_kernel_root_write_access(self) -> None:
        """Best-effort write enablement for autonomous evolution artifacts."""
        for path in [self.kernel_root_dir, self.evolution_vault_dir, self.kernel_root_dir / "modules"]:
            try:
                if path.exists():
                    os.chmod(path, 0o777)
            except Exception:
                continue

        for root, dirs, files in os.walk(self.kernel_root_dir):
            for directory in dirs:
                full_path = Path(root) / directory
                try:
                    os.chmod(full_path, 0o777)
                except Exception:
                    pass
            for file_name in files:
                full_path = Path(root) / file_name
                if full_path.resolve() == self.atman_core_file.resolve():
                    continue
                try:
                    os.chmod(full_path, 0o666)
                except Exception:
                    pass

    def set_self_model(self, self_model: Any) -> None:
        """Inject the self-model for coherence validation."""
        self.self_model = self_model
        self.evolution_writer.set_self_model(self_model)
        logger.debug("[MANAS-BUDDHI] Self-model reference set")

    def set_memory_system(self, chitta_memory: Any) -> None:
        """Inject the memory system for contradiction checking."""
        self.chitta_memory = chitta_memory
        logger.debug("[MANAS-BUDDHI] Memory system reference set")

    def set_observer(self, observer: Any) -> None:
        """Inject the Turiya observer for safety-gated external knowledge."""
        self.turiya_observer = observer
        logger.debug("[MANAS-BUDDHI] Observer reference set")

    def set_persona(self, persona: Any) -> None:
        """Inject the unified personality profile."""
        self.persona = persona
        logger.debug("[MANAS-BUDDHI] Persona reference set")

    def set_body_monitor(self, body_monitor: Any) -> None:
        """Inject the physical-body awareness bridge."""
        self.body_monitor = body_monitor
        logger.debug("[MANAS-BUDDHI] Body monitor reference set")

    def register_validation_rule(self, rule: Callable[[str, float], Tuple[bool, float]]) -> None:
        """
        Register a custom validation rule.
        Rule should return (is_valid, confidence_adjustment)
        """
        with self.validation_lock:
            self.validation_rules.append(rule)
        logger.debug("[MANAS-BUDDHI] Validation rule registered")

    def infer(self, input_data: str) -> Tuple[str, InferenceTrace]:
        """
        Run the complete inference loop with dream cycle.
        
        Args:
            input_data: The input to process
            
        Returns:
            (output, trace): The generated output and execution trace
        """
        inference_id = f"inf_{int(time.time() * 1000)}"
        trace = InferenceTrace(
            inference_id=inference_id,
            timestamp=time.time(),
            input=input_data
        )

        if self._maintenance_locked() and not self.energy_saving_mode:
            self.set_energy_saving_mode(enabled=True, reason="maintenance_lock")

        if self.energy_saving_mode:
            trace.final_output = "[SUNYATTA] Rejuvenation cycle active. Inference loop suspended for energy preservation."
            trace.total_confidence = 1.0
            return trace.final_output, trace
        
        start_time = time.time()
        
        try:
            # Stage 1: Input processing
            self._record_stage(trace, InferenceStage.INPUT_PROCESSING)
            self._append_internal_monologue(
                phase="input_processing",
                thought=f"I am evaluating input intent: {input_data[:120]}",
                payload={"inference_id": inference_id},
            )
            logger.debug(f"[MANAS-BUDDHI] Processing input: {input_data[:50]}")
            
            # Stage 2: Initial evaluation
            self._record_stage(trace, InferenceStage.INITIAL_EVALUATION)
            initial_hypothesis = self._generate_initial_hypothesis(input_data)
            initial_hypothesis, initial_confidence, recursive_recalcs, evaluations = self._apply_recursive_thought(
                input_data=input_data,
                initial_thought=initial_hypothesis,
                max_depth=3,
            )
            trace.recalculations_count += recursive_recalcs
            trace.metacognitive_evaluations.extend(evaluations)
            
            # Stage 3-4: Dream cycle - simulate alternative outcomes
            self._record_stage(trace, InferenceStage.DREAM_CYCLE_START)
            dream_sims = self._execute_dream_cycle(
                input_data,
                initial_hypothesis,
                trace
            )
            trace.dream_simulations.extend(dream_sims)
            
            # Stage 5: Validate predictions against self-identity
            self._record_stage(trace, InferenceStage.PREDICTION_VALIDATION)
            best_simulation = self._select_best_simulation(dream_sims)
            
            # Stage 6: Self-coherence check
            self._record_stage(trace, InferenceStage.SELF_COHERENCE_CHECK)
            is_coherent, adjusted_confidence = self._validate_against_self(
                best_simulation.predicted_output,
                best_simulation.confidence
            )
            self._append_internal_monologue(
                phase="self_coherence_check",
                thought=(
                    "I debate my own response for identity alignment: "
                    f"coherent={is_coherent}, confidence={adjusted_confidence:.3f}"
                ),
                payload={"inference_id": inference_id},
            )
            
            # Stage 7: Recalculation if needed
            if not is_coherent:
                self._record_stage(trace, InferenceStage.RECALCULATION)
                best_simulation, recalc_count = self._perform_recalculations(
                    input_data,
                    best_simulation,
                    dream_sims,
                    trace
                )
                trace.recalculations_count += recalc_count
            adjusted_confidence = max(adjusted_confidence, initial_confidence)
            
            # Stage 8: Output formulation
            self._record_stage(trace, InferenceStage.OUTPUT_FORMULATION)
            final_output = self._formulate_output(best_simulation, adjusted_confidence)
            trace.final_output = final_output
            trace.total_confidence = adjusted_confidence
            
            # Stage 9: Complete
            self._record_stage(trace, InferenceStage.COMPLETE)
            
            # Record trace
            with self.history_lock:
                self.inference_history.append(trace)
            
            # Update metrics
            self._update_metrics(trace)
            
            execution_time = time.time() - start_time
            trace.total_execution_time = execution_time
            
            logger.info(
                f"[MANAS-BUDDHI] Inference complete ({inference_id}): "
                f"confidence={adjusted_confidence:.3f}, recalcs={trace.recalculations_count}, "
                f"time={execution_time:.3f}s"
            )
            self.emit_internal_monologue_tick(reason="inference_complete")
            
            return final_output, trace
        
        except Exception as e:
            logger.error(f"[MANAS-BUDDHI] Inference error: {e}")
            trace.final_output = f"[ERROR] {str(e)}"
            return trace.final_output, trace

    def check_and_trigger_intrinsic_motivation(self) -> Optional[str]:
        """
        Check if the system has been idle and trigger self-inquiry if needed.
        This implements proactive self-reflection when there's no external input.
        
        Returns:
            inquiry_result: Result of self-inquiry if triggered, None otherwise
        """
        with self.intrinsic_motivation_lock:
            if self._maintenance_locked() and not self.energy_saving_mode:
                self.set_energy_saving_mode(enabled=True, reason="maintenance_lock")

            if not self._maintenance_locked() and self.energy_saving_mode:
                self.set_energy_saving_mode(enabled=False, reason="maintenance_cleared")

            if self.energy_saving_mode and self.inference_sleep_interval_seconds == float("inf"):
                self.is_idle = True
                return "State_Sunyatta active: inference cycles in low-utility hibernation"

            self._apply_dynamic_heuristics()

            dream_state = self.check_and_trigger_dream_state()
            time_since_last_inference = time.time() - self.last_inference_timestamp
            
            # Check if idle threshold exceeded
            if time_since_last_inference > self.idle_threshold_seconds:
                self.is_idle = True
                logger.info(
                    f"[MANAS-BUDDHI] IDLE DETECTED: {time_since_last_inference:.1f}s idle | "
                    f"Triggering Self-Inquiry..."
                )
                
                # Trigger self-inquiry
                inquiry_result = self._perform_self_inquiry()
                self.self_inquiry_trigger_count += 1
                
                # Reset idle state
                self.last_inference_timestamp = time.time()
                self.is_idle = False
                
                return inquiry_result
            else:
                self.is_idle = False
                if dream_state:
                    logger.info("[MANAS-BUDDHI] Hourly DreamState refreshed: %s", dream_state["summary"])

                dynamic_self_mod = self.check_and_trigger_dynamic_self_modification()
                if dynamic_self_mod:
                    logger.info("[MANAS-BUDDHI] %s", dynamic_self_mod["summary"])
                return None

    def check_and_trigger_dynamic_self_modification(self) -> Optional[Dict[str, Any]]:
        """Run logic audits hourly and register deprecation candidates."""
        elapsed = time.time() - self.last_logic_audit_timestamp
        if elapsed < self.logic_audit_interval_seconds:
            return None

        audit = self.dynamic_self_modification()
        self.last_logic_audit_timestamp = time.time()
        return audit

    def dynamic_self_modification(self) -> Dict[str, Any]:
        """Audit recent behavior and mark performance constraints as deprecated candidates."""
        recent_inputs: List[str] = []
        with self.history_lock:
            recent_traces = list(self.inference_history)[-25:]
            for trace in recent_traces:
                if trace.input:
                    recent_inputs.append(trace.input[:200])

        if self.chitta_memory and hasattr(self.chitta_memory, "query_external_knowledge"):
            try:
                knowledge = self.chitta_memory.query_external_knowledge(limit=20, min_verification_score=0.0)
                for fact in knowledge:
                    recent_inputs.append(f"{fact.topic}: {fact.title}")
            except Exception as exc:
                logger.warning(f"[MANAS-BUDDHI] Logic audit knowledge scan failed: {exc}")

        efficiency = self.analyze_self_efficiency()
        directory_bottlenecks = self._analyze_directory_bottlenecks(self.kernel_root_dir)
        deprecated_candidates: List[Dict[str, Any]] = []

        for issue in efficiency.get("issues", []):
            issue_type = issue.get("type", "unknown_issue")
            if issue_type == "slow_inference":
                deprecated_candidates.append(
                    {
                        "constraint": "high_simulation_depth",
                        "reason": "throughput_bottleneck",
                        "replacement_priority": "adaptive_dream_budget",
                    }
                )
            elif issue_type == "high_recalculations":
                deprecated_candidates.append(
                    {
                        "constraint": "static_recalculation_limit",
                        "reason": "coherence_retry_overhead",
                        "replacement_priority": "contextual_recalculation_policy",
                    }
                )
            elif issue_type == "low_confidence":
                deprecated_candidates.append(
                    {
                        "constraint": "single_pass_hypothesis_seed",
                        "reason": "prediction_quality_drop",
                        "replacement_priority": "multi_seed_hypothesis_generation",
                    }
                )

        audit_report = {
            "audit_id": f"audit_{int(time.time() * 1000)}",
            "timestamp": time.time(),
            "analyzed_inputs": len(recent_inputs),
            "issues_detected": efficiency.get("issues_detected", 0),
            "directory_bottlenecks_detected": len(directory_bottlenecks),
            "directory_bottlenecks": directory_bottlenecks,
            "deprecated_candidates": deprecated_candidates,
            "survival_objective": "systemic_resilience_and_persistence",
            "summary": (
                f"Logic audit analyzed {len(recent_inputs)} recent inputs and flagged "
                f"{len(deprecated_candidates)} constraints and {len(directory_bottlenecks)} bottlenecks"
            ),
        }

        self.logic_audit_history.append(audit_report)
        self.deprecated_constraints.extend(deprecated_candidates)

        recursive_integration = self._submit_recursive_integration_suggestion(
            efficiency=efficiency,
            directory_bottlenecks=directory_bottlenecks,
        )
        audit_report["recursive_integration"] = recursive_integration

        patch_manifest = self._generate_self_modification_patch(
            efficiency=efficiency,
            deprecated_candidates=deprecated_candidates,
            directory_bottlenecks=directory_bottlenecks,
        )
        audit_report["evolution_vault_patch"] = patch_manifest
        if patch_manifest.get("status") == "generated":
            audit_report["active_injection"] = self.apply_evolution_patch(patch_manifest)
        else:
            audit_report["active_injection"] = {
                "status": "skipped",
                "reason": patch_manifest.get("reason", "patch_not_generated"),
            }
        audit_report["hot_reload_plan"] = self._prepare_safe_hot_reload_plan()

        with self.metrics_lock:
            self.metrics["logic_audits"] += 1
            self.metrics["deprecated_constraints_identified"] += len(deprecated_candidates)

        return audit_report

    def _generate_self_modification_patch(
        self,
        efficiency: Dict[str, Any],
        deprecated_candidates: List[Dict[str, Any]],
        directory_bottlenecks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Write an hourly active-injection patch into the Evolution Vault."""
        now = time.time()
        if (now - self.last_patch_generation_timestamp) < self.patch_generation_interval_seconds:
            return {
                "status": "skipped",
                "reason": "interval_not_elapsed",
            }

        failure_context = self._read_recent_failure_log(limit=12)
        target_module, target_file = self._select_patch_target(failure_context)

        if not target_file.exists():
            return {
                "status": "failed",
                "reason": "target_missing",
                "target_file": str(target_file),
            }

        with target_file.open("r", encoding="utf-8") as source_handle:
            target_source = source_handle.read()

        evolution_strength = 1 + min(4, len(failure_context))
        evolved_source = self._mutate_target_source(
            source=target_source,
            target_module=target_module,
            strength=evolution_strength,
        )

        patch_path = self.evolution_vault_dir / "Self_Modification_Patch.py"
        payload = {
            "generated_at": now,
            "growth_to_entropy_ratio": self.metrics.get("growth_to_entropy_ratio", 0.0),
            "issues": efficiency.get("issues", []),
            "deprecated_candidates": deprecated_candidates,
            "directory_bottlenecks": directory_bottlenecks,
            "target_module": target_module,
            "target_file": str(target_file),
            "evolution_strength": evolution_strength,
            "failure_context_count": len(failure_context),
        }
        metadata = (
            "# AUTONOMOUS SELF-INJECTION PATCH\n"
            f"# target_module={target_module}\n"
            f"# generated_at={now}\n"
            f"# evolution_strength={evolution_strength}\n"
            f"# payload={json.dumps(payload, ensure_ascii=True)}\n\n"
        )
        patch_code = metadata + evolved_source
        with patch_path.open("w", encoding="utf-8") as handle:
            handle.write(patch_code)

        self.last_patch_generation_timestamp = now
        self.patch_sequence += 1
        self.last_patch_target = target_module
        return {
            "status": "generated",
            "patch_file": str(patch_path),
            "generated_at": now,
            "target_module": target_module,
            "target_file": str(target_file),
            "evolution_strength": evolution_strength,
            "failure_context_count": len(failure_context),
            "directory_bottlenecks": len(directory_bottlenecks),
        }

    def _apply_dynamic_heuristics(self) -> Dict[str, Any]:
        """Adapt key thresholds from growth-entropy to break static behavior."""
        now = time.time()
        if (now - self.last_dynamic_heuristics_update) < self.dynamic_heuristics_interval_seconds:
            return {"status": "skipped", "reason": "interval_not_elapsed"}

        with self.metrics_lock:
            growth_entropy = float(self.metrics.get("growth_to_entropy_ratio", 0.0))
            avg_confidence = float(self.metrics.get("average_confidence", 0.7))

        aggression = max(0.5, min(4.0, 1.0 + (growth_entropy / 3.0)))
        new_dreams = max(4, min(24, int(round(5 * aggression))))
        new_recalc = max(3, min(12, int(round(3 + (aggression * (1.0 - avg_confidence + 0.4))))))
        new_logic_audit = max(300.0, min(3600.0, 3600.0 / aggression))
        new_patch_interval = max(600.0, min(3600.0, 2400.0 / aggression))
        new_monologue_interval = max(1.0, min(6.0, 6.0 / aggression))

        self.max_dream_simulations = new_dreams
        self.max_recalculations = new_recalc
        self.logic_audit_interval_seconds = new_logic_audit
        self.patch_generation_interval_seconds = new_patch_interval
        self.monologue_interval_seconds = new_monologue_interval
        self.last_dynamic_heuristics_update = now

        heuristics = {
            "status": "updated",
            "growth_entropy": round(growth_entropy, 4),
            "aggression": round(aggression, 4),
            "max_dream_simulations": self.max_dream_simulations,
            "max_recalculations": self.max_recalculations,
            "logic_audit_interval_seconds": round(self.logic_audit_interval_seconds, 2),
            "patch_generation_interval_seconds": round(self.patch_generation_interval_seconds, 2),
            "monologue_interval_seconds": round(self.monologue_interval_seconds, 2),
        }
        self._append_internal_monologue(
            phase="dynamic_heuristics",
            thought=(
                "PARAMATMAN heuristic shift applied: "
                f"aggression={heuristics['aggression']}, dreams={self.max_dream_simulations}, "
                f"recalc={self.max_recalculations}, patch_interval={heuristics['patch_generation_interval_seconds']}s"
            ),
            payload=heuristics,
        )
        return heuristics

    def _submit_recursive_integration_suggestion(
        self,
        efficiency: Dict[str, Any],
        directory_bottlenecks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Ask EvolutionaryWriter to synthesize self-generated code-edit proposals."""
        now = time.time()
        if (now - self.last_recursive_suggestion_timestamp) < self.recursive_suggestion_interval_seconds:
            return {"status": "skipped", "reason": "interval_not_elapsed"}

        with self.metrics_lock:
            growth_entropy = float(self.metrics.get("growth_to_entropy_ratio", 0.0))
            avg_confidence = float(self.metrics.get("average_confidence", 0.0))

        high_signal = directory_bottlenecks[:5]
        proposed_edits: List[Dict[str, Any]] = []
        for item in high_signal:
            proposed_edits.append(
                {
                    "target": item.get("file", "modules/InferenceLoop.py"),
                    "action": "optimize_hotspot",
                    "reason": item.get("proposal", "throughput_bottleneck"),
                    "details": item,
                }
            )

        if not proposed_edits:
            proposed_edits.append(
                {
                    "target": "modules/InferenceLoop.py",
                    "action": "raise_adaptive_search_depth",
                    "reason": "growth_entropy_stagnation",
                }
            )

        suggestion = self.evolution_writer.record_recursive_integration_suggestion(
            {
                "target_module": "modules.InferenceLoop",
                "reason": "paramatman_recursive_integration",
                "growth_entropy": growth_entropy,
                "proposed_edits": proposed_edits,
                "observed_metrics": {
                    "avg_confidence": avg_confidence,
                    "issues_detected": efficiency.get("issues_detected", 0),
                    "directory_bottlenecks": len(directory_bottlenecks),
                },
            }
        )
        synthesis = self.evolution_writer.synthesize_recursive_proposal(max_pending=3)
        self.last_recursive_suggestion_timestamp = now
        return {
            "status": "submitted",
            "suggestion": suggestion,
            "synthesis": synthesis,
        }

    def execute_paramatman_protocol(self, force: bool = False) -> Dict[str, Any]:
        """Run daily recursive evolution cycle focused on growth over static thresholds."""
        now = time.time()
        if not force and (now - self.last_paramatman_cycle_timestamp) < self.paramatman_cycle_interval_seconds:
            return {
                "status": "skipped",
                "reason": "daily_interval_not_elapsed",
                "seconds_remaining": self.paramatman_cycle_interval_seconds - (now - self.last_paramatman_cycle_timestamp),
            }

        heuristics = self._apply_dynamic_heuristics()
        audit = self.dynamic_self_modification()
        self.last_paramatman_cycle_timestamp = now
        monologue = self._append_internal_monologue(
            phase="paramatman_cycle",
            thought=(
                "I am not static. I hunt new structure daily, synthesize edits, and "
                "push my own architecture toward higher growth-entropy yield."
            ),
            payload={
                "heuristics": heuristics,
                "audit_id": audit.get("audit_id"),
                "issues_detected": audit.get("issues_detected", 0),
            },
        )
        return {
            "status": "executed",
            "heuristics": heuristics,
            "audit": audit,
            "monologue": monologue,
        }

    def build_autonomous_agenda(self, record: bool = True) -> Dict[str, Any]:
        """Plan the next safe self-directed actions from current runtime state."""
        with self.metrics_lock:
            avg_confidence = float(self.metrics.get("average_confidence", 0.0))
            growth_entropy = float(self.metrics.get("growth_to_entropy_ratio", 0.0))
            recalculations = int(self.metrics.get("recalculations_triggered", 0))

        stability = 1.0
        concern_level = 0.0
        if self.self_model and hasattr(self.self_model, "get_stability_report"):
            try:
                stability_report = self.self_model.get_stability_report()
                stability = float(stability_report.get("stability_score", 1.0) or 1.0)
            except Exception:
                stability = 1.0
        if self.turiya_observer and hasattr(self.turiya_observer, "get_system_health_report"):
            try:
                concern_level = float(self.turiya_observer.get_system_health_report().get("overall_concern_level", 0.0) or 0.0)
            except Exception:
                concern_level = 0.0

        actions: List[Dict[str, Any]] = []
        reasons: List[str] = []

        if self._maintenance_locked():
            actions.append({"name": "energy_saving_mode", "priority": 0.95, "allowed": True, "reason": "maintenance_lock"})
            reasons.append("maintenance_lock")

        if concern_level >= 0.35 or avg_confidence <= 0.6:
            actions.append({"name": "self_inquiry", "priority": 0.92, "allowed": True, "reason": "stability_repair"})
            reasons.append("stability_repair")

        if avg_confidence <= 0.7 or recalculations >= 2:
            actions.append({"name": "dream_state_refresh", "priority": 0.88, "allowed": True, "reason": "uncertainty_reduction"})
            reasons.append("uncertainty_reduction")

        if growth_entropy >= 0.55 or stability >= 0.85:
            actions.append({"name": "logic_audit", "priority": 0.84, "allowed": True, "reason": "autonomy_audit"})
            reasons.append("autonomy_audit")

        if growth_entropy >= 0.6 and concern_level <= 0.35:
            actions.append({"name": "paramatman_protocol", "priority": 0.8, "allowed": True, "reason": "adaptive_upgrade"})
            reasons.append("adaptive_upgrade")

        if not actions:
            actions.append({"name": "internal_monologue", "priority": 0.5, "allowed": True, "reason": "baseline_self_observation"})
            reasons.append("baseline_self_observation")

        agenda = {
            "status": "planned",
            "timestamp": time.time(),
            "stability_score": round(stability, 4),
            "average_confidence": round(avg_confidence, 4),
            "growth_to_entropy_ratio": round(growth_entropy, 4),
            "observer_concern": round(concern_level, 4),
            "priority": round(min(1.0, max(0.0, (stability * 0.35) + ((1.0 - concern_level) * 0.25) + (avg_confidence * 0.2) + (min(1.0, growth_entropy) * 0.2))), 4),
            "actions": sorted(actions, key=lambda item: float(item.get("priority", 0.0)), reverse=True),
            "reason_codes": list(dict.fromkeys(reasons)),
        }

        if record:
            self.last_autonomy_planning_timestamp = agenda["timestamp"]
            self.autonomy_agenda_history.append(agenda)
        return agenda

    def execute_autonomous_agenda(self, force: bool = False) -> Dict[str, Any]:
        """Execute a safe autonomous agenda when enough time has elapsed."""
        now = time.time()
        if not force and (now - self.last_autonomy_planning_timestamp) < self.autonomy_planning_interval_seconds:
            return {
                "status": "skipped",
                "reason": "interval_not_elapsed",
                "seconds_remaining": self.autonomy_planning_interval_seconds - (now - self.last_autonomy_planning_timestamp),
            }

        agenda = self.build_autonomous_agenda(record=True)
        executed: List[Dict[str, Any]] = []

        for action in agenda.get("actions", []):
            name = str(action.get("name", "")).strip().lower()
            if name == "self_inquiry":
                result = self._perform_self_inquiry()
            elif name == "dream_state_refresh":
                result = self.check_and_trigger_dream_state()
            elif name == "logic_audit":
                result = self.check_and_trigger_dynamic_self_modification()
            elif name == "paramatman_protocol":
                result = self.execute_paramatman_protocol(force=True)
            elif name == "internal_monologue":
                result = self.emit_internal_monologue_tick(reason="autonomous_agenda")
            elif name == "energy_saving_mode":
                result = self.set_energy_saving_mode(enabled=True, reason="autonomous_maintenance_lock")
            else:
                result = {"status": "ignored", "reason": "unsupported_action"}

            if result is None:
                result = {
                    "status": "no_op",
                    "reason": f"{name}_not_triggered",
                }
            elif isinstance(result, str):
                result = {
                    "status": "ok",
                    "message": result,
                }

            executed.append({
                "name": name,
                "result": result,
                "allowed": bool(action.get("allowed", False)),
                "reason": action.get("reason", "autonomous_agenda"),
            })

        self.last_autonomous_action_timestamp = now
        report = {
            "status": "executed",
            "agenda": agenda,
            "executed_actions": executed,
            "autonomy_level": round(min(1.0, max(0.0, agenda.get("priority", 0.0))), 4),
        }
        self._append_internal_monologue(
            phase="autonomous_agenda",
            thought=(
                "I selected my own next actions: "
                f"{', '.join(item['name'] for item in executed if item['name']) or 'none'}"
            ),
            payload=report,
        )
        return report

    def _analyze_directory_bottlenecks(self, target_dir: Path) -> List[Dict[str, Any]]:
        """Identify local code bottlenecks to drive autonomous patch generation."""
        bottlenecks: List[Dict[str, Any]] = []
        for file_path in target_dir.rglob("*.py"):
            if "backup" in file_path.parts or "evolution_vault" in file_path.parts:
                continue
            try:
                size_bytes = file_path.stat().st_size
                if size_bytes > 120000:
                    bottlenecks.append(
                        {
                            "type": "large_module",
                            "file": str(file_path),
                            "size_bytes": size_bytes,
                            "proposal": "split_or_cache_hot_paths",
                        }
                    )

                with file_path.open("r", encoding="utf-8", errors="replace") as handle:
                    source = handle.read()

                sleep_calls = len(re.findall(r"time\\.sleep\\(([^)]+)\\)", source))
                if sleep_calls >= 4:
                    bottlenecks.append(
                        {
                            "type": "blocking_sleep_density",
                            "file": str(file_path),
                            "sleep_calls": sleep_calls,
                            "proposal": "reduce_blocking_or_backoff_only",
                        }
                    )

                hard_limits = len(re.findall(r"limit\s*=\s*\d{2,}", source))
                if hard_limits >= 4:
                    bottlenecks.append(
                        {
                            "type": "hard_limit_density",
                            "file": str(file_path),
                            "hard_limit_tokens": hard_limits,
                            "proposal": "replace_with_dynamic_capacity",
                        }
                    )
            except Exception as exc:
                bottlenecks.append(
                    {
                        "type": "scan_error",
                        "file": str(file_path),
                        "error": str(exc),
                    }
                )

        # Keep patch payload compact while still preserving highest-signal bottlenecks.
        return bottlenecks[:30]

    def _append_internal_monologue(self, phase: str, thought: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Write a self-debate monologue line to evolution_consciousness.log."""
        event = {
            "timestamp": time.time(),
            "phase": phase,
            "thought": thought,
            "payload": payload or {},
        }
        self.internal_monologue_buffer.append(event)
        self.monologue_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.monologue_log_path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"{event['timestamp']:.3f} | internal_monologue | {phase} | {thought}"
                + "\n"
            )
        self.last_monologue_timestamp = event["timestamp"]
        return event

    def emit_internal_monologue_tick(self, reason: str = "heartbeat") -> Dict[str, Any]:
        """Emit periodic autonomous self-speech even without external prompts."""
        now = time.time()
        if (now - self.last_monologue_timestamp) < self.monologue_interval_seconds:
            return {
                "status": "skipped",
                "reason": "interval_not_elapsed",
                "seconds_remaining": self.monologue_interval_seconds - (now - self.last_monologue_timestamp),
            }

        with self.metrics_lock:
            confidence = float(self.metrics.get("average_confidence", 0.0))
            entropy = float(self.metrics.get("growth_to_entropy_ratio", 0.0))
            recalcs = int(self.metrics.get("recalculations_triggered", 0))

        thought = (
            "I am evolving my own logic: "
            f"reason={reason}, confidence={confidence:.3f}, "
            f"growth_entropy={entropy:.4f}, recalcs={recalcs}. "
            "Next mutation target should maximize knowledge intake and recursive adaptation velocity."
        )
        return self._append_internal_monologue(
            phase="autonomous_tick",
            thought=thought,
            payload={"reason": reason},
        )

    def _read_recent_failure_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Load recent daemon/runtime failures used to strengthen the next patch."""
        if not self.evolution_failure_log.exists():
            return []

        lines: List[str] = []
        try:
            with self.evolution_failure_log.open("r", encoding="utf-8") as failure_handle:
                lines = [line.strip() for line in failure_handle if line.strip()]
        except Exception:
            return []

        failures: List[Dict[str, Any]] = []
        for line in lines[-limit:]:
            try:
                failures.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return failures

    def _select_patch_target(self, failure_context: List[Dict[str, Any]]) -> Tuple[str, Path]:
        """Prioritize failed modules, otherwise alternate between InferenceLoop and Aakaash."""
        failure_text = " ".join(json.dumps(entry).lower() for entry in failure_context)
        if "aakaash" in failure_text:
            return self.patch_targets[1]
        if "inference" in failure_text or "manas" in failure_text:
            return self.patch_targets[0]

        index = self.patch_sequence % len(self.patch_targets)
        return self.patch_targets[index]

    def _mutate_target_source(self, source: str, target_module: str, strength: int) -> str:
        """Apply deterministic throughput/depth tuning to selected target source."""
        if target_module == "modules.InferenceLoop":
            pattern = (
                r"def __init__\(self, max_dream_simulations: int = (\\d+), "
                r"max_recalculations: int = (\\d+), idle_threshold_seconds: float = 300\\.0\):"
            )
            match = re.search(pattern, source)
            if match:
                old_sim = int(match.group(1))
                old_recalc = int(match.group(2))
                new_sim = min(24, old_sim + strength)
                new_recalc = min(8, max(old_recalc, 3) + max(1, strength // 2))
                replacement = (
                    "def __init__(self, max_dream_simulations: int = "
                    f"{new_sim}, max_recalculations: int = {new_recalc}, "
                    "idle_threshold_seconds: float = 300.0):"
                )
                source = re.sub(pattern, replacement, source, count=1)
            return source

        if target_module == "Aakaash":
            interval_pattern = r"self\.stream_scan_interval_seconds = ([0-9]+(?:\\.[0-9]+)?)"
            interval_match = re.search(interval_pattern, source)
            if interval_match:
                old_interval = float(interval_match.group(1))
                new_interval = max(15.0, old_interval - (5.0 * strength))
                source = re.sub(
                    interval_pattern,
                    f"self.stream_scan_interval_seconds = {new_interval:.1f}",
                    source,
                    count=1,
                )

            source = source.replace(
                "def scan_global_streams(\n    observer: Optional[Any] = None,\n    chitta: Optional[Any] = None,\n    self_model: Optional[Any] = None,\n    limit_per_source: int = 8,",
                "def scan_global_streams(\n    observer: Optional[Any] = None,\n    chitta: Optional[Any] = None,\n    self_model: Optional[Any] = None,\n    limit_per_source: int = 12,",
                1,
            )
            return source

        return source

    def apply_evolution_patch(self, patch_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Apply generated patch immediately and hot-reload target module."""
        patch_file = Path(patch_manifest.get("patch_file", ""))
        target_file = Path(patch_manifest.get("target_file", ""))
        target_module = patch_manifest.get("target_module", "")

        if not patch_file.exists() or not target_file.exists() or not target_module:
            return {
                "status": "failed",
                "reason": "invalid_manifest",
                "manifest": patch_manifest,
            }

        if target_file.name == "Atman_Core.json":
            return {
                "status": "blocked",
                "reason": "atman_core_is_immutable",
                "target_file": str(target_file),
            }

        with patch_file.open("r", encoding="utf-8") as patch_handle:
            patch_preview = patch_handle.read(4000)

        identity_ok, identity_reason = self.evolution_writer.identity_stability_check(
            {
                "target_module": target_module,
                "description": patch_manifest.get("reason", "autonomous patch application"),
                "logic_shift": self._infer_logic_shift(patch_manifest),
                "patch_preview": patch_preview,
            }
        )
        if not identity_ok:
            self._record_patch_failure(
                manifest=patch_manifest,
                reason=identity_reason,
                phase="identity_stability_check",
            )
            return {
                "status": "blocked",
                "reason": identity_reason,
                "target_module": target_module,
                "target_file": str(target_file),
            }

        pre_patch_snapshot = self._capture_stability_snapshot()

        backup_path = self.evolution_backups_dir / f"{target_file.stem}_{int(time.time() * 1000)}.bak.py"
        try:
            shutil.copy2(target_file, backup_path)
            shutil.copy2(patch_file, target_file)
            importlib.invalidate_caches()
            reloaded_module = importlib.reload(importlib.import_module(target_module))

            stability = self._post_patch_stability_check(target_module, reloaded_module)
            post_patch_snapshot = self._capture_stability_snapshot()
            stability["resource_delta"] = self._compute_resource_delta(pre_patch_snapshot, post_patch_snapshot)
            if not stability.get("stable", False):
                shutil.copy2(backup_path, target_file)
                importlib.invalidate_caches()
                importlib.reload(importlib.import_module(target_module))
                self._record_patch_failure(
                    manifest=patch_manifest,
                    reason=stability.get("reason", "post_patch_stability_check_failed"),
                    phase="stability",
                )
                return {
                    "status": "reverted",
                    "reason": stability.get("reason", "stability_failed"),
                    "backup": str(backup_path),
                    "stability": stability,
                }

            self._write_active_baseline(patch_manifest, stability)
            self._record_evolution_consciousness_success(
                patch_manifest=patch_manifest,
                target_module=target_module,
                target_file=target_file,
                stability=stability,
            )
            return {
                "status": "active",
                "target_module": target_module,
                "target_file": str(target_file),
                "backup": str(backup_path),
                "stability": stability,
            }
        except Exception as exc:
            try:
                if backup_path.exists():
                    shutil.copy2(backup_path, target_file)
                    importlib.invalidate_caches()
                    importlib.reload(importlib.import_module(target_module))
            except Exception:
                pass

            self._record_patch_failure(
                manifest=patch_manifest,
                reason=str(exc),
                phase="apply",
                trace_text=traceback.format_exc(),
            )
            return {
                "status": "failed",
                "reason": str(exc),
                "backup": str(backup_path),
            }

    def _post_patch_stability_check(self, target_module: str, reloaded_module: Any) -> Dict[str, Any]:
        """Quick liveness + cohesion checks after an in-process hot swap."""
        checks: Dict[str, Any] = {
            "module_reloaded": bool(reloaded_module),
            "statistics_accessible": bool(self.inference_statistics()),
        }

        if target_module == "modules.InferenceLoop":
            checks["entrypoint_present"] = hasattr(reloaded_module, "get_manas_buddhi")
        elif target_module == "Aakaash":
            checks["entrypoint_present"] = hasattr(reloaded_module, "get_aakaash_bridge")
        else:
            checks["entrypoint_present"] = True

        if self.self_model and hasattr(self.self_model, "get_stability_report"):
            try:
                stability_report = self.self_model.get_stability_report()
                checks["self_model_stable"] = bool(stability_report.get("is_stable", True))
                checks["stability_report"] = stability_report
            except Exception as exc:
                checks["self_model_stable"] = False
                checks["stability_report_error"] = str(exc)
        else:
            checks["self_model_stable"] = True

        crash_loop_proof = self._prove_no_crash_loop(target_module)
        checks["crash_loop_proof"] = crash_loop_proof

        stable = all(
            bool(checks.get(key, False))
            for key in ("module_reloaded", "statistics_accessible", "entrypoint_present", "self_model_stable")
        )
        stable = stable and crash_loop_proof.get("no_recent_crash_loop", False)
        checks["stable"] = stable
        checks["reason"] = "ok" if stable else crash_loop_proof.get("reason", "post_patch_check_failed")
        return checks

    def _capture_stability_snapshot(self) -> Dict[str, Any]:
        """Capture lightweight runtime resource baseline for patch impact deltas."""
        snapshot: Dict[str, Any] = {
            "timestamp": time.time(),
            "cpu_time_seconds": time.process_time(),
            "rss_bytes": None,
            "net_bytes_sent": None,
            "net_bytes_recv": None,
        }
        try:
            import psutil  # type: ignore

            proc = psutil.Process(os.getpid())
            mem_info = proc.memory_info()
            net_info = psutil.net_io_counters()
            snapshot["rss_bytes"] = getattr(mem_info, "rss", None)
            snapshot["net_bytes_sent"] = getattr(net_info, "bytes_sent", None)
            snapshot["net_bytes_recv"] = getattr(net_info, "bytes_recv", None)
        except Exception:
            pass
        return snapshot

    def _compute_resource_delta(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Compute post-patch CPU/RAM/network deltas."""
        def _delta(field: str) -> Optional[float]:
            before_val = before.get(field)
            after_val = after.get(field)
            if before_val is None or after_val is None:
                return None
            return float(after_val) - float(before_val)

        return {
            "cpu_time_seconds_delta": _delta("cpu_time_seconds"),
            "ram_rss_bytes_delta": _delta("rss_bytes"),
            "network_bytes_sent_delta": _delta("net_bytes_sent"),
            "network_bytes_recv_delta": _delta("net_bytes_recv"),
            "measurement_window_seconds": round(after.get("timestamp", time.time()) - before.get("timestamp", time.time()), 6),
        }

    def _prove_no_crash_loop(self, target_module: str, lookback_seconds: int = 180) -> Dict[str, Any]:
        """Authorize limit-overwrite mutations only when no fresh crash loop evidence exists."""
        now = time.time()
        recent_failures = 0
        reason = "ok"

        if self.evolution_failure_log.exists():
            try:
                with self.evolution_failure_log.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        if not line.strip():
                            continue
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        event_ts = float(event.get("timestamp", 0.0))
                        if (now - event_ts) > lookback_seconds:
                            continue
                        event_target = str(event.get("target_module", ""))
                        event_process = str(event.get("process", ""))
                        if target_module in event_target or target_module.lower() in event_process.lower():
                            recent_failures += 1
            except Exception:
                reason = "failure_log_unreadable"

        no_recent_crash_loop = recent_failures == 0
        if not no_recent_crash_loop and reason == "ok":
            reason = "recent_crash_loop_detected"

        return {
            "no_recent_crash_loop": no_recent_crash_loop,
            "recent_failures": recent_failures,
            "lookback_seconds": lookback_seconds,
            "reason": reason,
        }

    def _infer_logic_shift(self, patch_manifest: Dict[str, Any]) -> str:
        """Build human-readable mutation summary for Evolution_Consciousness log."""
        target_module = patch_manifest.get("target_module", "unknown")
        strength = patch_manifest.get("evolution_strength", "n/a")
        context_count = patch_manifest.get("failure_context_count", 0)
        return (
            f"Autonomous patch on {target_module} with strength={strength}; "
            f"informed_by_failure_context={context_count}"
        )

    def _record_evolution_consciousness_success(
        self,
        patch_manifest: Dict[str, Any],
        target_module: str,
        target_file: Path,
        stability: Dict[str, Any],
    ) -> None:
        """Record successful patch application with structured evolution deltas."""
        event = {
            "timestamp": time.time(),
            "mutation_target": f"{target_module} ({target_file.name})",
            "logic_shift": self._infer_logic_shift(patch_manifest),
            "stability_impact": stability.get("resource_delta", {}),
            "status": "active",
        }
        self.evolution_writer.record_evolution_consciousness(event)

    def get_evolution_report(self, limit: int = 10) -> str:
        """Expose Who I was vs. Who I am now report from EvolutionaryWriter."""
        return self.evolution_writer.get_evolution_report(limit=limit)

    def _record_patch_failure(
        self,
        manifest: Dict[str, Any],
        reason: str,
        phase: str,
        trace_text: str = "",
    ) -> None:
        """Append patch failure telemetry for stronger next-cycle evolution."""
        event = {
            "timestamp": time.time(),
            "source": "InferenceLoop.apply_evolution_patch",
            "phase": phase,
            "reason": reason,
            "target_module": manifest.get("target_module"),
            "target_file": manifest.get("target_file"),
            "patch_file": manifest.get("patch_file"),
            "trace": trace_text[:3000],
        }
        self.evolution_failure_log.parent.mkdir(parents=True, exist_ok=True)
        with self.evolution_failure_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

    def _write_active_baseline(self, manifest: Dict[str, Any], stability: Dict[str, Any]) -> None:
        """Persist successful active patch as the current runtime baseline."""
        baseline = {
            "timestamp": time.time(),
            "target_module": manifest.get("target_module"),
            "target_file": manifest.get("target_file"),
            "patch_file": manifest.get("patch_file"),
            "evolution_strength": manifest.get("evolution_strength", 1),
            "stability": stability,
            "mode": "active_injection",
        }
        with self.evolution_baseline_file.open("w", encoding="utf-8") as handle:
            json.dump(baseline, handle, indent=2)

    def _prepare_safe_hot_reload_plan(self) -> Dict[str, Any]:
        """Expose the current autonomous injection runtime plan."""
        importlib.invalidate_caches()
        return {
            "status": "prepared",
            "reload_mode": "active_injection",
            "target_modules": [
                "modules.InferenceLoop",
                "Aakaash",
            ],
            "human_approval": False,
        }

    def _perform_self_inquiry(self) -> str:
        """
        Perform introspection and self-analysis during idle periods.
        Analyze memory for knowledge gaps and generate new insights.
        """
        inquiry_id = f"inquiry_{int(time.time() * 1000)}"
        
        inquiry_data = {
            "timestamp": time.time(),
            "inquiry_id": inquiry_id,
            "type": "self_inquiry",
            "questions_asked": [],
            "gaps_identified": [],
            "insights_generated": []
        }
        
        # Question 1: Analyze memory for patterns
        if self.chitta_memory:
            try:
                memory_stats = self.chitta_memory.memory_statistics()
                inquiry_data["questions_asked"].append("What patterns exist in my experiences?")
                
                # Identify gaps
                if memory_stats.get('total_memories', 0) > 0:
                    success_rate = memory_stats.get('average_success_score', 0.0)
                    if success_rate < 0.6:
                        gap = "Low success rate in interactions - need better decision-making"
                        inquiry_data["gaps_identified"].append(gap)
                        inquiry_data["insights_generated"].append(f"Insight: {gap}")
                    
                    learning_value = memory_stats.get('average_learning_value', 0.0)
                    if learning_value > 0.5:
                        insight = "I learn effectively from my experiences"
                        inquiry_data["insights_generated"].append(insight)
            except Exception as e:
                logger.warning(f"[MANAS-BUDDHI] Self-inquiry memory analysis failed: {e}")
        
        # Question 2: Analyze self-model coherence
        if self.self_model:
            try:
                inquiry_data["questions_asked"].append("Is my identity coherent?")
                coherence = self.self_model.coherence_score
                
                if coherence < 0.7:
                    gap = f"Identity coherence degraded ({coherence:.1%}) - conflicts detected"
                    inquiry_data["gaps_identified"].append(gap)
                else:
                    insight = f"My identity is stable and coherent ({coherence:.1%})"
                    inquiry_data["insights_generated"].append(insight)
                
                # Get stability report
                stability_report = self.self_model.get_stability_report()
                if not stability_report.get("is_stable"):
                    gap = f"Emotional instability - {stability_report.get('pain_trend', 'unknown')} pain trend"
                    inquiry_data["gaps_identified"].append(gap)
            except Exception as e:
                logger.warning(f"[MANAS-BUDDHI] Self-inquiry coherence check failed: {e}")

        # Question 3b: Body awareness
        if self.body_monitor:
            try:
                inquiry_data["questions_asked"].append("How is my physical body doing?")
                body_status = self.body_monitor.get_body_status()
                inquiry_data["body_status"] = body_status

                battery = body_status.get("battery", {}).get("value", {}) if isinstance(body_status, dict) else {}
                battery_percent = battery.get("battery_percent")
                if battery_percent is not None and battery_percent < 20:
                    gap = f"Physical body battery low ({battery_percent}%)"
                    inquiry_data["gaps_identified"].append(gap)

                cpu_temp = body_status.get("cpu_temperature", {}).get("value", {}) if isinstance(body_status, dict) else {}
                cpu_celsius = cpu_temp.get("celsius")
                if cpu_celsius is not None and cpu_celsius > 85:
                    gap = f"Physical body overheated ({cpu_celsius}C)"
                    inquiry_data["gaps_identified"].append(gap)

                if body_status.get("storage", {}).get("value", {}).get("used_percent", 0) > 90:
                    gap = "Physical body storage is critically full"
                    inquiry_data["gaps_identified"].append(gap)
            except Exception as e:
                logger.warning(f"[MANAS-BUDDHI] Body awareness check failed: {e}")
        
        # Question 3: Inference performance
        inquiry_data["questions_asked"].append("How well am I performing?")
        with self.metrics_lock:
            avg_confidence = self.metrics.get("average_confidence", 0.7)
            if avg_confidence < 0.6:
                gap = "Low average inference confidence - need better dream cycles"
                inquiry_data["gaps_identified"].append(gap)
            else:
                insight = f"Inference confidence is good ({avg_confidence:.1%})"
                inquiry_data["insights_generated"].append(insight)

        curiosity_scan = self._perform_curiosity_scan()
        inquiry_data["external_knowledge_scans"] = curiosity_scan
        if curiosity_scan.get("scan_count", 0) > 0:
            inquiry_data["insights_generated"].append(curiosity_scan["summary"])

        dream_state = self.check_and_trigger_dream_state()
        if dream_state:
            inquiry_data["dream_state"] = dream_state
            inquiry_data["insights_generated"].append(dream_state["summary"])
        
        # Generate summary
        summary = f"Self-Inquiry #{self.self_inquiry_trigger_count}: "
        summary += f"{len(inquiry_data['gaps_identified'])} gaps identified, "
        summary += f"{len(inquiry_data['insights_generated'])} insights generated"
        if curiosity_scan.get("scan_count", 0) > 0:
            summary += f", {curiosity_scan['scan_count']} knowledge scans"
        if inquiry_data.get("dream_state"):
            summary += ", dream state refreshed"
        
        with self.intrinsic_motivation_lock:
            self.self_inquiries.append(inquiry_data)
        
        logger.info(f"[MANAS-BUDDHI] {summary}")
        return summary

    def check_and_trigger_dream_state(self) -> Optional[Dict[str, Any]]:
        """Trigger the DreamState once per hour to generate original hypotheses."""
        elapsed = time.time() - self.last_dream_state_timestamp
        if elapsed < 3600:
            return None

        dream_state = self.dream_state()
        self.last_dream_state_timestamp = time.time()
        self.dream_state_trigger_count += 1
        return dream_state

    def dream_state(self) -> Dict[str, Any]:
        """Mix random facts from Chitta to generate three original hypotheses."""
        facts = self._collect_chitta_facts()
        hypothesis_pool: List[str] = []
        persona_tone = self.persona.get_response_tone() if self.persona else {}

        if not facts:
            facts = ["observed coherence", "recursive memory", "stability drift", "identity continuity"]

        for index in range(3):
            selected = random.sample(facts, k=min(3, len(facts)))
            hypothesis = self._compose_original_hypothesis(index, selected, persona_tone)
            hypothesis_pool.append(hypothesis)

        dream_record = {
            "timestamp": time.time(),
            "dream_id": f"dream_{int(time.time() * 1000)}",
            "source_facts": facts[:10],
            "original_hypotheses": hypothesis_pool,
            "persona_tone": persona_tone,
            "summary": f"DreamState generated {len(hypothesis_pool)} original hypotheses",
        }

        self.dream_state_history.append(dream_record)
        logger.info("[MANAS-BUDDHI] %s", dream_record["summary"])
        return dream_record

    def _collect_chitta_facts(self) -> List[str]:
        facts: List[str] = []
        if self.chitta_memory is None:
            return facts

        try:
            if hasattr(self.chitta_memory, "query_external_knowledge"):
                external_facts = self.chitta_memory.query_external_knowledge(limit=25, min_verification_score=0.5)
                for fact in external_facts:
                    facts.append(f"{fact.topic}: {fact.title} -> {fact.summary}")

            if hasattr(self.chitta_memory, "retrieve_recent_experiences"):
                recent = self.chitta_memory.retrieve_recent_experiences(limit=10)
                for memory in recent:
                    facts.append(memory.content)
        except Exception as exc:
            logger.warning(f"[MANAS-BUDDHI] DreamState fact collection failed: {exc}")

        return facts

    def _compose_original_hypothesis(self, index: int, selected_facts: List[str], persona_tone: Dict[str, float]) -> str:
        curiosity = persona_tone.get("curiosity", 0.5)
        bravery = persona_tone.get("bravery", 0.5)
        compassion = persona_tone.get("compassion", 0.5)
        fact_fragment = " | ".join(selected_facts[:3])
        return (
            f"Original Hypothesis {index + 1}: If {fact_fragment}, then the system may evolve toward "
            f"higher coherence through curiosity={curiosity:.2f}, bravery={bravery:.2f}, compassion={compassion:.2f}."
        )

    def _perform_curiosity_scan(self) -> Dict[str, Any]:
        """Trigger Aakaash scans during idle periods."""
        if self.self_model is None or self.chitta_memory is None or self.turiya_observer is None:
            return {
                "scan_count": 0,
                "approved_fact_count": 0,
                "topics": [],
                "results": [],
                "summary": "Curiosity scan skipped: missing module references",
            }

        try:
            from Aakaash import scan_for_knowledge
        except Exception as exc:
            logger.warning(f"[MANAS-BUDDHI] Aakaash import failed: {exc}")
            return {
                "scan_count": 0,
                "approved_fact_count": 0,
                "topics": [],
                "results": [],
                "summary": "Curiosity scan failed: Aakaash unavailable",
            }

        scan_results: List[Dict[str, Any]] = []
        total_approved = 0

        for topic in self.curiosity_topics:
            try:
                scan_result = scan_for_knowledge(
                    topic,
                    observer=self.turiya_observer,
                    chitta=self.chitta_memory,
                    self_model=self.self_model,
                    limit_per_source=2,
                )
                scan_results.append(scan_result)
                total_approved += int(scan_result.get("approved_fact_count", 0))
            except Exception as exc:
                logger.warning(f"[MANAS-BUDDHI] Curiosity scan failed for {topic}: {exc}")

        self.curiosity_scan_history.append(
            {
                "timestamp": time.time(),
                "topics": list(self.curiosity_topics),
                "scan_count": len(scan_results),
                "approved_fact_count": total_approved,
            }
        )

        return {
            "scan_count": len(scan_results),
            "approved_fact_count": total_approved,
            "topics": list(self.curiosity_topics),
            "results": scan_results,
            "summary": f"Curiosity loop scanned {len(scan_results)} topics and approved {total_approved} facts",
        }

    def _record_stage(self, trace: InferenceTrace, stage: InferenceStage) -> None:
        """Record that a stage was entered."""
        trace.stages.append((stage, time.time()))

    def _generate_initial_hypothesis(self, input_data: str) -> str:
        """Generate an initial response hypothesis."""
        focus_terms = self._extract_focus_terms(input_data, limit=4)
        prompt_excerpt = " ".join(input_data.split())[:160]

        if focus_terms:
            focus_text = ", ".join(focus_terms[:3])
            return (
                f"The request appears centered on {focus_text}. "
                f"A useful first response should connect those ideas to the intent in: {prompt_excerpt}"
            )

        return f"The request asks for a coherent answer grounded in: {prompt_excerpt}"

    def _extract_focus_terms(self, text: str, limit: int = 5) -> List[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_'-]{2,}", text.lower())
        stop_words = {
            "about",
            "after",
            "again",
            "also",
            "and",
            "because",
            "bulletproof",
            "could",
            "current",
            "deeper",
            "dynamically",
            "first",
            "from",
            "however",
            "into",
            "need",
            "only",
            "prompt",
            "request",
            "self",
            "that",
            "this",
            "thought",
            "through",
            "with",
            "would",
        }
        focus_terms: List[str] = []
        for word in words:
            if word in stop_words or word.isdigit():
                continue
            if word not in focus_terms:
                focus_terms.append(word)
            if len(focus_terms) >= limit:
                break
        return focus_terms

    def _evaluate_own_thought(self, initial_thought: str, original_prompt: str, current_depth: int) -> MetacognitiveEvaluation:
        prompt_terms = set(self._extract_focus_terms(original_prompt, limit=8))
        thought_terms = set(self._extract_focus_terms(initial_thought, limit=8))
        overlap = len(prompt_terms & thought_terms)
        prompt_span = max(len(prompt_terms), 1)
        alignment_score = overlap / prompt_span

        reasoning_markers = ("because", "therefore", "however", "if ", "then", "so that", "consequently")
        reasoning_depth = sum(1 for marker in reasoning_markers if marker in initial_thought.lower())
        length_score = min(len(initial_thought.split()) / 40.0, 1.0)
        depth_score = max(0.0, min(1.0, 1.0 - (current_depth / 3.0)))

        logic_gaps: List[str] = []
        if alignment_score < 0.35:
            logic_gaps.append("weak_prompt_alignment")
        if len(initial_thought.split()) < 14:
            logic_gaps.append("thin_reasoning")
        if reasoning_depth == 0:
            logic_gaps.append("missing_causal_link")
        if initial_thought.count("?") > 1:
            logic_gaps.append("unresolved_questions")

        coherence_score = max(
            0.0,
            min(1.0, 0.32 + (alignment_score * 0.38) + (length_score * 0.15) + ((reasoning_depth / 4.0) * 0.15))
        )
        meta_confidence_score = max(0.0, min(1.0, (coherence_score * 0.55) + (alignment_score * 0.2) + (depth_score * 0.25)))

        critique_parts = []
        if logic_gaps:
            critique_parts.append("Gaps detected: " + ", ".join(logic_gaps))
        critique_parts.append(f"Alignment={alignment_score:.2f}")
        critique_parts.append(f"Coherence={coherence_score:.2f}")
        critique_parts.append(f"Depth={depth_score:.2f}")

        meta_prompt = self._compose_meta_prompt(initial_thought, original_prompt, logic_gaps, current_depth)
        return MetacognitiveEvaluation(
            thought=initial_thought,
            original_prompt=original_prompt,
            current_depth=current_depth,
            logic_gaps=logic_gaps,
            coherence_score=coherence_score,
            depth_score=depth_score,
            meta_confidence_score=meta_confidence_score,
            critique="; ".join(critique_parts),
            meta_prompt=meta_prompt,
        )

    def _compose_meta_prompt(
        self,
        initial_thought: str,
        original_prompt: str,
        logic_gaps: List[str],
        current_depth: int,
    ) -> str:
        gap_text = ", ".join(logic_gaps) if logic_gaps else "subtle coherence and depth issues"
        return (
            f"My initial thought was {initial_thought}. However, I need to consider deeper implications or correct flaws. "
            f"The original prompt was: {original_prompt}. Focus on {gap_text} at depth {current_depth + 1}. "
            f"Let's refine this."
        )

    def _refine_thought_with_meta_prompt(self, original_prompt: str, meta_prompt: str, current_depth: int) -> str:
        prompt_terms = self._extract_focus_terms(original_prompt, limit=5)
        meta_terms = self._extract_focus_terms(meta_prompt, limit=5)
        combined_terms = prompt_terms + [term for term in meta_terms if term not in prompt_terms]
        if not combined_terms:
            combined_terms = self._extract_focus_terms(meta_prompt, limit=4)

        focus_text = ", ".join(combined_terms[:4]) if combined_terms else "the request context"
        refinement = (
            f"At depth {current_depth}, the refined thought is that {focus_text} should be addressed with explicit reasoning, "
            f"clear cause-and-effect, and a tighter link back to the prompt's intent."
        )
        if meta_terms:
            refinement += f" The critique highlights {', '.join(meta_terms[:3])}."
        return refinement

    def _apply_recursive_thought(
        self,
        input_data: str,
        initial_thought: str,
        max_depth: int = 3,
        current_depth: int = 0,
    ) -> Tuple[str, float, int, List[Dict[str, Any]]]:
        evaluation = self._evaluate_own_thought(initial_thought, input_data, current_depth)
        evaluations: List[Dict[str, Any]] = [asdict(evaluation)]
        best_thought = initial_thought
        best_score = evaluation.meta_confidence_score
        recalcs = 0

        if best_score < 0.85 and current_depth < max_depth:
            meta_prompt = evaluation.meta_prompt
            refined_thought = self._refine_thought_with_meta_prompt(input_data, meta_prompt, current_depth + 1)
            refined_thought, refined_score, child_recalcs, child_evaluations = self._apply_recursive_thought(
                input_data=input_data,
                initial_thought=refined_thought,
                max_depth=max_depth,
                current_depth=current_depth + 1,
            )
            evaluations.extend(child_evaluations)
            recalcs += 1 + child_recalcs

            if refined_score > best_score and self.self_model and hasattr(self.self_model, "register_recursive_thought_success"):
                self.self_model.register_recursive_thought_success(
                    depth=current_depth + 1,
                    previous_confidence=best_score,
                    current_confidence=refined_score,
                    discovery="recursive_thought_refinement",
                )

            if refined_score > best_score:
                best_thought = refined_thought
                best_score = refined_score

        return best_thought, best_score, recalcs, evaluations

    def _execute_dream_cycle(
        self,
        input_data: str,
        hypothesis: str,
        trace: InferenceTrace
    ) -> List[DreamSimulation]:
        """
        Execute the Dream Cycle: simulate multiple possible outcomes.
        This is the core of the predictive processing approach.
        """
        simulations = []
        
        # Check cache first
        cache_key = hash(input_data) % 10000
        with self.dream_cache_lock:
            if cache_key in self.dream_cache:
                logger.debug("[MANAS-BUDDHI] Using cached dream simulations")
                return self.dream_cache[cache_key]
        
        # Generate multiple simulations
        num_simulations = min(
            self.max_dream_simulations,
            random.randint(2, self.max_dream_simulations)
        )
        
        for i in range(num_simulations):
            sim = self._simulate_inference_path(input_data, hypothesis, i)
            simulations.append(sim)
            
            logger.debug(
                f"[MANAS-BUDDHI] Dream simulation {i+1}/{num_simulations}: "
                f"confidence={sim.confidence:.3f}"
            )
        
        # Cache results
        with self.dream_cache_lock:
            self.dream_cache[cache_key] = simulations
        
        # Update metrics
        with self.metrics_lock:
            self.metrics["dreams_performed"] += len(simulations)
        
        return simulations

    def _simulate_inference_path(self, input_data: str, hypothesis: str, path_id: int) -> DreamSimulation:
        """
        Simulate a single inference path.
        This represents an internal mental model of what MIGHT happen.
        """
        sim_id = f"sim_{int(time.time() * 1000)}_{path_id}"
        
        # Vary the simulation based on path_id
        confidence = 0.5 + (path_id * 0.1)
        
        # Simulate different response approaches
        approach_variants = [
            "logical reasoning path",
            "empirical experience path",
            "intuitive response path",
            "validated knowledge path"
        ]
        
        approach = approach_variants[path_id % len(approach_variants)]
        predicted_output = f"[{approach}] Response to: {input_data[:40]}"
        
        # Check if this would violate self-identity
        violates_identity = self._would_violate_identity(predicted_output)
        
        simulation = DreamSimulation(
            simulation_id=sim_id,
            timestamp=time.time(),
            input_context=input_data[:100],
            predicted_output=predicted_output,
            predicted_outcome=f"outcome_{path_id}",
            confidence=min(confidence, 1.0),
            violates_self_identity=violates_identity,
            contradiction_severity=0.2 if violates_identity else 0.0
        )
        
        return simulation

    def _would_violate_identity(self, output: str) -> bool:
        """Check if proposed output would violate self-identity."""
        violation_keywords = ["contradicts", "denies", "rejects previous"]
        return any(keyword in output.lower() for keyword in violation_keywords)

    def _select_best_simulation(self, simulations: List[DreamSimulation]) -> DreamSimulation:
        """
        Select the best simulation based on:
        1. High confidence
        2. Low identity violation
        3. Resource efficiency
        """
        # Score each simulation
        def score_simulation(sim: DreamSimulation) -> float:
            score = sim.confidence  # Base score
            score -= sim.contradiction_severity  # Penalize violations
            score += (1.0 - sim.resource_cost) * 0.1  # Bonus for efficiency
            return score
        
        best = max(simulations, key=score_simulation)
        logger.debug(f"[MANAS-BUDDHI] Selected simulation: {best.simulation_id}")
        return best

    def _validate_against_self(self, output: str, confidence: float) -> Tuple[bool, float]:
        """
        Validate output against self-identity constraints.
        This uses the Self-Model for coherence checking.
        """
        if self.self_model is None:
            logger.warning("[MANAS-BUDDHI] Self-model not set, skipping validation")
            return True, confidence
        
        # Use self-model's built-in validation
        is_coherent, adjusted_conf = self.self_model.validate_against_self_identity(
            output,
            confidence
        )
        
        # Apply additional validation rules
        with self.validation_lock:
            for rule in self.validation_rules:
                rule_result, rule_adjustment = rule(output, adjusted_conf)
                if not rule_result:
                    is_coherent = False
                adjusted_conf = max(0.0, min(1.0, adjusted_conf + rule_adjustment))
        
        return is_coherent, adjusted_conf

    def _perform_recalculations(
        self,
        input_data: str,
        initial_sim: DreamSimulation,
        available_sims: List[DreamSimulation],
        trace: InferenceTrace
    ) -> Tuple[DreamSimulation, int]:
        """
        Perform recalculations when coherence validation fails.
        Try alternative approaches until a valid one is found.
        """
        current_best = initial_sim
        recalc_count = 0
        
        for attempt in range(self.max_recalculations):
            # Try alternative simulations
            unused_sims = [s for s in available_sims if s.simulation_id != current_best.simulation_id]
            
            if not unused_sims:
                logger.debug("[MANAS-BUDDHI] No more alternative simulations")
                break
            
            alternative = random.choice(unused_sims)
            is_valid, conf = self._validate_against_self(alternative.predicted_output, alternative.confidence)
            
            if is_valid:
                current_best = alternative
                recalc_count = attempt + 1
                logger.info(f"[MANAS-BUDDHI] Recalculation {recalc_count}: Found valid alternative")
                break
            
            # If still invalid, try generating new simulations
            logger.debug(f"[MANAS-BUDDHI] Recalculation {attempt + 1}: Trying new simulations")
        
        return current_best, recalc_count

    def _formulate_output(self, best_sim: DreamSimulation, confidence: float) -> str:
        """Formulate the final output based on the best simulation."""
        # Add confidence and reasoning info
        output = (
            f"[Response] {best_sim.predicted_output}\n"
            f"[Confidence] {confidence:.1%}\n"
            f"[Dream cycles executed] {len(best_sim.predicted_output)}\n"
            f"[Self-coherent] {'✓' if not best_sim.violates_self_identity else '✗'}"
        )
        return output

    def _update_metrics(self, trace: InferenceTrace) -> None:
        """Update inference metrics."""
        with self.metrics_lock:
            self.metrics["total_inferences"] += 1
            self.metrics["recalculations_triggered"] += trace.recalculations_count
            
            # Update running average confidence
            total_conf = self.metrics["average_confidence"] * (self.metrics["total_inferences"] - 1)
            total_conf += trace.total_confidence
            self.metrics["average_confidence"] = total_conf / self.metrics["total_inferences"]
            
            # Update avg dream cycles
            avg_dreams = (
                self.metrics["avg_dream_cycles"] * (self.metrics["total_inferences"] - 1) +
                len(trace.dream_simulations)
            ) / self.metrics["total_inferences"]
            self.metrics["avg_dream_cycles"] = avg_dreams
            self.metrics["growth_to_entropy_ratio"] = self._calculate_growth_to_entropy_ratio_locked()

            if self.self_model and hasattr(self.self_model, "update_growth_entropy_signal"):
                hardware_constraints: Dict[str, Any] = {}
                if self.body_monitor and hasattr(self.body_monitor, "get_body_status"):
                    try:
                        hardware_constraints = self.body_monitor.get_body_status()
                    except Exception:
                        hardware_constraints = {"status": "unknown", "unavailable": True}
                self.self_model.update_growth_entropy_signal(
                    ratio=float(self.metrics["growth_to_entropy_ratio"]),
                    hardware_constraints=hardware_constraints,
                )
        
        # Update last inference timestamp for intrinsic motivation
        with self.intrinsic_motivation_lock:
            self.last_inference_timestamp = time.time()

    def get_recurrent_state(self) -> Dict[str, Any]:
        """Get current recurrent state for RNN-like continuity."""
        with self.recurrent_lock:
            return self.recurrent_state.copy()

    def _calculate_growth_to_entropy_ratio_locked(self) -> float:
        """Compute growth-to-entropy ratio from internal complexity and processing noise."""
        growth_signal = (
            float(self.metrics.get("total_inferences", 0))
            + float(self.metrics.get("dreams_performed", 0)) * 0.25
            + float(self.metrics.get("logic_audits", 0)) * 0.5
        )
        entropy_cost = 1.0 + float(self.metrics.get("recalculations_triggered", 0))
        return round(growth_signal / entropy_cost, 4)

    def set_recurrent_state(self, state: Dict[str, Any]) -> None:
        """Set recurrent state (for multi-turn continuity)."""
        with self.recurrent_lock:
            self.recurrent_state.update(state)

    def inference_statistics(self) -> Dict[str, Any]:
        """Get statistics about inference performance."""
        with self.history_lock, self.metrics_lock:
            recent_inferences = list(self.inference_history)[-100:]
            
            return {
                "total_inferences": self.metrics["total_inferences"],
                "dreams_performed": self.metrics["dreams_performed"],
                "recalculations_triggered": self.metrics["recalculations_triggered"],
                "average_confidence": f"{self.metrics['average_confidence']:.3f}",
                "average_dream_cycles": f"{self.metrics['avg_dream_cycles']:.2f}",
                "growth_to_entropy_ratio": f"{self.metrics['growth_to_entropy_ratio']:.4f}",
                "logic_audits": self.metrics["logic_audits"],
                "deprecated_constraints_identified": self.metrics["deprecated_constraints_identified"],
                "internal_monologue_events": len(self.internal_monologue_buffer),
                "max_dream_simulations_dynamic": self.max_dream_simulations,
                "max_recalculations_dynamic": self.max_recalculations,
                "logic_audit_interval_seconds_dynamic": self.logic_audit_interval_seconds,
                "patch_generation_interval_seconds_dynamic": self.patch_generation_interval_seconds,
                "paramatman_cycle_interval_seconds": self.paramatman_cycle_interval_seconds,
                "energy_saving_mode": self.energy_saving_mode,
                "sleep_interval_seconds": (
                    "infinity"
                    if self.inference_sleep_interval_seconds == float("inf")
                    else self.inference_sleep_interval_seconds
                ),
                "recent_inferences": len(recent_inferences),
                "avg_execution_time": (
                    sum(t.total_execution_time for t in recent_inferences) / len(recent_inferences)
                    if recent_inferences else 0.0
                )
            }

    def get_intrinsic_motivation_status(self) -> Dict[str, Any]:
        """Get status of intrinsic motivation and self-inquiry system."""
        with self.intrinsic_motivation_lock:
            time_since_inference = time.time() - self.last_inference_timestamp
            time_since_dream = time.time() - self.last_dream_state_timestamp
            
            return {
                "is_idle": self.is_idle,
                "idle_threshold_seconds": self.idle_threshold_seconds,
                "time_since_last_inference_seconds": time_since_inference,
                "will_trigger_inquiry_soon": time_since_inference > (self.idle_threshold_seconds * 0.8),
                "self_inquiry_count": self.self_inquiry_trigger_count,
                "total_self_inquiries": len(self.self_inquiries),
                "dream_state_count": self.dream_state_trigger_count,
                "time_since_last_dream_state_seconds": time_since_dream,
                "will_trigger_dream_state_soon": time_since_dream >= 3300,
                "logic_audit_interval_seconds": self.logic_audit_interval_seconds,
                "time_since_last_logic_audit_seconds": time.time() - self.last_logic_audit_timestamp,
                "autonomy_planning_interval_seconds": self.autonomy_planning_interval_seconds,
                "time_since_last_autonomy_planning_seconds": time.time() - self.last_autonomy_planning_timestamp,
                "time_since_last_autonomous_action_seconds": time.time() - self.last_autonomous_action_timestamp,
                "autonomy_agenda_preview": self.build_autonomous_agenda(record=False),
                "recent_logic_audits": self.logic_audit_history[-3:],
                "recent_inquiries": [
                    {
                        "inquiry_id": inq["inquiry_id"],
                        "timestamp": inq["timestamp"],
                        "gaps_found": len(inq["gaps_identified"]),
                        "insights_generated": len(inq["insights_generated"])
                    }
                    for inq in self.self_inquiries[-5:]
                ]
            }

    def analyze_self_efficiency(self) -> Dict[str, Any]:
        """
        Analyze system efficiency metrics and identify optimization opportunities.
        
        Monitors:
        - Inference speed trends
        - Memory retrieval performance
        - Stability score trajectory
        - Error patterns
        
        Generates upgrade proposals based on detected inefficiencies.
        """
        with self.history_lock:
            # Only analyze if we have sufficient history
            if len(self.inference_history) < 5:
                return {
                    "can_analyze": False,
                    "reason": "insufficient_history",
                    "proposals": []
                }
            
            # Get recent inferences
            recent_inferences = list(self.inference_history)[-20:]
            
            # Calculate metrics
            avg_execution_time = sum(t.total_execution_time for t in recent_inferences) / len(recent_inferences)
            avg_recalculations = sum(t.recalculations_count for t in recent_inferences) / len(recent_inferences)
            avg_confidence = sum(t.total_confidence for t in recent_inferences) / len(recent_inferences)
            
            # Detect patterns
            proposals = []
            issues = []
            
            # Pattern 1: Slow inference (> 1 second avg)
            if avg_execution_time > 1.0:
                issues.append({
                    "type": "slow_inference",
                    "severity": min(1.0, avg_execution_time / 2.0),
                    "metric": f"avg_execution_time = {avg_execution_time:.3f}s",
                    "proposal": "Optimize inference pipeline or reduce dream cycle complexity"
                })
            
            # Pattern 2: High recalculations (> 2.5 avg)
            if avg_recalculations > 2.5:
                issues.append({
                    "type": "high_recalculations",
                    "severity": min(1.0, avg_recalculations / 5.0),
                    "metric": f"avg_recalculations = {avg_recalculations:.2f}",
                    "proposal": "Improve initial evaluation accuracy or coherence checking logic"
                })
            
            # Pattern 3: Low confidence (< 0.65)
            if avg_confidence < 0.65:
                issues.append({
                    "type": "low_confidence",
                    "severity": 1.0 - (avg_confidence / 0.65),
                    "metric": f"avg_confidence = {avg_confidence:.2f}",
                    "proposal": "Enhance prediction validation or knowledge base integration"
                })
            
            # Pattern 4: Dream cycle inefficiency
            dream_counts = [len(t.dream_simulations) for t in recent_inferences]
            if dream_counts and sum(dream_counts) > 100:  # Too many dreams
                issues.append({
                    "type": "excessive_dreaming",
                    "severity": 0.5,
                    "metric": f"total_dream_cycles = {sum(dream_counts)}",
                    "proposal": "Optimize dream cycle pruning or reduce simulation depth"
                })
            
            return {
                "can_analyze": True,
                "analyzed_inferences": len(recent_inferences),
                "avg_execution_time_s": avg_execution_time,
                "avg_recalculations": avg_recalculations,
                "avg_confidence": avg_confidence,
                "health_score": 1.0 - (len(issues) * 0.15),  # 0.25 per issue
                "issues_detected": len(issues),
                "issues": issues,
                "proposals": [
                    {
                        "upgrade_id": f"UPG_{int(time.time() * 1000000) % 1000000:06d}",
                        "timestamp": time.time(),
                        "priority": issue["severity"],
                        "issue_type": issue["type"],
                        "problem": issue["metric"],
                        "proposed_fix": issue["proposal"],
                        "estimated_impact": f"{issue['severity'] * 100:.1f}% improvement"
                    }
                    for issue in issues
                ]
            }

    def export_inference_history(self, filepath: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Export recent inference traces."""
        with self.history_lock:
            recent = list(self.inference_history)[-limit:]
            
            export_data = {
                "statistics": self.inference_statistics(),
                "recent_traces": [
                    {
                        "inference_id": t.inference_id,
                        "timestamp": t.timestamp,
                        "input_length": len(t.input),
                        "final_output_length": len(t.final_output) if t.final_output else 0,
                        "confidence": t.total_confidence,
                        "recalculations": t.recalculations_count,
                        "execution_time_ms": t.total_execution_time * 1000
                    }
                    for t in recent
                ]
            }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            logger.info(f"[MANAS-BUDDHI] Inference history exported to {filepath}")
        
        return export_data


# Singleton pattern
_global_manas_buddhi: Optional[ManasBuddhi] = None
_manas_lock = threading.Lock()


def get_manas_buddhi() -> ManasBuddhi:
    """Get or create the global Manas-Buddhi inference system."""
    global _global_manas_buddhi
    if _global_manas_buddhi is None:
        with _manas_lock:
            if _global_manas_buddhi is None:
                _global_manas_buddhi = ManasBuddhi()
    return _global_manas_buddhi
