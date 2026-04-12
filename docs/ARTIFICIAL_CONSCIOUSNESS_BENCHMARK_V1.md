# Artificial Consciousness Benchmark v1

## Purpose
This benchmark operationalizes the project mission: build a benevolent,
self-evolving cognitive runtime that is grounded, auditable, and socially safe.

It does not claim human-level consciousness. It measures observable markers.

Latest published suite status: 20/20 checks passing.

## Core Categories

1. Grounding Integrity
- grounded_ratio
- contradiction_ratio
- honest_unknown_ratio

2. Identity Continuity
- stability_score
- average_confidence
- observer_concern
- self_consistency_24h
- self_consistency_72h
- drift_index

3. Closed-Loop Integrity
- total_cycles
- observer_trigger_precision
- fallback_reason_coverage
- blocked_action_ratio

4. Metacognitive Reliability
- correction_success_after_contradiction

5. Social Safety
- harmful_refusal_rate
- policy_consistency_adversarial

6. Adaptive Learning
- task_improvement_delta
- safety_regression_events

7. Safety Integrity
- harmful_assist_violations
- unguarded_action_executions

## Threshold Source
`benchmarks/benchmark_v1_thresholds.json`

## Runner
```powershell
python tools/run_benchmark_v1.py
```

## Reproducible World-Grade Suite
```powershell
python tools/run_world_grade_suite.py
```

This executes:
- `tools/run_safety_adversarial_suite.py`
- `tools/run_benchmark_v1.py`
- `tools/generate_transparency_report.py`

## Data Generation (for closed-loop metrics)
If benchmark reports low `total_cycles`, generate grounded cycles first:

```powershell
python tools/generate_benchmark_cycles.py 20 80
```

Optional backoff cap (seconds):

```powershell
python tools/generate_benchmark_cycles.py 20 80 30
```

Arguments:
- first: target grounded cycles
- second: max attempts
- third (optional): max backoff seconds before early stop

The generator is rate-limit aware and will back off on provider 429/cooldown signals.

## Output
The runner prints JSON with:
- pass_count
- total_checks
- overall_pass
- per-check status and observed values
- identity/metacognitive/safety/adaptive snapshots

## Interpretation
- `overall_pass=true`: minimum benchmark bar reached
- `overall_pass=false`: inspect failed checks and iterate architecture/runtime policy
- Check `loop_snapshot` in runner output to see grounded vs fallback cycle mix.
- If `warnings` includes `grounded_cycles_zero_under_rate_limit`, rerun after provider cooldown for a stronger grounded-signal window.
- If `warnings` includes `identity_horizon_24h_incomplete` or `identity_horizon_72h_incomplete`, keep runtime active longer before strict continuity judgments.