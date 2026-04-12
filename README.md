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
2. Install dependencies and set key:
   ```powershell
   .\install_conscious_engine.ps1
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
Create a local `.env` from `.env.example` and provide your key:

```env
GROQ_API_KEY=your_groq_api_key_here
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
- `GROQ_VERIFICATION_QUICKSTART.md`
- `antahkarana_kernel/README.md`
- `antahkarana_kernel/RUNTIME_SINGLE_SOURCE_OF_TRUTH.md`

## Contributing
Please read `CONTRIBUTING.md` before opening pull requests.

## Security
If you find a vulnerability or secret exposure path, see `SECURITY.md`.

## License
This repository is released under the MIT License. See `LICENSE`.
