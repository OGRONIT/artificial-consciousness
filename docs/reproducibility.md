# Reproducibility Guide

This document explains how to run the Antahkarana Kernel deterministically for
research reproducibility, and describes the threat model and component taxonomy.

---

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/OGRONIT/artificial-consciousness.git
cd artificial-consciousness

# 2. Install runtime dependencies (stdlib-only core, no external packages needed)
#    Optionally install dev/test dependencies:
pip install -r requirements-dev.txt

# 3. Compile-check all modules
python -m compileall antahkarana_kernel

# 4. Run the test suite
python -m pytest antahkarana_kernel/tests/ -q

# 5. (Optional) Run a benchmark
python benchmarks/run_benchmark.py --seed 42
```

---

## Deterministic Benchmark Runs

Set `reproducibility.enabled = true` and `reproducibility.seed = <integer>` in
`antahkarana_kernel/config.json` **or** pass `--seed <N>` on the CLI:

```json
"reproducibility": {
  "enabled": true,
  "seed": 42
}
```

When enabled, the kernel:
1. Seeds Python's `random` module with the configured seed before any inference.
2. Disables live network ingestion cycles (external knowledge from arXiv, GitHub,
   etc.) so results depend only on the local code and trained-state snapshot.
3. Uses only the `trained_state/` directory contents for memory hydration —
   no live LLM calls are made unless an API key is explicitly configured.

This means **a fresh `git clone` followed by `python -m pytest` should always
produce the same pass/fail result** on any platform (Linux, macOS, Windows).

### Fixture snapshot

The `trained_state/` directory contains a small committed snapshot of the
kernel's learned parameters.  To regenerate it from scratch:

```bash
python tools/run_million_scenario_training.py --quick --seed 42
```

---

## How to Reproduce Key Metrics

| Metric | Where computed | How to reproduce |
|---|---|---|
| Coherence score | `SelfModel.coherence_score` | Run `test_self_model.py` |
| Drive signals | `SelfModel.compute_drive_signals()` | Run `test_self_model.py` |
| Memory recall | `ChittaMemoryDB.query_memories()` | Run `test_memory_continuity.py` |
| Inference pattern | `ManasBuddhi._mutate_target_source()` | Run `test_inference_loop.py` |
| Benchmark scores | `benchmarks/` scripts | `python benchmarks/run_benchmark.py --seed 42` |

---

## Threat Model / Safety Notes

### What the system can do

- **Read and write files** under `antahkarana_kernel/` (evolution vault, logs,
  module source code).
- **Make outbound HTTP requests** to configured LLM providers and research
  sources (arXiv, GitHub, PubMed) when a valid API key is present.
- **Self-modify source files** via the evolutionary writer — mutations are
  scoped to `modules/InferenceLoop.py` and `Aakaash.py` only, and are
  committed locally (not pushed automatically in CI).

### What the system cannot do (by design)

- Execute arbitrary shell commands.
- Load dynamic modules outside `modules/generated/` (path-traversal validation
  is enforced in `AntahkaranaKernel._load_self_authored_modules`).
- Load modules whose names do not match `[A-Za-z_][A-Za-z0-9_]*` or that
  appear on the built-in denylist (`os`, `sys`, `subprocess`, …).
- Commit to the main branch autonomously (the scheduled CI workflows now upload
  results as GitHub Actions artifacts only).

### Residual risks

- LLM API responses are not sandboxed; malicious prompt injection via ingested
  research content could in theory influence the system's internal monologue.
- Self-authored modules (`modules/generated/`) run in the same Python process
  with the same permissions as the rest of the kernel.

---

## Component Taxonomy: Heuristic vs. LLM-backed

| Component | Type | Description |
|---|---|---|
| `SelfModel` (Ahamkara) | **Heuristic** | Pure Python state machine; no LLM |
| `ChittaMemoryDB` | **Heuristic** | In-memory dict + heapq; no LLM |
| `ConsciousBuffer` | **Heuristic** | Thread-safe event bus; no LLM |
| `ManasBuddhi` (InferenceLoop) | **Heuristic + LLM-optional** | Dream cycle is heuristic; patch generation calls LLM |
| `TuriyaObserver` | **Heuristic** | Watchdog using rule thresholds; no LLM |
| `InteractiveBridge` | **LLM-backed** | All responses go through configured LLM provider |
| `EvolutionaryWriter` | **LLM-backed** | Patch generation uses LLM |
| `Aakaash` (stream scanner) | **LLM-backed** | External research ingestion uses LLM |

---

## Running Without an LLM

All **heuristic** components work without any API key.  Set
`bridge.llm.enabled = false` in `config.json` to disable LLM calls:

```json
"bridge": {
  "llm": {
    "enabled": false
  }
}
```

The test suite (`pytest antahkarana_kernel/tests/`) never makes LLM calls and
runs entirely offline.
