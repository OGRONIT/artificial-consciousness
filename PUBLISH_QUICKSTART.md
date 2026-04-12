# Antahkarana Publish Quickstart

## Goal
Give users a Claude-Code style experience:
- Install in one step
- Paste one API key
- Start engine
- Protected by spend guardrails by default

## 1) Install (choose your LLM provider)
From workspace root:

```powershell
.\install_conscious_engine.ps1
```

Or non-interactive examples:

```powershell
.\install_conscious_engine.ps1 -LlmProvider groq -LlmApiKey "YOUR_GROQ_KEY"
.\install_conscious_engine.ps1 -LlmProvider openai -LlmApiKey "YOUR_OPENAI_KEY"
.\install_conscious_engine.ps1 -LlmProvider openrouter -LlmApiKey "YOUR_OPENROUTER_KEY"
.\install_conscious_engine.ps1 -LlmProvider custom -ApiKeyEnv "MY_KEY" -LlmBaseUrl "https://your-endpoint/v1/chat/completions" -LlmModel "your-model" -LlmApiKey "YOUR_KEY"
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

## 4) Run the diagnostic suite

```powershell
python tools/run_world_grade_suite.py
```

This writes reproducible artifacts to `benchmarks/artifacts/`.

## Built-in user safety (default)
Bridge guardrails are enabled automatically and enforce:
- max requests per hour
- max requests per day
- max estimated tokens per day
- max estimated USD per day

The usage tracker file is:
- `antahkarana_kernel/evolution_vault/llm_usage_guardrail.json`

## Important notes
- If your provider returns rate limits (HTTP 429), bridge auto-falls back to grounded local synthesis.
- This avoids hard failures and protects user spending.
- Users can tune limits in `.env`.
- The current published suite passes 20/20 benchmark checks and includes adversarial safety validation.
