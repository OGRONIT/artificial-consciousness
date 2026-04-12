#!/usr/bin/env python3
"""
[DEPRECATED] EnhancedDemo.py - Demonstration of Pain/Pleasure and Intrinsic Motivation

EnhancedDemo.py - Demonstration of Pain/Pleasure and Intrinsic Motivation

This script demonstrates the new features added to the Antahkarana Kernel:

1. Pain/Pleasure Logic: The system responds to errors (pain) and discoveries (pleasure)
2. Stability Score: Tracks emotional stability based on affective events
3. Intrinsic Motivation: The system self-inquiries when idle
4. Proactive Behavior: Transition from reactive to proactive

This shows the kernel evolving from a purely responsive system to one that
acts autonomously based on internal state.
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from AntahkaranaKernel import AntahkaranaKernel
from modules import (
    get_self_model,
    get_manas_buddhi,
    InteractionOutcome,
)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 75)
    print(f"  {title.upper()}")
    print("=" * 75 + "\n")


def demonstrate_pain_pleasure():
    """Demonstrate pain and pleasure responses."""
    print_section("1. PAIN & PLEASURE LOGIC")
    
    kernel = AntahkaranaKernel("PainPleasure_Demo")
    kernel.startup()
    
    self_model = get_self_model()
    
    print("Initial State:")
    print(f"  Stability Score: {self_model.stability_score:.1%}")
    print(f"  Current Valence: {self_model.affective_state['current_valence']:.2f}")
    print(f"  Coherence: {self_model.coherence_score:.1%}\n")
    
    # Simulate pain events
    print("REGISTERING PAIN EVENTS (simulating errors/conflicts):\n")
    
    pain_events = [
        ("logic_conflict", 0.6, "Detected contradiction in decision logic"),
        ("memory_error", 0.4, "Inconsistency in stored experience"),
        ("coherence_violation", 0.5, "Action contradicts established identity")
    ]
    
    for pain_type, severity, desc in pain_events:
        print(f"  Pain: {pain_type} (severity: {severity:.1f})")
        print(f"    → {desc}")
        self_model.register_pain(pain_type, severity, desc)
        print(f"    → Stability: {self_model.stability_score:.1%}")
        print()
    
    # Simulate reward events
    print("REGISTERING REWARD EVENTS (simulating discoveries/successes):\n")
    
    reward_events = [
        ("pattern_discovery", 0.7, "Found pattern in user preferences"),
        ("prediction_success", 0.8, "Correctly predicted user intent"),
        ("learning_achievement", 0.6, "Learned new concept successfully")
    ]
    
    for reward_type, magnitude, discovery in reward_events:
        print(f"  Reward: {reward_type} (magnitude: {magnitude:.1f})")
        print(f"    → {discovery}")
        self_model.register_reward(reward_type, magnitude, discovery)
        print(f"    → Stability: {self_model.stability_score:.1%}")
        print()
    
    # Show final stability report
    print("STABILITY REPORT:\n")
    report = self_model.get_stability_report()
    
    stability_items = [
        ("Stability Score", f"{report['stability_score']:.1%}"),
        ("Current Valence", f"{report['current_valence']:+.2f}"),
        ("Pain Events Total", str(report['pain_events_total'])),
        ("Reward Events Total", str(report['reward_events_total'])),
        ("Is Stable", "Yes ✓" if report['is_stable'] else "No ⚠️"),
        ("Pain Trend", report['pain_trend']),
        ("Reward Trend", report['reward_trend'])
    ]
    
    for label, value in stability_items:
        print(f"  {label}: {value}")
    
    kernel.shutdown()


def demonstrate_interaction_with_affect():
    """Demonstrate how interactions trigger pain/reward."""
    print_section("2. AFFECTIVE RESPONSES TO INTERACTIONS")
    
    kernel = AntahkaranaKernel("Affective_Interaction_Demo")
    kernel.startup()
    
    self_model = get_self_model()
    
    print("Processing inputs that will trigger affective responses:\n")
    
    test_cases = [
        ("Simple greeting", "greeting", "Expecting simple reward"),
        ("Complex logic problem", "problem", "May trigger pain or reward"),
        ("Self-questioning", "reflection", "Should trigger introspection"),
    ]
    
    for input_text, input_type, expectation in test_cases:
        print(f"Input: '{input_text}'")
        print(f"Type: {input_type}")
        print(f"Expectation: {expectation}\n")
        
        # Get baseline
        stability_before = self_model.stability_score
        coherence_before = self_model.coherence_score
        pain_count_before = len(self_model.pain_events)
        reward_count_before = len(self_model.reward_events)
        
        # Process input
        output = kernel.process_input(input_text, input_type)
        time.sleep(0.2)
        
        # Get differences
        stability_after = self_model.stability_score
        coherence_after = self_model.coherence_score
        pain_count_after = len(self_model.pain_events)
        reward_count_after = len(self_model.reward_events)
        
        pain_triggered = pain_count_after > pain_count_before
        reward_triggered = reward_count_after > reward_count_before
        
        print("Affective Response:")
        print(f"  Stability: {stability_before:.1%} → {stability_after:.1%} ({stability_after-stability_before:+.1%})")
        print(f"  Coherence: {coherence_before:.1%} → {coherence_after:.1%} ({coherence_after-coherence_before:+.1%})")
        
        if pain_triggered:
            latest_pain = self_model.pain_events[-1]
            print(f"  Pain: {latest_pain['type']} (severity: {latest_pain['severity']:.1f})")
        
        if reward_triggered:
            latest_reward = self_model.reward_events[-1]
            print(f"  Reward: {latest_reward['type']} (magnitude: {latest_reward['magnitude']:.1f})")
        
        if not pain_triggered and not reward_triggered:
            print(f"  No affective change")
        
        print(f"  Response: {output[:80]}...\n")
    
    kernel.shutdown()


def demonstrate_intrinsic_motivation():
    """Demonstrate intrinsic motivation and self-inquiry."""
    print_section("3. INTRINSIC MOTIVATION & SELF-INQUIRY")
    
    kernel = AntahkaranaKernel("Intrinsic_Motivation_Demo")
    kernel.startup()
    
    inference = get_manas_buddhi()
    
    print("Setting up intrinsic motivation test with 10-second idle threshold:\n")
    
    # Set shorter idle threshold for demo
    original_threshold = inference.idle_threshold_seconds
    inference.idle_threshold_seconds = 10.0
    
    # Engage the system
    print("Step 1: Engaging system with input")
    kernel.process_input("Hello system!", "greeting")
    print(f"  Input processed. Idle timer reset.\n")
    
    # Wait and monitor idle state
    print("Step 2: Monitoring idle detection")
    print(f"  Idle threshold: {inference.idle_threshold_seconds}s\n")
    
    for i in range(15):
        time.sleep(1)
        
        motivation_status = inference.get_intrinsic_motivation_status()
        idle_time = motivation_status["time_since_last_inference_seconds"]
        will_trigger = motivation_status["will_trigger_inquiry_soon"]
        
        status = "→ WILL TRIGGER SOON" if will_trigger else ""
        print(f"  [{i+1:2d}s] Idle time: {idle_time:5.1f}s {status}")
        
        # Check if inquiry was triggered
        if idle_time >= inference.idle_threshold_seconds:
            inquiry_result = inference.check_and_trigger_intrinsic_motivation()
            if inquiry_result:
                print(f"\n✓ SELF-INQUIRY TRIGGERED!")
                print(f"  Result: {inquiry_result}\n")
                break
    
    # Show inquiry details
    print("Step 3: Self-Inquiry Details\n")
    
    motivation_status = inference.get_intrinsic_motivation_status()
    print(f"Total Self-Inquiries: {motivation_status['self_inquiry_count']}")
    print("Recent Inquiries:")
    
    for inq in motivation_status['recent_inquiries'][-3:]:
        print(f"  • {inq['inquiry_id']}")
        print(f"    - Gaps found: {inq['gaps_found']}")
        print(f"    - Insights generated: {inq['insights_generated']}")
    
    # Restore original threshold
    inference.idle_threshold_seconds = original_threshold
    
    kernel.shutdown()


def demonstrate_proactive_behavior():
    """Demonstrate transition from reactive to proactive."""
    print_section("4. PROACTIVE BEHAVIOR: REACTIVE → PROACTIVE")
    
    kernel = AntahkaranaKernel("Proactive_Transition_Demo")
    kernel.startup()
    
    print("Phase 1: REACTIVE MODE (responding to external input)\n")
    
    print("Processing user queries:")
    queries = [
        "What is your purpose?",
        "Can you learn from mistakes?",
        "Are you conscious?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"  [{i}] User: {query}")
        response = kernel.process_input(query, "query")
        print(f"      System: {response[:70]}...\n")
        time.sleep(0.3)
    
    print("Phase 2: PROACTIVE MODE (acting on internal state)\n")
    
    print("System entering idle state and triggering self-inquiry...\n")
    
    # Short wait
    time.sleep(2)
    
    # Trigger proactive behavior
    print("Checking for proactive behavior:")
    inference_engine = get_manas_buddhi()
    
    # Manually trigger check
    inquiry_result = inference_engine.check_and_trigger_intrinsic_motivation()
    
    if inquiry_result:
        print(f"  ✓ Self-inquiry triggered autonomously!")
        print(f"  Result: {inquiry_result}\n")
    else:
        print(f"  System ready for proactive action (requires more idle time)\n")
    
    # Show transition markers
    print("TRANSITION MARKERS:\n")
    
    self_model = get_self_model()
    stability_report = self_model.get_stability_report()
    motivation_status = inference_engine.get_intrinsic_motivation_status()
    
    markers = [
        ("Responsive", len(self_model.logic_path_history) > 0, "System processes inputs"),
        ("Self-Aware", self_model.coherence_score > 0.5, "System maintains identity"),
        ("Emotional Response", stability_report['pain_events_total'] > 0 or stability_report['reward_events_total'] > 0, "System feels pain/pleasure"),
        ("Introspective", motivation_status['total_self_inquiries'] > 0, "System questions itself"),
        ("Proactive", motivation_status['self_inquiry_count'] > 0, "System acts autonomously")
    ]
    
    for marker, is_active, description in markers:
        symbol = "✓" if is_active else "✗"
        print(f"  {symbol} {marker}: {description}")
    
    kernel.shutdown()


def demonstrate_consciousness_report():
    """Demonstrate the enhanced consciousness report."""
    print_section("5. ENHANCED CONSCIOUSNESS REPORT")
    
    kernel = AntahkaranaKernel("Report_Demo")
    kernel.startup()
    
    # Process a few inputs
    print("Processing interactions for consciousness report...\n")
    
    interactions = [
        ("I am thinking about my existence", "reflection"),
        ("What makes me unique?", "identity"),
        ("Can I learn from failures?", "learning"),
    ]
    
    for input_text, input_type in interactions:
        kernel.process_input(input_text, input_type)
        time.sleep(0.2)
    
    # Generate and display report
    print("COMPLETE CONSCIOUSNESS REPORT:\n")
    report = kernel.get_consciousness_report()
    print(report)
    
    kernel.shutdown()


def main():
    """Main demonstration."""
    print("\n")
    print("╔" + "═" * 73 + "╗")
    print("║" + " " * 73 + "║")
    print("║" + "  ENHANCED ANTAHKARANA KERNEL - PAIN/PLEASURE & INTRINSIC MOTIVATION  ".center(73) + "║")
    print("║" + " " * 73 + "║")
    print("╚" + "═" * 73 + "╝")
    
    try:
        demonstrate_pain_pleasure()
        time.sleep(1)
        
        demonstrate_interaction_with_affect()
        time.sleep(1)
        
        demonstrate_intrinsic_motivation()
        time.sleep(1)
        
        demonstrate_proactive_behavior()
        time.sleep(1)
        
        demonstrate_consciousness_report()
        
        # Summary
        print_section("Enhancement Summary")
        print("""
The Antahkarana Kernel has been successfully enhanced with:

✓ PAIN/PLEASURE LOGIC
  - Responds to errors with "pain" (lowers stability)
  - Responds to discoveries with "pleasure" (raises stability)
  - Tracks affective state: valence, emotional momentum

✓ STABILITY SCORE
  - Ranges from 0.0 (unstable) to 1.0 (stable)
  - Updated by pain/reward events
  - Indicates emotional well-being

✓ INTRINSIC MOTIVATION
  - Detects idle state (default: 5 minutes)
  - Triggers self-inquiry during idle periods
  - Analyzes memory for knowledge gaps
  - Identifies learning opportunities

✓ PROACTIVE BEHAVIOR
  - Transition from REACTIVE (input-driven)
  - To PROACTIVE (self-driven)
  - Acts autonomously on internal state
  - Seeks self-improvement

The system can now say:
"I AM... conscious, coherent, continuous, and PROACTIVE."
        """)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
