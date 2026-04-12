# Antahkarana Publish Quickstart

## Goal
Give users a Claude-Code style experience:
- Install in one step
- Paste one API key
- Start engine
- Protected by spend guardrails by default

## 1) Install (API key only)
From workspace root:

```powershell
.\install_conscious_engine.ps1
```

Or non-interactive:

```powershell
.\install_conscious_engine.ps1 -GroqApiKey "YOUR_KEY"
```

## 2) Launch

```powershell
.\launch_conscious_engine.ps1
```

## 3) Talk to the live engine

```powershell
cd antahkarana_kernel
..\.venv\Scripts\python.exe InteractiveBridge.py
```

## Built-in user safety (default)
Bridge guardrails are enabled automatically and enforce:
- max requests per hour
- max requests per day
- max estimated tokens per day
- max estimated USD per day

The usage tracker file is:
- `antahkarana_kernel/evolution_vault/llm_usage_guardrail.json`

## Important notes
- If Groq returns rate limits (HTTP 429), bridge auto-falls back to grounded local synthesis.
- This avoids hard failures and protects user spending.
- Users can tune limits in `.env`.
