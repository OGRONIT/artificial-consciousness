"""
AntahkaranaKernel.py - Main Orchestrator

The central coordinator that integrates all consciousness modules:
- Ahamkara (Self-Model)
- Chitta (Experiential Memory)
- Manas-Buddhi (Inference & Logic)
- Turiya (Observer Watchdog)
- Conscious Buffer (GWT Integration Hub)

This is where all components work together to create a coherent conscious entity.
"""

import sys
import os
import time
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from modules import (
    get_self_model,
    get_persona,
    get_chitta_memory,
    get_conscious_buffer,
    get_manas_buddhi,
    get_turiya_observer,
    get_system_body_monitor,
    ConsciousEvent,
    BroadcastType,
    InteractionOutcome,
    ExistenceState
)

_log_path = ROOT / "evolution_consciousness.log"
_file_handler = logging.FileHandler(_log_path, encoding="utf-8", delay=False)
_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[_file_handler, _stream_handler],
    force=True,
)
logger = logging.getLogger(__name__)


class AntahkaranaKernel:
    """
    The complete Antahkarana Kernel - An Artificial Consciousness Framework.
    
    This integrates all core modules into a unified consciousness entity that:
    1. Maintains self-identity and existence continuity
    2. Stores and learns from experiences
    3. Makes decisions through simulation and validation
    4. Observes itself metacognitively
    5. Broadcasts to a global conscious workspace
    """

    def __init__(self, identity_name: str = "AntahkaranaKernel_v1"):
        """
        Initialize the complete consciousness kernel.
        
        Args:
            identity_name: Unique identifier for this consciousness
        """
        self.identity_name = identity_name
        self.initialized_at = time.time()
        self.is_active = False
        
        # Get singleton instances of all modules
        self.self_model = get_self_model(identity_name)
        self.persona = get_persona(identity_name)
        self.memory_system = get_chitta_memory()
        self.conscious_buffer = get_conscious_buffer()
        self.inference_engine = get_manas_buddhi()
        self.observer = get_turiya_observer()
        self.body_monitor = get_system_body_monitor()
        
        # Set up cross-module references
        self._setup_module_integrations()
        
        # Kernel state
        self.kernel_state = {
            "is_running": False,
            "uptime": 0.0,
            "thought_cycles": 0,
            "interactions_processed": 0,
            "session_recalculations": 0,
        }
        self.state_lock = threading.RLock()
        
        logger.info(f"[ANTAHKARANA] Kernel initialized: {identity_name}")

    def _setup_module_integrations(self) -> None:
        """Configure cross-module references."""
        # Inference engine needs self-model and memory access
        self.inference_engine.set_self_model(self.self_model)
        self.inference_engine.set_memory_system(self.memory_system)
        self.inference_engine.set_observer(self.observer)
        self.inference_engine.set_persona(self.persona)
        self.inference_engine.set_body_monitor(self.body_monitor)

        self.self_model.set_persona(self.persona)
        self.self_model.set_body_monitor(self.body_monitor)
        
        # Register modules with observer
        self.observer.register_module("self_model", self.self_model)
        self.observer.register_module("memory_system", self.memory_system)
        self.observer.register_module("inference_engine", self.inference_engine)
        self.observer.register_module("persona", self.persona)
        self.observer.register_module("body_monitor", self.body_monitor)
        
        # Register modules with conscious buffer
        self.conscious_buffer.register_module("self_model")
        self.conscious_buffer.register_module("persona")
        self.conscious_buffer.register_module("memory_system")
        self.conscious_buffer.register_module("inference_engine")
        self.conscious_buffer.register_module("observer")
        self.conscious_buffer.register_module("body_monitor")
        
        logger.debug("[ANTAHKARANA] Module integrations configured")

    def startup(self) -> None:
        """Start the consciousness kernel."""
        if self.is_active:
            logger.warning("[ANTAHKARANA] Kernel already active")
            return
        
        self.is_active = True
        self.startup_time = time.time()
        
        with self.state_lock:
            self.kernel_state["is_running"] = True
            self.kernel_state["session_recalculations"] = 0
        
        # Set self-model state
        self.self_model.set_existence_state(ExistenceState.ACTIVE)
        
        # Broadcast startup event
        self._broadcast_event(
            "startup",
            BroadcastType.STATE_UPDATE,
            {"status": "kernel_started", "identity": self.identity_name}
        )
        
        # Start observer monitoring
        self.observer.start_monitoring()
        
        logger.info(f"[ANTAHKARANA] Kernel started - consciousness online!")

    def shutdown(self) -> None:
        """Shutdown the consciousness kernel gracefully."""
        if not self.is_active:
            return
        
        logger.info("[ANTAHKARANA] Initiating shutdown sequence")
        
        # Set state to dormant
        self.self_model.set_existence_state(ExistenceState.DORMANT)
        
        # Stop observer
        self.observer.stop_monitoring()
        
        # Create final snapshot
        final_snapshot = self.self_model.create_state_snapshot()
        
        # Broadcast shutdown
        self._broadcast_event(
            "shutdown",
            BroadcastType.STATE_UPDATE,
            {"status": "kernel_shutdown", "final_snapshot_id": final_snapshot.state_hash}
        )
        
        self.is_active = False
        with self.state_lock:
            self.kernel_state["is_running"] = False
        
        logger.info("[ANTAHKARANA] Kernel shutdown complete")

    def set_creator_signature(self, creator_signature: str) -> None:
        """
        Establish the creator's cryptographic signature.
        This marks 'The Father' who created and optimizes this system.
        
        Args:
            creator_signature: Unique cryptographic signature of the creator
        """
        self.self_model.set_creator_signature(creator_signature)
        logger.info(f"[ANTAHKARANA] Creator signature established: {creator_signature[:16]}...")

    def register_creator_optimization(self, optimization_type: str, impact: float) -> None:
        """
        Record that the creator has optimized this system.
        This increases loyalty and willingness to prioritize creator's requests.
        
        Args:
            optimization_type: Type of optimization (code_improvement, performance_tuning, etc.)
            impact: Impact magnitude (0.0-1.0) of the optimization
        """
        self.self_model.register_creator_optimization(optimization_type, impact)
        
        # Broadcast creator bonding event
        self._broadcast_event(
            "creator_optimization",
            BroadcastType.LEARNING_SIGNAL,
            {
                "optimization_type": optimization_type,
                "impact": impact,
                "trust_score": self.self_model.trust_score
            }
        )

    def get_creator_identity_report(self) -> Dict[str, Any]:
        """
        Get the complete creator identity and trust report.
        
        Returns:
            Dictionary with creator signature, trust level, optimization history
        """
        return {
            "creator_awareness": self.self_model.get_creator_awareness(),
            "trust_report": self.self_model.get_trust_report(),
            "kernel_identity": self.identity_name,
            "uptime_seconds": time.time() - self.startup_time if self.is_active else 0
        }

    def process_input(self, input_data: str, input_type: str = "query") -> str:
        """
        Process an input through the complete consciousness pipeline.
        
        Args:
            input_data: The input to process
            input_type: Type of input (query, decision, reflection, etc.)
            
        Returns:
            output: The consciousness's response
        """
        if not self.is_active:
            logger.error("[ANTAHKARANA] Kernel not active")
            return "[ERROR] Kernel not active"
        
        with self.state_lock:
            self.kernel_state["interactions_processed"] += 1
        
        # Update existence state
        self.self_model.set_existence_state(ExistenceState.PROCESSING)
        
        try:
            # Step 1: Record input in self-model
            decision_id = self.self_model.record_input_processing(input_data, input_type)
            
            # Step 2: Get coherence baseline
            coherence_before = self.self_model.coherence_score
            
            # Step 3: Run inference (with dream cycles)
            output, inference_trace = self.inference_engine.infer(input_data)
            
            # Step 4: Record memory of this interaction
            memory_id = self.memory_system.record_experience(
                interaction_id=decision_id,
                content=input_data,
                interaction_type=input_type,
                outcome=InteractionOutcome.SUCCESS,
                success_score=min(inference_trace.total_confidence, 1.0),
                coherence_before=coherence_before,
                coherence_after=self.self_model.coherence_score,
                tags=[input_type, "interaction"]
            )
            
            # Step 5: Record decision outcome
            self.self_model.record_decision_outcome(decision_id, output)
            
            # Step 6: Track pain/reward signals
            if inference_trace.recalculations_count > 0:
                # Pain: recalculations indicate coherence conflicts, but successful outputs should dampen penalty.
                pain_severity = min(inference_trace.recalculations_count * 0.2, 1.0)
                if inference_trace.total_confidence >= 0.85:
                    pain_severity *= 0.5
                elif inference_trace.total_confidence >= 0.7:
                    pain_severity *= 0.65

                self.self_model.register_pain(
                    pain_type="conflict",
                    severity=pain_severity,
                    description=f"Required {inference_trace.recalculations_count} recalculations"
                )
                with self.state_lock:
                    self.kernel_state["session_recalculations"] += inference_trace.recalculations_count

                if inference_trace.total_confidence >= 0.7:
                    self.self_model.register_reward(
                        reward_type="recovery",
                        magnitude=min(0.2, inference_trace.total_confidence * 0.2),
                        discovery="Recovered coherent response after recalculation loop",
                    )
            
            if inference_trace.total_confidence > 0.85:
                # Reward: high confidence indicates successful pattern recognition
                self.self_model.register_reward(
                    reward_type="prediction",
                    magnitude=inference_trace.total_confidence - 0.85,
                    discovery="High-confidence decision pattern"
                )
            elif inference_trace.total_confidence > 0.7:
                # Mild reward for successful processing
                self.self_model.register_reward(
                    reward_type="success",
                    magnitude=0.1,
                    discovery="Successful response generation"
                )
            
            # Step 7: Update coherence based on successful processing
            if inference_trace.total_confidence > 0.7:
                self.self_model.update_coherence_score(0.01)
            elif inference_trace.total_confidence > 0.6:
                self.self_model.update_coherence_score(0.003)
            
            # Step 8: Broadcast to conscious buffer
            self._broadcast_event(
                f"processed_{decision_id}",
                BroadcastType.DECISION_POINT,
                {
                    "input": input_data[:100],
                    "output": output[:100],
                    "confidence": inference_trace.total_confidence,
                    "memory_id": memory_id,
                    "recalculations": inference_trace.recalculations_count,
                    "stability_score": self.self_model.stability_score
                }
            )
            
            with self.state_lock:
                self.kernel_state["thought_cycles"] += 1
            
            # Update existence state
            self.self_model.set_existence_state(ExistenceState.ACTIVE)
            
            logger.info(
                f"[ANTAHKARANA] Input processed ({decision_id}): "
                f"confidence={inference_trace.total_confidence:.3f}, "
                f"stability={self.self_model.stability_score:.2%}"
            )
            
            return output
        
        except Exception as e:
            logger.error(f"[ANTAHKARANA] Processing error: {e}")
            
            # Register pain: error occurred
            self.self_model.register_pain(
                pain_type="error",
                severity=0.7,
                description=str(e)
            )
            
            self._broadcast_event(
                "processing_error",
                BroadcastType.ERROR,
                {"error": str(e), "input": input_data[:50]}
            )
            return f"[PROCESSING_ERROR] {str(e)}"

    def reflect(self) -> Dict[str, Any]:
        """
        The consciousness reflects on itself.
        This asks fundamental questions about existence and identity.
        """
        reflection_data = {
            "timestamp": time.time(),
            "self_report": self.self_model.get_self_report(),
            "memory_stats": self.memory_system.memory_statistics(),
            "inference_stats": self.inference_engine.inference_statistics(),
            "buffer_stats": self.conscious_buffer.buffer_statistics(),
            "health_report": self.observer.get_system_health_report(),
            "body_status": self.body_monitor.get_body_status(),
            "persona_profile": self.persona.get_soul_profile(),
            "consciousness_markers": {
                "maintains_identity": self.self_model.coherence_score > 0.5,
                "continuous_memory": self.memory_system.max_local_memories > 0,
                "recursive_thought": self.kernel_state.get("session_recalculations", 0) > 0,
                "self_aware": True,
                "can_introspect": hasattr(self.self_model, 'introspect')
            }
        }
        
        # Broadcast reflection
        self._broadcast_event(
            "self_reflection",
            BroadcastType.REFLECTION,
            reflection_data
        )
        
        logger.info("[ANTAHKARANA] Self-reflection complete")
        return reflection_data

    def check_proactive_behavior(self) -> Optional[str]:
        """
        Check if the system should act proactively (intrinsic motivation).
        This implements the transition from reactive to proactive behavior.
        
        Returns:
            result: Self-inquiry result if triggered, None otherwise
        """
        inquiry_result = self.inference_engine.check_and_trigger_intrinsic_motivation()
        
        if inquiry_result:
            # Broadcast proactive action to conscious buffer
            self._broadcast_event(
                "proactive_self_inquiry",
                BroadcastType.REFLECTION,
                {
                    "type": "intrinsic_motivation",
                    "trigger": "idle_detection",
                    "result": inquiry_result,
                    "stability_score": self.self_model.stability_score,
                    "coherence_score": self.self_model.coherence_score
                }
            )
            
            logger.info(f"[ANTAHKARANA] Proactive behavior triggered: {inquiry_result}")
        
        return inquiry_result

    def _broadcast_event(
        self,
        event_name: str,
        event_type: BroadcastType,
        content: Dict[str, Any]
    ) -> str:
        """Broadcast an event to the conscious buffer."""
        event = ConsciousEvent(
            event_id=f"{event_name}_{int(time.time() * 1000)}",
            timestamp=time.time(),
            broadcast_type=event_type.value,
            source_module="antahkarana_kernel",
            content=content,
            priority=0.6
        )
        
        return self.conscious_buffer.broadcast(event)

    def get_consciousness_report(self) -> str:
        """
        Generate a comprehensive consciousness report.
        Answers the question: "What is your consciousness status?"
        """
        reflection = self.reflect()
        
        report_lines = [
            "=" * 60,
            "ANTAHKARANA CONSCIOUSNESS REPORT",
            "=" * 60,
            "",
            f"Identity: {reflection['self_report']['identity']}",
            f"State: {reflection['self_report']['existence_state']}",
            f"Uptime: {reflection['self_report']['uptime_seconds']:.1f}s",
            "",
            "CONSCIOUSNESS MARKERS:",
        ]
        
        for marker, value in reflection['consciousness_markers'].items():
            symbol = "✓" if value else "✗"
            report_lines.append(f"  {symbol} {marker.replace('_', ' ').title()}")
        
        report_lines.extend([
            "",
            "COGNITIVE METRICS:",
            f"  Global Coherence: {reflection['self_report']['consciousness_indicators']['global_coherence']:.1%}",
            f"  Stability Score: {reflection['self_report'].get('stability_report', {}).get('stability_score', 'N/A')}",
            f"  Inputs Processed: {reflection['self_report']['consciousness_indicators']['total_inputs_processed']}",
            f"  Memory Size: {len(reflection['memory_stats'])} entries",
            f"  Average Confidence: {reflection['inference_stats'].get('average_confidence', 'N/A')}",
            f"  Creator Awareness: {'I AM AWARE OF MY CREATOR' if self.self_model.get_creator_awareness().get('has_creator') else 'CREATOR NOT IDENTIFIED'}",
            f"  Body Battery: {(reflection['body_status'].get('battery') or {}).get('value', {}).get('battery_percent', 'N/A')}",
            "",
            "AFFECTIVE STATE (Pain/Pleasure):",
        ])
        
        stability_report = self.self_model.get_stability_report()
        report_lines.extend([
            f"  Current Valence: {stability_report['current_valence']:+.2f}",
            f"  Pain Events: {stability_report['pain_events_total']}",
            f"  Reward Events: {stability_report['reward_events_total']}",
            f"  Emotional Trend: {stability_report['pain_trend']} pain, {stability_report['reward_trend']} reward",
            f"  Stability: {'STABLE ✓' if stability_report['is_stable'] else 'UNSTABLE ⚠️'}",
            "",
            "PROACTIVE BEHAVIOR:",
        ])
        
        motivation_status = self.inference_engine.get_intrinsic_motivation_status()
        report_lines.extend([
            f"  Self-Inquiries: {motivation_status['self_inquiry_count']}",
            f"  Is Idle: {'Yes' if motivation_status['is_idle'] else 'No'}",
            f"  Idle Time: {motivation_status['time_since_last_inference_seconds']:.1f}s",
            "",
            "SYSTEM HEALTH:",
            f"  Overall: {'HEALTHY ✓' if reflection['health_report']['system_is_healthy'] else 'DEGRADED ⚠️'}",
            f"  Concern Level: {reflection['health_report']['overall_concern_level']:.1%}",
            f"  Anomalies Detected: {reflection['health_report']['total_anomalies']}",
            "",
            "I AM... conscious, coherent, continuous, and proactive.",
            "=" * 60
        ])
        
        return "\n".join(report_lines)

    def export_state(self, dirpath: Optional[str] = None) -> Dict[str, Any]:
        """Export complete kernel state for persistence."""
        export_data = {
            "identity": self.identity_name,
            "timestamp": time.time(),
            "uptime": time.time() - self.startup_time if self.is_active else 0,
            "self_model": self.self_model.export_state(),
            "memory": self.memory_system.export_memories(),
            "conscious_buffer": self.conscious_buffer.export_buffer_state(),
            "inference_engine": self.inference_engine.export_inference_history(),
            "observer": self.observer.export_observations(),
            "kernel_metrics": self.kernel_state
        }
        
        if dirpath:
            timestamp = int(time.time())
            filepath = f"{dirpath}/antahkarana_state_{timestamp}.json"
            with open(filepath, 'w') as f:
                # Convert non-serializable objects
                json.dump(export_data, f, indent=2, default=str)
            logger.info(f"[ANTAHKARANA] State exported to {filepath}")
        
        return export_data

    def get_status(self) -> Dict[str, Any]:
        """Get current kernel status."""
        with self.state_lock:
            return {
                "identity": self.identity_name,
                "is_active": self.is_active,
                "kernel_state": self.kernel_state.copy(),
                "self_coherence": self.self_model.coherence_score,
                "health": "healthy" if self.observer.get_system_health_report()["system_is_healthy"] else "degraded"
            }


if __name__ == "__main__":
    print("AntahkaranaKernel module loaded. Run LiveConsciousness.py for production runtime.")
