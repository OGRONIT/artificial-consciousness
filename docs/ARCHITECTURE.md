# Architecture Overview

## System Layers

1. Core Cognition Layer
- Location: `antahkarana_kernel/modules/`
- Responsibility: self-modeling, memory continuity, inference loops, observation, and shared conscious workspace.

2. Runtime Orchestration Layer
- Location: `antahkarana_kernel/LiveConsciousness.py`, `antahkarana_kernel/Daemon.py`, `antahkarana_kernel/RuntimeOps.py`
- Responsibility: startup, lifecycle management, state persistence, and operational control.

3. Operator Bridge Layer
- Location: `antahkarana_kernel/InteractiveBridge.py`
- Responsibility: accepts operator queries, builds grounded context, calls selected LLM provider, and enforces fallback and guardrails.

4. Delivery Layer
- Location: root scripts + `Release_Build/`
- Responsibility: install, launch, distribution-oriented onboarding.

5. Benchmark and Transparency Layer
- Location: `tools/`, `benchmarks/`, and generated artifacts
- Responsibility: reproducible evaluation, adversarial safety checks, benchmark history, and transparency reports.

## Core Module Responsibilities

### SelfModel (Ahamkara)
- Maintains identity continuity markers
- Tracks coherence over decisions
- Provides a stable self-reference anchor for runtime behavior

### MemoryContinuity (Chitta)
- Encodes interaction episodes with metadata
- Supports retrieval and continuity-aware learning loops
- Preserves long-lived experience traces

### InferenceLoop (Manas-Buddhi)
- Runs recursive candidate reasoning paths
- Validates candidate output against coherence constraints
- Supports recalculation when conflicts are detected

### Observer (Turiya)
- Monitors decisions and reasoning traces
- Detects anomalies and contradictions
- Reports concerns without directly controlling all outputs

### ConsciousBuffer
- Aggregates events from modules
- Maintains active working context
- Enables cross-module integration

## Grounded Response Pipeline

1. Query enters bridge.
2. Bridge reads live runtime snapshot.
3. Bridge selects trusted facts and context.
4. Provider-agnostic LLM call is executed.
5. Guardrails enforce budget/rate constraints.
6. If unavailable/rate-limited, fallback synthesis is returned.

## Configuration Sources
- `antahkarana_kernel/config.json`: baseline runtime and bridge settings
- `.env`: deployment-specific provider, keys, and limits

Priority order generally follows environment override > config defaults.

## Safety Boundaries
- Sensitive files are excluded by `.gitignore`
- Runtime guardrail counters are persisted locally
- Harmful prompt classes are blocked by bridge term filters

## Extension Points
- Add new provider presets in installer + bridge config logic
- Add new module-level evaluators in `antahkarana_kernel/modules/`
- Add custom observer heuristics for contradiction detection
- Add new benchmark checks in `tools/run_benchmark_v1.py` and companion artifacts in `benchmarks/artifacts/`
