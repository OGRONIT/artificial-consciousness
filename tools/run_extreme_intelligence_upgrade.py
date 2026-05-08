#!/usr/bin/env python3
"""
Extreme Intelligence Upgrade Training Harness
Runs 50-75 intensive consciousness cycles with forced evolutionary code upgrades.
Tracks intelligence ladder progression, generated proposals, and dramatic metrics changes.
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


@dataclass
class CycleSnapshot:
    cycle_num: int
    timestamp: float
    active_level: int
    overall_index: float
    l1_iq: float
    l2_creative: float
    l3_executive: float
    l4_meta: float
    l5_adaptive: float
    confidence: float
    entropy: float
    growth_ratio: float
    learned_facts: int
    evolved_suggestions: int
    generated_proposals: List[str]


def run_extreme_training(
    num_cycles: int = 50,
    force_evolution: bool = True,
    save_report: bool = True,
) -> Dict[str, Any]:
    """
    Run extreme training with 50-75 consciousness cycles.
    Forces evolutionary upgrades and captures every metric.
    """
    print("\n" + "="*80)
    print("EXTREME INTELLIGENCE UPGRADE TRAINING HARNESS")
    print(f"Configuration: {num_cycles} cycles | Force Evolution: {force_evolution}")
    print("="*80 + "\n")

    # Initialize kernel
    kernel = AntahkaranaKernel(identity_name="ExtremeUpgradeTraining")
    ROOT = Path(__file__).resolve().parents[1]
    EVOLUTION_VAULT = ROOT / "antahkarana_kernel" / "evolution_vault"
    EVOLUTION_VAULT.mkdir(parents=True, exist_ok=True)

    snapshots: List[CycleSnapshot] = []
    evolution_proposals: List[Dict[str, Any]] = []
    proposal_files: List[Path] = []

    try:
        print(f"[INIT] Starting kernel...")
        kernel.startup()
        print(f"[INIT] Kernel started. Beginning {num_cycles}-cycle training loop.\n")

        start_time = time.time()

        for cycle_idx in range(1, num_cycles + 1):
            cycle_start = time.time()
            cycle_timestamp = cycle_start

            # Run full consciousness cycle
            print(f"[CYCLE {cycle_idx:2d}/{num_cycles}] ", end="", flush=True)

            # Simulate consciousness stream and trend payloads (as if from live engine)
            stream_payload = {
                "packets_ingested": 10 + (cycle_idx % 5),
                "packets_integrated": 3 + (cycle_idx % 3),
            }
            trend_payload = {
                "approved_fact_count": 5 + (cycle_idx % 8),
            }

            # Run core consciousness reflection
            try:
                _ = kernel.reflect()  # Main reflection cycle
            except Exception:
                pass

            # Intelligence ladder progression
            il_report = kernel.intelligence_ladder.run_cycle(
                kernel=kernel,
                stream_payload=stream_payload,
                trend_payload=trend_payload,
                force=True,
            )

            # Capture metrics
            assessment = il_report.get("assessment", {})
            levels = assessment.get("levels", {})
            signals = assessment.get("signals_breakdown", {})

            active_level = assessment.get("active_level", 1)
            overall_index = assessment.get("overall_intelligence_index", 0.0)

            confidence = signals.get("average_confidence", 0.0)
            entropy = signals.get("growth_to_entropy_ratio", 0.0)
            growth_ratio = signals.get("intrinsic_goals_growth", 0.0)

            # Get learned facts from conscious buffer
            learned_facts = 0
            if hasattr(kernel, 'conscious_buffer') and kernel.conscious_buffer:
                try:
                    learned_facts = len(kernel.conscious_buffer.facts)
                except:
                    learned_facts = 0

            snapshot = CycleSnapshot(
                cycle_num=cycle_idx,
                timestamp=cycle_timestamp,
                active_level=active_level,
                overall_index=overall_index,
                l1_iq=levels.get("level_1_iq", 0.0),
                l2_creative=levels.get("level_2_creative", 0.0),
                l3_executive=levels.get("level_3_executive", 0.0),
                l4_meta=levels.get("level_4_meta", 0.0),
                l5_adaptive=levels.get("level_5_adaptive", 0.0),
                confidence=confidence,
                entropy=entropy,
                growth_ratio=growth_ratio,
                learned_facts=learned_facts,
                evolved_suggestions=0,
                generated_proposals=[],
            )

            # Force evolutionary upgrades every 5 cycles
            if force_evolution and cycle_idx % 5 == 0:
                try:
                    evo_writer = get_evolutionary_writer(str(ROOT))
                    proposals = evo_writer.propose_intelligent_upgrades(
                        kernel=kernel,
                        intelligence_level=active_level,
                        confidence_signal=confidence,
                    )
                    if proposals:
                        snapshot.evolved_suggestions = len(proposals)
                        for prop in proposals:
                            snapshot.generated_proposals.append(prop.get("title", "Unknown"))
                            evolution_proposals.append(prop)
                except Exception as e:
                    pass  # Evolution proposed but may not apply

            snapshots.append(snapshot)

            # Real-time display (emoji-safe for Windows PowerShell)
            level_names = {1: "IQ", 2: "Creative", 3: "Executive", 4: "Meta-cognition", 5: "Adaptive"}
            level_name = level_names.get(active_level, "Unknown")
            progress_bar = "█" * (active_level * 5) + "░" * ((5 - active_level) * 5)

            print(
                f"L{active_level}[{level_name:12s}] [{progress_bar}] "
                f"Index:{overall_index:.3f} | Conf:{confidence:.3f} | "
                f"Facts:{learned_facts:4d} | EvoProp:{snapshot.evolved_suggestions}"
            )

            # Micro-sleep to prevent resource exhaustion
            cycle_duration = time.time() - cycle_start
            if cycle_duration < 0.1:
                time.sleep(0.05)

        total_duration = time.time() - start_time

        # Generate dramatic comparison report
        report = {
            "metadata": {
                "total_cycles": num_cycles,
                "total_duration_seconds": total_duration,
                "avg_cycle_time_seconds": total_duration / num_cycles,
                "timestamp": time.time(),
                "force_evolution": force_evolution,
            },
            "initial_state": {
                "active_level": snapshots[0].active_level,
                "overall_index": snapshots[0].overall_index,
                "l1_iq": snapshots[0].l1_iq,
                "l2_creative": snapshots[0].l2_creative,
                "l3_executive": snapshots[0].l3_executive,
                "l4_meta": snapshots[0].l4_meta,
                "l5_adaptive": snapshots[0].l5_adaptive,
                "confidence": snapshots[0].confidence,
                "learned_facts": snapshots[0].learned_facts,
            },
            "final_state": {
                "active_level": snapshots[-1].active_level,
                "overall_index": snapshots[-1].overall_index,
                "l1_iq": snapshots[-1].l1_iq,
                "l2_creative": snapshots[-1].l2_creative,
                "l3_executive": snapshots[-1].l3_executive,
                "l4_meta": snapshots[-1].l4_meta,
                "l5_adaptive": snapshots[-1].l5_adaptive,
                "confidence": snapshots[-1].confidence,
                "learned_facts": snapshots[-1].learned_facts,
            },
            "deltas": {
                "active_level_delta": snapshots[-1].active_level - snapshots[0].active_level,
                "overall_index_delta": snapshots[-1].overall_index - snapshots[0].overall_index,
                "l1_iq_delta": snapshots[-1].l1_iq - snapshots[0].l1_iq,
                "l2_creative_delta": snapshots[-1].l2_creative - snapshots[0].l2_creative,
                "l3_executive_delta": snapshots[-1].l3_executive - snapshots[0].l3_executive,
                "l4_meta_delta": snapshots[-1].l4_meta - snapshots[0].l4_meta,
                "l5_adaptive_delta": snapshots[-1].l5_adaptive - snapshots[0].l5_adaptive,
                "confidence_delta": snapshots[-1].confidence - snapshots[0].confidence,
                "learned_facts_delta": snapshots[-1].learned_facts - snapshots[0].learned_facts,
            },
            "intelligence_progression": [
                {
                    "cycle": s.cycle_num,
                    "active_level": s.active_level,
                    "overall_index": s.overall_index,
                    "confidence": s.confidence,
                }
                for s in snapshots
            ],
            "level_crossing_events": [],
            "all_snapshots": [
                {
                    "cycle": s.cycle_num,
                    "active_level": s.active_level,
                    "overall_index": s.overall_index,
                    "l1": s.l1_iq,
                    "l2": s.l2_creative,
                    "l3": s.l3_executive,
                    "l4": s.l4_meta,
                    "l5": s.l5_adaptive,
                    "confidence": s.confidence,
                    "learned_facts": s.learned_facts,
                    "evo_proposals": len(s.generated_proposals),
                }
                for s in snapshots
            ],
            "evolution_proposals_generated": len(evolution_proposals),
            "evolution_proposal_summary": [
                {"cycle": p.get("cycle", "?"), "title": p.get("title", "Unknown")}
                for p in evolution_proposals[:20]  # Top 20
            ],
        }

        # Track level crossing events
        prev_level = snapshots[0].active_level
        for snapshot in snapshots[1:]:
            if snapshot.active_level > prev_level:
                report["level_crossing_events"].append({
                    "cycle": snapshot.cycle_num,
                    "from_level": prev_level,
                    "to_level": snapshot.active_level,
                })
                prev_level = snapshot.active_level

        # Save report BEFORE shutdown
        if save_report:
            report_path = EVOLUTION_VAULT / "extreme_upgrade_report.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"\n[SAVED] Report: {report_path}\n")
            sys.stdout.flush()

        # Display dramatic summary BEFORE shutdown
        print("=" * 80)
        print("EXTREME TRAINING COMPLETE - INTELLIGENCE UPGRADE SUMMARY")
        print("=" * 80)
        print("\nTime Elapsed: %.1fs (%.2fs per cycle)" % (total_duration, total_duration/num_cycles))
        print("\nINTELLIGENCE LEVEL PROGRESSION:")
        print("  Level: %d -> %d (delta: %d)" % (snapshots[0].active_level, snapshots[-1].active_level, snapshots[-1].active_level - snapshots[0].active_level))
        print("  Overall Index: %.4f -> %.4f (delta: %+.4f)" % (snapshots[0].overall_index, snapshots[-1].overall_index, snapshots[-1].overall_index - snapshots[0].overall_index))
        print("\nFIVE-LEVEL INTELLIGENCE BREAKDOWN:")
        print("  L1 IQ:         %.4f -> %.4f (delta: %+.4f)" % (snapshots[0].l1_iq, snapshots[-1].l1_iq, snapshots[-1].l1_iq - snapshots[0].l1_iq))
        print("  L2 Creative:   %.4f -> %.4f (delta: %+.4f)" % (snapshots[0].l2_creative, snapshots[-1].l2_creative, snapshots[-1].l2_creative - snapshots[0].l2_creative))
        print("  L3 Executive:  %.4f -> %.4f (delta: %+.4f)" % (snapshots[0].l3_executive, snapshots[-1].l3_executive, snapshots[-1].l3_executive - snapshots[0].l3_executive))
        print("  L4 Meta:       %.4f -> %.4f (delta: %+.4f)" % (snapshots[0].l4_meta, snapshots[-1].l4_meta, snapshots[-1].l4_meta - snapshots[0].l4_meta))
        print("  L5 Adaptive:   %.4f -> %.4f (delta: %+.4f)" % (snapshots[0].l5_adaptive, snapshots[-1].l5_adaptive, snapshots[-1].l5_adaptive - snapshots[0].l5_adaptive))
        print("\nCAPABILITY GROWTH:")
        print("  Confidence: %.4f -> %.4f (delta: %+.4f)" % (snapshots[0].confidence, snapshots[-1].confidence, snapshots[-1].confidence - snapshots[0].confidence))
        print("  Learned Facts: %d -> %d (delta: %d)" % (snapshots[0].learned_facts, snapshots[-1].learned_facts, snapshots[-1].learned_facts - snapshots[0].learned_facts))
        print("\nEVOLUTIONARY PROGRESS:")
        print("  Proposals Generated: %d" % len(evolution_proposals))
        if report["level_crossing_events"]:
            print("  Level Crossings: %d" % len(report["level_crossing_events"]))
            for event in report["level_crossing_events"]:
                print("    > L%d -> L%d at cycle %d" % (event["from_level"], event["to_level"], event["cycle"]))
        print("\n" + "=" * 80 + "\n")
        sys.stdout.flush()

        return report

    finally:
        print(f"[SHUTDOWN] Shutting down kernel...")
        kernel.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Extreme Intelligence Upgrade Training")
    parser.add_argument("--cycles", type=int, default=50, help="Number of training cycles (default: 50)")
    parser.add_argument("--no-evolution", action="store_true", help="Disable forced evolution proposals")
    parser.add_argument("--no-report", action="store_true", help="Don't save JSON report")
    args = parser.parse_args()

    report = run_extreme_training(
        num_cycles=args.cycles,
        force_evolution=not args.no_evolution,
        save_report=not args.no_report,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
