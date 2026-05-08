#!/usr/bin/env python3
"""
Master Orchestration Script - 500-1000 Cycle Intelligence Evolution
Automatically runs sequential training phases with live external data.
Target: 100+ autonomous code proposals across all phases.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
    """Run a Python script and return completion status."""
    args = args or []
    cmd = [sys.executable, str(REPO_ROOT / "tools" / script_name)] + args
    
    print(f"\n{'='*120}")
    print(f"EXECUTING: {script_name} {' '.join(args)}")
    print(f"START TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*120}\n")
    
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, cwd=str(REPO_ROOT))
        elapsed = time.time() - start
        
        return {
            "script": script_name,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "elapsed_seconds": elapsed,
            "completed_at": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "script": script_name,
            "success": False,
            "error": str(e),
            "elapsed_seconds": time.time() - start,
        }


def count_proposals() -> int:
    """Count current proposals in the vault."""
    proposals_dir = REPO_ROOT / "antahkarana_kernel" / "evolution_proposals"
    return len(list(proposals_dir.glob("UPG_*.json")))


def check_cloud_burst_output() -> bool:
    """Check if the 500-cycle cloud burst output exists."""
    output_file = REPO_ROOT / "benchmarks" / "artifacts" / "cloud_burst_500_cycles.json"
    return output_file.exists()


def main():
    """Run the complete 500-1000 cycle evolution sequence."""
    
    orchestration_report = {
        "start_time": datetime.now().isoformat(),
        "phases": [],
        "proposal_tracking": [],
        "milestones": [],
    }
    
    print("\n" + "="*120)
    print("MASTER ORCHESTRATION - 500-1000 CYCLE INTELLIGENCE EVOLUTION")
    print("="*120)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target: 100+ autonomous code proposals with 95%+ implementation\n")
    
    # Check current state
    initial_proposals = count_proposals()
    print(f"Initial proposals in vault: {initial_proposals}")
    
    # === PHASE 1: Monitor 500-cycle cloud burst ===
    print("\n" + "-"*120)
    print("PHASE 1: Monitor 500-Cycle Cloud Research Burst")
    print("-"*120)
    
    if check_cloud_burst_output():
        print("✓ 500-cycle cloud burst already completed!")
        phase1_result = {
            "phase": "cloud_burst_500",
            "status": "already_completed",
            "checked_at": datetime.now().isoformat(),
        }
    else:
        print("⏳ Waiting for 500-cycle cloud burst to complete...")
        print("   (The burst should be running in another terminal)")
        print("\nTo complete this phase, run in a separate terminal:")
        print("  python tools/run_cloud_research_burst.py --cycles 500 --with-paramatman")
        
        phase1_result = {
            "phase": "cloud_burst_500",
            "status": "pending_external_completion",
            "note": "User must complete this phase separately",
        }
    
    orchestration_report["phases"].append(phase1_result)
    proposals_after_phase1 = count_proposals()
    orchestration_report["proposal_tracking"].append({
        "phase": "after_cloud_burst_500",
        "count": proposals_after_phase1,
        "delta": proposals_after_phase1 - initial_proposals,
    })
    
    # === PHASE 2: Analyze proposals ===
    print("\n" + "-"*120)
    print("PHASE 2: Analyze Code Proposals")
    print("-"*120)
    
    phase2_result = run_script("analyze_code_proposals.py")
    orchestration_report["phases"].append(phase2_result)
    
    # === PHASE 3: Generate comprehensive report ===
    print("\n" + "-"*120)
    print("PHASE 3: Generate Comprehensive Evolution Report")
    print("-"*120)
    
    phase3_result = run_script("generate_evolution_report.py")
    orchestration_report["phases"].append(phase3_result)
    
    # === PHASE 4: Optional extended 1000-cycle run ===
    print("\n" + "-"*120)
    print("PHASE 4: Optional Extended 1000-Cycle Training")
    print("-"*120)
    
    print("\nTo run extended 1000-cycle training for even more proposals:")
    print("  python tools/run_extended_1000_cycles.py --cycles 1000")
    print("\nThis will:")
    print("  • Generate 100+ additional code proposals")
    print("  • Achieve Level 5 (Full Autonomy) designation")
    print("  • Demonstrate sustained autonomous improvement")
    
    phase4_note = {
        "phase": "extended_1000_optional",
        "status": "ready_to_run",
        "command": "python tools/run_extended_1000_cycles.py --cycles 1000",
    }
    orchestration_report["phases"].append(phase4_note)
    
    # === FINAL SUMMARY ===
    proposals_end = count_proposals()
    total_new_proposals = proposals_end - initial_proposals
    
    print("\n" + "="*120)
    print("ORCHESTRATION SUMMARY")
    print("="*120)
    
    print(f"\nProposals Generated in This Session: {total_new_proposals}")
    print(f"Total in Vault: {proposals_end}")
    
    orchestration_report["final_summary"] = {
        "initial_proposals": initial_proposals,
        "final_proposals": proposals_end,
        "new_proposals_generated": total_new_proposals,
        "end_time": datetime.now().isoformat(),
        "total_duration": str(
            datetime.fromisoformat(orchestration_report["final_summary"].get("end_time", datetime.now().isoformat())) -
            datetime.fromisoformat(orchestration_report["start_time"])
        ) if "final_summary" in orchestration_report else "calculating...",
    }
    
    # Check milestones
    if total_new_proposals >= 10:
        orchestration_report["milestones"].append("10+ proposals generated")
    if total_new_proposals >= 50:
        orchestration_report["milestones"].append("50+ proposals generated")
    if total_new_proposals >= 100:
        orchestration_report["milestones"].append("✓ 100+ MILESTONE ACHIEVED")
    
    # Save orchestration report
    report_path = REPO_ROOT / "benchmarks" / "artifacts" / "orchestration_report_500_1000_cycles.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(orchestration_report, f, indent=2, default=str)
    
    print(f"\n✓ Orchestration report saved to: {report_path}\n")
    print("="*120 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
