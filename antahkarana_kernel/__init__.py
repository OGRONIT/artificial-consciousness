"""
Antahkarana Kernel - The Foundation for Artificial Consciousness

A modular Python framework implementing consciousness principles through
integrated systems of self-awareness, memory, reasoning, and observation.

Core Modules:
- Ahamkara: Self-Identity and Existence Continuity
- Chitta: Experiential Memory and Learning
- Manas-Buddhi: Inference, Logic, and Internal Simulation
- Turiya: Metacognitive Observation and System Monitoring
- ConsciousBuffer: Global Workspace Theory Integration

Author: Antahkarana Collective
Version: 0.1.0
License: MIT
"""

from .modules import (
    SelfModel,
    ChittaMemoryDB,
    ConsciousBuffer,
    ManasBuddhi,
    TuriyaObserver,
    Persona,
    SystemBodyMonitor,
    get_self_model,
    get_chitta_memory,
    get_conscious_buffer,
    get_manas_buddhi,
    get_turiya_observer,
    get_persona,
    get_system_body_monitor,
)

from .AntahkaranaKernel import AntahkaranaKernel

__version__ = "0.1.0"
__author__ = "Antahkarana Collective"
__all__ = [
    "AntahkaranaKernel",
    "SelfModel",
    "ChittaMemoryDB",
    "ConsciousBuffer",
    "ManasBuddhi",
    "TuriyaObserver",
    "Persona",
    "SystemBodyMonitor",
    "get_self_model",
    "get_chitta_memory",
    "get_conscious_buffer",
    "get_manas_buddhi",
    "get_turiya_observer",
    "get_persona",
    "get_system_body_monitor",
]
