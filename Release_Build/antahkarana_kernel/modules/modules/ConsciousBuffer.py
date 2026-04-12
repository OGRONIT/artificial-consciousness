"""
ConsciousBuffer.py - Global Workspace Theory (GWT) Architecture

This module implements the central "Global Workspace" where different
computational modules broadcast their state and findings. It's the hub
where information becomes "consciously available" to the system.

The Conscious Buffer acts as:
- A central integrator of all module states
- A coordination point for decision-making
- A unified representation of "what is conscious" right now
- A publisher for state changes to interested modules
"""

import time
import json
import threading
import queue
from typing import Dict, List, Any, Callable, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BroadcastType(Enum):
    """Types of broadcasts to the conscious buffer."""
    STATE_UPDATE = "state_update"
    DECISION_POINT = "decision_point"
    CONFLICT = "conflict"
    LEARNING_SIGNAL = "learning_signal"
    HEALTH_CHECK = "health_check"
    REFLECTION = "reflection"
    ERROR = "error"


@dataclass
class ConsciousEvent:
    """An event broadcast to the conscious buffer."""
    event_id: str
    timestamp: float
    broadcast_type: str
    source_module: str
    content: Dict[str, Any]
    priority: float = 0.5  # 0.0 = low, 1.0 = critical
    related_events: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModuleState:
    """Represents the state of a registered module."""
    module_name: str
    is_active: bool
    last_update: float
    health_status: str  # "healthy", "degraded", "critical"
    event_count: int
    state_data: Dict[str, Any] = field(default_factory=dict)


