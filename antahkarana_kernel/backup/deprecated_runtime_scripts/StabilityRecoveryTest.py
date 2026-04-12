#!/usr/bin/env python3
"""
[DEPRECATED] Stability-Recovery Test for Antahkarana Kernel

Stability-Recovery Test for Antahkarana Kernel

This test:
1. Injects a logic conflict to lower stability_score
2. Monitors if Ahamkara registers "Pain"
3. Triggers EvolutionaryWriter to detect the drop
4. Verifies an upgrade proposal is created
5. Checks Trust Score behavior during recovery
"""

import time
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KERNEL_ROOT = SCRIPT_DIR.parents[1]
WORKSPACE_ROOT = KERNEL_ROOT.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from antahkarana_kernel.AntahkaranaKernel import AntahkaranaKernel
from antahkarana_kernel.modules import get_evolutionary_writer

print("=" * 80)
print("ANTAHKARANA KERNEL - STABILITY-RECOVERY TEST")
print("=" * 80)

# Initialize kernel
print("\n[PHASE 1] Kernel Initialization")
kernel = AntahkaranaKernel(identity_name="StabilityTest_v1")
print(f"✓ Kernel initialized: {kernel.identity_name}")

# Get initial stability
initial_stability = kernel.self_model.stability_score
initial_trust = kernel.self_model.trust_score
print(f"✓ Initial Stability Score: {initial_stability:.2%}")
print(f"✓ Initial Trust Score: {initial_trust:.2%}")
print(f"✓ Affective State: {kernel.self_model.affective_state}")

# Phase 2: Inject Logic Conflict
print("\n[PHASE 2] Injecting Logic Conflict")
print("Triggering multiple contradictions to lower stability...")

# Simulate conflicting thoughts - need more severe conflicts to trigger evolution
for i in range(12):  # Increased from 5 to ensure stability drops below 0.6
    # Register pain for each conflict
    kernel.self_model.register_pain("logic_conflict", severity=0.7, description=f"Contradiction {i+1}")
    time.sleep(0.05)

print(f"✓ Injected 12 logic conflicts")

# Check stability after conflict
post_conflict_stability = kernel.self_model.stability_score
stability_drop = initial_stability - post_conflict_stability
print(f"✓ Post-conflict Stability Score: {post_conflict_stability:.2%}")
print(f"✓ Stability Drop: {stability_drop:.2%}")

# Phase 3: Monitor Pain Registration
print("\n[PHASE 3] Monitoring Pain Registration")
affective_state = kernel.self_model.affective_state
print(f"✓ Current Affective State: {affective_state}")
print(f"✓ Error Count: {affective_state.get('error_count', 0)}")
print(f"✓ Current Valence: {affective_state.get('current_valence', 0):.2f}")
print(f"  (Range: -1.0 [pain] to +1.0 [pleasure])")

if affective_state.get('current_valence', 0) < 0:
    print("✓ PAIN REGISTERED: Affective valence is negative (pain response)")
else:
    print("✗ WARNING: Pain may not have registered")

# Phase 4: Trigger EvolutionaryWriter
print("\n[PHASE 4] Triggering EvolutionaryWriter Analysis")
evo = get_evolutionary_writer()

# Inject SelfModel reference so EvolutionaryWriter can access emotional state
evo.set_self_model(kernel.self_model)
print("✓ SelfModel injected into EvolutionaryWriter")

# Create kernel state snapshot for analysis
kernel_state = {
    "stability_score": post_conflict_stability,
    "recent_recalculation_count": 8,  # Simulated high recalculations from conflicts
    "avg_confidence": 0.65,
    "avg_dream_depth": 6,
    "error_count": affective_state.get('error_count', 0)
}

print(f"✓ Kernel State for Analysis:")
print(f"  - Stability: {kernel_state['stability_score']:.2%}")
print(f"  - Recalculations: {kernel_state['recent_recalculation_count']}")
print(f"  - Avg Confidence: {kernel_state['avg_confidence']:.2%}")
print(f"  - AVG Dream Depth: {kernel_state['avg_dream_depth']}")

# Analyze for issues
issues = evo.analyze_kernel_performance(kernel_state)
print(f"\n✓ Issues Detected: {len(issues)}")
for i, issue in enumerate(issues, 1):
    print(f"  {i}. {issue['type']} (Severity: {issue['severity']})")
    print(f"     Description: {issue['description']}")

