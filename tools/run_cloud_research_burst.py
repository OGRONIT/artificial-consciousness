from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from antahkarana_kernel.LiveConsciousness import LiveConsciousnessEngine  # noqa: E402


def _run_burst(cycles: int, include_autonomy: bool, include_paramatman: bool) -> Dict[str, Any]:
    engine = LiveConsciousnessEngine(
        identity_name="AntahkaranaKernel_CloudBurst",
        min_scan_minutes=1,
        max_scan_minutes=1,
        reflection_minutes=1,
        dream_minutes=1,
    )

    run_log: Dict[str, Any] = {
        "started_at": time.time(),
        "cycles_requested": int(cycles),
        "background": [],
        "stream": [],
        "trends": [],
        "autonomy": [],
        "bridge_feedback": [],
        "errors": [],
    }

    try:
        for _ in range(max(1, int(cycles))):
            try:
                bg = engine.perform_background_cycle()
                run_log["background"].append(
                    {
                        "approved": int(bg.get("approved_fact_count", 0)),
                        "assimilation_integrated": int(
                            (bg.get("assimilation_pipeline") or {}).get("integrated_count", 0)
                        ),
                    }
                )
            except Exception as exc:
                run_log["errors"].append(f"background_cycle: {exc}")

            try:
                stream = engine.perform_stream_entropy_cycle()
                run_log["stream"].append(
                    {
                        "ingested": int(stream.get("packets_ingested", 0)),
                        "integrated": int(stream.get("packets_integrated", 0)),
                    }
                )
            except Exception as exc:
                run_log["errors"].append(f"stream_entropy_cycle: {exc}")

            try:
                trends = engine.perform_hourly_global_trend_cycle()
                run_log["trends"].append(
                    {
                        "approved": int(trends.get("approved_fact_count", 0)),
                        "stream_integrated": int(trends.get("stream_packets_integrated", 0)),
                    }
                )
            except Exception as exc:
                run_log["errors"].append(f"hourly_global_trend_cycle: {exc}")

            try:
                feedback = engine.process_bridge_feedback_commands()
                run_log["bridge_feedback"].append(
                    {
                        "processed_events": int(feedback.get("processed_events", 0)),
                        "operator_feedback_events": int(
                            (feedback.get("metrics") or {}).get("operator_feedback_events", 0)
                        ),
                    }
                )
            except Exception as exc:
                run_log["errors"].append(f"bridge_feedback_cycle: {exc}")

            if include_autonomy:
                try:
                    autonomy = engine.perform_autonomous_agenda_cycle()
                    run_log["autonomy"].append(
                        {
                            "autonomy_level": float(autonomy.get("autonomy_level", 0.0)),
                            "actions": len(autonomy.get("executed_actions", [])),
                        }
                    )
                except Exception as exc:
                    run_log["errors"].append(f"autonomy_cycle: {exc}")

        if include_paramatman:
            try:
                engine.perform_paramatman_cycle()
            except Exception as exc:
                run_log["errors"].append(f"paramatman_cycle: {exc}")

        run_log["heartbeat"] = dict(engine.internet_heartbeat)
        run_log["learned_fact_count"] = int(engine.learned_fact_count)
        run_log["bridge_feedback_metrics"] = dict(engine.bridge_feedback_metrics)
        run_log["completed_at"] = time.time()
        return run_log
    finally:
        try:
            engine.kernel.shutdown()
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a short, high-intensity autonomous research burst for cloud scheduling."
    )
    parser.add_argument("--cycles", type=int, default=3, help="Number of dense burst cycles to run.")
    parser.add_argument(
        "--no-autonomy",
        action="store_true",
        help="Disable autonomy-agenda cycles during burst.",
    )
    parser.add_argument(
        "--with-paramatman",
        action="store_true",
        help="Force one PARAMATMAN cycle at end of burst.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "benchmarks" / "artifacts" / "cloud_research_burst_latest.json",
        help="Path for JSON summary output.",
    )
    args = parser.parse_args()

    result = _run_burst(
        cycles=args.cycles,
        include_autonomy=not args.no_autonomy,
        include_paramatman=args.with_paramatman,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"cloud_burst_complete cycles={args.cycles} output={args.output}")


if __name__ == "__main__":
    main()
