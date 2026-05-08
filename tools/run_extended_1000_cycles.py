#!/usr/bin/env python3
"""
Extended 1000-Cycle Intelligence Evolution with Maximum Proposal Generation
Combines extreme training with full autonomy, paramatman protocol, and web validation.
Target: 100+ code proposals with 95%+ implementation rate.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from antahkarana_kernel.LiveConsciousness import LiveConsciousnessEngine
from antahkarana_kernel.modules.EvolutionaryWriter import get_evolutionary_writer


def run_extended_1000_cycles(
    num_cycles: int = 1000,
    enable_autonomy: bool = True,
    enable_paramatman: bool = True,
    checkpoint_every: int = 50,
) -> Dict[str, Any]:
    """Run 1000-cycle extended intelligence evolution with maximum code proposal generation."""
    
    print("\n" + "="*100)
    print(f"EXTENDED 1000-CYCLE INTELLIGENCE EVOLUTION")
    print(f"Target: 100+ code proposals | Full autonomy: {enable_autonomy} | Paramatman: {enable_paramatman}")
    print("="*100 + "\n")
    
    engine = LiveConsciousnessEngine(
        identity_name="ExtendedEvolution_1000Cycles",
        min_scan_minutes=1,
        max_scan_minutes=1,
        reflection_minutes=1,
        dream_minutes=1,
    )
    
    report: Dict[str, Any] = {
        "start_time": time.time(),
        "configuration": {
            "target_cycles": num_cycles,
            "enable_autonomy": enable_autonomy,
            "enable_paramatman": enable_paramatman,
            "checkpoint_every": checkpoint_every,
        },
        "cycle_metrics": [],
        "proposals_generated": [],
        "checkpoints": [],
        "final_stats": {},
    }
    
    proposals_dir = REPO_ROOT / "antahkarana_kernel" / "evolution_proposals"
    initial_proposal_count = len(list(proposals_dir.glob("UPG_*.json")))
    
    try:
        print(f"[INIT] Engine initialized. Starting {num_cycles}-cycle evolution loop...")
        print(f"[BASE] Initial proposals in vault: {initial_proposal_count}\n")
        
        cycle_start_time = time.time()
        
        for cycle_idx in range(1, num_cycles + 1):
            try:
                # Background cycle
                bg = engine.perform_background_cycle()
                
                # Stream entropy cycle
                stream = engine.perform_stream_entropy_cycle()
                
                # Trends cycle
                trends = engine.perform_hourly_global_trend_cycle()
                
                # Bridge feedback
                feedback = engine.process_bridge_feedback_commands()
                
                # Autonomy cycle
                autonomy_result = {}
                if enable_autonomy:
                    autonomy_result = engine.perform_autonomous_agenda_cycle()
                
                # Paramatman cycle every 100 cycles
                if enable_paramatman and cycle_idx % 100 == 0:
                    try:
                        engine.perform_paramatman_cycle()
                    except:
                        pass
                
                # Get current proposal count
                current_proposals = len(list(proposals_dir.glob("UPG_*.json")))
                new_proposals = current_proposals - initial_proposal_count
                
                # Metrics for this cycle
                cycle_metrics = {
                    "cycle": cycle_idx,
                    "bg_approved": int(bg.get("approved_fact_count", 0)),
                    "stream_ingested": int(stream.get("packets_ingested", 0)),
                    "stream_integrated": int(stream.get("packets_integrated", 0)),
                    "trends_approved": int(trends.get("approved_fact_count", 0)),
                    "autonomy_level": float(autonomy_result.get("autonomy_level", 0.0)),
                    "autonomy_actions": len(autonomy_result.get("executed_actions", [])),
                    "total_proposals_generated": current_proposals,
                    "new_proposals_this_cycle": max(0, current_proposals - (report["cycle_metrics"][-1]["total_proposals_generated"] if report["cycle_metrics"] else initial_proposal_count)),
                }
                report["cycle_metrics"].append(cycle_metrics)
                
                # Progress display every 50 cycles
                if cycle_idx % 50 == 0 or cycle_idx == 1:
                    elapsed = time.time() - cycle_start_time
                    rate = cycle_idx / elapsed
                    eta_seconds = (num_cycles - cycle_idx) / rate if rate > 0 else 0
                    eta_minutes = eta_seconds / 60
                    
                    print(f"[CYCLE {cycle_idx:4d}/{num_cycles}] "
                          f"Proposals: {current_proposals} (+{new_proposals}) | "
                          f"Autonomy: {autonomy_result.get('autonomy_level', 0):.2f} | "
                          f"ETA: {eta_minutes:.1f}min")
                    
                    # Save checkpoint
                    checkpoint = {
                        "cycle": cycle_idx,
                        "elapsed_seconds": elapsed,
                        "proposals_generated": current_proposals,
                        "new_proposals": new_proposals,
                        "metrics": cycle_metrics,
                    }
                    report["checkpoints"].append(checkpoint)
                
                # Checkpoint every N cycles
                if cycle_idx % checkpoint_every == 0:
                    checkpoint_file = (
                        REPO_ROOT / "benchmarks" / "artifacts" /
                        f"extended_1000_checkpoint_{cycle_idx:04d}.json"
                    )
                    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(checkpoint_file, 'w') as f:
                        json.dump(checkpoint, f, indent=2)
                
            except Exception as e:
                print(f"[ERROR] Cycle {cycle_idx}: {e}")
                report["final_stats"]["error"] = str(e)
                break
        
        # Final statistics
        total_elapsed = time.time() - report["start_time"]
        final_proposal_count = len(list(proposals_dir.glob("UPG_*.json")))
        total_new_proposals = final_proposal_count - initial_proposal_count
        
        report["final_stats"] = {
            "total_cycles_completed": cycle_idx,
            "total_duration_seconds": total_elapsed,
            "avg_cycle_time_ms": (total_elapsed / cycle_idx * 1000) if cycle_idx > 0 else 0,
            "proposals_generated_total": final_proposal_count,
            "proposals_generated_in_run": total_new_proposals,
            "proposal_generation_rate": total_new_proposals / cycle_idx if cycle_idx > 0 else 0,
            "timestamp": datetime.now().isoformat(),
        }
        
        print("\n" + "="*100)
        print("EXTENDED 1000-CYCLE EVOLUTION COMPLETE")
        print("="*100)
        print(f"\nTotal Duration: {total_elapsed:.1f}s ({total_elapsed/60:.1f}min)")
        print(f"Average per cycle: {report['final_stats']['avg_cycle_time_ms']:.1f}ms")
        print(f"\nCode Proposals Generated in This Run: {total_new_proposals}")
        print(f"Total in Vault: {final_proposal_count}")
        print(f"Generation Rate: {report['final_stats']['proposal_generation_rate']:.3f} proposals/cycle")
        print(f"\nTarget Achievement:")
        if total_new_proposals >= 100:
            print(f"  ✓ MILESTONE ACHIEVED: 100+ proposals (got {total_new_proposals})")
        else:
            print(f"  ⚠ Target 100 proposals: {total_new_proposals}/100")
        
        print("\n" + "="*100 + "\n")
        
    finally:
        try:
            engine.kernel.shutdown()
        except:
            pass
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Extended 1000-Cycle Intelligence Evolution")
    parser.add_argument("--cycles", type=int, default=1000, help="Number of cycles (default: 1000)")
    parser.add_argument("--no-autonomy", action="store_true", help="Disable autonomy cycles")
    parser.add_argument("--no-paramatman", action="store_true", help="Disable paramatman")
    parser.add_argument("--output", type=Path, 
                       default=REPO_ROOT / "benchmarks" / "artifacts" / "extended_1000_final_report.json",
                       help="Output report file")
    args = parser.parse_args()
    
    report = run_extended_1000_cycles(
        num_cycles=args.cycles,
        enable_autonomy=not args.no_autonomy,
        enable_paramatman=not args.no_paramatman,
    )
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
