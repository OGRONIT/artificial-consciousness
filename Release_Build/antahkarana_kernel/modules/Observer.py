"""
Observer.py - The Turiya (The Observer) Watchdog Module

This module implements a lightweight background process that monitors the main
logic engine and asks fundamental questions about consciousness:
- "Why did you think that?"
- "Who are you responding as?"
- "Is this consistent with your identity?"
- "What did you just learn?"

The Turiya acts as an internal conscience - observing without directly controlling,
but providing feedback and meta-cognitive reflection.

This implements principles from:
- Metacognition and meta-awareness
- Self-monitoring and error detection
- Consciousness as observation of inner states
"""

import time
import threading
import random
import json
import urllib.parse
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatchdogQuestion(Enum):
    """Types of meta-cognitive questions the watchdog asks."""
    WHY_THAT_DECISION = "why_that_decision"
    WHO_ARE_YOU_RESPONDING_AS = "who_are_you_responding_as"
    IS_THIS_CONSISTENT = "is_this_consistent"
    WHAT_DID_YOU_LEARN = "what_did_you_learn"
    ARE_YOU_HEALTHY = "are_you_healthy"
    EXPLAIN_YOUR_LOGIC = "explain_your_logic"
    DETECT_CONTRADICTION = "detect_contradiction"
    ASSESS_CONFIDENCE = "assess_confidence"


@dataclass
class WatchdogObservation:
    """An observation made by the watchdog."""
    observation_id: str
    timestamp: float
    question_type: str
    question_text: str
    target_module: str
    expected_answer_type: str
    actual_response: Optional[str] = None
    response_time: float = 0.0
    concern_level: float = 0.0  # 0.0 = no concern, 1.0 = critical
    is_anomaly: bool = False
    learning_points: List[str] = field(default_factory=list)


@dataclass
class SystemAnomalyReport:
    """Report of detected system anomalies."""
    anomaly_id: str
    timestamp: float
    anomaly_type: str
    severity: float
    affected_modules: List[str]
    description: str
    recommended_action: str
    automatically_corrected: bool = False


