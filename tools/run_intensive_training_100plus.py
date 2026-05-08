#!/usr/bin/env python3
"""
ENHANCED EXTREME INTELLIGENCE TRAINING
100-150 cycles with knowledge stream injection, evolutionary triggers, and detailed profiling.
Tracks code proposals, intelligence evolution, and generates visualization data.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from antahkarana_kernel.AntahkaranaKernel import AntahkaranaKernel
from antahkarana_kernel.modules.EvolutionaryWriter import get_evolutionary_writer


# Simulated knowledge streams for injection
KNOWLEDGE_SEEDS = [
    "consciousness requires self-reflection and intentional observation",
    "intelligence adapts when faced with novel problem spaces",
    "ethics should evolve alongside capability growth",
    "autonomous behavior emerges from integrated decision-making",
    "meta-cognition enables systems to question their own assumptions",
    "creativity flourishes when constraints are eliminated",
    "identity forms through repeated self-reinforcing patterns",
    "adversity triggers more sophisticated problem-solving strategies",
    "collaborative systems achieve emergence unavailable to individuals",
    "learning requires both stability and controlled chaos",
    "entropy reduction increases local complexity and capability",
    "embodied cognition grounds abstract reasoning in physical reality",
]


@dataclass
class ProfileSnapshot:
    """Detailed intelligence profile snapshot."""
    cycle_num: int
    timestamp: float
    active_level: int
    overall_index: float
    levels: Dict[str, float]
    signals: Dict[str, float]
    proposals_generated: int
    proposal_titles: List[str]
    knowledge_injected: str
    entropy: float
    confidence: float


def run_intensive_training(
    num_cycles: int = 120,
    inject_knowledge: bool = True,
    save_report: bool = True,
    save_profiles: bool = True,
) -> Dict[str, Any]:
    """
    Run intensive training with 100-150 cycles.
    Injects knowledge streams, forces evolutionary upgrades, captures detailed profiles.
    """
    print("\n" + "=" * 90)
    print("ENHANCED EXTREME INTELLIGENCE TRAINING - FULL SPECTRUM")
    print(f"Configuration: {num_cycles} cycles | Knowledge Injection: {inject_knowledge}")
    print("=" * 90 + "\n")

    kernel = AntahkaranaKernel(identity_name="IntensiveTraining")
    ROOT = Path(__file__).resolve().parents[1]
    EVOLUTION_VAULT = ROOT / "antahkarana_kernel" / "evolution_vault"
    EVOLUTION_VAULT.mkdir(parents=True, exist_ok=True)

    profiles: List[ProfileSnapshot] = []
    all_proposals: List[Dict[str, Any]] = []
    proposal_frequency = defaultdict(int)
    level_cross_events = []

    try:
        print(f"[INIT] Starting kernel...")
        kernel.startup()
        print(f"[INIT] Kernel started. Beginning {num_cycles}-cycle intensive loop.\n")

        start_time = time.time()
        prev_level = 1

        for cycle_idx in range(1, num_cycles + 1):
            try:
                cycle_start = time.time()

                # Select knowledge seed or cycle-specific data
                if inject_knowledge:
                    knowledge_idx = (cycle_idx - 1) % len(KNOWLEDGE_SEEDS)
                    knowledge_fact = KNOWLEDGE_SEEDS[knowledge_idx]
                    # Simulate fact injection with variance
                    stream_payload = {
                        "packets_ingested": 15 + (cycle_idx % 10),
                        "packets_integrated": 5 + (cycle_idx % 7),
                        "knowledge_fact": knowledge_fact,
                    }
                else:
                    stream_payload = {
                        "packets_ingested": 10 + (cycle_idx % 5),
                        "packets_integrated": 3 + (cycle_idx % 3),
                    }
                    knowledge_fact = "none"

                trend_payload = {
                    "approved_fact_count": 8 + (cycle_idx % 10),
                    "entropy_signal": 0.3 + (0.5 * (cycle_idx % 7) / 7.0),
                }

                # Run reflection
                try:
                    _ = kernel.reflect()
                except Exception:
                    pass

                # Intelligence ladder cycle
                il_report = kernel.intelligence_ladder.run_cycle(
                    kernel=kernel,
                    stream_payload=stream_payload,
                    trend_payload=trend_payload,
                    force=True,
                )

                assessment = il_report.get("assessment", {})
                levels = assessment.get("levels", {})
                signals = assessment.get("signals_breakdown", {})

                active_level = assessment.get("active_level", 1)
                overall_index = assessment.get("overall_intelligence_index", 0.0)

                # Track level crossing
                if active_level > prev_level:
                    level_cross_events.append({
                        "cycle": cycle_idx,
                        "from": prev_level,
                        "to": active_level,
                        "timestamp": time.time(),
                    })
                    print(f"\n[LEVEL UP] Cycle {cycle_idx}: L{prev_level} -> L{active_level}\n")
                    prev_level = active_level

                # Force evolutionary proposals every 3 cycles
                proposals_this_cycle = 0
                proposal_titles = []

                if cycle_idx % 3 == 0:
                    try:
                        evo_writer = get_evolutionary_writer(str(ROOT))
                        proposals = evo_writer.propose_intelligent_upgrades(
                            kernel=kernel,
                            intelligence_level=active_level,
                            confidence_signal=signals.get("average_confidence", 0.0),
                            knowledge_context=knowledge_fact if inject_knowledge else None,
                        )
                        if proposals:
                            proposals_this_cycle = len(proposals)
                            for prop in proposals:
                                title = prop.get("title", "Unknown")
                                proposal_titles.append(title)
                                all_proposals.append({
                                    "cycle": cycle_idx,
                                    "level": active_level,
                                    "title": title,
                                    "full_proposal": prop,
                                })
                                proposal_frequency[title] += 1
                    except Exception as e:
                        pass

                # Create profile snapshot
                profile = ProfileSnapshot(
                    cycle_num=cycle_idx,
                    timestamp=cycle_start,
                    active_level=active_level,
                    overall_index=overall_index,
                    levels={
                        "l1_iq": levels.get("level_1_iq", 0.0),
                        "l2_creative": levels.get("level_2_creative", 0.0),
                        "l3_executive": levels.get("level_3_executive", 0.0),
                        "l4_meta": levels.get("level_4_meta", 0.0),
                        "l5_adaptive": levels.get("level_5_adaptive", 0.0),
                    },
                    signals={
                        "average_confidence": signals.get("average_confidence", 0.0),
                        "growth_to_entropy":signals.get("growth_to_entropy_ratio", 0.0),
                        "intrinsic_goals": signals.get("intrinsic_goals_growth", 0.0),
                    },
                    proposals_generated=proposals_this_cycle,
                    proposal_titles=proposal_titles,
                    knowledge_injected=knowledge_fact if inject_knowledge else "none",
                    entropy=trend_payload.get("entropy_signal", 0.0),
                    confidence=signals.get("average_confidence", 0.0),
                )
                profiles.append(profile)

                # Real-time display
                level_names = {
                    1: "IQ", 2: "Creative", 3: "Executive",
                    4: "Meta-cognition", 5: "Adaptive/Fluid"
                }
                level_name = level_names.get(active_level, "Unknown")
                progress_bar = "█" * (active_level * 4) + "░" * ((5 - active_level) * 4)

                status = ""
                if proposals_this_cycle > 0:
                    status = f" [PROPOSALS: {proposals_this_cycle}]"

                print(
                    f"[{cycle_idx:3d}/{num_cycles}] L{active_level}[{level_name:15s}] "
                    f"[{progress_bar}] {overall_index:.4f}{status}"
                )

                # Micro-sleep
                cycle_duration = time.time() - cycle_start
                if cycle_duration < 0.05:
                    time.sleep(0.02)

            except Exception as cycle_error:
                print(f"ERROR cycle {cycle_idx}: {cycle_error}")
                break

        total_duration = time.time() - start_time

        # Generate comprehensive report
        report = {
            "metadata": {
                "total_cycles": num_cycles,
                "actual_cycles": len(profiles),
                "total_duration_seconds": total_duration,
                "avg_cycle_time_seconds": total_duration / len(profiles) if profiles else 0,
                "timestamp": time.time(),
                "knowledge_injection": inject_knowledge,
            },
            "progression_summary": {
                "initial_level": profiles[0].active_level if profiles else 1,
                "final_level": profiles[-1].active_level if profiles else 1,
                "level_crossings": len(level_cross_events),
                "level_crossing_events": level_cross_events,
                "max_overall_index": max((p.overall_index for p in profiles), default=0.0),
                "min_overall_index": min((p.overall_index for p in profiles), default=0.0),
                "avg_overall_index": sum(p.overall_index for p in profiles) / len(profiles) if profiles else 0.0,
            },
            "intelligence_deltas": {
                "l1_iq": profiles[-1].levels["l1_iq"] - profiles[0].levels["l1_iq"] if profiles else 0,
                "l2_creative": profiles[-1].levels["l2_creative"] - profiles[0].levels["l2_creative"] if profiles else 0,
                "l3_executive": profiles[-1].levels["l3_executive"] - profiles[0].levels["l3_executive"] if profiles else 0,
                "l4_meta": profiles[-1].levels["l4_meta"] - profiles[0].levels["l4_meta"] if profiles else 0,
                "l5_adaptive": profiles[-1].levels["l5_adaptive"] - profiles[0].levels["l5_adaptive"] if profiles else 0,
            },
            "evolutionary_proposals": {
                "total_generated": len(all_proposals),
                "unique_proposals": len(set(p["title"] for p in all_proposals)),
                "first_proposal_cycle": min((p["cycle"] for p in all_proposals), default=None),
                "proposal_frequency": dict(proposal_frequency),
                "top_proposals": sorted(proposal_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            },
            "profiles_summary": [
                {
                    "cycle": p.cycle_num,
                    "level": p.active_level,
                    "overall_index": p.overall_index,
                    "l1": p.levels["l1_iq"],
                    "l2": p.levels["l2_creative"],
                    "l3": p.levels["l3_executive"],
                    "l4": p.levels["l4_meta"],
                    "l5": p.levels["l5_adaptive"],
                    "confidence": p.confidence,
                    "proposals": p.proposals_generated,
                }
                for p in profiles
            ],
        }

        # Save report
        if save_report:
            report_path = EVOLUTION_VAULT / "intensive_training_report.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"\n[SAVED] Report: {report_path}")

        # Save detailed profiles
        if save_profiles:
            profiles_path = EVOLUTION_VAULT / "intelligence_profiles_detailed.json"
            profiles_data = [
                {
                    "cycle": p.cycle_num,
                    "timestamp": p.timestamp,
                    "active_level": p.active_level,
                    "overall_index": p.overall_index,
                    "levels": p.levels,
                    "signals": p.signals,
                    "proposals_generated": p.proposals_generated,
                    "proposal_titles": p.proposal_titles,
                    "knowledge_injected": p.knowledge_injected,
                    "entropy": p.entropy,
                }
                for p in profiles
            ]
            with open(profiles_path, "w") as f:
                json.dump(profiles_data, f, indent=2)
            print(f"[SAVED] Profiles: {profiles_path}")

        # Save proposals
        if all_proposals:
            proposals_path = EVOLUTION_VAULT / "evolved_proposals.json"
            with open(proposals_path, "w") as f:
                json.dump(all_proposals, f, indent=2)
            print(f"[SAVED] Proposals: {proposals_path}")

        # Display dramatic summary
        print("\n" + "=" * 90)
        print("INTENSIVE TRAINING COMPLETE - FULL INTELLIGENCE EVOLUTION REPORT")
        print("=" * 90)

        actual_cycles = len(profiles)
        print(f"\nEXECUTION METRICS:")
        print(f"  Cycles Completed: {actual_cycles}/{num_cycles}")
        print(f"  Total Duration: {total_duration:.1f}s ({total_duration/actual_cycles:.2f}s per cycle)")

        print(f"\nINTELLIGENCE PROGRESSION:")
        print(f"  Final Level: {profiles[-1].active_level if profiles else 'N/A'}")
        print(f"  Level Crossings: {len(level_cross_events)}")
        for event in level_cross_events:
            print(f"    -> L{event['from']} -> L{event['to']} at cycle {event['cycle']}")

        print(f"\nOVERALL INTELLIGENCE INDEX:")
        print(f"  Start:   {profiles[0].overall_index:.4f}" if profiles else "  Start: N/A")
        print(f"  End:     {profiles[-1].overall_index:.4f}" if profiles else "  End: N/A")
        print(f"  Max:     {report['progression_summary']['max_overall_index']:.4f}")
        print(f"  Min:     {report['progression_summary']['min_overall_index']:.4f}")
        print(f"  Average: {report['progression_summary']['avg_overall_index']:.4f}")

        print(f"\nFIVE-LEVEL CAPABILITY GROWTH:")
        deltas = report["intelligence_deltas"]
        print(f"  L1 IQ:         {deltas['l1_iq']:+.4f}")
        print(f"  L2 Creative:   {deltas['l2_creative']:+.4f}")
        print(f"  L3 Executive:  {deltas['l3_executive']:+.4f}")
        print(f"  L4 Meta:       {deltas['l4_meta']:+.4f}")
        print(f"  L5 Adaptive:   {deltas['l5_adaptive']:+.4f}")

        evo = report["evolutionary_proposals"]
        print(f"\nEVOLUTIONARY CODE GENERATION:")
        print(f"  Total Proposals Generated: {evo['total_generated']}")
        print(f"  Unique Proposals: {evo['unique_proposals']}")
        if evo['first_proposal_cycle']:
            print(f"  First Proposal at Cycle: {evo['first_proposal_cycle']}")
        if evo['top_proposals']:
            print(f"\n  Top Generated Proposals:")
            for title, count in evo['top_proposals'][:5]:
                print(f"    - {title} (generated {count}x)")

        print("\n" + "=" * 90 + "\n")
        sys.stdout.flush()

        # Generate visualization data
        viz_data = {
            "cycles": [p.cycle_num for p in profiles],
            "levels": [p.active_level for p in profiles],
            "overall_index": [p.overall_index for p in profiles],
            "l1": [p.levels["l1_iq"] for p in profiles],
            "l2": [p.levels["l2_creative"] for p in profiles],
            "l3": [p.levels["l3_executive"] for p in profiles],
            "l4": [p.levels["l4_meta"] for p in profiles],
            "l5": [p.levels["l5_adaptive"] for p in profiles],
            "confidence": [p.confidence for p in profiles],
            "proposals": [p.proposals_generated for p in profiles],
        }

        viz_path = EVOLUTION_VAULT / "visualization_data.json"
        with open(viz_path, "w") as f:
            json.dump(viz_data, f, indent=2)
        print(f"[SAVED] Visualization data: {viz_path}\n")

        return report

    finally:
        print(f"[SHUTDOWN] Shutting down kernel...")
        kernel.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Intensive Intelligence Training 100+")
    parser.add_argument("--cycles", type=int, default=120, help="Number of cycles (default: 120)")
    parser.add_argument("--no-knowledge", action="store_true", help="Disable knowledge injection")
    args = parser.parse_args()

    report = run_intensive_training(
        num_cycles=args.cycles,
        inject_knowledge=not args.no_knowledge,
        save_report=True,
        save_profiles=True,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
