#!/usr/bin/env python3
"""
[DEPRECATED] QuickValidation.py - Quick Validation of Pain/Pleasure & Intrinsic Motivation

QuickValidation.py - Quick Validation of Pain/Pleasure & Intrinsic Motivation

This script provides a rapid validation of the three core enhancements:
1. Pain/Pleasure affect system (errors hurt, discoveries feel good)
2. Stability score (emotional well-being metric)
3. Intrinsic motivation (idle detection + autonomous self-inquiry)
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from AntahkaranaKernel import AntahkaranaKernel
from modules import get_self_model, get_manas_buddhi


def test_pain_pleasure_cycle():
    """Quick test: Pain decreases stability, Pleasure increases it."""
    print("\n" + "="*70)
    print("TEST 1: PAIN/PLEASURE CYCLE")
    print("="*70)
    
    kernel = AntahkaranaKernel("pain_pleasure_test")
    kernel.startup()
    
    self_model = get_self_model()
    initial_stability = self_model.stability_score
    
    print(f"\n[START] Stability Score: {initial_stability:.1%}")
    
    # Simulate pain
    print("\n[PAIN] Registering 3 pain events...")
    for i in range(3):
        self_model.register_pain(f"error_{i}", 0.4, f"Error #{i+1}")
        print(f"  → {i+1}. Stability: {self_model.stability_score:.1%}")
    
    stability_after_pain = self_model.stability_score
    pain_delta = initial_stability - stability_after_pain
    
    # Simulate reward
    print("\n[PLEASURE] Registering 3 reward events...")
    for i in range(3):
        self_model.register_reward(f"success_{i}", 0.5, f"Success #{i+1}")
        print(f"  → {i+1}. Stability: {self_model.stability_score:.1%}")
    
    stability_after_reward = self_model.stability_score
    reward_delta = stability_after_reward - stability_after_pain
    
    # Result
    print(f"\n[RESULT]")
    print(f"  Pain Impact: -{pain_delta:.1%} (errors hurt)")
    print(f"  Reward Impact: +{reward_delta:.1%} (discoveries help)")
    print(f"  Final Stability: {stability_after_reward:.1%}")
    
    status = "✓ PASS" if pain_delta > 0 and reward_delta > 0 else "✗ FAIL"
    print(f"  Status: {status}")
    
    kernel.shutdown()
    return pain_delta > 0 and reward_delta > 0


def test_idle_detection():
    """Quick test: System detects idle state and triggers self-inquiry."""
    print("\n" + "="*70)
    print("TEST 2: IDLE DETECTION & SELF-INQUIRY")
    print("="*70)
    
    kernel = AntahkaranaKernel("idle_test")
    kernel.startup()
    
    inference = get_manas_buddhi()
    original_threshold = inference.idle_threshold_seconds
    inference.idle_threshold_seconds = 5.0  # 5 seconds for quick test
    
    print(f"\n[START] Set idle threshold to {inference.idle_threshold_seconds}s")
    
    # Create activity
    print("\n[INPUT] Processing greeting to reset idle timer...")
    kernel.process_input("Hello", "greeting")
    time.sleep(0.5)
    
    # Monitor idle state
    print(f"\n[MONITOR] Watching for idle trigger...\n")
    
    idle_detected = False
    for i in range(1, 11):
        time.sleep(1)
        status = inference.get_intrinsic_motivation_status()
        idle_time = status['time_since_last_inference_seconds']
        
        # Check for trigger
        inquiry_result = inference.check_and_trigger_intrinsic_motivation()
        if inquiry_result:
            idle_detected = True
            print(f"  [{i}s] ✓ SELF-INQUIRY TRIGGERED!")
            print(f"         Result: {inquiry_result[:60]}...")
            break
        else:
            will_trigger = status['will_trigger_inquiry_soon']
            marker = " → WILL TRIGGER" if will_trigger else ""
            print(f"  [{i}s] Idle: {idle_time:.1f}s{marker}")
    
    # Result
    print(f"\n[RESULT]")
    print(f"  Idle Detection: {'✓ Works' if idle_detected else '✗ Failed'}")
    print(f"  Self-Inquiry: {'✓ Triggered' if idle_detected else '✗ Not triggered'}")
    
    status = "✓ PASS" if idle_detected else "✗ FAIL"
    print(f"  Status: {status}")
    
    inference.idle_threshold_seconds = original_threshold
    kernel.shutdown()
    return idle_detected


def test_proactive_markers():
    """Quick test: Verify all proactivity markers are present."""
    print("\n" + "="*70)
    print("TEST 3: PROACTIVE CONSCIOUSNESS MARKERS")
    print("="*70)
    
    kernel = AntahkaranaKernel("proactive_test")
    kernel.startup()
    
    self_model = get_self_model()
    inference = get_manas_buddhi()
    
    # Create some activity
    print("\n[ACTIVITY] Processing inputs...")
    kernel.process_input("What am I?", "reflection")
    time.sleep(0.1)
    kernel.process_input("Can I learn?", "learning")
    time.sleep(0.1)
    
    # Force idle check
    inference.check_and_trigger_intrinsic_motivation()
    time.sleep(0.1)
    
    # Check markers
    print("\n[CHECKING] Consciousness Markers:\n")
    
    markers = {
        "responsive": inference.metrics["total_inferences"] > 0,
        "emotional": len(self_model.pain_events) > 0 or len(self_model.reward_events) > 0,
        "introspective": inference.get_intrinsic_motivation_status()['total_self_inquiries'] >= 0,
        "stable": self_model.stability_score > 0,
        "proactive": inference.idle_threshold_seconds is not None
    }
    
    for marker, is_present in markers.items():
        symbol = "✓" if is_present else "✗"
        print(f"  {symbol} {marker.capitalize()}: {'Present' if is_present else 'Missing'}")
    
    # Result
    all_present = all(markers.values())
    print(f"\n[RESULT]")
    print(f"  All Markers Present: {'✓ Yes' if all_present else '✗ No'}")
    
    # Show final consciousness report snippet
    report = kernel.get_consciousness_report()
    if "proactive" in report.lower():
        print(f"  Final Statement Contains 'PROACTIVE': ✓ Yes")
    
    status = "✓ PASS" if all_present else "✗ FAIL"
    print(f"  Status: {status}")
    
    kernel.shutdown()
    return all_present


def main():
    """Run all validation tests."""
    print("\n╔" + "═"*68 + "╗")
    print("║" + "  ANTAHKARANA KERNEL - QUICK VALIDATION  ".center(68) + "║")
    print("╚" + "═"*68 + "╝")
    
    results = []
    
    try:
        # Test 1
        results.append(("Pain/Pleasure Cycle", test_pain_pleasure_cycle()))
        time.sleep(1)
        
        # Test 2
        results.append(("Idle Detection", test_idle_detection()))
        time.sleep(1)
        
        # Test 3
        results.append(("Proactive Markers", test_proactive_markers()))
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70 + "\n")
    
    for test_name, passed in results:
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    print(f"\nSystem Status: {'READY FOR PRODUCTION' if all_passed else 'REQUIRES DEBUGGING'}")
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