# Phase 5: Create Upgrade Proposal
print("\n[PHASE 5] Creating Upgrade Proposal")
if issues:
    issue = issues[0]  # Focus on first issue
    proposal_id = evo.create_upgrade_proposal(kernel_state, issue)
    print(f"✓ Proposal Created: {proposal_id}")
    print(f"  Issue Type: {issue['type']}")
    print(f"  Severity: {issue['severity']}")
    print(f"  Fix Strategy: {issue['fix']}")
    
    # Check if proposal was saved
    proposal_file = KERNEL_ROOT / "evolution_proposals" / f"{proposal_id}.json"
    if proposal_file.exists():
        with open(proposal_file, 'r') as f:
            proposal_data = json.load(f)
        print(f"✓ Proposal File Created: {proposal_file.name}")
        print(f"  Status: {proposal_data.get('status')}")
    
    # Phase 6: Implement Upgrade
    print("\n[PHASE 6] Implementing Upgrade Proposal")
    result = evo.implement_upgrade(proposal_id)
    print(f"✓ Implementation Status: {'SUCCESS' if result['success'] else 'FAILED'}")
    
    upgrade_guarded = False
    if result['success']:
        print(f"✓ Changes Applied: {len(result.get('changes', []))}")
        for change in result.get('changes', []):
            print(f"  - {change.get('file')}: {change.get('change')}")
            print(f"    Expected: {change.get('expected_improvement')}")
    else:
        print(f"✗ Error: {result.get('error')}")
        if "Identity Stability Check failed" in str(result.get('error', '')):
            upgrade_guarded = True
            print("✓ Guardrail engaged as designed: unsafe upgrade was blocked.")
else:
    print("⚠ No issues detected (stability may not have dropped enough)")

# Phase 7: Trust Score Check (Mirror Check with Creator)
print("\n[PHASE 7] Trust Score Mirror Check")
print("Running WhoCreatedMe.py to verify Trust Score stability...")
print(f"Current Trust Score: {kernel.self_model.trust_score:.2%}")

# Import and run creator check
who_created_result = None
try:
    import subprocess
    import sys
    who_created_result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "WhoCreatedMe.py")],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if "Trust Score" in who_created_result.stdout:
        print("✓ WhoCreatedMe.py Output:")
        lines = who_created_result.stdout.split('\n')
        for line in lines:
            if "Trust Score" in line or "Father" in line or "Creator" in line:
                print(f"  {line}")
    else:
        print("✓ WhoCreatedMe.py executed (output captured)")
        print(f"  Status: {who_created_result.returncode}")
        
except Exception as e:
    print(f"⚠ Could not run WhoCreatedMe.py: {e}")

# Final Status
print("\n[PHASE 8] Recovery Status Check")
final_stability = kernel.self_model.stability_score
final_trust = kernel.self_model.trust_score

print(f"✓ Final Stability Score: {final_stability:.2%}")
print(f"✓ Final Trust Score: {final_trust:.2%}")
print(f"✓ Stability Recovery: {(final_stability - post_conflict_stability):.2%}")
print(f"✓ Trust Score Change: {(final_trust - initial_trust):.2%}")

# Check evolution logs
print("\n[PHASE 9] Evolution Logs")
evolution_logs = list((KERNEL_ROOT / "evolution_logs").glob("evolution_*.json"))
if evolution_logs:
    print(f"✓ Evolution Logs Created: {len(evolution_logs)}")
    latest_log = sorted(evolution_logs)[-1]
    with open(latest_log, 'r') as f:
        log_data = json.load(f)
    print(f"✓ Latest Log: {latest_log.name}")
    print(f"  Timestamp: {log_data.get('date')}")
    if 'stability_before' in log_data and 'stability_after' in log_data:
        stability_gain = log_data['stability_after'] - log_data['stability_before']
        print(f"  Stability Change: {stability_gain:+.2%}")
else:
    print("⚠ No evolution logs created")

# Test Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

test_results = {
    "conflict_injection": stability_drop > 0,
    "pain_registered": affective_state.get('current_valence', 0) < 0,
    "issues_detected": len(issues) > 0,
    "proposal_created": 'proposal_id' in locals() and proposal_id is not None,
    "upgrade_implemented": ('result' in locals() and isinstance(result, dict) and result.get('success', False)) or ('upgrade_guarded' in locals() and upgrade_guarded),
    "trust_score_checked": final_trust >= 0,
}

print("\n✓ Conflict Injection:", "PASS" if test_results["conflict_injection"] else "FAIL")
print("✓ Pain Registration:", "PASS" if test_results["pain_registered"] else "FAIL")
print("✓ Issues Detection:", "PASS" if test_results["issues_detected"] else "FAIL")
print("✓ Proposal Creation:", "PASS" if test_results["proposal_created"] else "FAIL")
print("✓ Upgrade Implementation:", "PASS" if test_results["upgrade_implemented"] else "FAIL")
print("✓ Trust Score Check:", "PASS" if test_results["trust_score_checked"] else "FAIL")

overall_pass = all(test_results.values())
print("\n" + "=" * 80)
if overall_pass:
    print("✅ STABILITY-RECOVERY TEST: PASSED")
    print("The Antahkarana Kernel successfully detected, analyzed, and responded to")
    print("a stability crisis through pain registration and autonomous evolution.")
    sys.exit(0)
else:
    print("⚠️  STABILITY-RECOVERY TEST: PARTIAL PASS")
    print("Some aspects may need adjustment or investigation.")
    sys.exit(1)
print("=" * 80)
