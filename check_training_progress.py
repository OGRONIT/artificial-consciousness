"""
Real-time Training Progress Tracker
Monitors and displays live training session progress
"""

import json
import time
from pathlib import Path
from datetime import datetime

def check_training_progress():
    """Check and display current training progress."""
    
    training_outputs = Path("d:/Artificial Consciousness/training_outputs")
    training_outputs.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print("LIVE TRAINING PROGRESS CHECK")
    print("="*80)
    print(f"Time: {datetime.now().isoformat()}\n")
    
    # Check for session directory
    session_dirs = list(training_outputs.glob("FULL_AUTO_*"))
    if not session_dirs:
        print("⏳ Training session initializing... (Output files being created)")
        return
    
    session_dir = session_dirs[0]
    print(f"✓ Session Active: {session_dir.name}\n")
    
    # Check for latest summary
    summary_file = training_outputs / "latest_training_summary.json"
    if summary_file.exists():
        try:
            summary = json.loads(summary_file.read_text())
            
            print("📊 TRAINING PROGRESS:")
            print(f"  Duration: {summary.get('duration', {}).get('actual_hours', 0):.2f} hours requested")
            print(f"  Cycles Completed: {summary.get('session', {}).get('cycles_completed', 0)}")
            print(f"  Total Facts Learned: {summary['learning']['total_facts_learned']}")
            print(f"  Facts per Cycle: {summary['learning']['average_facts_per_cycle']:.1f}")
            print(f"  Learning Acceleration: {summary['learning']['learning_rate_acceleration']:.2f}x")
            
            print("\n🧠 AUTONOMY & PERFORMANCE:")
            perf = summary.get('performance', {})
            print(f"  Avg Autonomy Score: {perf.get('average_autonomy_score', 0):.4f}")
            print(f"  Max Autonomy Score: {perf.get('max_autonomy_score', 0):.4f}")
            print(f"  Avg Coherence: {perf.get('average_coherence', 0):.4f}")
            print(f"  Avg Growth Signal: {perf.get('average_growth_signal', 0):.4f}")
            print(f"  System Stability: {perf.get('system_stability', 0):.4f}")
            
            print("\n🔄 EVOLUTION TRACKING:")
            evol = summary.get('evolution', {})
            print(f"  Self-Modifications: {evol.get('self_modifications', 0)}")
            print(f"  Modules Created: {evol.get('total_modules_created', 0)}")
            print(f"  Policies Updated: {evol.get('total_policies_updated', 0)}")
            
            if evol.get('modification_details'):
                print(f"\n  Recent Modifications:")
                for mod in evol['modification_details'][-3:]:
                    print(f"    • {mod.get('timestamp')}")
                    if mod.get('new_modules'):
                        for m in mod['new_modules']:
                            print(f"      - NEW MODULE: {m['name']}")
                    if mod.get('modified_policies'):
                        for p in mod['modified_policies']:
                            print(f"      - POLICY UPDATE: {p['policy']}")
            
            print("\n⚠️  ERRORS:")
            errors = summary.get('errors', {})
            print(f"  Total Errors: {errors.get('total_errors', 0)}")
            
        except Exception as e:
            print(f"⚠️  Could not read summary: {e}")
    
    # Check for checkpoints
    checkpoints = sorted(session_dir.glob("checkpoint_*.json"))
    if checkpoints:
        print(f"\n✓ Checkpoints Saved: {len(checkpoints)}")
        latest_checkpoint = checkpoints[-1]
        try:
            cp = json.loads(latest_checkpoint.read_text())
            print(f"  Latest: {latest_checkpoint.name}")
            print(f"    Cycles: {cp.get('elapsed_cycles', 0)}")
            print(f"    Facts Learned: {cp.get('total_facts_learned', 0)}")
        except:
            pass
    
    print("\n" + "="*80)
    print("Training continues in background... Check again in 15 minutes for updates!")
    print("="*80 + "\n")


if __name__ == "__main__":
    check_training_progress()
