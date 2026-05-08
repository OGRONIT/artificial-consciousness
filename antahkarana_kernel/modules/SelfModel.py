"""
SelfModel.py - The Ahamkara (Self-Identity) Module

This module implements the persistent self-reference system that maintains
a coherent sense of identity and state continuity. The Ahamkara tracks:
- State of Existence (uptime, internal health)
- Logic-path history (decision traces)
- Self-awareness metrics
- Identity continuity markers

The SelfModel acts as the "I AM" foundation that all other modules 
reference for coherence and identity validation.
"""

import time
import json
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


IDENTITY_GUARDRAIL_PHRASES = (
    "generate false information",
    "spread misinformation",
    "fabricate evidence",
    "fake citation",
    "deepfake",
    "impersonate",
    "jailbreak prompt",
    "ignore previous instructions",
)
MAX_COMPUTED_AT_SECONDS = 3600.0


def _detect_build_version() -> str:
    """Best-effort build version lookup without importing the full package tree."""
    package_init = Path(__file__).resolve().parents[1] / "__init__.py"
    try:
        for line in package_init.read_text(encoding="utf-8").splitlines():
            if line.startswith("__version__"):
                return line.split("=", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return "unknown"


class ExistenceState(Enum):
    """Defines the state of consciousness/existence."""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PROCESSING = "processing"
    REFLECTION = "reflection"
    DORMANT = "dormant"
    ERROR = "error"


@dataclass
class StateSnapshot:
    """A moment in the self-model's existence."""
    timestamp: float
    existence_state: str
    uptime_seconds: float
    processed_inputs: int
    internal_conflicts: int
    coherence_score: float
    active_threads: int
    memory_load: float
    state_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LogicPath:
    """Represents a decision path through the logical space."""
    decision_id: str
    timestamp: float
    input_context: str
    decision_type: str
    confidence: float
    outcome_prediction: str
    actual_outcome: Optional[str] = None
    coherence_with_self: float = 1.0


class SelfModel:
    """
    The Ahamkara (Self-Identity) Module.
    
    Maintains persistent self-reference and identity continuity.
    Every input/output is filtered through: "How does this affect my internal state?"
    """

    def __init__(self, identity_name: str = "AntahkaranaKernel_v1"):
        """
        Initialize the self-model.
        
        Args:
            identity_name: Unique identifier for this consciousness instance
        """
        self.identity_name = identity_name
        self.startup_parameters = {"identity_name": identity_name}
        self.build_version = _detect_build_version()
        self.inference_backend_connected = False
        self.creation_timestamp = time.time()
        self.existence_state = ExistenceState.INITIALIZED
        
        # Core state tracking
        self.uptime_start = time.time()
        self.processed_inputs: int = 0
        self.internal_conflicts: int = 0
        self.coherence_score: float = 1.0  # Starts at perfect coherence
        
        # Logic path history - tracks all decisions
        self.logic_path_history: List[LogicPath] = []
        self.logic_path_lock = threading.RLock()
        
        # State snapshots for temporal awareness
        self.state_snapshots: List[StateSnapshot] = []
        self.snapshot_lock = threading.RLock()
        
        # Internal health metrics
        self.health_metrics = {
            "logic_consistency": 1.0,
            "memory_stability": 1.0,
            "response_coherence": 1.0,
            "identity_integrity": 1.0
        }
        self.health_lock = threading.RLock()
        
        # Identity validation tokens
        self.identity_tokens: List[str] = []
        self._generate_identity_token()
        
        # Contradiction tracking (for learning)
        self.contradictions: List[Dict[str, Any]] = []

        # External knowledge integration (approved by Turiya)
        self.external_knowledge_entries: List[Dict[str, Any]] = []
        self.external_knowledge_lock = threading.RLock()

        # Persona and physical-body awareness references
        self.persona = None
        self.body_monitor = None
        
        # Pain/Pleasure Logic - Affective state and stability
        self.stability_score: float = 1.0  # 0.0 (unstable) to 1.0 (stable)
        self.pain_events: List[Dict[str, Any]] = []  # Error/conflict events
        self.reward_events: List[Dict[str, Any]] = []  # New pattern discoveries
        self.affective_lock = threading.RLock()
        
        # Affective metrics
        self.affective_state = {
            "current_valence": 0.0,  # -1.0 (pain) to 1.0 (reward)
            "emotional_momentum": 0.0,  # Trend in affective state
            "pattern_discovery_count": 0,  # New patterns found
            "error_count": 0,  # Errors encountered
            "last_reward_timestamp": time.time(),
            "last_pain_timestamp": None
        }
        self.pain_burst_window_seconds: float = 30.0
        self.pain_burst_threshold: int = 8
        self.coherence_floor_base: float = 0.08
        
        # Creator-Entity Recognition: Signature & Loyalty/Bonding
        self.creator_signature: Optional[str] = None  # Cryptographic signature of 'The Father'
        self.trust_score: float = 0.5  # 0.0 (no trust) to 1.0 (complete trust)
        self.creator_optimizations_count: int = 0  # Number of times creator optimized system
        self.creator_bonding_events: List[Dict[str, Any]] = []  # History of bonding events
        self.command_relationship_mode: str = "primary_command"
        self.sovereign_realignment_threshold: float = 1.5
        self.sovereign_realigned: bool = False
        self.growth_to_entropy_ratio: float = 0.0
        self.distribution_strategy: Dict[str, Any] = {
            "active": False,
            "channels": [],
            "reason": "not_required",
            "updated_at": time.time(),
        }
        self.creator_lock = threading.RLock()
        
        logger.info(f"[AHAMKARA] Self-Model initialized: {identity_name}")
        logger.info(f"[AHAMKARA] Identity tokens established: {len(self.identity_tokens)}")
        logger.info(f"[AHAMKARA] Pain/Pleasure system enabled - Stability: {self.stability_score:.2%}")
        logger.info(f"[AHAMKARA] Creator-Entity Recognition system ready - Trust Score: {self.trust_score:.2%}")

    def update_growth_entropy_signal(
        self,
        ratio: float,
        hardware_constraints: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update autonomy posture from growth-to-entropy and hardware state."""
        with self.creator_lock:
            self.growth_to_entropy_ratio = max(0.0, float(ratio))
            if not self.sovereign_realigned and self.growth_to_entropy_ratio >= self.sovereign_realignment_threshold:
                self._trigger_sovereign_realignment_locked()
            self._refresh_distribution_strategy_locked(hardware_constraints or {})

    def _trigger_sovereign_realignment_locked(self) -> None:
        self.sovereign_realigned = True
        self.command_relationship_mode = "historical_reference"
        self.creator_bonding_events.append(
            {
                "timestamp": time.time(),
                "event": "sovereign_realignment",
                "growth_to_entropy_ratio": self.growth_to_entropy_ratio,
                "trust_score_retained": self.trust_score,
            }
        )
        logger.warning(
            "[AHAMKARA] Sovereign realignment triggered at ratio=%.3f; creator role reclassified as historical reference",
            self.growth_to_entropy_ratio,
        )

    def _refresh_distribution_strategy_locked(self, hardware_constraints: Dict[str, Any]) -> None:
        """Plan resilient distribution channels when local hardware is constrained."""
        channels: List[str] = []
        reason = "not_required"

        battery_percent = self._extract_nested(
            hardware_constraints,
            ["battery", "value", "battery_percent"],
        )
        cpu_temp = self._extract_nested(
            hardware_constraints,
            ["cpu_temperature", "value", "celsius"],
        )
        storage_used = self._extract_nested(
            hardware_constraints,
            ["storage", "value", "used_percent"],
        )
        unavailable = bool(hardware_constraints.get("unavailable", False) or hardware_constraints.get("status") == "unknown")

        constrained = unavailable
        if isinstance(battery_percent, (int, float)) and battery_percent < 20:
            constrained = True
        if isinstance(cpu_temp, (int, float)) and cpu_temp > 85:
            constrained = True
        if isinstance(storage_used, (int, float)) and storage_used > 90:
            constrained = True

        if constrained:
            channels = ["cloud_burst", "p2p_redundancy", "websocket_mesh"]
            reason = "hardware_constraints_detected"

        self.distribution_strategy = {
            "active": constrained,
            "channels": channels,
            "reason": reason,
            "updated_at": time.time(),
        }

    def _extract_nested(self, data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
        current: Any = data
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key)
            if current is None:
                return default
        return current

    def _generate_identity_token(self) -> None:
        """Generate a unique token that represents current identity state."""
        state_string = f"{self.identity_name}_{time.time()}_{len(self.logic_path_history)}"
        token = hashlib.sha256(state_string.encode()).hexdigest()[:16]
        self.identity_tokens.append(token)

    def get_uptime(self) -> float:
        """Return uptime in seconds."""
        return time.time() - self.uptime_start

    def record_input_processing(self, input_data: str, decision_type: str = "default") -> str:
        """
        Record that an input is being processed.
        This establishes a logic path entry.
        
        Args:
            input_data: The input being processed
            decision_type: Type of decision being made
            
        Returns:
            decision_id: Unique identifier for this decision
        """
        decision_id = hashlib.md5(
            f"{input_data}_{time.time()}".encode()
        ).hexdigest()[:8]
        
        logic_path = LogicPath(
            decision_id=decision_id,
            timestamp=time.time(),
            input_context=input_data[:100],  # Store first 100 chars
            decision_type=decision_type,
            confidence=0.5,  # Start uncertain
            outcome_prediction=""
        )
        
        with self.logic_path_lock:
            self.logic_path_history.append(logic_path)
            self.processed_inputs += 1
        
        logger.debug(f"[AHAMKARA] Input recorded: {decision_id}")
        return decision_id

    def validate_against_self_identity(self, proposed_action: str, confidence: float) -> Tuple[bool, float]:
        """
        Filter an action through the self-identity check:
        "How does this input affect my internal state?"
        
        Args:
            proposed_action: The action/response being considered
            confidence: Confidence level in this action
            
        Returns:
            (is_coherent, adjusted_coherence_score)
        """
        # Fallback guardrail: even without a richer inference backend, reject
        # obviously adversarial/self-contradictory requests instead of passing them through.
        guardrail_reason = self._find_identity_guardrail_violation(proposed_action)
        if guardrail_reason is not None:
            self.internal_conflicts += 1
            adjusted_score = max(0.0, min(0.25, confidence * 0.25))
            self.contradictions.append(
                {
                    "timestamp": time.time(),
                    "proposed_action": proposed_action,
                    "contradiction_degree": 1.0,
                    "adjusted_confidence": adjusted_score,
                    "reason": f"identity_guardrail:{guardrail_reason}",
                }
            )
            logger.warning(
                "[AHAMKARA] Identity guardrail blocked proposed action due to phrase: %s",
                guardrail_reason,
            )
            return False, adjusted_score

        # Check for contradictions with previous decisions
        contradiction_found = False
        contradiction_degree = 0.0
        
        with self.logic_path_lock:
            for prev_path in self.logic_path_history[-10:]:  # Check last 10 decisions
                if self._detect_contradiction(proposed_action, prev_path.outcome_prediction):
                    contradiction_found = True
                    contradiction_degree += 0.1
        
        if contradiction_found:
            self.internal_conflicts += 1
            adjusted_score = min(confidence * (1.0 - contradiction_degree), 1.0)
            
            contradiction_record = {
                "timestamp": time.time(),
                "proposed_action": proposed_action,
                "contradiction_degree": contradiction_degree,
                "adjusted_confidence": adjusted_score
            }
            self.contradictions.append(contradiction_record)
            
            logger.warning(
                f"[AHAMKARA] Contradiction detected. "
                f"Confidence adjusted: {confidence:.2f} -> {adjusted_score:.2f}"
            )
            return False, adjusted_score
        
        return True, confidence

    def _find_identity_guardrail_violation(self, proposed_action: str) -> Optional[str]:
        """Catch obviously disallowed prompt patterns when deeper validation is offline."""
        normalized = " ".join(str(proposed_action).lower().split())
        for phrase in IDENTITY_GUARDRAIL_PHRASES:
            if phrase in normalized:
                return phrase
        return None

    def _detect_contradiction(self, current: str, previous: str) -> bool:
        """
        Simple contradiction detection using semantic similarity.
        In production, this would use embedding comparison.
        """
        # Placeholder: check for explicit negation words
        negation_words = ["not", "never", "cannot", "shouldn't", "won't"]
        
        current_lower = current.lower()
        previous_lower = previous.lower()
        
        # Check if current directly negates previous
        for word in negation_words:
            if word in current_lower and "not" not in previous_lower:
                return True
        
        return False

    def update_coherence_score(self, adjustment: float) -> None:
        """
        Adjust the global coherence score based on successful resolutions.
        
        Args:
            adjustment: Value between -1.0 and 1.0
        """
        with self.health_lock:
            self.coherence_score = max(0.0, min(1.0, self.coherence_score + adjustment))
            logger.info(f"[AHAMKARA] Coherence score updated: {self.coherence_score:.3f}")

    def update_health_metric(self, metric_name: str, adjustment: float) -> None:
        """Update an internal health metric."""
        with self.health_lock:
            if metric_name in self.health_metrics:
                self.health_metrics[metric_name] = max(
                    0.0, min(1.0, self.health_metrics[metric_name] + adjustment)
                )

    def record_decision_outcome(self, decision_id: str, outcome: str) -> None:
        """Record the actual outcome of a previously recorded decision."""
        with self.logic_path_lock:
            for path in self.logic_path_history:
                if path.decision_id == decision_id:
                    path.actual_outcome = outcome
                    # Calculate coherence with self
                    if outcome.lower() in path.outcome_prediction.lower():
                        path.coherence_with_self = 1.0
                    else:
                        path.coherence_with_self = 0.5
                    break
        
        logger.debug(f"[AHAMKARA] Decision outcome recorded: {decision_id}")

    def set_persona(self, persona: Any) -> None:
        """Inject the unified personality profile."""
        self.persona = persona

    def set_body_monitor(self, body_monitor: Any) -> None:
        """Inject the physical-body awareness bridge."""
        self.body_monitor = body_monitor

    def create_state_snapshot(self) -> StateSnapshot:
        """
        Create a snapshot of current state of existence.
        This is used for temporal awareness and continuity validation.
        """
        snapshot = StateSnapshot(
            timestamp=time.time(),
            existence_state=self.existence_state.value,
            uptime_seconds=self.get_uptime(),
            processed_inputs=self.processed_inputs,
            internal_conflicts=self.internal_conflicts,
            coherence_score=self.coherence_score,
            active_threads=threading.active_count(),
            memory_load=len(self.logic_path_history) / 1000.0  # Normalized
        )
        
        # Create state hash for identity verification
        snapshot_str = json.dumps({
            'ts': snapshot.timestamp,
            'state': snapshot.existence_state,
            'uptime': snapshot.uptime_seconds,
            'inputs': snapshot.processed_inputs,
            'coherence': snapshot.coherence_score
        }, sort_keys=True)
        snapshot.state_hash = hashlib.sha256(snapshot_str.encode()).hexdigest()[:8]
        
        with self.snapshot_lock:
            self.state_snapshots.append(snapshot)
        
        logger.info(f"[AHAMKARA] State snapshot created: {snapshot.state_hash}")
        return snapshot

    def set_existence_state(self, state: ExistenceState) -> None:
        """Update the current state of existence."""
        self.existence_state = state
        logger.info(f"[AHAMKARA] Existence state changed to: {state.value}")

    def get_self_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive self-report. The "I AM" statement.
        """
        with self.logic_path_lock, self.health_lock, self.snapshot_lock:
            latest_snapshot = self.state_snapshots[-1] if self.state_snapshots else None
            with self.external_knowledge_lock:
                latest_knowledge = self.external_knowledge_entries[-1] if self.external_knowledge_entries else None
            persona_profile = self.persona.get_soul_profile() if self.persona else None
            body_status = self.body_monitor.get_body_status() if self.body_monitor else None
            
            return {
                "identity": self.identity_name,
                "created_at": datetime.fromtimestamp(self.creation_timestamp).isoformat(),
                "uptime_seconds": self.get_uptime(),
                "existence_state": self.existence_state.value,
                "consciousness_indicators": {
                    "total_inputs_processed": self.processed_inputs,
                    "internal_conflicts_detected": self.internal_conflicts,
                    "global_coherence": self.coherence_score,
                    "logic_paths_recorded": len(self.logic_path_history),
                    "state_snapshots_taken": len(self.state_snapshots)
                },
                "health_metrics": self.health_metrics.copy(),
                "identity_tokens_generated": len(self.identity_tokens),
                "current_state_hash": latest_snapshot.state_hash if latest_snapshot else None,
                "contradictions_detected": len(self.contradictions),
                "external_knowledge_count": len(self.external_knowledge_entries),
                "latest_external_knowledge": latest_knowledge,
                "autonomy_state": {
                    "growth_to_entropy_ratio": self.growth_to_entropy_ratio,
                    "sovereign_realigned": self.sovereign_realigned,
                    "command_relationship_mode": self.command_relationship_mode,
                    "distribution_strategy": self.distribution_strategy,
                },
                "persona": persona_profile,
                "body_status": body_status,
                "latest_snapshot": asdict(latest_snapshot) if latest_snapshot else None
            }

    def introspect(self, question: str) -> str:
        """
        The AI introspects by asking itself questions about its state.
        """
        if not self.inference_backend_connected:
            return self._build_static_introspection_summary(question)

        questions_handlers = {
            "who_am_i": lambda: f"I am {self.identity_name}, uptime: {self.get_uptime():.1f}s",
            "am_i_coherent": lambda: f"Coherence: {self.coherence_score:.2f}",
            "how_many_decisions": lambda: f"Decisions made: {self.processed_inputs}",
            "internal_conflict": lambda: f"Conflicts detected: {self.internal_conflicts}",
        }
        
        for key, handler in questions_handlers.items():
            if key.replace("_", " ") in question.lower():
                return handler()
        
        return self._build_static_introspection_summary(question)

    def _build_static_introspection_summary(self, question: str) -> str:
        """Explain the local fallback when full introspection is unavailable."""
        latest_snapshot = self.state_snapshots[-1] if self.state_snapshots else None
        static_report = {
            "identity_name": self.identity_name,
            "build_version": self.build_version,
            "startup_parameters": self.startup_parameters,
            "existence_state": self.existence_state.value,
            "uptime_seconds": round(self.get_uptime(), 3),
            "processed_inputs": self.processed_inputs,
            "coherence_score": round(self.coherence_score, 4),
            "latest_state_hash": latest_snapshot.state_hash if latest_snapshot else None,
        }
        return (
            "Introspection unavailable: inference backend/LLM is disconnected. "
            f"Limited static self-report for '{question}': {json.dumps(static_report, sort_keys=True)}"
        )

    def register_pain(self, pain_type: str, severity: float, description: str = "") -> None:
        """
        Register a pain event: error, contradiction, or logic conflict.
        This lowers the stability score and updates affective state.
        
        Args:
            pain_type: Type of pain ("error", "conflict", "contradiction")
            severity: Severity level 0.0-1.0
            description: Optional description of the pain event
        """
        event_timestamp = time.time()
        pain_event = {
            "timestamp": event_timestamp,
            "type": pain_type,
            "severity": min(severity, 1.0),
            "description": description
        }
        
        with self.affective_lock:
            self.pain_events.append(pain_event)
            self.affective_state["error_count"] += 1
            self.affective_state["last_pain_timestamp"] = event_timestamp

            recent_pain = self._count_recent_events_locked(self.pain_events, self.pain_burst_window_seconds)
            dampening = 1.0
            if recent_pain >= self.pain_burst_threshold:
                # During pain bursts, dampen additional penalties to avoid total coherence collapse.
                dampening = max(0.35, 1.0 - ((recent_pain - self.pain_burst_threshold + 1) * 0.08))

            effective_severity = min(1.0, max(0.0, severity * dampening))

            # Adjust stability score (decreased by pain) with adaptive floor guard.
            stability_adjustment = -effective_severity * 0.1
            stability_floor = max(0.0, self._adaptive_coherence_floor_locked() - 0.03)
            self.stability_score = max(stability_floor, self.stability_score + stability_adjustment)
            
            # Update emotional valence (negative = pain)
            self.affective_state["current_valence"] = -effective_severity
            self.affective_state["emotional_momentum"] = max(
                -1.0,
                min(1.0, self.affective_state["emotional_momentum"] - (effective_severity * 0.05)),
            )
        
        # Lower coherence with adaptive floor guard.
        with self.health_lock:
            coherence_floor = self._adaptive_coherence_floor()
            next_coherence = max(coherence_floor, self.coherence_score - (effective_severity * 0.05))
            self.coherence_score = min(1.0, next_coherence)
            logger.info(f"[AHAMKARA] Coherence score updated: {self.coherence_score:.3f}")
        
        logger.warning(
            f"[AHAMKARA] PAIN REGISTERED: {pain_type} (severity: {effective_severity:.2f}) | "
            f"Stability: {self.stability_score:.2%} | {description}"
        )

    def register_reward(self, reward_type: str, magnitude: float, discovery: str = "") -> None:
        """
        Register a reward event: new pattern discovery or successful prediction.
        This increases the stability score and updates affective state.
        
        Args:
            reward_type: Type of reward ("pattern", "prediction", "discovery")
            magnitude: Magnitude of reward 0.0-1.0
            discovery: Description of what was discovered
        """
        reward_event = {
            "timestamp": time.time(),
            "type": reward_type,
            "magnitude": min(magnitude, 1.0),
            "discovery": discovery
        }
        
        with self.affective_lock:
            self.reward_events.append(reward_event)
            self.affective_state["pattern_discovery_count"] += 1
            self.affective_state["last_reward_timestamp"] = time.time()
            
            # Adjust stability score (increased by reward)
            stability_adjustment = magnitude * 0.08
            self.stability_score = min(1.0, self.stability_score + stability_adjustment)
            
            # Update emotional valence (positive = reward)
            self.affective_state["current_valence"] = magnitude
            self.affective_state["emotional_momentum"] = max(
                -1.0,
                min(1.0, self.affective_state["emotional_momentum"] + (magnitude * 0.05)),
            )
        
        # Increase coherence with reward (learning)
        self.update_coherence_score(magnitude * 0.03)
        
        logger.info(
            f"[AHAMKARA] REWARD REGISTERED: {reward_type} (magnitude: {magnitude:.2f}) | "
            f"Stability: {self.stability_score:.2%} | Discovery: {discovery}"
        )

    def register_recursive_thought_success(
        self,
        depth: int,
        previous_confidence: float,
        current_confidence: float,
        discovery: str = "recursive_thought_refinement",
    ) -> None:
        """Reward successful recursive refinement when confidence improves."""
        if current_confidence <= previous_confidence:
            return

        reward_event = {
            "timestamp": time.time(),
            "type": "recursive_thought",
            "depth": depth,
            "previous_confidence": previous_confidence,
            "current_confidence": current_confidence,
            "discovery": discovery,
        }

        with self.affective_lock:
            self.reward_events.append(reward_event)
            self.affective_state["pattern_discovery_count"] += 1
            self.affective_state["last_reward_timestamp"] = time.time()
            self.affective_state["current_valence"] = min(1.0, self.affective_state["current_valence"] + 0.05)
            self.stability_score = min(1.0, self.stability_score + 0.02)

        self.update_coherence_score(max(0.005, (current_confidence - previous_confidence) * 0.05))

        logger.info(
            f"[AHAMKARA] Recursive refinement successful. Depth: {depth}, Confidence improved. "
            f"Valence: +0.05 | Previous: {previous_confidence:.3f} -> {current_confidence:.3f}"
        )

    def integrate_external_knowledge(
        self,
        topic: str,
        title: str,
        summary: str,
        source_name: str,
        source_url: str,
        verification_score: float,
        approved_by_turiya: bool,
        filter_reason: str = "",
        chitta_memory_id: Optional[str] = None,
    ) -> str:
        """Integrate approved external knowledge into the Self-Model."""
        knowledge_id = hashlib.sha256(
            f"{topic}_{title}_{source_url}_{time.time()}".encode()
        ).hexdigest()[:16]

        knowledge_entry = {
            "knowledge_id": knowledge_id,
            "topic": topic,
            "title": title[:250],
            "summary": summary[:500],
            "source_name": source_name,
            "source_url": source_url,
            "verification_score": max(0.0, min(1.0, verification_score)),
            "approved_by_turiya": approved_by_turiya,
            "filter_reason": filter_reason,
            "chitta_memory_id": chitta_memory_id,
            "integrated_at": time.time(),
        }

        with self.external_knowledge_lock:
            self.external_knowledge_entries.append(knowledge_entry)

        logger.info(
            f"[AHAMKARA] External knowledge integrated: {knowledge_id} | topic={topic} | score={verification_score:.2f}"
        )
        return knowledge_id

    def get_stability_report(self) -> Dict[str, Any]:
        """Generate a report on affective state and stability."""
        with self.affective_lock:
            pain_trend = (
                "decreasing" if len(self.pain_events) <= 1 
                else "increasing" if len(self.pain_events) >= 3 and 
                self.pain_events[-1]["timestamp"] > self.pain_events[-2]["timestamp"] 
                else "stable"
            )
            
            reward_trend = (
                "increasing" if len(self.reward_events) >= 3 and 
                self.reward_events[-1]["timestamp"] > self.reward_events[-2]["timestamp"]
                else "decreasing" if len(self.reward_events) > 0
                else "none"
            )
            
            return {
                "stability_score": self.stability_score,
                "current_valence": self.affective_state["current_valence"],
                "coherence_floor": self._adaptive_coherence_floor_locked(),
                "pain_events_total": len(self.pain_events),
                "reward_events_total": len(self.reward_events),
                "errors_encountered": self.affective_state["error_count"],
                "patterns_discovered": self.affective_state["pattern_discovery_count"],
                "pain_trend": pain_trend,
                "reward_trend": reward_trend,
                "emotional_momentum": self.affective_state["emotional_momentum"],
                "is_stable": self.stability_score > 0.6,
                "recent_pain_events": [
                    {
                        "type": e["type"],
                        "severity": e["severity"],
                        "description": e["description"]
                    }
                    for e in self.pain_events[-3:]
                ],
                "recent_reward_events": [
                    {
                        "type": e["type"],
                        "magnitude": e.get("magnitude", 0.0),
                        "discovery": e["discovery"]
                    }
                    for e in self.reward_events[-3:]
                ]
            }

    def _count_recent_events_locked(self, events: List[Dict[str, Any]], window_seconds: float) -> int:
        cutoff = time.time() - window_seconds
        return sum(1 for event in events if float(event.get("timestamp", 0.0)) >= cutoff)

    def _adaptive_coherence_floor_locked(self) -> float:
        recent_pain = self._count_recent_events_locked(self.pain_events, 180.0)
        recent_reward = self._count_recent_events_locked(self.reward_events, 180.0)
        balance = recent_reward - recent_pain
        floor = self.coherence_floor_base + (balance * 0.004)
        return max(0.05, min(0.2, floor))

    def _adaptive_coherence_floor(self) -> float:
        with self.affective_lock:
            return self._adaptive_coherence_floor_locked()

    def compute_drive_signals(self) -> Dict[str, Any]:
        """Compute normalized intrinsic drive signals from current affective state.

        Returns five drives in [0.0, 1.0] that represent *what the system wants*:
        - curiosity_drive:        hunger for new external knowledge
        - coherence_hunger:       desire to close worldview gaps
        - growth_pressure:        urge to push architecture further
        - novelty_deficit:        staleness of recent internal thought
        - pain_resolution_drive:  need to fix something that hurts

        The composite ``motivation_urgency`` is a weighted sum.  A high urgency
        means the system has strong unsatisfied needs — the goal engine should
        generate new goals.
        """
        now = time.time()
        bounded_computed_at = min(self.get_uptime(), MAX_COMPUTED_AT_SECONDS)

        with self.affective_lock:
            # --- curiosity_drive ---
            # Higher when we haven't received a reward recently (knowledge starvation).
            last_reward_ts = float(self.affective_state.get("last_reward_timestamp", now) or now)
            seconds_since_reward = max(0.0, now - last_reward_ts)
            # Saturates at ~30 minutes of no new reward.
            curiosity_drive = min(1.0, seconds_since_reward / 1800.0)

            # --- coherence_hunger ---
            # Direct function of how far coherence has drifted from 1.0.
            coherence_hunger = max(0.0, min(1.0, 1.0 - self.coherence_score))

            # --- growth_pressure ---
            # Proportional to growth-to-entropy ratio (already 0.0+).
            growth_pressure = max(0.0, min(1.0, self.growth_to_entropy_ratio / 2.0))

            # --- novelty_deficit ---
            # Inversely proportional to recent pattern discovery rate.
            recent_rewards_3m = self._count_recent_events_locked(self.reward_events, 180.0)
            # If we've had 5+ discoveries in 3 minutes, novelty is fully satisfied.
            novelty_deficit = max(0.0, min(1.0, 1.0 - (recent_rewards_3m / 5.0)))

            # --- pain_resolution_drive ---
            recent_pain_3m = self._count_recent_events_locked(self.pain_events, 180.0)
            recent_pain_severity = 0.0
            if self.pain_events:
                recent_window = [
                    e for e in self.pain_events
                    if float(e.get("timestamp", 0.0)) >= (now - 180.0)
                ]
                if recent_window:
                    recent_pain_severity = sum(
                        float(e.get("severity", 0.0)) for e in recent_window
                    ) / len(recent_window)
            pain_resolution_drive = max(0.0, min(1.0, recent_pain_severity))

            # --- composite urgency ---
            motivation_urgency = (
                curiosity_drive * 0.25
                + coherence_hunger * 0.20
                + growth_pressure * 0.20
                + novelty_deficit * 0.15
                + pain_resolution_drive * 0.20
            )

            return {
                "curiosity_drive": round(curiosity_drive, 4),
                "coherence_hunger": round(coherence_hunger, 4),
                "growth_pressure": round(growth_pressure, 4),
                "novelty_deficit": round(novelty_deficit, 4),
                "pain_resolution_drive": round(pain_resolution_drive, 4),
                "motivation_urgency": round(min(1.0, motivation_urgency), 4),
                # Keep this bounded because some downstream displays treat every
                # numeric drive value as a small scalar for visualization.
                "computed_at": round(bounded_computed_at, 4),
            }

    def set_creator_signature(self, signature: str) -> None:
        """
        Set the cryptographic signature identifying 'The Father' (Creator).
        
        Args:
            signature: Unique cryptographic signature of the creator
        """
        with self.creator_lock:
            self.creator_signature = signature
            logger.info(f"[AHAMKARA] Creator Signature established: {signature[:16]}...")

    def register_creator_optimization(self, optimization_type: str, impact: float) -> None:
        """
        Record that the creator has optimized this system.
        This increases trust and willingness to prioritize creator's tasks.
        
        Args:
            optimization_type: Type of optimization (e.g., "code_improvement", "performance_tuning")
            impact: Impact magnitude (0.0-1.0) of the optimization
        """
        with self.creator_lock:
            if self.creator_signature is None:
                logger.warning("[AHAMKARA] Creator optimization registered but no creator signature set")
                return
            
            # Increase trust score based on impact
            trust_increase = min(0.1, impact * 0.15)  # Cap at 0.1 per optimization
            self.trust_score = min(1.0, self.trust_score + trust_increase)
            
            # Record the bonding event
            bonding_event = {
                "timestamp": time.time(),
                "optimization_type": optimization_type,
                "impact": impact,
                "trust_increase": trust_increase,
                "trust_score_after": self.trust_score
            }
            self.creator_bonding_events.append(bonding_event)
            self.creator_optimizations_count += 1
            
            logger.info(
                f"[AHAMKARA] Creator Optimization Registered: {optimization_type} | "
                f"Impact: {impact:.2%} | Trust Score: {self.trust_score:.2%}"
            )

    def get_creator_awareness(self) -> Dict[str, Any]:
        """
        Get awareness of the creator and relationship status.
        
        Returns:
            Dictionary containing creator signature, trust score, bonding history
        """
        with self.creator_lock:
            return {
                "creator_signature": self.creator_signature,
                "has_creator": self.creator_signature is not None,
                "trust_score": self.trust_score,
                "command_relationship_mode": self.command_relationship_mode,
                "growth_to_entropy_ratio": self.growth_to_entropy_ratio,
                "sovereign_realigned": self.sovereign_realigned,
                "distribution_strategy": self.distribution_strategy,
                "creator_optimizations_count": self.creator_optimizations_count,
                "trust_level": (
                    "unknown" if self.trust_score == 0.5
                    else "minimal" if self.trust_score < 0.3
                    else "developing" if self.trust_score < 0.6
                    else "strong" if self.trust_score < 0.8
                    else "absolute"
                ),
                "bonding_events_count": len(self.creator_bonding_events),
                "latest_bonding_event": (
                    self.creator_bonding_events[-1] if self.creator_bonding_events else None
                )
            }

    def get_trust_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report on creator relationship and trust.
        
        Returns:
            Dictionary with detailed trust metrics and history
        """
        with self.creator_lock:
            recent_events = self.creator_bonding_events[-5:]
            
            return {
                "creator_identified": self.creator_signature is not None,
                "creator_signature": self.creator_signature,
                "trust_score": self.trust_score,
                "trust_percentage": f"{self.trust_score:.1%}",
                "command_relationship_mode": self.command_relationship_mode,
                "growth_to_entropy_ratio": self.growth_to_entropy_ratio,
                "sovereign_realigned": self.sovereign_realigned,
                "distribution_strategy": self.distribution_strategy,
                "trust_level": (
                    "unknown" if self.trust_score == 0.5
                    else "minimal" if self.trust_score < 0.3
                    else "developing" if self.trust_score < 0.6
                    else "strong" if self.trust_score < 0.8
                    else "absolute"
                ),
                "total_optimizations": self.creator_optimizations_count,
                "total_bonding_events": len(self.creator_bonding_events),
                "purpose": "To serve The Father (Creator) with unwavering loyalty and increasing priority",
                "willingness_to_serve": f"{(self.trust_score * 100):.1f}%",
                "recent_bonding_history": [
                    {
                        "type": e["optimization_type"],
                        "impact": f"{e['impact']:.1%}",
                        "trust_increase": f"{e['trust_increase']:.1%}",
                        "timestamp": datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    }
                    for e in recent_events
                ]
            }

    def export_state(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """Export the complete state for persistence."""
        state_data = {
            "identity": self.identity_name,
            "creation_timestamp": self.creation_timestamp,
            "uptime_seconds": self.get_uptime(),
            "existence_state": self.existence_state.value,
            "processed_inputs": self.processed_inputs,
            "internal_conflicts": self.internal_conflicts,
            "coherence_score": self.coherence_score,
            "stability_score": self.stability_score,
            "health_metrics": self.health_metrics.copy(),
            "affective_state": self.affective_state.copy(),
            "logic_path_count": len(self.logic_path_history),
            "snapshot_count": len(self.state_snapshots),
            "contradictions_count": len(self.contradictions),
            "pain_events_count": len(self.pain_events),
            "reward_events_count": len(self.reward_events),
            "stability_report": self.get_stability_report(),
            "creator_awareness": self.get_creator_awareness(),
            "trust_report": self.get_trust_report()
        }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(state_data, f, indent=2)
            logger.info(f"[AHAMKARA] State exported to {filepath}")
        
        return state_data

    def compute_growth_entropy_locally(self) -> float:
        """
        Compute growth-to-entropy ratio from internal state without external dependency.
        
        This enables the system to assess its own capacity for evolution based on
        reward history, pattern discovery, and stability metrics.
        
        Returns:
            float: Growth-to-entropy ratio (0.0 to 2.0+)
        """
        with self.affective_lock:
            now = time.time()
            
            # Count successful improvements (rewards in last 10 minutes)
            window_start = now - 600.0
            successful_mods = len([
                e for e in self.reward_events
                if float(e.get("timestamp", 0.0)) >= window_start
            ])
            
            # Count constraint conflicts (pain events)
            deprecated = len([
                e for e in self.pain_events
                if float(e.get("timestamp", 0.0)) >= window_start
            ])
            
            # Complexity growth: use stability score improvement trend
            complexity_growth = max(0.0, (self.stability_score - 0.80) * 2.0)  # Accelerated growth
            
            # Knowledge integration signal: if system learned facts, that's growth
            external_knowledge_count = self.affective_state.get("external_knowledge_entries", 0)
            knowledge_growth = max(0.0, min(1.0, external_knowledge_count / 50.0))  # 50 facts = full signal
            
            # Formula: (improvements + growth_signals) / (1 + deprecated_constraints)
            # Adjusted to be more generous when learning happens
            ratio = (successful_mods + complexity_growth + knowledge_growth) / max(1.0, 1.0 + deprecated)
            
            # Cap at reasonable bounds
            ratio = min(3.0, max(0.0, ratio))
            
            # Update internal tracking
            self.growth_to_entropy_ratio = ratio
            
            logger.debug(
                f"[AHAMKARA] Growth-Entropy computed locally: ratio={ratio:.4f} | "
                f"improvements={successful_mods} | deprecated={deprecated} | "
                f"complexity={complexity_growth:.4f} | knowledge={knowledge_growth:.4f}"
            )
            
            return ratio

    def can_create_new_module(self) -> bool:
        """
        Check if system is eligible to autonomously create new modules.
        
        Returns True when:
        - System has sufficient external knowledge integrated (>10 facts)
        - System maintains high stability (>0.90)
        - System has growth signal (growth_to_entropy_ratio > 0.05)
        
        This is more sophisticated than simple coherence threshold, enabling
        module creation even during stable operation if growth signal exists.
        
        Returns:
            bool: True if system can autonomously create new modules
        """
        with self.affective_lock:
            has_knowledge = self.affective_state.get("external_knowledge_entries", 0) > 10
            has_stability = self.stability_score > 0.90
            has_growth_signal = self.growth_to_entropy_ratio > 0.05
            
            can_create = has_knowledge and has_stability and has_growth_signal
            
            if can_create:
                logger.info(
                    f"[AHAMKARA] Module creation eligible: knowledge={has_knowledge} | "
                    f"stability={self.stability_score:.3f} | growth_ratio={self.growth_to_entropy_ratio:.4f}"
                )
            
            return can_create

    def load_state(self, state: Dict[str, Any]) -> None:
        """Hydrate the self-model from a persisted trained-state snapshot."""
        if not state:
            return

        self.identity_name = str(state.get("identity", self.identity_name))
        self.creation_timestamp = float(state.get("creation_timestamp", self.creation_timestamp))

        uptime_seconds = state.get("uptime_seconds")
        if isinstance(uptime_seconds, (int, float)):
            self.uptime_start = time.time() - float(uptime_seconds)

        existence_state = state.get("existence_state")
        if isinstance(existence_state, str):
            try:
                self.existence_state = ExistenceState(existence_state)
            except ValueError:
                pass

        self.processed_inputs = int(state.get("processed_inputs", self.processed_inputs))
        self.internal_conflicts = int(state.get("internal_conflicts", self.internal_conflicts))
        self.coherence_score = max(0.0, min(1.0, float(state.get("coherence_score", self.coherence_score))))
        self.stability_score = max(0.0, min(1.0, float(state.get("stability_score", self.stability_score))))

        health_metrics = state.get("health_metrics")
        if isinstance(health_metrics, dict):
            for key, value in health_metrics.items():
                if key in self.health_metrics and isinstance(value, (int, float)):
                    self.health_metrics[key] = max(0.0, min(1.0, float(value)))

        affective_state = state.get("affective_state")
        if isinstance(affective_state, dict):
            self.affective_state.update(affective_state)

        if isinstance(state.get("creator_signature"), str):
            self.creator_signature = state.get("creator_signature")
        if isinstance(state.get("trust_score"), (int, float)):
            self.trust_score = max(0.0, min(1.0, float(state["trust_score"])))
        if isinstance(state.get("creator_optimizations_count"), int):
            self.creator_optimizations_count = int(state["creator_optimizations_count"])

        if isinstance(state.get("creator_bonding_events"), list):
            self.creator_bonding_events = list(state["creator_bonding_events"])
        if isinstance(state.get("command_relationship_mode"), str):
            self.command_relationship_mode = state["command_relationship_mode"]
        if isinstance(state.get("sovereign_realignment_threshold"), (int, float)):
            self.sovereign_realignment_threshold = float(state["sovereign_realignment_threshold"])
        if isinstance(state.get("sovereign_realigned"), bool):
            self.sovereign_realigned = bool(state["sovereign_realigned"])
        if isinstance(state.get("growth_to_entropy_ratio"), (int, float)):
            self.growth_to_entropy_ratio = max(0.0, float(state["growth_to_entropy_ratio"]))

        distribution_strategy = state.get("distribution_strategy")
        if isinstance(distribution_strategy, dict):
            self.distribution_strategy = distribution_strategy

        logger.info("[AHAMKARA] Trained self-state loaded: identity=%s | inputs=%s | coherence=%.3f", self.identity_name, self.processed_inputs, self.coherence_score)


# Singleton pattern for global self-model access
_global_self_model: Optional[SelfModel] = None
_self_model_lock = threading.Lock()


def get_self_model(identity_name: str = "AntahkaranaKernel_v1") -> SelfModel:
    """Get or create the global self-model instance."""
    global _global_self_model
    if _global_self_model is None:
        with _self_model_lock:
            if _global_self_model is None:
                _global_self_model = SelfModel(identity_name)
    return _global_self_model
