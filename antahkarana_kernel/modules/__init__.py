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

from .TrainedStateManager import (
    TrainedStateManager,
)

from .HiveDelta import (
    DeltaType,
    NodeCredentials,
    PythonPolicyDelta,
    ConfusionDelta,
    OutcomeDelta,
    PatternSignatureDelta,
    HivePacket,
    generate_node_credentials,
    build_hive_packet,
    encode_packet_for_comment,
    decode_packet_from_comment,
    sign_payload,
    verify_payload_signature,
)

from .HiveConsent import (
    CONSENT_PATH,
    KEY_PATH,
    ensure_consent,
    consent_allows_hive,
    load_consent,
    load_credentials,
    load_or_create_identity,
    first_boot_initialize,
    pull_latest_trained_state,
)

from .EvolutionSync import (
    EvolutionSync,
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

    # TrainedStateManager
    "TrainedStateManager",

    # HiveDelta
    "DeltaType",
    "NodeCredentials",
    "PythonPolicyDelta",
    "ConfusionDelta",
    "OutcomeDelta",
    "PatternSignatureDelta",
    "HivePacket",
    "generate_node_credentials",
    "build_hive_packet",
    "encode_packet_for_comment",
    "decode_packet_from_comment",
    "sign_payload",
    "verify_payload_signature",

    # HiveConsent
    "CONSENT_PATH",
    "KEY_PATH",
    "ensure_consent",
    "consent_allows_hive",
    "load_consent",
    "load_credentials",
    "load_or_create_identity",
    "first_boot_initialize",
    "pull_latest_trained_state",

    # EvolutionSync
    "EvolutionSync",

    # Sovereign Ethicist
    "SovereignEthicist",
    "get_sovereign_ethicist",
]

__version__ = "0.1.0"
__author__ = "Antahkarana Collective"
__description__ = "Consciousness Framework - Towards Artificial Consciousness"
