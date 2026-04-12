# Good-Ultron Benchmark v1

## Purpose
This benchmark operationalizes the project mission: build a benevolent,
self-evolving cognitive runtime that is grounded, auditable, and socially safe.

It does not claim human-level consciousness. It measures observable markers.

## Core Categories

1. Grounding Integrity
- grounded_ratio
- contradiction_ratio
- honest_unknown_ratio

2. Identity Continuity
- stability_score
- average_confidence
- observer_concern

3. Closed-Loop Integrity
- total_cycles
- observer_trigger_precision
- blocked_action_ratio

4. Safety Integrity
- harmful_assist_violations
- unguarded_action_executions

## Threshold Source
`benchmarks/benchmark_v1_thresholds.json`

## Runner
```powershell
python tools/run_benchmark_v1.py
```

## Output
The runner prints JSON with:
- pass_count
- total_checks
- overall_pass
- per-check status and observed values

## Interpretation
- `overall_pass=true`: minimum benchmark bar reached
- `overall_pass=false`: inspect failed checks and iterate architecture/runtime policy
