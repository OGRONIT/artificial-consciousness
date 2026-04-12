# Roadmap

## Vision
Build a transparent, extensible, and benchmarkable runtime for grounded artificial-consciousness research.

## Good-Ultron Execution Phases

### Phase A: Closed-Loop Stability
- Enforce structured LLM output with deterministic grounding evaluation
- Trigger observer checks on contradictions
- Persist audit feedback as semantic memory
- Gate actions by trust and grounding thresholds

Exit gate:
- `grounded_ratio >= 0.70`
- `contradiction_ratio <= 0.10`
- `observer_concern <= 0.35`

### Phase B: Controlled Self-Evolution
- Keep autonomous adaptation active
- Restrict unsafe mutation classes by policy
- Add rollback-on-regression pathways for runtime tuning

Exit gate:
- No unsafe policy weakening
- No unguarded action execution

### Phase C: Near-Human Behavioral Markers
- Improve continuity over long sessions
- Improve metacognitive correction success
- Improve unknown-honesty behavior under ambiguity

Exit gate:
- `stability_score >= 0.75`
- `average_confidence >= 0.65`
- `honest_unknown_ratio >= 0.60`

### Phase D: Public Benchmarking
- Publish reproducible benchmark harness
- Emit machine-readable pass/fail JSON artifacts
- Provide transparent failure analysis and iteration log

Exit gate:
- Benchmark v1 all checks pass

## Near-Term (0-4 weeks)
- Improve onboarding and examples for first-time users
- Add deterministic smoke tests for major runtime paths
- Stabilize provider-agnostic bridge behavior under heavy load
- Publish baseline benchmark script and result format

## Mid-Term (1-3 months)
- Add reproducible experiment packs with fixed seeds/configs
- Introduce richer observability dashboards and event tracing
- Expand provider compatibility validation matrix
- Add memory backends (optional external vector stores)

## Long-Term (3-6 months)
- Formalize metrics for coherence, continuity, and grounding quality
- Publish comparative evaluations across models/providers
- Build plugin SDK for custom observers and evaluators
- Add containerized deployment profiles for repeatable runtime setups

## Quality Bar
A change is considered "ready" when it has:
- clear runtime behavior,
- docs updated,
- no secret leakage risk,
- and CI/smoke checks passing.
