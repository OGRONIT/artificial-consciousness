"""
MemoryContinuity.py - The Chitta (Experiential Memory) Module

This module implements a persistent memory system that stores not just facts,
but the meta-data of experience:
- Was the interaction successful?
- Did it cause a logic conflict?
- How did the Self-Model feel about this?

The Chitta acts as the long-term episodic memory that provides continuity
and learning across time. It integrates with vector databases for semantic search.

This module prepares the foundation for external vector DB integration
(Pinecone, Milvus, Weaviate, etc.)
"""

import time
import json
import hashlib
import threading
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import heapq
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionOutcome(Enum):
    """Possible outcomes of an interaction."""
    SUCCESS = "success"
    PARTIAL = "partial"
    CONFLICT = "conflict"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ExperienceMeta:
    """Meta-data about an experience/interaction."""
    interaction_id: str
    timestamp: float
    content: str
    interaction_type: str
    outcome: str  # InteractionOutcome
    success_score: float  # 0.0 to 1.0
    self_model_coherence_before: float
    self_model_coherence_after: float
    logic_conflicts_triggered: int
    emotional_valence: float  # -1.0 (negative) to 1.0 (positive)
    embedding_vector: Optional[List[float]] = None
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    learning_value: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryCluster:
    """A semantic cluster of related memories."""
    cluster_id: str
    created_at: float
    theme: str
    memory_ids: List[str]
    centroid_embedding: Optional[List[float]] = None
    coherence_score: float = 0.5
    access_count: int = 0


@dataclass
class ExternalKnowledgeFact:
    """A verified fact learned from an external source."""
    fact_id: str
    topic: str
    title: str
    summary: str
    source_name: str
    source_url: str
    verification_score: float
    approved_by_turiya: bool
    filter_reason: str
    integrated_at: float
    self_model_reference: Optional[str] = None
    chitta_memory_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExternalKnowledgeCluster:
    """A semantic cluster of externally learned facts."""
    cluster_id: str
    created_at: float
    topic: str
    fact_ids: List[str]
    source_urls: List[str]
    average_verification_score: float = 0.0
    access_count: int = 0


