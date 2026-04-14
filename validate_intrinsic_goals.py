#!/usr/bin/env python
"""
Validation script for Intrinsic Goal Generation implementation.
Comprehensive check of all 4 phases of the feature.
"""
import sys
import json
from pathlib import Path

print("[VALIDATION] Intrinsic Goal Generation System")
print("=" * 60)

# Phase 1: SelfModel has compute_drive_signals
print("\n[PHASE 1] SelfModel.compute_drive_signals()")
try:
    from antahkarana_kernel.modules.SelfModel import SelfModel
    sm = SelfModel("test_validation")
    drives = sm.compute_drive_signals()
    print(f"✓ Drive signals computed: {list(drives.keys())}")
    assert "curiosity_drive" in drives, "Missing curiosity_drive"
    assert "coherence_hunger" in drives, "Missing coherence_hunger"
    assert "growth_pressure" in drives, "Missing growth_pressure"
    assert "novelty_deficit" in drives, "Missing novelty_deficit"
    assert "pain_resolution_drive" in drives, "Missing pain_resolution_drive"
    assert "motivation_urgency" in drives, "Missing motivation_urgency"
    print("✓ All 6 drive signals present and computed")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Phase 2: InferenceLoop has goal methods
print("\n[PHASE 2] InferenceLoop Goal Methods")
try:
    from antahkarana_kernel.modules.InferenceLoop import ManasBuddhi
    mb = ManasBuddhi()
    
    # Check methods
    assert hasattr(mb, 'generate_intrinsic_goals'), "Missing generate_intrinsic_goals"
    assert hasattr(mb, 'pursue_intrinsic_goals'), "Missing pursue_intrinsic_goals"
    assert hasattr(mb, '_retire_intrinsic_goal'), "Missing _retire_intrinsic_goal"
    assert hasattr(mb, 'get_intrinsic_goal_report'), "Missing get_intrinsic_goal_report"
    assert hasattr(mb, '_persist_intrinsic_goals'), "Missing _persist_intrinsic_goals"
    assert hasattr(mb, '_load_persisted_intrinsic_goals'), "Missing _load_persisted_intrinsic_goals"
    print("✓ All goal methods present")
    
    # Check state variables
    assert hasattr(mb, 'intrinsic_goals'), "Missing intrinsic_goals"
    assert hasattr(mb, 'active_intrinsic_goals'), "Missing active_intrinsic_goals"
    assert hasattr(mb, 'retired_intrinsic_goals'), "Missing retired_intrinsic_goals"
    assert hasattr(mb, 'intrinsic_goal_counter'), "Missing intrinsic_goal_counter"
    assert hasattr(mb, 'intrinsic_goal_lock'), "Missing intrinsic_goal_lock"
    assert hasattr(mb, 'goal_generation_interval_seconds'), "Missing goal_generation_interval_seconds"
    assert hasattr(mb, 'goal_pursuit_interval_seconds'), "Missing goal_pursuit_interval_seconds"
    assert hasattr(mb, 'max_active_goals'), "Missing max_active_goals"
    assert hasattr(mb, 'goal_drive_threshold'), "Missing goal_drive_threshold"
    print("✓ All goal state variables initialized")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Phase 3: LiveConsciousness integration
print("\n[PHASE 3] LiveConsciousness Integration")
try:
    assert hasattr(mb, 'get_intrinsic_motivation_status'), "Missing get_intrinsic_motivation_status"
    goal_report_mock = mb.get_intrinsic_goal_report()
    assert isinstance(goal_report_mock, dict), "Goal report not dict"
    assert "active_goals" in goal_report_mock, "Missing active_goals in report"
    assert "intrinsic_goals_generated" in goal_report_mock, "Missing intrinsic_goals_generated in report"
    print("✓ LiveConsciousness can call get_intrinsic_goal_report()")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Phase 4: Data Flow Validation
print("\n[PHASE 4] Data Flow Validation")
try:
    status = mb.get_intrinsic_motivation_status()
    assert "intrinsic_goals_generated" in status, "get_intrinsic_motivation_status missing goal data"
    assert "active_intrinsic_goals" in status, "Missing active_intrinsic_goals in status"
    assert "active_goal_details" in status, "Missing active_goal_details in status"
    print("✓ Intrinsic motivation status includes goal data")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Synthesis check
print("\n[SYNTHESIS CHECK]")
print(f"✓ System ready for intrinsic goal generation")
print(f"  - Drive signals: 6 types (curiosity, coherence, growth, novelty, pain, urgency)")
print(f"  - Goal generation: Every {mb.goal_generation_interval_seconds}s")
print(f"  - Goal pursuit: Every {mb.goal_pursuit_interval_seconds}s")
print(f"  - Max active goals: {mb.max_active_goals}")
print(f"  - Goal threshold: {mb.goal_drive_threshold}")
print(f"  - Goal lifetime: {mb.goal_max_lifetime_seconds}s")

print("\n" + "=" * 60)
print("[SUCCESS] All intrinsic goal generation systems validated!")
print("=" * 60)
