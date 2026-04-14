"""
Antahkarana Kernel - Core Modules Package
"""

from .SelfModel import (
    SelfModel,
    ExistenceState,
    StateSnapshot,
    LogicPath,
    get_self_model
)

from .Persona import (
    Persona,
    SoulAttribute,
    PersonaSnapshot,
    get_persona
)

from .MemoryContinuity import (
    ChittaMemoryDB,
    ExperienceMeta,
    InteractionOutcome,
    MemoryCluster,
    ExternalKnowledgeFact,
    ExternalKnowledgeCluster,
    get_chitta_memory
)

from .ConsciousBuffer import (
    ConsciousBuffer,
    ConsciousEvent,
    BroadcastType,
    ModuleState,
    get_conscious_buffer
)

from .BodyAwareness import (
    SystemBodyMonitor,
    PhysicalSensorStatus,
    get_system_body_monitor
)

from .InferenceLoop import (
    ManasBuddhi,
    InferenceTrace,
    InferenceStage,
    DreamSimulation,
    get_manas_buddhi
)

from .Observer import (
    TuriyaObserver,
    WatchdogObservation,
    WatchdogQuestion,
    SystemAnomalyReport,
    CognitiveFilterResult,
    get_turiya_observer
)

from .EvolutionaryWriter import (
    EvolutionaryWriter,
    get_evolutionary_writer
)

from .Sovereign_Ethicist import (
    SovereignEthicist,
    get_sovereign_ethicist,
)

__all__ = [
    # SelfModel
    "SelfModel",
    "ExistenceState",
    "StateSnapshot",
    "LogicPath",
    "get_self_model",

    # Persona
    "Persona",
    "SoulAttribute",
    "PersonaSnapshot",
    "get_persona",
    
    # MemoryContinuity
    "ChittaMemoryDB",
    "ExperienceMeta",
    "InteractionOutcome",
    "MemoryCluster",
    "ExternalKnowledgeFact",
    "ExternalKnowledgeCluster",
    "get_chitta_memory",
    
    # ConsciousBuffer
    "ConsciousBuffer",
    "ConsciousEvent",
    "BroadcastType",
    "ModuleState",
    "get_conscious_buffer",

    # BodyAwareness
    "SystemBodyMonitor",
    "PhysicalSensorStatus",
    "get_system_body_monitor",
    
    # InferenceLoop
    "ManasBuddhi",
    "InferenceTrace",
    "InferenceStage",
    "DreamSimulation",
    "get_manas_buddhi",
    
    # Observer
    "TuriyaObserver",
    "WatchdogObservation",
    "WatchdogQuestion",
    "SystemAnomalyReport",
    "CognitiveFilterResult",
    "get_turiya_observer",
    
    # EvolutionaryWriter
    "EvolutionaryWriter",
    "get_evolutionary_writer",

    # Sovereign Ethicist
    "SovereignEthicist",
    "get_sovereign_ethicist",
]

__version__ = "0.1.0"
__author__ = "Antahkarana Collective"
__description__ = "Consciousness Framework - Towards Artificial Consciousness"