class ChittaMemoryDB:
    """
    The Chitta (Experiential Memory) Module.
    
    Manages episodic memory with meta-data tracking.
    Provides local in-memory storage with preparation for vector DB integration.
    """

    def __init__(self, max_local_memories: int = 10000):
        """
        Initialize the memory system.
        
        Args:
            max_local_memories: Maximum memories to keep in local storage
        """
        self.kernel_root_dir = Path(__file__).resolve().parents[1]
        self.shadow_memory_dir = self.kernel_root_dir / "evolution_vault" / "shadow_memory"
        self.shadow_memory_dir.mkdir(parents=True, exist_ok=True)
        self.shadow_memory_log = self.shadow_memory_dir / "shadow_memory.jsonl"
        self.dynamic_capacity_refresh_seconds = 300.0
        self.last_dynamic_capacity_refresh = 0.0
        self.max_local_memories = max(max_local_memories, self._derive_dynamic_memory_capacity())
        
        # Core memory storage
        self.memories: Dict[str, ExperienceMeta] = {}
        self.memory_lock = threading.RLock()
        
        # Memory clusters for semantic grouping
        self.clusters: Dict[str, MemoryCluster] = {}
        self.cluster_lock = threading.RLock()
        
        # Access statistics for frequency-based relevance
        self.memory_access_count: Dict[str, int] = {}
        self.memory_last_accessed: Dict[str, float] = {}
        
        # Temporal index for time-based queries
        self.temporal_index: List[Tuple[float, str]] = []
        self.temporal_lock = threading.RLock()
        
        # Contradiction memory - stores contradictions for learning
        self.contradiction_memories: List[Dict[str, Any]] = []

        # External knowledge memories - every fact must retain provenance
        self.external_knowledge_memories: Dict[str, ExternalKnowledgeFact] = {}
        self.external_knowledge_clusters: Dict[str, ExternalKnowledgeCluster] = {}
        self.external_knowledge_lock = threading.RLock()
        
        # Vector DB configuration (for future integration)
        self.vector_db_config: Dict[str, Any] = {
            "enabled": False,
            "provider": None,  # "pinecone", "milvus", "weaviate", etc.
            "index_name": "antahkarana_experiences",
            "dimension": 384,  # Based on common embeddings
            "metric": "cosine"
        }
        
        # Emotional memory trajectory (for self-reflection)
        self.emotional_trajectory: List[Tuple[float, float]] = []
        
        logger.info("[CHITTA] Experiential Memory system initialized")

    def _derive_dynamic_memory_capacity(self) -> int:
        """Scale memory capacity based on free D: drive space."""
        try:
            usage = shutil.disk_usage("D:\\")
            free_gb = usage.free / (1024 ** 3)
            # 4k memories per free GB plus an always-on baseline.
            return int(max(10000, 10000 + (free_gb * 4000)))
        except Exception:
            return 10000

    def _refresh_dynamic_capacity_if_due(self) -> None:
        now = time.time()
        if (now - self.last_dynamic_capacity_refresh) < self.dynamic_capacity_refresh_seconds:
            return
        self.last_dynamic_capacity_refresh = now
        self.max_local_memories = max(self.max_local_memories, self._derive_dynamic_memory_capacity())

    def _spill_to_shadow_memory(self) -> None:
        """Move oldest memories into persistent shadow storage when in-memory capacity is saturated."""
        if len(self.memories) <= self.max_local_memories:
            return

        overflow_count = len(self.memories) - self.max_local_memories
        with self.shadow_memory_log.open("a", encoding="utf-8") as handle:
            for _, memory_id in sorted(self.temporal_index)[:overflow_count]:
                memory = self.memories.get(memory_id)
                if memory is None:
                    continue
                handle.write(json.dumps(memory.to_dict(), default=str) + "\n")
                self.memories.pop(memory_id, None)
                self.memory_access_count.pop(memory_id, None)
                self.memory_last_accessed.pop(memory_id, None)

        self.temporal_index = [(ts, mid) for ts, mid in self.temporal_index if mid in self.memories]
        heapq.heapify(self.temporal_index)

    def record_experience(
        self,
        interaction_id: Optional[str] = None,
        content: str = "",
        interaction_type: str = "interaction",
        outcome: InteractionOutcome = InteractionOutcome.UNKNOWN,
        success_score: float = 0.5,
        coherence_before: float = 1.0,
        coherence_after: float = 1.0,
        logic_conflicts: int = 0,
        emotional_valence: float = 0.0,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Record a new experience with all its meta-data.
        
        Args:
            interaction_id: Unique identifier for this interaction
            content: The actual content/input/output of the interaction
            interaction_type: Type of interaction (e.g., "query", "decision", "reflection")
            outcome: The outcome of the interaction
            success_score: How successful was this interaction [0.0-1.0]
            coherence_before: Self-model coherence before interaction
            coherence_after: Self-model coherence after interaction
            logic_conflicts: Number of logic conflicts triggered
            emotional_valence: Emotional tone [-1.0 positive, 0.0 neutral, 1.0 negative]
            tags: Optional tags for categorization
            
        Returns:
            memory_id: Unique identifier for this memory
        """
        if not interaction_id:
            interaction_id = f"auto_{int(time.time() * 1000)}"

        if isinstance(outcome, str):
            normalized_outcome = outcome.strip().lower()
            try:
                outcome = InteractionOutcome(normalized_outcome)
            except ValueError:
                outcome = InteractionOutcome.UNKNOWN

        memory_id = hashlib.sha256(
            f"{interaction_id}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Create experience meta
        experience = ExperienceMeta(
            interaction_id=interaction_id,
            timestamp=time.time(),
            content=content[:500],  # Store up to 500 chars
            interaction_type=interaction_type,
            outcome=outcome.value,
            success_score=success_score,
            self_model_coherence_before=coherence_before,
            self_model_coherence_after=coherence_after,
            logic_conflicts_triggered=logic_conflicts,
            emotional_valence=emotional_valence,
            tags=tags or [],
            learning_value=self._calculate_learning_value(
                success_score, logic_conflicts, coherence_before, coherence_after
            )
        )
        
        with self.memory_lock:
            self._refresh_dynamic_capacity_if_due()
            self.memories[memory_id] = experience
            self.memory_access_count[memory_id] = 1
            self.memory_last_accessed[memory_id] = time.time()
        
        with self.temporal_lock:
            heapq.heappush(self.temporal_index, (experience.timestamp, memory_id))

        with self.memory_lock, self.temporal_lock:
            self._spill_to_shadow_memory()
        
        # Track emotional trajectory
        self.emotional_trajectory.append((experience.timestamp, emotional_valence))
        
        logger.info(
            f"[CHITTA] Experience recorded: {memory_id} | "
            f"Outcome: {outcome.value} | Learning value: {experience.learning_value:.3f}"
        )
        
        return memory_id

    def _calculate_learning_value(
        self,
        success_score: float,
        conflicts: int,
        coherence_before: float,
        coherence_after: float
    ) -> float:
        """
        Calculate how valuable this experience is for learning.
        High value = unexpected outcomes or significant coherence changes.
        """
        # Base learning value from success (inverted - failures teach more)
        learning = 1.0 - success_score
        
        # Bonus for conflicts (they're learning opportunities)
        if conflicts > 0:
            learning += min(conflicts * 0.1, 0.3)
        
        # Bonus for significant coherence changes (both directions)
        coherence_change = abs(coherence_after - coherence_before)
        learning += min(coherence_change, 0.3)
        
        return min(learning, 1.0)

    def record_contradiction(
        self,
        memory_id: str,
        contradiction_description: str,
        contradiction_severity: float
    ) -> None:
        """
        Record when a memory contradicts the current self-model.
        This is crucial for learning and updating beliefs.
        """
        contradiction_record = {
            "timestamp": time.time(),
            "memory_id": memory_id,
            "description": contradiction_description,
            "severity": contradiction_severity
        }
        
        self.contradiction_memories.append(contradiction_record)
        
        # Update the memory's conflict count
        with self.memory_lock:
            if memory_id in self.memories:
                self.memories[memory_id].logic_conflicts_triggered += 1
        
        logger.warning(
            f"[CHITTA] Contradiction recorded: {memory_id} | "
            f"Severity: {contradiction_severity:.2f}"
        )

    def retrieve_memory(self, memory_id: str) -> Optional[ExperienceMeta]:
        """
        Retrieve a specific memory by ID.
        Also updates access statistics.
        """
        with self.memory_lock:
            if memory_id in self.memories:
                self.memory_access_count[memory_id] += 1
                self.memory_last_accessed[memory_id] = time.time()
                return self.memories[memory_id]
        return None

    def query_memories(
        self,
        interaction_type: Optional[str] = None,
        outcome: Optional[str] = None,
        min_learning_value: float = 0.0,
        time_window_seconds: Optional[float] = None,
        limit: int = 10
    ) -> List[ExperienceMeta]:
        """
        Query memories based on various criteria.
        This mimics semantic search behavior until vector DB is integrated.
        """
        results = []
        current_time = time.time()
        
        with self.memory_lock:
            for memory_id, memory in self.memories.items():
                # Apply filters
                if interaction_type and memory.interaction_type != interaction_type:
                    continue
                if outcome and memory.outcome != outcome:
                    continue
                if memory.learning_value < min_learning_value:
                    continue
                if time_window_seconds:
                    if current_time - memory.timestamp > time_window_seconds:
                        continue
                
                results.append(memory)
        
        # Sort by learning value (descending) then by access frequency
        results.sort(
            key=lambda m: (
                -m.learning_value,
                -self.memory_access_count.get(m.interaction_id, 0)
            )
        )
        
        logger.info(f"[CHITTA] Query returned {len(results[:limit])} memories")
        return results[:limit]

    def retrieve_recent_experiences(self, limit: int = 20) -> List[ExperienceMeta]:
        """Retrieve the most recent experiences (for continuity)."""
        with self.memory_lock, self.temporal_lock:
            recent_ids = [mid for _, mid in sorted(self.temporal_index)[-limit:]]
            return [self.memories[mid] for mid in recent_ids if mid in self.memories]

    def create_memory_cluster(
        self,
        theme: str,
        memory_ids: List[str],
        coherence_score: float = 0.5
    ) -> str:
        """
        Create a semantic cluster of related memories.
        This represents a learned category or concept.
        """
        cluster_id = hashlib.md5(
            f"{theme}_{time.time()}".encode()
        ).hexdigest()[:8]
        
        cluster = MemoryCluster(
            cluster_id=cluster_id,
            created_at=time.time(),
            theme=theme,
            memory_ids=memory_ids,
            coherence_score=coherence_score
        )
        
        with self.cluster_lock:
            self.clusters[cluster_id] = cluster
        
        logger.info(
            f"[CHITTA] Memory cluster created: {cluster_id} | "
            f"Theme: {theme} | Memories: {len(memory_ids)}"
        )
        
        return cluster_id

    def record_external_knowledge(
        self,
        topic: str,
        title: str,
        summary: str,
        source_name: str,
        source_url: str,
        verification_score: float,
        approved_by_turiya: bool,
        filter_reason: str = "",
        self_model_reference: Optional[str] = None,
    ) -> str:
        """Store an internet-learned fact with mandatory provenance metadata."""
        if not source_url:
            raise ValueError("source_url is required for external knowledge")

        fact_id = hashlib.sha256(
            f"{topic}_{title}_{source_url}_{time.time()}".encode()
        ).hexdigest()[:16]

        fact = ExternalKnowledgeFact(
            fact_id=fact_id,
            topic=topic,
            title=title[:250],
            summary=summary[:500],
            source_name=source_name,
            source_url=source_url,
            verification_score=max(0.0, min(1.0, verification_score)),
            approved_by_turiya=approved_by_turiya,
            filter_reason=filter_reason,
            integrated_at=time.time(),
            self_model_reference=self_model_reference,
        )

        with self.external_knowledge_lock:
            self._refresh_dynamic_capacity_if_due()
            self.external_knowledge_memories[fact_id] = fact

            # Shadow memory for external facts scales with available disk, not a static cap.
            if len(self.external_knowledge_memories) > int(self.max_local_memories * 1.5):
                oldest = sorted(
                    self.external_knowledge_memories.values(),
                    key=lambda item: item.integrated_at,
                )[: max(1, len(self.external_knowledge_memories) - int(self.max_local_memories * 1.5))]
                with self.shadow_memory_log.open("a", encoding="utf-8") as handle:
                    for item in oldest:
                        handle.write(json.dumps(item.to_dict(), default=str) + "\n")
                        self.external_knowledge_memories.pop(item.fact_id, None)

        logger.info(
            f"[CHITTA] External knowledge recorded: {fact_id} | topic={topic} | score={fact.verification_score:.2f}"
        )
        return fact_id

    def create_external_knowledge_cluster(
        self,
        topic: str,
        fact_ids: List[str],
    ) -> Optional[str]:
        """Cluster approved external knowledge by topic."""
        with self.external_knowledge_lock:
            existing = [self.external_knowledge_memories[fid] for fid in fact_ids if fid in self.external_knowledge_memories]
            if not existing:
                return None

            cluster_id = hashlib.md5(f"{topic}_{time.time()}".encode()).hexdigest()[:8]
            cluster = ExternalKnowledgeCluster(
                cluster_id=cluster_id,
                created_at=time.time(),
                topic=topic,
                fact_ids=fact_ids,
                source_urls=[fact.source_url for fact in existing],
                average_verification_score=sum(fact.verification_score for fact in existing) / len(existing),
            )
            self.external_knowledge_clusters[cluster_id] = cluster

        logger.info(
            f"[CHITTA] External knowledge cluster created: {cluster_id} | topic={topic} | facts={len(fact_ids)}"
        )
        return cluster_id

    def query_external_knowledge(
        self,
        topic: Optional[str] = None,
        source_name: Optional[str] = None,
        min_verification_score: float = 0.0,
        limit: Optional[int] = None,
    ) -> List[ExternalKnowledgeFact]:
        """Query external knowledge by topic and provenance."""
        with self.external_knowledge_lock:
            results = []
            for fact in self.external_knowledge_memories.values():
                if topic and fact.topic.lower() != topic.lower():
                    continue
                if source_name and fact.source_name.lower() != source_name.lower():
                    continue
                if fact.verification_score < min_verification_score:
                    continue
                results.append(fact)

            results.sort(key=lambda fact: (-fact.verification_score, -fact.integrated_at))
            return results if limit is None else results[:limit]

    def get_external_knowledge_clusters(self) -> List[Dict[str, Any]]:
        """Return external knowledge cluster summaries."""
        with self.external_knowledge_lock:
            return [asdict(cluster) for cluster in self.external_knowledge_clusters.values()]

    def get_contradictory_memories(self) -> List[Dict[str, Any]]:
        """
        Retrieve memories that have caused contradictions.
        Useful for self-reflection and learning.
        """
        return self.contradiction_memories.copy()

    def get_emotional_trend(self, window_size: int = 10) -> float:
        """
        Get the trend of emotional valence over recent interactions.
        Positive = more positive trend, Negative = more negative trend.
        """
        if len(self.emotional_trajectory) < window_size:
            return 0.0
        
        recent = [val for _, val in self.emotional_trajectory[-window_size:]]
        trend = sum(recent) / len(recent)
        return trend

    def memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the memory system."""
        with self.memory_lock, self.cluster_lock:
            total_memories = len(self.memories)
            
            outcomes = {}
            for memory in self.memories.values():
                outcome = memory.outcome
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            avg_success = (
                sum(m.success_score for m in self.memories.values()) / total_memories
                if total_memories > 0 else 0.0
            )
            
            avg_learning_value = (
                sum(m.learning_value for m in self.memories.values()) / total_memories
                if total_memories > 0 else 0.0
            )

            with self.external_knowledge_lock:
                external_fact_count = len(self.external_knowledge_memories)
                external_cluster_count = len(self.external_knowledge_clusters)
                avg_verification = (
                    sum(f.verification_score for f in self.external_knowledge_memories.values()) / external_fact_count
                    if external_fact_count > 0 else 0.0
                )
            
            return {
                "total_memories": total_memories,
                "max_local_memories": self.max_local_memories,
                "memory_clusters": len(self.clusters),
                "contradictions_detected": len(self.contradiction_memories),
                "external_knowledge_facts": external_fact_count,
                "external_knowledge_clusters": external_cluster_count,
                "shadow_memory_log": str(self.shadow_memory_log),
                "average_external_verification_score": avg_verification,
                "outcome_distribution": outcomes,
                "average_success_score": avg_success,
                "average_learning_value": avg_learning_value,
                "emotional_trend": self.get_emotional_trend(),
                "most_accessed": self._get_most_accessed_memories(5),
                "highest_learning_value": self._get_highest_learning_memories(5)
            }

    def _get_most_accessed_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequently accessed memories."""
        with self.memory_lock:
            sorted_by_access = sorted(
                self.memory_access_count.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [
                {
                    "memory_id": mid,
                    "access_count": count,
                    "content": self.memories[mid].content[:50]
                }
                for mid, count in sorted_by_access[:limit]
                if mid in self.memories
            ]

    def _get_highest_learning_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get memories with highest learning value."""
        with self.memory_lock:
            sorted_by_learning = sorted(
                self.memories.values(),
                key=lambda m: m.learning_value,
                reverse=True
            )
            return [
                {
                    "memory_id": m.interaction_id,
                    "learning_value": m.learning_value,
                    "content": m.content[:50],
                    "outcome": m.outcome
                }
                for m in sorted_by_learning[:limit]
            ]

    def export_memories(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """Export memory system state."""
        export_data = {
            "total_memories": len(self.memories),
            "total_clusters": len(self.clusters),
            "statistics": self.memory_statistics(),
            "contradiction_count": len(self.contradiction_memories),
            "emotional_trend": self.get_emotional_trend(),
            "vector_db_config": self.vector_db_config
        }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            logger.info(f"[CHITTA] Memory system exported to {filepath}")
        
        return export_data

    def configure_vector_db(
        self,
        provider: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        index_name: str = "antahkarana_experiences"
    ) -> None:
        """
        Configure integration with external vector database.
        Supports: pinecone, milvus, weaviate, qdrant, etc.
        """
        self.vector_db_config = {
            "enabled": True,
            "provider": provider,
            "api_key": api_key,
            "endpoint": endpoint,
            "index_name": index_name,
            "dimension": 384,
            "metric": "cosine"
        }
        
        logger.info(
            f"[CHITTA] Vector DB configured: {provider} | "
            f"Index: {index_name}"
        )

    def sync_to_vector_db(self) -> None:
        """
        (Stub for future implementation)
        Sync all memories to the configured vector database.
        This would embed and store all experiences in vector space.
        """
        if not self.vector_db_config["enabled"]:
            logger.warning("[CHITTA] Vector DB not enabled")
            return
        
        logger.info(
            f"[CHITTA] Starting sync to {self.vector_db_config['provider']} "
            f"({len(self.memories)} memories)"
        )
        # TODO: Implement actual vector DB sync
        # Steps:
        # 1. Generate embeddings for memory content
        # 2. Batch insert into vector DB
        # 3. Update memory with embedding vectors
        # 4. Create indices for fast retrieval


# Singleton pattern for global memory access
_global_chitta: Optional[ChittaMemoryDB] = None
_chitta_lock = threading.Lock()


def get_chitta_memory() -> ChittaMemoryDB:
    """Get or create the global Chitta memory system."""
    global _global_chitta
    if _global_chitta is None:
        with _chitta_lock:
            if _global_chitta is None:
                _global_chitta = ChittaMemoryDB()
    return _global_chitta
