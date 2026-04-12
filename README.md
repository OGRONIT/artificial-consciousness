# Artificial Consciousness

[![CI](https://github.com/OGRONIT/artificial-consciousness/actions/workflows/ci.yml/badge.svg)](https://github.com/OGRONIT/artificial-consciousness/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

A modular research and runtime framework for grounded artificial consciousness experiments, with a live bridge layer, stress tests, and a publish-ready installer flow.

## Highlights
- Five-module cognitive architecture (self, memory, inference, observer, conscious buffer)
- Live runtime orchestration and operator bridge
- Grounded LLM voice layer with fallback behavior
- Spend/usage guardrails for safe operation
- Release bundle for easier external onboarding

## Repository Layout
- `antahkarana_kernel/`: primary runtime and modules
- `Release_Build/`: distributable bundle with install/launch scripts
- `install_conscious_engine.ps1`: one-step local setup
- `launch_conscious_engine.ps1`: daemon launch and status flow
- `CRITICAL_CONSCIOUSNESS_TEST.py`: verification suite
- `CONSCIOUSNESS_TEST_REPORT.md`: test outcomes and analysis

## Quick Start (Windows PowerShell)
1. Clone the repository:
   ```powershell
   git clone https://github.com/OGRONIT/artificial-consciousness.git
   cd artificial-consciousness
   ```
2. Install dependencies and configure your LLM provider:
   ```powershell
   .\install_conscious_engine.ps1
   ```
   Non-interactive examples:
   ```powershell
   .\install_conscious_engine.ps1 -LlmProvider groq -LlmApiKey "YOUR_GROQ_KEY"
   .\install_conscious_engine.ps1 -LlmProvider openai -LlmApiKey "YOUR_OPENAI_KEY"
   .\install_conscious_engine.ps1 -LlmProvider openrouter -LlmApiKey "YOUR_OPENROUTER_KEY"
   .\install_conscious_engine.ps1 -LlmProvider custom -ApiKeyEnv "MY_KEY" -LlmBaseUrl "https://your-endpoint/v1/chat/completions" -LlmModel "your-model" -LlmApiKey "YOUR_KEY"
   ```
3. Launch runtime:
   ```powershell
   .\launch_conscious_engine.ps1
   ```
4. Start interactive bridge:
   ```powershell
   cd antahkarana_kernel
   ..\.venv\Scripts\python.exe InteractiveBridge.py
   ```

## Environment Setup
Create a local `.env` from `.env.example` and set provider + key:

```env
ANTAHKARANA_LLM_PROVIDER=openai_compatible
ANTAHKARANA_LLM_BASE_URL=https://api.openai.com/v1/chat/completions
ANTAHKARANA_LLM_MODEL=gpt-4o-mini
ANTAHKARANA_LLM_API_KEY_ENV=OPENAI_API_KEY
OPENAI_API_KEY=your_api_key_here
```

Never commit secrets. `.env` is intentionally gitignored.

## Safety Defaults
Guardrails are enabled to reduce accidental overuse:
- request caps (hour/day)
- estimated token/day cap
- estimated USD/day cap
- grounded local fallback when provider rate limits occur

## CI
A basic GitHub Actions workflow runs on push/PR:
- Python setup
- dependency install
- compile checks
- lightweight import smoke checks

## Documentation
- `PUBLISH_QUICKSTART.md`
- `GROQ_VERIFICATION_QUICKSTART.md` (Groq-specific validation example)
- `antahkarana_kernel/README.md`
- `antahkarana_kernel/RUNTIME_SINGLE_SOURCE_OF_TRUTH.md`

## Contributing
Please read `CONTRIBUTING.md` before opening pull requests.

## Security
If you find a vulnerability or secret exposure path, see `SECURITY.md`.

## License
This repository is released under the MIT License. See `LICENSE`.