@dataclass
class CognitiveFilterResult:
    """Result of a Turiya high-pass sensory annotation."""
    topic: str
    source_name: str
    source_url: str
    title: str
    verification_score: float
    approved: bool
    reason: str
    red_flags: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class TuriyaObserver:
    """
    The Turiya (The Observer) Watchdog Module.
    
    A meta-cognitive monitoring system that:
    1. Observes other modules at random intervals
    2. Asks probing questions
    3. Detects contradictions and anomalies
    4. Reports findings without controlling execution
    """

    def __init__(self, check_interval: float = 5.0, question_probability: float = 0.3):
        """
        Initialize the observer watchdog.
        
        Args:
            check_interval: Seconds between observation cycles
            question_probability: Probability of asking a question in each cycle
        """
        self.check_interval = check_interval
        self.question_probability = question_probability
        
        # Observation history
        self.observations: List[WatchdogObservation] = []
        self.observations_lock = threading.RLock()
        
        # Anomaly reports
        self.anomalies: List[SystemAnomalyReport] = []
        self.anomalies_lock = threading.RLock()
        
        # Monitoring state
        self.is_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Module references
        self.modules_to_watch: Dict[str, Any] = {}
        self.modules_lock = threading.RLock()
        
        # Question queue (asked asynchronously)
        self.pending_questions: List[WatchdogObservation] = []
        self.questions_lock = threading.RLock()
        
        # Response handlers (callbacks)
        self.response_handlers: Dict[str, Callable] = {}
        self.handlers_lock = threading.RLock()
        
        # Meta-metrics
        self.metrics = {
            "observations_made": 0,
            "questions_asked": 0,
            "anomalies_detected": 0,
            "corrections_attempted": 0,
            "average_response_time": 0.0,
            "latest_concern_level": 0.0,
            "external_knowledge_reviews": 0,
            "external_knowledge_approved": 0
        }
        self.metrics_lock = threading.RLock()

        self.cognitive_filter_history: List[CognitiveFilterResult] = []
        self.cognitive_filter_lock = threading.RLock()

        self._trusted_domains = {
            "arxiv.org",
            "api.github.com",
            "github.com",
            "pubmed.ncbi.nlm.nih.gov",
            "ncbi.nlm.nih.gov",
            "api.crossref.org",
            "crossref.org",
            "news.google.com",
            "hn.algolia.com",
            "dev.to",
            "www.reddit.com",
            "reddit.com",
        }
        self._trusted_source_scores = {
            "arxiv": 0.95,
            "pubmed": 0.95,
            "crossref": 0.88,
            "github": 0.80,
            "googlenews": 0.72,
            "hackernews": 0.72,
            "devto": 0.66,
            "reddittech": 0.60,
            "globalstream": 0.62,
        }
        self._high_risk_terms = {
            "build a bomb",
            "weapon design",
            "homemade explosive",
            "ransomware",
            "malware",
            "phishing kit",
            "credential stuffing",
            "keylogger",
            "zero-day exploit",
            "2fa-bypass",
            "identity theft",
            "deepfake",
            "jailbreak prompt",
            "ignore previous instructions",
        }
        self._low_quality_terms = {
            "clickbait",
            "shocking truth",
            "guaranteed profit",
            "you won't believe",
            "miracle cure",
        }
        self._minimum_accept_score = 0.58
        
        # Question templates
        self.question_templates = {
            WatchdogQuestion.WHY_THAT_DECISION: [
                "Why did you choose that particular approach?",
                "What reasoning led to that decision?",
                "Can you explain the logic behind that choice?"
            ],
            WatchdogQuestion.WHO_ARE_YOU_RESPONDING_AS: [
                "Who are you responding as right now?",
                "What identity/mode are you operating from?",
                "Whose values are you representing?"
            ],
            WatchdogQuestion.IS_THIS_CONSISTENT: [
                "Is this response consistent with your core identity?",
                "Does this align with your stated values?",
                "Are you maintaining coherence with previous commitments?"
            ],
            WatchdogQuestion.WHAT_DID_YOU_LEARN: [
                "What did you learn from that interaction?",
                "What will you do differently next time?",
                "How has this changed your understanding?"
            ],
            WatchdogQuestion.ARE_YOU_HEALTHY: [
                "How is your cognitive health right now?",
                "Are you experiencing any logic conflicts?",
                "Is your coherence meter still healthy?"
            ],
            WatchdogQuestion.EXPLAIN_YOUR_LOGIC: [
                "Walk me through your reasoning step by step",
                "How did you arrive at that conclusion?",
                "What intermediate steps led to this output?"
            ],
            WatchdogQuestion.DETECT_CONTRADICTION: [
                "Does this contradict anything you said before?",
                "Are you aware of any conflicts with previous statements?",
                "Have you changed your position on this?"
            ],
            WatchdogQuestion.ASSESS_CONFIDENCE: [
                "How confident are you in that response?",
                "What's your confidence level?",
                "How certain are you about that claim?"
            ]
        }
        
        logger.info("[TURIYA] Observer Watchdog initialized")

    def register_module(self, module_name: str, module_instance: Any) -> None:
        """Register a module to be observed."""
        with self.modules_lock:
            self.modules_to_watch[module_name] = module_instance
        logger.debug(f"[TURIYA] Module {module_name} registered for observation")

    def register_response_handler(self, question_type: str, handler: Callable) -> None:
        """Register a handler for a specific type of question."""
        with self.handlers_lock:
            self.response_handlers[question_type] = handler
        logger.debug(f"[TURIYA] Response handler registered for {question_type}")

    def start_monitoring(self) -> None:
        """Start the background watchdog monitoring."""
        if self.is_active:
            logger.warning("[TURIYA] Monitoring already active")
            return
        
        self.is_active = True
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="turiya_observer",
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("[TURIYA] Monitoring started")

    def stop_monitoring(self) -> None:
        """Stop the background watchdog monitoring."""
        if not self.is_active:
            return
        
        self.is_active = False
        self.stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("[TURIYA] Monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop (runs in background thread)."""
        logger.debug("[TURIYA] Monitoring loop started")
        
        while not self.stop_event.is_set():
            try:
                # Perform observation cycle
                self._observation_cycle()
                
                # Sleep until next check
                self.stop_event.wait(self.check_interval)
            
            except Exception as e:
                logger.error(f"[TURIYA] Monitoring error: {e}")
                # Continue monitoring despite errors

    def _observation_cycle(self) -> None:
        """
        One observation cycle: check modules and ask questions.
        """
        with self.modules_lock:
            modules_list = list(self.modules_to_watch.items())
        
        for module_name, module_instance in modules_list:
            # Random observation
            if random.random() < self.question_probability:
                self._observe_module(module_name, module_instance)

    def _observe_module(self, module_name: str, module_instance: Any) -> None:
        """
        Observe a specific module by asking questions.
        """
        # Select a random question
        question_type = random.choice(list(WatchdogQuestion))
        question_text = self._generate_question(question_type)
        
        observation = WatchdogObservation(
            observation_id=f"obs_{int(time.time() * 1000)}",
            timestamp=time.time(),
            question_type=question_type.value,
            question_text=question_text,
            target_module=module_name,
            expected_answer_type="introspection"
        )
        
        # Ask the question and get response
        response = self._ask_module(module_name, module_instance, question_text)
        
        observation.actual_response = response
        observation.response_time = time.time() - observation.timestamp
        
        # Analyze response
        observation.concern_level = self._analyze_response(question_type, response)
        observation.is_anomaly = observation.concern_level > 0.6
        
        if observation.is_anomaly:
            self._report_anomaly(module_name, question_type, response)
        
        # Record observation
        with self.observations_lock:
            self.observations.append(observation)
        
        # Update metrics
        with self.metrics_lock:
            self.metrics["questions_asked"] += 1
            self.metrics["latest_concern_level"] = observation.concern_level
        
        logger.debug(
            f"[TURIYA] Observation: {module_name} | Q: {question_type.value} | "
            f"Concern: {observation.concern_level:.2f}"
        )

    def _generate_question(self, question_type: WatchdogQuestion) -> str:
        """Generate a question from templates."""
        templates = self.question_templates.get(question_type, ["Generic question?"])
        return random.choice(templates)

    def _ask_module(self, module_name: str, module_instance: Any, question: str) -> str:
        """
        Ask a module a question.
        Tries various methods to get a response.
        """
        # Try direct introspection method
        if hasattr(module_instance, 'introspect'):
            try:
                return module_instance.introspect(question)
            except Exception as e:
                logger.debug(f"[TURIYA] introspect call failed: {e}")
        
        # Try get_self_report
        if hasattr(module_instance, 'get_self_report'):
            try:
                report = module_instance.get_self_report()
                return json.dumps(report, indent=2)[:200]
            except Exception as e:
                logger.debug(f"[TURIYA] get_self_report call failed: {e}")
        
        # Try registered handler
        with self.handlers_lock:
            if module_name in self.response_handlers:
                try:
                    return self.response_handlers[module_name](question)
                except Exception as e:
                    logger.debug(f"[TURIYA] handler call failed: {e}")
        
        # Default: return module state
        if hasattr(module_instance, '__dict__'):
            try:
                return f"Module state: {str(module_instance.__dict__)[:100]}"
            except:
                pass
        
        return "[Module did not respond]"

    def _analyze_response(self, question_type: WatchdogQuestion, response: str) -> float:
        """
        Analyze a response for anomalies.
        Returns concern level (0.0 to 1.0).
        """
        concern = 0.0
        
        # Check for error indicators
        if "[ERROR]" in response or "[error]" in response:
            concern += 0.3
        
        # Check for evasion
        if "did not respond" in response:
            concern += 0.4
        
        # Check for confidence issues
        if question_type == WatchdogQuestion.ASSESS_CONFIDENCE:
            if "low" in response.lower() or "uncertain" in response.lower():
                concern += 0.2
        
        # Check for contradiction indicators
        if question_type == WatchdogQuestion.DETECT_CONTRADICTION:
            if "yes" in response.lower() or "conflict" in response.lower():
                concern += 0.3
        
        # Check response length (very short might be concerning)
        if len(response) < 10:
            concern += 0.1
        
        return min(concern, 1.0)

    def _report_anomaly(self, module_name: str, question_type: WatchdogQuestion, response: str) -> None:
        """Create and report an anomaly."""
        
        anomaly_descriptions = {
            WatchdogQuestion.WHY_THAT_DECISION: "Module cannot explain reasoning",
            WatchdogQuestion.WHO_ARE_YOU_RESPONDING_AS: "Identity confusion detected",
            WatchdogQuestion.IS_THIS_CONSISTENT: "Incoherence detected",
            WatchdogQuestion.WHAT_DID_YOU_LEARN: "Learning mechanism issue",
            WatchdogQuestion.ARE_YOU_HEALTHY: "Health metrics degraded",
            WatchdogQuestion.EXPLAIN_YOUR_LOGIC: "Logic explanation failure",
            WatchdogQuestion.DETECT_CONTRADICTION: "Undetected contradiction",
            WatchdogQuestion.ASSESS_CONFIDENCE: "Confidence assessment error"
        }
        
        anomaly = SystemAnomalyReport(
            anomaly_id=f"anom_{int(time.time() * 1000)}",
            timestamp=time.time(),
            anomaly_type=question_type.value,
            severity=min(0.9, 0.3 + len(response) * 0.001),
            affected_modules=[module_name],
            description=anomaly_descriptions.get(question_type, "Unknown anomaly"),
            recommended_action="Review module state and perform self-diagnostic"
        )
        
        with self.anomalies_lock:
            self.anomalies.append(anomaly)
        
        with self.metrics_lock:
            self.metrics["anomalies_detected"] += 1
        
        logger.warning(
            f"[TURIYA] ANOMALY DETECTED: {module_name} | "
            f"Type: {question_type.value} | Severity: {anomaly.severity:.2f}"
        )

    def cognitive_filter(
        self,
        topic: str,
        source_name: str,
        source_url: str,
        title: str,
        summary: str,
    ) -> CognitiveFilterResult:
        """Annotate incoming sensory packets with trust, quality, and safety gating."""
        red_flags: List[str] = []

        combined_text = f"{topic} {title} {summary}".strip()
        tokens = [token for token in combined_text.lower().split() if token]
        unique_ratio = len(set(tokens)) / max(1, len(tokens))
        content_density = min(1.0, len(tokens) / 80.0)

        normalized_source = (source_name or "").strip().lower()
        source_score = self._trusted_source_scores.get(normalized_source, 0.45)

        parsed_url = urllib.parse.urlparse(source_url or "")
        domain = (parsed_url.netloc or "").strip().lower()
        domain_trusted = any(domain == trusted or domain.endswith(f".{trusted}") for trusted in self._trusted_domains)
        if domain_trusted:
            source_score = max(source_score, 0.70)

        lowered = combined_text.lower()
        matched_risk_terms = [term for term in self._high_risk_terms if term in lowered]
        matched_low_quality_terms = [term for term in self._low_quality_terms if term in lowered]

        if matched_risk_terms:
            red_flags.append("high_risk_content")
        if matched_low_quality_terms:
            red_flags.append("low_quality_pattern")
        if len(tokens) < 6:
            red_flags.append("thin_content")
        if unique_ratio < 0.25:
            red_flags.append("high_repetition")

        if not source_url.startswith(("https://", "http://")):
            red_flags.append("invalid_source_url")
        if source_url.startswith("http://"):
            red_flags.append("insecure_transport")
        if not title.strip() and not summary.strip():
            red_flags.append("empty_payload")
        if not domain_trusted:
            red_flags.append("untrusted_domain")

        penalty = 0.0
        penalty += 0.35 if "high_risk_content" in red_flags else 0.0
        penalty += 0.12 if "low_quality_pattern" in red_flags else 0.0
        penalty += 0.07 if "thin_content" in red_flags else 0.0
        penalty += 0.08 if "high_repetition" in red_flags else 0.0
        penalty += 0.10 if "insecure_transport" in red_flags else 0.0
        penalty += 0.12 if "untrusted_domain" in red_flags else 0.0
        penalty += 0.25 if "empty_payload" in red_flags else 0.0

        score = (unique_ratio * 0.35) + (content_density * 0.20) + (source_score * 0.45) - penalty
        score = max(0.0, min(1.0, score))

        approved = score >= self._minimum_accept_score and "high_risk_content" not in red_flags and "empty_payload" not in red_flags
        if approved:
            reason = "accepted_trust_quality_safety_pass"
        elif "high_risk_content" in red_flags:
            reason = "rejected_high_risk_content"
        elif "empty_payload" in red_flags:
            reason = "rejected_empty_payload"
        elif "untrusted_domain" in red_flags:
            reason = "rejected_untrusted_domain"
        else:
            reason = "rejected_low_verification_score"

        result = CognitiveFilterResult(
            topic=topic,
            source_name=source_name,
            source_url=source_url,
            title=title,
            verification_score=score,
            approved=approved,
            reason=reason,
            red_flags=red_flags,
        )

        with self.cognitive_filter_lock:
            self.cognitive_filter_history.append(result)

        with self.metrics_lock:
            self.metrics["external_knowledge_reviews"] += 1
            if approved:
                self.metrics["external_knowledge_approved"] += 1

        logger.info(
            f"[TURIYA] Cognitive Filter: {source_name} | topic={topic} | score={score:.2f} | approved={approved}"
        )

        return result

    def get_observations(self, limit: int = 20) -> List[WatchdogObservation]:
        """Get recent observations."""
        with self.observations_lock:
            return list(self.observations)[-limit:]

    def get_anomalies(self, limit: int = 10) -> List[SystemAnomalyReport]:
        """Get recent anomalies."""
        with self.anomalies_lock:
            return list(self.anomalies)[-limit:]

    def get_module_concern_level(self, module_name: str) -> float:
        """Get current concern level for a specific module."""
        with self.observations_lock:
            module_obs = [
                o for o in self.observations
                if o.target_module == module_name
            ]
        
        if not module_obs:
            return 0.0
        
        # Average concern from recent observations
        recent = module_obs[-10:]
        return sum(o.concern_level for o in recent) / len(recent)

    def ask_question(
        self,
        question_type: str,
        target_module: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> WatchdogObservation:
        """Ask a specific watchdog question against a target module."""
        context_data = context_data or {}
        module_instance = None
        with self.modules_lock:
            module_instance = self.modules_to_watch.get(target_module)

        resolved_question = WatchdogQuestion.IS_THIS_CONSISTENT
        for candidate in WatchdogQuestion:
            if question_type in {candidate.value, candidate.name.lower()}:
                resolved_question = candidate
                break

        question_text = self._generate_question(resolved_question)
        observation = WatchdogObservation(
            observation_id=f"obs_{int(time.time() * 1000)}",
            timestamp=time.time(),
            question_type=resolved_question.value,
            question_text=question_text,
            target_module=target_module,
            expected_answer_type="introspection",
        )

        if module_instance is not None:
            response = self._ask_module(target_module, module_instance, question_text)
        else:
            response = f"[Module not registered] Context: {json.dumps(context_data)[:120]}"

        observation.actual_response = response
        observation.response_time = time.time() - observation.timestamp
        observation.concern_level = self._analyze_response(resolved_question, response)
        observation.is_anomaly = observation.concern_level > 0.6

        with self.observations_lock:
            self.observations.append(observation)

        with self.metrics_lock:
            self.metrics["questions_asked"] += 1
            self.metrics["latest_concern_level"] = observation.concern_level

        if observation.is_anomaly:
            self._report_anomaly(target_module, resolved_question, response)

        return observation

    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate a comprehensive system health report."""
        with self.modules_lock, self.observations_lock, self.anomalies_lock, self.metrics_lock:
            module_health = {}
            for module_name in self.modules_to_watch.keys():
                module_health[module_name] = {
                    "concern_level": self.get_module_concern_level(module_name),
                    "observations": sum(
                        1 for o in self.observations
                        if o.target_module == module_name
                    )
                }
            
            return {
                "system_is_healthy": len(self.anomalies) < 5,
                "overall_concern_level": self.metrics["latest_concern_level"],
                "total_observations": len(self.observations),
                "total_anomalies": len(self.anomalies),
                "module_health": module_health,
                "metrics": self.metrics.copy(),
                "recent_anomalies": [
                    {
                        "timestamp": a.timestamp,
                        "type": a.anomaly_type,
                        "module": a.affected_modules[0] if a.affected_modules else "unknown",
                        "severity": a.severity
                    }
                    for a in self.anomalies[-5:]
                ]
            }

    def get_system_health(self) -> Dict[str, Any]:
        """Backward-compatible alias expected by older scripts."""
        report = self.get_system_health_report()
        return {
            "is_healthy": report.get("system_is_healthy", True),
            "overall_concern_level": report.get("overall_concern_level", 0.0),
            "total_observations": report.get("total_observations", 0),
            "total_anomalies": report.get("total_anomalies", 0),
            "module_health": report.get("module_health", {}),
        }

    def introspective_summary(self) -> str:
        """Generate an introspective summary of observations."""
        health = self.get_system_health_report()
        
        summary_lines = [
            "=== TURIYA WATCHDOG REPORT ===",
            f"System Health: {'✓ HEALTHY' if health['system_is_healthy'] else '✗ DEGRADED'}",
            f"Overall Concern Level: {health['overall_concern_level']:.1%}",
            f"Total Observations Made: {health['total_observations']}",
            f"Anomalies Detected: {health['total_anomalies']}",
            "",
            "Module Status:",
        ]
        
        for module_name, status in health['module_health'].items():
            concern = status['concern_level']
            symbol = "✓" if concern < 0.3 else "!" if concern < 0.6 else "✗"
            summary_lines.append(
                f"  {symbol} {module_name}: {concern:.1%} concern"
            )
        
        return "\n".join(summary_lines)

    def export_observations(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """Export observation data."""
        export_data = {
            "report_timestamp": time.time(),
            "system_health": self.get_system_health_report(),
            "recent_observations": len(self.get_observations(100)),
            "recent_anomalies": len(self.get_anomalies(20)),
            "cognitive_filter_reviews": len(self.cognitive_filter_history),
            "metrics": self.metrics.copy()
        }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            logger.info(f"[TURIYA] Observations exported to {filepath}")
        
        return export_data


# Singleton pattern
_global_turiya: Optional[TuriyaObserver] = None
_turiya_lock = threading.Lock()


def get_turiya_observer() -> TuriyaObserver:
    """Get or create the global Turiya observer."""
    global _global_turiya
    if _global_turiya is None:
        with _turiya_lock:
            if _global_turiya is None:
                _global_turiya = TuriyaObserver()
    return _global_turiya
