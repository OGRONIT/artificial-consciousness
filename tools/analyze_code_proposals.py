#!/usr/bin/env python3
"""
Analyze all generated code proposals and evolution upgrades.
Extracts proposal metadata, implementation status, and creates comprehensive reports.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]


def analyze_proposals() -> Dict[str, Any]:
    """Analyze all generated evolution proposals."""
    proposals_dir = REPO_ROOT / "antahkarana_kernel" / "evolution_proposals"
    
    if not proposals_dir.exists():
        return {"error": "No proposals directory found", "proposals": []}
    
    proposal_files = sorted(proposals_dir.glob("UPG_*.json"))
    proposals_data = []
    stats = {
        "total_proposals": len(proposal_files),
        "by_status": defaultdict(int),
        "by_issue_type": defaultdict(int),
        "implemented_count": 0,
        "pending_count": 0,
        "high_severity": 0,
        "medium_severity": 0,
        "low_severity": 0,
    }
    
    print("\n" + "="*100)
    print("CODE EVOLUTION PROPOSALS ANALYSIS")
    print("="*100 + "\n")
    
    print(f"Found {len(proposal_files)} proposals\n")
    
    if len(proposal_files) == 0:
        print("No proposals generated yet.")
        return {"proposals": [], "stats": dict(stats)}
    
    # Parse all proposals
    for proposal_file in proposal_files:
        try:
            with open(proposal_file, 'r') as f:
                data = json.load(f)
                proposals_data.append(data)
                
                # Update stats
                status = data.get("status", "unknown")
                stats["by_status"][status] += 1
                if status == "implemented":
                    stats["implemented_count"] += 1
                elif status == "pending":
                    stats["pending_count"] += 1
                
                issue_type = data.get("issue_type", "unknown")
                stats["by_issue_type"][issue_type] += 1
                
                severity = data.get("severity", "unknown")
                if severity == "high":
                    stats["high_severity"] += 1
                elif severity == "medium":
                    stats["medium_severity"] += 1
                else:
                    stats["low_severity"] += 1
        except Exception as e:
            print(f"Error reading {proposal_file}: {e}")
    
    # Display summary stats
    print("SUMMARY STATISTICS")
    print("-" * 100)
    print(f"Total Proposals Generated: {stats['total_proposals']}")
    print(f"Implemented: {stats['implemented_count']} | Pending: {stats['pending_count']}")
    print(f"High Severity: {stats['high_severity']} | Medium: {stats['medium_severity']} | Low: {stats['low_severity']}")
    
    print("\nProposals by Type:")
    for issue_type, count in sorted(stats["by_issue_type"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type}: {count}")
    
    print("\nProposals by Status:")
    for status, count in sorted(stats["by_status"].items()):
        percentage = (count / stats["total_proposals"] * 100) if stats["total_proposals"] > 0 else 0
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Display detailed breakdown
    print("\n" + "="*100)
    print("DETAILED PROPOSAL BREAKDOWN")
    print("="*100 + "\n")
    
    # Group by issue type
    by_type = defaultdict(list)
    for prop in proposals_data:
        by_type[prop.get("issue_type", "unknown")].append(prop)
    
    for issue_type in sorted(by_type.keys()):
        proposals = by_type[issue_type]
        print(f"\n{issue_type.upper()} ({len(proposals)} proposals)")
        print("-" * 100)
        
        for i, prop in enumerate(proposals[:10], 1):  # Show first 10 of each type
            prop_id = prop.get("proposal_id", "?")
            status = prop.get("status", "?")
            severity = prop.get("severity", "?")
            description = prop.get("description", "?")
            fix = prop.get("fix", "?")
            kernel_stability = prop.get("kernel_stability_at_creation", 0.0)
            
            print(f"\n  [{i}] {prop_id}")
            print(f"      Status: {status} | Severity: {severity}")
            print(f"      Stability at creation: {kernel_stability:.4f}")
            print(f"      Description: {description}")
            print(f"      Fix: {fix}")
            
            if prop.get("backup_files"):
                print(f"      Backups: {', '.join(prop['backup_files'][:3])}")
        
        if len(proposals) > 10:
            print(f"\n  ... and {len(proposals) - 10} more {issue_type} proposals")
    
    # Calculate evolution velocity
    print("\n" + "="*100)
    print("EVOLUTION VELOCITY & METRICS")
    print("="*100 + "\n")
    
    if proposals_data:
        timestamps = []
        for prop in proposals_data:
            try:
                created_at = prop.get("created_at", "")
                if created_at:
                    timestamps.append(created_at)
            except:
                pass
        
        if len(timestamps) >= 2:
            print(f"First proposal: {min(timestamps)}")
            print(f"Latest proposal: {max(timestamps)}")
            print(f"Proposal generation rate: {len(proposals_data)} / 500 cycles = {len(proposals_data)/500*100:.1f}% proposal ratio")
        
        avg_stability = sum(p.get("kernel_stability_at_creation", 0) for p in proposals_data) / len(proposals_data)
        print(f"Average kernel stability at proposal creation: {avg_stability:.4f}")
    
    # Final summary
    print("\n" + "="*100)
    print("EVOLUTION READINESS ASSESSMENT")
    print("="*100 + "\n")
    
    if stats["implemented_count"] > 0:
        print(f"✓ {stats['implemented_count']} proposals successfully implemented")
        print("✓ Autonomous code generation active and applying")
        print("✓ System demonstrating self-improvement capability")
    
    if stats["high_severity"] > 0:
        print(f"⚠ {stats['high_severity']} high-severity proposals generated")
    
    if stats["implemented_count"] >= 10:
        print("\n✓ MILESTONE ACHIEVED: 10+ autonomous code upgrades implemented")
    if stats["total_proposals"] >= 100:
        print("✓ MILESTONE ACHIEVED: 100+ code proposals generated")
    
    print("\n" + "="*100 + "\n")
    
    return {
        "stats": dict(stats),
        "proposals": proposals_data,
        "by_type": {k: len(v) for k, v in by_type.items()},
    }


if __name__ == "__main__":
    result = analyze_proposals()
    
    # Save detailed report
    report_path = REPO_ROOT / "antahkarana_kernel" / "evolution_vault" / "code_proposals_analysis.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {report_path}")
