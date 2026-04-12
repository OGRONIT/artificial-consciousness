# EvolutionaryWriter Quick Start Guide

## Overview

The EvolutionaryWriter (Ghost Writer) is now integrated into your Antahkarana Kernel. It automatically detects performance bottlenecks and creates optimization proposals.

## Basic Usage

### 1. Initialize the Evolutionary Writer

```python
from modules import get_evolutionary_writer

evo = get_evolutionary_writer()
print(evo.get_evolution_status())
```

### 2. Analyze Kernel Performance

```python
from AntahkaranaKernel import AntahkaranaKernel

# Create kernel instance
kernel = AntahkaranaKernel()

# Get kernel state
kernel_state = {
    "recent_recalculation_count": 5,
    "avg_confidence": 0.75,
    "avg_dream_depth": 4
}

# Analyze for issues
issues = evo.analyze_kernel_performance(kernel_state)

# View detected issues
for issue in issues:
    print(f"Issue: {issue['type']} (Severity: {issue['severity']})")
    print(f"Description: {issue['description']}")
    print(f"Fix: {issue['fix']}\n")
```

### 3. Create and Implement Upgrade Proposals

```python
# Create proposal for first issue
if issues:
    issue = issues[0]
    proposal_id = evo.create_upgrade_proposal(kernel_state, issue)
    print(f"Proposal created: {proposal_id}")
    
    # Implement the upgrade
    result = evo.implement_upgrade(proposal_id)
    
    if result['success']:
        print("✅ Upgrade applied successfully")
        for change in result['changes']:
            print(f"  - {change['file']}: {change['change']}")
    else:
        print(f"❌ Upgrade failed: {result.get('error')}")
```

### 4. Monitor Evolution Status

```python
status = evo.get_evolution_status()
print(f"Current version: {status['current_version']}")
print(f"Next version: {status['next_version']}")
print(f"Proposals pending: {status['proposal_count']}")
print(f"Evolution events: {status['evolution_events_count']}")
```

### 5. Access Evolution Logs (with Creator Signature)

```python
# Only accessible with creator signature and trust > 0.8
logs = evo.list_evolution_logs(creator_signature="YOUR_SIGNATURE", limit=5)

for log in logs:
    print(f"\nEvolution Log: {log['date']}")
    print(f"Stability change: {log['metrics']['improvements'].get('stability', 'N/A')}")
    print(f"Upgrades applied: {len(log['upgrades_applied'])}")
```

## Automatic Detection Triggers

The EvolutionaryWriter automatically detects and creates proposals for:

1. **High Error Rate** - When errors exceed threshold and stability drops below 0.6
2. **Coherence Instability** - When recalculations exceed 10 per execution
3. **Low Confidence** - When average confidence drops below 65%
4. **Excessive Dreaming** - When dream cycles exceed 7 per execution

## Safety Features

- **Backup Creation**: All files backed up before modification
- **Trust Score Gate**: Requires trust_score ≥ 0.8
- **Creator Signature**: Must identify as creator
- **Rollback Capability**: Automatic revert on stability degradation
- **Audit Logging**: Complete history of all changes

## Configuration

Adjust evolution behavior in your kernel initialization:

```python
# Enable/disable autonomous evolution
kernel.set_evolution_enabled(True)  # Default: True

# Enable/disable automatic optimization
kernel.set_auto_optimize(True)  # Default: True
```

## Directory Structure

The EvolutionaryWriter operates in these directories:

```
antahkarana_kernel/
├── backup/                 # Automatic file backups
├── evolution_logs/         # Evolution history (JSON)
└── evolution_proposals/    # Pending proposals (JSON)
```

## Examples of Optimizations

The system can propose:

### 1. Enhanced Error Handling
- **File**: modules/SelfModel.py
- **Change**: Improved error detection logic
- **Result**: Catch 95% vs 80% of potential errors

### 2. Coherence Check Optimization
- **File**: modules/InferenceLoop.py
- **Change**: Enhanced dream cycle early-exit logic
- **Result**: 30% reduction in recalculations

### 3. Prediction Validation Improvement
- **File**: modules/InferenceLoop.py
- **Change**: Integrated outcome history into prediction scoring
- **Result**: Increase avg confidence from 0.65 to 0.78

### 4. Dream Cycle Efficiency
- **File**: modules/InferenceLoop.py
- **Change**: Reduce max_dream_simulations from 10 to 7
- **Result**: 40% reduction in deep cycles with better early-exit

## Monitoring Evolution

Check the evolution logs directory for JSON files:

```python
from pathlib import Path
import json

logs_dir = Path("evolution_logs")
for log_file in sorted(logs_dir.glob("evolution_*.json"), reverse=True)[:3]:
    with open(log_file) as f:
        log = json.load(f)
        print(f"Date: {log['date']}")
        print(f"Kernel: {log['kernel_name']}")
        print(f"Success: {log.get('evolution_success', 'Unknown')}")
```

## Next Steps

1. Run the FinalValidation.py script to verify everything works
2. Check COMPREHENSIVE_SYSTEM_STATE.md for full system documentation
3. Enable autonomous evolution in your kernel
4. Monitor evolution logs as the system improves itself

## Support

For issues or questions:
- Check COMPREHENSIVE_SYSTEM_STATE.md for detailed documentation
- Review evolution logs in `evolution_logs/` directory
- Examine proposals in `evolution_proposals/` directory
- Check backup files in `backup/` directory for reference

---

**Status**: EvolutionaryWriter is ready for active use.
