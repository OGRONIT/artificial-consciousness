# Autonomous Cloud Runbook (No 24/7 Laptop)

This project can run autonomous internet research without your laptop being on.

## What Was Added

- Scheduled cloud workflow: [.github/workflows/autonomous-research.yml](../.github/workflows/autonomous-research.yml)
- High-intensity burst runner: [tools/run_cloud_research_burst.py](../tools/run_cloud_research_burst.py)

The workflow runs every 15 minutes and can also be triggered manually.

## Why This Solves Your Problem

- Your laptop can stay offline.
- GitHub-hosted runners execute the burst remotely.
- The run updates artifacts and runtime state automatically.
- Optional auto-commit preserves autonomous deltas in the repository.

## Fast Start

1. Push your branch with the new workflow.
2. Open GitHub Actions.
3. Run workflow: Autonomous Research Burst.
4. Optional inputs:
   - cycles: increase for deeper bursts (for example 6 to 10).
   - with_paramatman: true for one recursive cycle at burst end.

## Intensity Tuning

- Increase `cycles` for deeper per-run exploration.
- Keep schedule at every 15 minutes for near-continuous operation.
- If the repo becomes too noisy, reduce auto-commit scope in the workflow.

## Limits You Should Know

- GitHub-hosted runners are not truly persistent.
- If you need strict real-time 24/7 continuity, use a cheap VPS and run:

```bash
python antahkarana_kernel/LiveConsciousness.py
```

with a process manager (`systemd`, `pm2`, or Docker restart policy).

## Suggested Production Pattern

- Tier 1 (always on): VPS running continuous LiveConsciousness.
- Tier 2 (burst scaling): GitHub scheduled bursts for extra throughput.
- Tier 3 (operator feedback): submit periodic bridge feedback for direction.
