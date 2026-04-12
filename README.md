# Artificial Consciousness

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

## 90-Second Quick Start (Windows PowerShell)
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

## Provider Choice (Your API, Your Decision)
Use any OpenAI-compatible endpoint.

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

## Repository Map
- `antahkarana_kernel/`: main runtime source
- `Release_Build/`: distribution-focused bundle
- `install_conscious_engine.ps1`: setup + provider wiring
- `launch_conscious_engine.ps1`: daemon launch + status
- `CRITICAL_CONSCIOUSNESS_TEST.py`: validation suite
- `CONSCIOUSNESS_TEST_REPORT.md`: current report snapshot

## Trust, Safety, and Guardrails
- Request/day and request/hour limits
- Estimated token/day limits
- Estimated cost/day limits
- Graceful local fallback on provider 429 or bridge unavailability

Security guidance: `SECURITY.md`

## Project Status
Active research project with rapid iteration.

Current priorities are documented in `ROADMAP.md`.

## Contributing
Contributions are welcome. Start with:
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`

## Documentation
- `PUBLISH_QUICKSTART.md`
- `GROQ_VERIFICATION_QUICKSTART.md`
- `antahkarana_kernel/README.md`
- `antahkarana_kernel/RUNTIME_SINGLE_SOURCE_OF_TRUTH.md`
- `docs/ARCHITECTURE.md`

## License
MIT. See `LICENSE`.