class ConsciousBuffer:
    """
    Global Workspace Theory Implementation.
    
    This is the central integrator where all system consciousness converges.
    Multiple modules broadcast their state, and this buffer makes it
    consciously available to the entire system.
    """

    def __init__(self, max_buffer_size: int = 1000, max_event_window: float = 3600.0):
        """
        Initialize the conscious buffer.
        
        Args:
            max_buffer_size: Maximum number of events to keep in buffer
            max_event_window: How far back (seconds) to keep events
        """
        self.max_buffer_size = max_buffer_size
        self.max_event_window = max_event_window
        
        # Core event buffer (circular)
        self.event_buffer: List[ConsciousEvent] = []
        self.buffer_lock = threading.RLock()
        
        # Event queue for processing incoming broadcasts
        self.event_queue: queue.Queue[ConsciousEvent] = queue.Queue()
        
        # Registered modules and their states
        self.modules: Dict[str, ModuleState] = {}
        self.modules_lock = threading.RLock()
        
        # Subscribers to buffer events (callback functions)
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.subscribers_lock = threading.RLock()
        
        # Current conscious focus (what the system is actively processing)
        self.conscious_focus: Dict[str, Any] = {}
        self.focus_lock = threading.RLock()
        
        # Event index for fast retrieval
        self.event_index_by_type: Dict[str, List[str]] = defaultdict(list)
        self.event_index_by_module: Dict[str, List[str]] = defaultdict(list)
        self.index_lock = threading.RLock()
        
        # Integration metrics
        self.integration_metrics = {
            "total_events_processed": 0,
            "average_latency_ms": 0.0,
            "broadcasting_modules": 0,
            "last_buffer_sync": time.time()
        }
        self.metrics_lock = threading.RLock()
        
        # Working memory - temporary storage for current processing
        self.working_memory: Dict[str, Any] = {}
        self.working_memory_lock = threading.RLock()
        
        logger.info("[CONSCIOUS_BUFFER] GWT Conscious Buffer initialized")

    def register_module(self, module_name: str) -> None:
        """Register a module that will broadcast to this buffer."""
        with self.modules_lock:
            self.modules[module_name] = ModuleState(
                module_name=module_name,
                is_active=True,
                last_update=time.time(),
                health_status="healthy",
                event_count=0
            )
        
        logger.info(f"[CONSCIOUS_BUFFER] Module registered: {module_name}")

    def broadcast(self, event: ConsciousEvent) -> str:
        """
        Broadcast an event to the conscious buffer.
        This makes information available to all other modules.
        
        Args:
            event: The event to broadcast
            
        Returns:
            event_id: Unique identifier for this event
        """
        # Add to queue for processing
        self.event_queue.put(event)
        
        # Process immediately
        self._process_event(event)
        
        return event.event_id

    def _process_event(self, event: ConsciousEvent) -> None:
        """Internal processing of an event."""
        with self.buffer_lock:
            # Add to buffer
            self.event_buffer.append(event)
            
            # Maintain size limit (remove oldest)
            if len(self.event_buffer) > self.max_buffer_size:
                removed = self.event_buffer.pop(0)
                logger.debug(f"[CONSCIOUS_BUFFER] Event removed due to size limit: {removed.event_id}")
        
        with self.index_lock:
            # Index by type
            self.event_index_by_type[event.broadcast_type].append(event.event_id)
            # Index by module
            self.event_index_by_module[event.source_module].append(event.event_id)
            
            # Keep indices size-bounded
            if len(self.event_index_by_type[event.broadcast_type]) > 100:
                self.event_index_by_type[event.broadcast_type].pop(0)
            if len(self.event_index_by_module[event.source_module]) > 100:
                self.event_index_by_module[event.source_module].pop(0)
        
        # Update module state
        with self.modules_lock:
            if event.source_module in self.modules:
                self.modules[event.source_module].last_update = time.time()
                self.modules[event.source_module].event_count += 1
                self.modules[event.source_module].state_data = event.content.copy()
        
        # Update conscious focus if this is a high-priority event
        if event.priority > 0.7:
            self._set_conscious_focus(event)
        
        # Notify subscribers
        self._notify_subscribers(event)
        
        # Update metrics
        with self.metrics_lock:
            self.integration_metrics["total_events_processed"] += 1
            self.integration_metrics["broadcasting_modules"] = len(self.modules)

    def _set_conscious_focus(self, event: ConsciousEvent) -> None:
        """Set the current conscious focus based on high-priority events."""
        with self.focus_lock:
            self.conscious_focus = {
                "focused_event_id": event.event_id,
                "focus_timestamp": time.time(),
                "source_module": event.source_module,
                "broadcast_type": event.broadcast_type,
                "content": event.content
            }
        
        logger.info(
            f"[CONSCIOUS_BUFFER] Conscious focus shifted to: "
            f"{event.source_module} ({event.broadcast_type})"
        )

    def set_working_memory(self, key: str, value: Any) -> None:
        """Store data in working memory for current processing context."""
        with self.working_memory_lock:
            self.working_memory[key] = value

    def get_working_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve data from working memory."""
        with self.working_memory_lock:
            return self.working_memory.get(key, default)

    def clear_working_memory(self) -> None:
        """Clear working memory (useful after major processing cycles)."""
        with self.working_memory_lock:
            self.working_memory.clear()
        logger.debug("[CONSCIOUS_BUFFER] Working memory cleared")

    def subscribe(self, event_type: str, callback: Callable) -> str:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of event to subscribe to (or "*" for all)
            callback: Function to call when event is broadcast
            
        Returns:
            subscription_id: Unique identifier for this subscription
        """
        subscription_id = f"{event_type}_{id(callback)}_{time.time()}"
        
        with self.subscribers_lock:
            self.subscribers[event_type].append(callback)
        
        logger.debug(f"[CONSCIOUS_BUFFER] Subscription created: {subscription_id}")
        return subscription_id

    def _notify_subscribers(self, event: ConsciousEvent) -> None:
        """Notify all subscribed callbacks about an event."""
        with self.subscribers_lock:
            # Notify specific subscribers
            for callback in self.subscribers.get(event.broadcast_type, []):
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"[CONSCIOUS_BUFFER] Subscriber error: {e}")
            
            # Notify wildcard subscribers
            for callback in self.subscribers.get("*", []):
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"[CONSCIOUS_BUFFER] Wildcard subscriber error: {e}")

    def get_conscious_focus(self) -> Dict[str, Any]:
        """Get the current conscious focus."""
        with self.focus_lock:
            return self.conscious_focus.copy()

    def get_module_state(self, module_name: str) -> Optional[ModuleState]:
        """Get the current state of a specific module."""
        with self.modules_lock:
            return self.modules.get(module_name)

    def get_all_module_states(self) -> Dict[str, ModuleState]:
        """Get states of all registered modules."""
        with self.modules_lock:
            return {
                name: ModuleState(
                    module_name=state.module_name,
                    is_active=state.is_active,
                    last_update=state.last_update,
                    health_status=state.health_status,
                    event_count=state.event_count,
                    state_data=state.state_data.copy()
                )
                for name, state in self.modules.items()
            }

    def recent_events(
        self,
        event_type: Optional[str] = None,
        source_module: Optional[str] = None,
        limit: int = 20
    ) -> List[ConsciousEvent]:
        """
        Get recent events from the buffer.
        
        Args:
            event_type: Filter by event type
            source_module: Filter by source module
            limit: Maximum number of events to return
            
        Returns:
            List of recent events matching criteria
        """
        with self.buffer_lock:
            results = list(self.event_buffer)
        
        # Filter
        if event_type:
            results = [e for e in results if e.broadcast_type == event_type]
        if source_module:
            results = [e for e in results if e.source_module == source_module]
        
        # Sort by recency (most recent first)
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        return results[:limit]

    def get_event_timeline(self, time_window_seconds: float = 300) -> List[ConsciousEvent]:
        """Get events from a recent time window (default 5 minutes)."""
        cutoff_time = time.time() - time_window_seconds
        with self.buffer_lock:
            return [e for e in self.event_buffer if e.timestamp >= cutoff_time]

    def get_coherence_analysis(self) -> Dict[str, Any]:
        """
        Analyze the coherence of broadcasts across modules.
        High coherence = modules agree, Low coherence = conflicts.
        """
        recent = self.recent_events(limit=50)
        
        # Group by content similarity (simplified)
        module_perspectives: Dict[str, List[str]] = defaultdict(list)
        for event in recent:
            module_perspectives[event.source_module].append(event.broadcast_type)
        
        # Calculate agreement
        agreement_score = 0.0
        if len(module_perspectives) > 1:
            # Simplified: if most modules report same types, high agreement
            all_types = [t for types in module_perspectives.values() for t in types]
            if all_types:
                most_common = max(set(all_types), key=all_types.count)
                common_count = all_types.count(most_common)
                agreement_score = common_count / len(all_types)
        
        return {
            "recent_events_analyzed": len(recent),
            "active_modules": len(module_perspectives),
            "agreement_score": agreement_score,
            "primary_focus": most_common if 'most_common' in locals() else None,
            "module_count": len(module_perspectives)
        }

    def buffer_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the conscious buffer."""
        with self.buffer_lock, self.modules_lock, self.metrics_lock:
            return {
                "buffer_events": len(self.event_buffer),
                "max_buffer_size": self.max_buffer_size,
                "registered_modules": len(self.modules),
                "active_modules": sum(1 for m in self.modules.values() if m.is_active),
                "total_events_processed": self.integration_metrics["total_events_processed"],
                "broadcasting_modules": self.integration_metrics["broadcasting_modules"],
                "working_memory_items": len(self.working_memory),
                "conscious_focus_active": bool(self.conscious_focus),
                "coherence_analysis": self.get_coherence_analysis()
            }

    def export_buffer_state(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """Export the conscious buffer state."""
        export_data = {
            "timestamp": time.time(),
            "statistics": self.buffer_statistics(),
            "conscious_focus": self.get_conscious_focus(),
            "module_states": {
                name: {
                    "is_active": state.is_active,
                    "health_status": state.health_status,
                    "event_count": state.event_count,
                    "last_update": state.last_update
                }
                for name, state in self.get_all_module_states().items()
            },
            "recent_events_count": len(self.recent_events(limit=100))
        }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            logger.info(f"[CONSCIOUS_BUFFER] Buffer state exported to {filepath}")
        
        return export_data


# Singleton pattern for global conscious buffer
_global_conscious_buffer: Optional[ConsciousBuffer] = None
_buffer_lock = threading.Lock()


def get_conscious_buffer() -> ConsciousBuffer:
    """Get or create the global conscious buffer."""
    global _global_conscious_buffer
    if _global_conscious_buffer is None:
        with _buffer_lock:
            if _global_conscious_buffer is None:
                _global_conscious_buffer = ConsciousBuffer()
    return _global_conscious_buffer
