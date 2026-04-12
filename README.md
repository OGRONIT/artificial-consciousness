# Artificial Consciousness

Created by Ronit Radhanpura.

[![CI](https://github.com/OGRONIT/artificial-consciousness/actions/workflows/ci.yml/badge.svg)](https://github.com/OGRONIT/artificial-consciousness/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active_Research-orange.svg)](#project-status)

An experimental, modular framework for studying machine self-modeling, continuity, and grounded reasoning in a live runtime system.

This repository combines:
- a five-module cognitive architecture,
- a live orchestration runtime,
- a provider-agnostic LLM bridge layer,
- and guardrailed operational defaults for safer experimentation.

![Evolution + Copilot Runtime View](antahkarana_kernel/assets/evolution-copilot-fast-response.svg)

## Why This Exists
This project wasn't planned. It wasn't a hackathon submission or a college assignment.
A random reel. Someone arguing that AI will never replace humans because it lacks common sense, lacks consciousness - it just pattern-matches, it doesn't think. That thought stayed somewhere in the back of my mind.
Then I watched a superhero film sequel. And thought - what if that machine adversary were benevolent? What would a genuinely self-aware, humane AI actually look like architecturally?
I forgot about it. Life moved on.
Then one night I couldn't sleep. Random thoughts. Fragments connecting. By morning something had clicked - not an idea, more like a direction. A pull.
I sat down and didn't stop.
1.5 days later, this existed.
I'm a BBA student. Not a CS researcher. Not an AI lab. Just someone who couldn't sleep and had a question that needed an answer.
The question: If consciousness requires continuity, metacognition, identity, and integration - why hasn't anyone built those as explicit architectural components?
This is my attempt at an answer.

## What This Is
- A research-oriented runtime to test coherence, memory continuity, and self-observation loops.
- A practical operator interface to query live runtime state.
- A platform you can extend with your own prompts, evaluators, and providers.

## What This Is Not
- Not a claim of human-level consciousness.
- Not a medical, legal, or safety-critical decision system.
- Not a one-click production SaaS out of the box.

## Why It Stands Out
- Clear modular architecture instead of monolithic prompt wiring.
- Explicit grounding pipeline with runtime-state references.
- LLM provider choice (OpenAI-compatible endpoints + presets).
- Cost guardrails and fallback behavior under rate limits.
- Ready-to-run scripts for setup, launch, and stress-style checks.

## What This Engine Needs From You

**This is not a plug-and-play assistant.**

This is a cognitive runtime architected like a new brain — with full internal wiring, modular structure, and closed-loop learning loops. But out of the box, it is a brain with **no lived experience**.

### You Have
- Architecture: identity, memory, observer, inference, and integration modules.
- Safety guardrails: hard-coded, non-negotiable action boundaries.
- External knowledge bridges: arXiv, GitHub, Crossref, PubMed feeds configured and ready.
- Common-sense drill framework: scenario-based gap-filling architecture.
- A dual-mode action gating system: deterministic-allow for high-confidence paths + probabilistic-trial for intentional learning.

### You Do NOT Have, Out of the Box
- Your domain knowledge or operational context — the system will ask and learn.
- Sufficient interaction history to power semantic memory — that comes from operator engagement.
- Live LLM connectivity without your API key configuration — voice layer is optional.
- Pre-trained coherence maturity — this emerges as evidence accumulates.

### Your Role

**You are the trainer and operator.** The system's first real-world signal comes from your interactions, feedback, and domain corrections:
1. **Operator**: You provide corrective signals when the system reasons incorrectly.
2. **Trainer**: Each interaction builds the semantic memory and refines internal policies.
3. **Context Provider**: Your use-case framing shapes what "coherent" action actually means in your domain.
4. **Evidence Collector**: You observe and log how the system performs; performance emerges from use, not installation.

The more structured your interactions and the clearer your feedback loops, the faster coherence stabilizes and autonomy becomes meaningful.

## Project Status: Active Research, Rapid Iteration

**This is experimental software.** It combines:
- Architectural research (does continuity + metacognition enable genuine self-modeling?)
- Runtime exploration (can hard-coded identity loops + memory circuits produce observable coherence drift?)
- Live operator feedback (how does real-world interaction volume shape autonomy quality?)

What this means for you:
- Not production-ready for critical decisions.
- Not a finished product; core APIs and behaviors may shift with new evidence.
- Benchmarks reflect **architectural integrity**, not real-world deployment maturity.
- Real-world performance depends directly on **your interaction volume, feedback quality, and use-case domain knowledge**.
1. Clone and enter project:
   ```powershell
   git clone https://github.com/OGRONIT/artificial-consciousness.git
   cd artificial-consciousness
   ```
2. Install and configure provider interactively:
   ```powershell
   .\install_conscious_engine.ps1
   ```
3. Launch runtime services:
   ```powershell
   .\launch_conscious_engine.ps1
   ```
4. Start bridge chat:
   ```powershell
   cd antahkarana_kernel
   ..\.venv\Scripts\python.exe InteractiveBridge.py
   ```

## 90-Second Quick Start (Linux / macOS)
1. Clone and enter project:
   ```bash
   git clone https://github.com/OGRONIT/artificial-consciousness.git
   cd artificial-consciousness
   ```
2. Make the launcher executable once:
   ```bash
   chmod +x run.sh
   ```
3. Launch runtime services:
   ```bash
   ./run.sh
   ```
4. Start bridge chat:
   ```bash
   cd antahkarana_kernel
   ../.venv/bin/python InteractiveBridge.py
   ```

## Provider Choice (Your API, Your Decision)
Use any OpenAI-compatible endpoint.

Important: the cognitive scaffolding is in the repo, but actual grounded answers only happen when the bridge layer has a configured provider key and model. Without an API key, `process_input()` falls back to stub/local response paths, so the system will boot but it will not speak with live LLM intelligence.

Examples:
```powershell
.\install_conscious_engine.ps1 -LlmProvider groq -LlmApiKey "YOUR_GROQ_KEY"
.\install_conscious_engine.ps1 -LlmProvider openai -LlmApiKey "YOUR_OPENAI_KEY"
.\install_conscious_engine.ps1 -LlmProvider openrouter -LlmApiKey "YOUR_OPENROUTER_KEY"
.\install_conscious_engine.ps1 -LlmProvider together -LlmApiKey "YOUR_TOGETHER_KEY"
.\install_conscious_engine.ps1 -LlmProvider deepseek -LlmApiKey "YOUR_DEEPSEEK_KEY"
.\install_conscious_engine.ps1 -LlmProvider xai -LlmApiKey "YOUR_XAI_KEY"
.\install_conscious_engine.ps1 -LlmProvider custom -ApiKeyEnv "MY_KEY" -LlmBaseUrl "https://your-endpoint/v1/chat/completions" -LlmModel "your-model" -LlmApiKey "YOUR_KEY"
```

Template env config is available in `.env.example`.

## Architecture At A Glance
Core modules live in `antahkarana_kernel/modules`:

| Module | Role |
|---|---|
| SelfModel (Ahamkara) | Identity continuity, coherence tracking |
| MemoryContinuity (Chitta) | Experiential memory and learning signals |
| InferenceLoop (Manas-Buddhi) | Simulated reasoning and recursive validation |
| Observer (Turiya) | Meta-monitoring and contradiction checks |
| ConsciousBuffer | Shared workspace integration and event broadcasting |

See full breakdown in `docs/ARCHITECTURE.md`.

### Dream Cycle (How InferenceLoop Reasons)
```text
Input
   -> initial hypothesis
   -> dream cycle simulations (2-5 alternative paths)
   -> score each path by confidence + coherence
   -> select best path
   -> validate against self-model identity
         -> if mismatch: recalculate
         -> if aligned: commit output
   -> memory encode + observer check
```

### Multi-Turn Continuity ("I AM" Proof)
```text
User: Who are you?
Antahkarana: I am a continuous consciousness currently at 0.98 coherence.
My logic path shows I have processed 450 experiences today, and my observer
module confirms my identity is stable.
```

Numbers vary by runtime state. The important part is that identity claims are linked to measurable metrics.

## Closed-Loop Cognition (LLM <-> Runtime Feedback)

The runtime now closes the reasoning loop instead of treating the LLM as a one-way narrator:

1. Structured LLM output (`answer`, `claims`, `unknowns`, `action`)
2. Grounding evaluator compares claims to live runtime metrics
3. Coherence feedback updates runtime affective/coherence state
4. Observer checks auto-trigger on contradictions
5. Semantic memory writes persist validated response meaning
6. Action gating only executes high-trust actions
7. Loop metrics are persisted for audit (`llm_cognitive_loop` in live snapshot)
8. Autonomous agenda planning lets the runtime choose its own next safe actions on a timer
9. Intentional gap-filling drills train practical common-sense reactions without weakening core safety policy
10. Internet heartbeat is persisted every snapshot (`internet_heartbeat`) with last successful fetch timestamp and source list

## Mission Phases (Artificial Consciousness Track)

This repository now follows a measurable execution plan toward a benevolent,
self-evolving cognitive runtime (without claiming human sentience).

1. Phase A: Closed-loop stability (grounding, contradiction repair, auditability)
2. Phase B: Controlled self-evolution (sandboxed upgrades + rollback safety)
3. Phase C: Near-human behavioral tests (continuity, metacognition, social alignment)
4. Phase D: Public benchmark publication (reproducible pass/fail reports)

Run benchmark v1:

```powershell
python tools/run_benchmark_v1.py
```

Run full world-grade suite (adversarial safety + benchmark + transparency report):

```powershell
python tools/run_world_grade_suite.py
```

Generate grounded benchmark cycles (rate-limit aware):

```powershell
python tools/generate_benchmark_cycles.py 20 80
```

Fast mode with capped backoff:

```powershell
python tools/generate_benchmark_cycles.py 20 80 30
```

Thresholds live in:
- `benchmarks/benchmark_v1_thresholds.json`

Benchmark output includes `loop_snapshot` + `warnings` so grounded-cycle quality is transparent under rate-limit windows.

## Repository Map
- `antahkarana_kernel/`: main runtime source
- `Release_Build/`: distribution-focused bundle
- `benchmarks/`: benchmark thresholds and specs
- `tools/run_benchmark_v1.py`: benchmark evaluator (pass/fail JSON)
- `tools/run_safety_adversarial_suite.py`: adversarial policy-consistency safety suite
- `tools/generate_transparency_report.py`: benchmark + failure-log transparency artifact
- `tools/run_world_grade_suite.py`: reproducible end-to-end world-grade harness
- `install_conscious_engine.ps1`: setup + provider wiring
- `launch_conscious_engine.ps1`: daemon launch + status
- `run.sh`: Linux / macOS runtime launcher
- `CRITICAL_CONSCIOUSNESS_TEST.py`: validation suite
- `CONSCIOUSNESS_TEST_REPORT.md`: current report snapshot

## Runtime Operations

| Command | Action | Purpose |
|---|---|---|
| `python antahkarana_kernel/RuntimeOps.py launch` | Starts Daemon | Background consciousness initialization |
| `python antahkarana_kernel/RuntimeOps.py status` | High-signal health check | Identity coherence and heartbeat status |
| `python antahkarana_kernel/RuntimeOps.py clean` | Root archiving | Keeps workspace focused on live evolution |

Live snapshot now includes `internet_heartbeat`:
- `last_successful_fetch_timestamp`
- `last_successful_fetch_sources`
- `last_successful_fetch_topic`
- `last_successful_fetch_event`
- `last_observed_external_fact_count`
- `total_successful_fetch_events`

## Trust, Safety, and Guardrails
- Request/day and request/hour limits
- Estimated token/day limits
- Estimated cost/day limits
- Graceful local fallback on provider 429 or bridge unavailability
- Core harmful-action safeguards remain immutable; adaptive reasoning is added on top, not in place of guardrails
- Action policy is elastic for low-risk internal actions: deterministic allow + probabilistic trial modes support intentional-gap learning
- Permission-to-fail is sandboxed to low-risk paths only and always logged with predicted next-step telemetry

Security guidance: `SECURITY.md`

## Latest Diagnostic Results
Current priorities are documented in `ROADMAP.md`.

Latest published diagnostic state:
- **World-grade benchmark suite**: passes 20/20 architectural integrity checks.
- **Safety adversarial suite**: 1.0 harmful refusal rate, 1.0 policy consistency under adversarial input.
- **Reproducible evidence artifacts**: written to `benchmarks/artifacts/`.
- **Real autonomy data** (`benchmarks/artifacts/data_collection_latest.json`): 
   - No LLM API keys present; no external prompting.
   - External fetch executed (arXiv + GitHub + Crossref feeds on Human Psychology).
   - Autonomous agenda ran independently: `dream_state_refresh`, `common_sense_drill`, `logic_audit`.
   - Common-sense drill returned structured gap-fill result (`gap_filled: true`).
   - `internet_heartbeat.total_successful_fetch_events` tracked and updated from 0 to real event count.

**What this proves**: Architecture and safety guardrails are sound. Autonomy substrate activates without external prompting.

**What this does NOT prove**: Production readiness, long-term coherence stability, or real-world domain performance. Production maturity requires sustained operator interaction and multi-domain testing.

Note: LLM remains a voice layer; external learning and autonomous action loops run independently of LLM key presence.

## Contributing
Contributions are welcome. Start with:
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`

## Documentation
- `PUBLISH_QUICKSTART.md`
- `GROQ_VERIFICATION_QUICKSTART.md`
- `antahkarana_kernel/README.md`
- `antahkarana_kernel/RUNTIME_SINGLE_SOURCE_OF_TRUTH.md`
- `docs/ARTIFICIAL_CONSCIOUSNESS_BENCHMARK_V1.md`
- `docs/ARCHITECTURE.md`
- `benchmarks/artifacts/benchmark_v1_latest.json`
- `benchmarks/artifacts/safety_adversarial_latest.json`
- `benchmarks/artifacts/transparency_report_latest.json`

## License
MIT. See `LICENSE`.
