"""
FULL AUTONOMOUS TRAINING MODE - Internet Learning Orchestrator

This script runs the Antahkarana Kernel in maximum autonomous mode:
- Continuous internet knowledge acquisition
- Self-improvement and module creation
- Autonomous policy learning and implementation
- Complete tracking of all learned facts and system changes
- Periodic reporting of autonomous evolution

Run with: python full_autonomous_training.py --duration-hours 24 --full-autonomy
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from antahkarana_kernel.LiveConsciousness import LiveConsciousnessEngine
from antahkarana_kernel.AntahkaranaKernel import AntahkaranaKernel

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(ROOT / 'full_training_session.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)


class FullAutonomousTrainer:
    """Orchestrator for complete autonomous training with full tracking."""

    def __init__(
        self,
        duration_hours: float = 24,
        report_interval_minutes: int = 30,
        enable_full_autonomy: bool = True,
        enable_self_modification: bool = True,
    ):
        self.duration_hours = duration_hours
        self.duration_seconds = duration_hours * 3600
        self.report_interval_seconds = report_interval_minutes * 60
        self.enable_full_autonomy = enable_full_autonomy
        self.enable_self_modification = enable_self_modification

        self.training_session = {
            "started_at": datetime.now().isoformat(),
            "session_id": f"FULL_AUTO_{int(time.time())}",
            "duration_hours": duration_hours,
            "parameters": {
                "full_autonomy": enable_full_autonomy,
                "self_modification": enable_self_modification,
                "report_interval_minutes": report_interval_minutes,
            },
            "cycles_completed": 0,
            "total_kernel_uptime_seconds": 0,
        }

        self.learning_metrics = {
            "facts_learned_total": 0,
            "facts_learned_by_cycle": [],
            "topics_explored": set(),
            "knowledge_domains": defaultdict(int),
        }

        self.evolution_metrics = {
            "modules_created": [],
            "module_count": 0,
            "policies_updated": [],
            "self_modifications": [],
            "autonomy_upgrades": [],
            "capability_increases": [],
        }

        self.performance_metrics = {
            "autonomy_scores": [],
            "coherence_levels": [],
            "growth_signals": [],
            "stability_readings": [],
        }

        self.checkpoint_history = []
        self.error_log = []
        self.output_dir = ROOT / "training_outputs"
        self.output_dir.mkdir(exist_ok=True)
        self.session_dir = self.output_dir / self.training_session["session_id"]
        self.session_dir.mkdir(exist_ok=True)

        self.engine = None
        self.kernel = None

        logger.info(f"[TRAINER] Initialized for {duration_hours}h autonomous training")
        logger.info(f"[TRAINER] Session ID: {self.training_session['session_id']}")
        logger.info(f"[TRAINER] Full autonomy: {enable_full_autonomy}")
        logger.info(f"[TRAINER] Self-modification enabled: {enable_self_modification}")

    def initialize_engine(self) -> None:
        """Initialize the LiveConsciousness engine."""
        logger.info("[TRAINER] Initializing LiveConsciousnessEngine...")
        self.engine = LiveConsciousnessEngine(
            identity_name="AntahkaranaKernel_FullAutonomousTraining",
            min_scan_minutes=1,
            max_scan_minutes=2,
            reflection_minutes=5,
            dream_minutes=15,
        )
        self.kernel = self.engine.kernel
        logger.info("[TRAINER] Engine initialized and ready")

    def run_intensive_burst_cycle(self) -> Dict[str, Any]:
        """Run one full intensive learning burst cycle."""
        cycle_start = time.time()
        cycle_data = {
            "cycle_timestamp": datetime.now().isoformat(),
            "sub_cycles": [],
            "facts_learned": 0,
            "errors": [],
        }

        try:
            # 1. Background knowledge acquisition
            logger.info("[CYCLE] Running background knowledge cycle...")
            try:
                bg_result = self.engine.perform_background_cycle()
                approved_facts = bg_result.get("approved_fact_count", 0)
                cycle_data["sub_cycles"].append({
                    "type": "background",
                    "facts_approved": approved_facts,
                    "status": "success"
                })
                cycle_data["facts_learned"] += approved_facts
                logger.info(f"[CYCLE] Background: {approved_facts} facts approved")
            except Exception as e:
                logger.error(f"[CYCLE] Background cycle error: {e}")
                cycle_data["errors"].append({"type": "background", "error": str(e)})

            # 2. Stream entropy processing
            logger.info("[CYCLE] Processing stream entropy...")
            try:
                stream_result = self.engine.perform_stream_entropy_cycle()
                packets_integrated = stream_result.get("packets_integrated", 0)
                cycle_data["sub_cycles"].append({
                    "type": "stream_entropy",
                    "packets_integrated": packets_integrated,
                    "status": "success"
                })
                logger.info(f"[CYCLE] Stream: {packets_integrated} packets processed")
            except Exception as e:
                logger.error(f"[CYCLE] Stream cycle error: {e}")
                cycle_data["errors"].append({"type": "stream_entropy", "error": str(e)})

            # 3. Global trend analysis
            logger.info("[CYCLE] Analyzing global trends...")
            try:
                trends_result = self.engine.perform_hourly_global_trend_cycle()
                trend_facts = trends_result.get("approved_fact_count", 0)
                cycle_data["sub_cycles"].append({
                    "type": "trends",
                    "facts_approved": trend_facts,
                    "status": "success"
                })
                cycle_data["facts_learned"] += trend_facts
                logger.info(f"[CYCLE] Trends: {trend_facts} facts from global analysis")
            except Exception as e:
                logger.error(f"[CYCLE] Trends cycle error: {e}")
                cycle_data["errors"].append({"type": "trends", "error": str(e)})

            # 4. Bridge feedback processing
            logger.info("[CYCLE] Processing bridge feedback...")
            try:
                feedback_result = self.engine.process_bridge_feedback_commands()
                processed_events = feedback_result.get("processed_events", 0)
                cycle_data["sub_cycles"].append({
                    "type": "bridge_feedback",
                    "events_processed": processed_events,
                    "status": "success"
                })
                logger.info(f"[CYCLE] Bridge: {processed_events} feedback events")
            except Exception as e:
                logger.error(f"[CYCLE] Bridge feedback error: {e}")
                cycle_data["errors"].append({"type": "bridge_feedback", "error": str(e)})

            # 5. Full autonomy agenda
            if self.enable_full_autonomy:
                logger.info("[CYCLE] Running full autonomy agenda...")
                try:
                    autonomy_result = self.engine.perform_autonomous_agenda_cycle()
                    autonomy_level = autonomy_result.get("autonomy_level", 0.0)
                    executed_actions = len(autonomy_result.get("executed_actions", []))
                    cycle_data["sub_cycles"].append({
                        "type": "autonomy_agenda",
                        "autonomy_level": float(autonomy_level),
                        "actions_executed": executed_actions,
                        "status": "success"
                    })
                    self.performance_metrics["autonomy_scores"].append(float(autonomy_level))
                    logger.info(f"[CYCLE] Autonomy: level={autonomy_level:.4f}, actions={executed_actions}")
                except Exception as e:
                    logger.error(f"[CYCLE] Autonomy agenda error: {e}")
                    cycle_data["errors"].append({"type": "autonomy_agenda", "error": str(e)})

            # 6. Capture current system metrics
            logger.info("[CYCLE] Capturing system metrics...")
            try:
                state = self.kernel.get_full_state()
                self.performance_metrics["coherence_levels"].append(
                    state.get("chitta", {}).get("coherence", 0.0)
                )
                if "growth_ratio" in state:
                    self.performance_metrics["growth_signals"].append(state["growth_ratio"])
                if "overall_stability" in state:
                    self.performance_metrics["stability_readings"].append(state["overall_stability"])
                logger.info(f"[CYCLE] Metrics captured: coherence={state.get('chitta', {}).get('coherence', 0.0):.4f}")
            except Exception as e:
                logger.error(f"[CYCLE] Metrics capture error: {e}")

        except Exception as e:
            logger.error(f"[CYCLE] Fatal error: {e}")
            self.error_log.append({"timestamp": time.time(), "error": str(e)})
            cycle_data["errors"].append({"type": "fatal", "error": str(e)})

        cycle_duration = time.time() - cycle_start
        cycle_data["duration_seconds"] = cycle_duration
        self.learning_metrics["facts_learned_by_cycle"].append(cycle_data["facts_learned"])
        self.learning_metrics["facts_learned_total"] += cycle_data["facts_learned"]
        self.training_session["cycles_completed"] += 1

        return cycle_data

    def check_for_self_modifications(self) -> Dict[str, Any]:
        """Check if the system has made any self-modifications."""
        modifications = {
            "timestamp": datetime.now().isoformat(),
            "new_modules": [],
            "modified_policies": [],
            "updated_capabilities": [],
            "autonomy_upgraded": False,
        }

        try:
            state = self.kernel.get_full_state()
            
            # Check for new capability modules
            if "modules" in state:
                modules = state.get("modules", {})
                for module_name, module_data in modules.items():
                    if module_data.get("created_during_training"):
                        modifications["new_modules"].append({
                            "name": module_name,
                            "created_at": module_data.get("creation_timestamp"),
                            "context": module_data.get("context", ""),
                        })
                        logger.info(f"[EVOLUTION] NEW MODULE CREATED: {module_name}")

            # Check for policy updates
            if "policies" in state:
                for policy_name, policy_data in state.get("policies", {}).items():
                    if policy_data.get("updated_during_training"):
                        modifications["modified_policies"].append({
                            "policy": policy_name,
                            "version": policy_data.get("version"),
                            "change": policy_data.get("last_change", ""),
                        })
                        logger.info(f"[EVOLUTION] POLICY UPDATED: {policy_name}")

            # Check autonomy upgrades
            current_autonomy = state.get("autonomy_level", 0.0)
            if current_autonomy > 0.65:  # Upgraded from level 4
                modifications["autonomy_upgraded"] = True
                logger.info(f"[EVOLUTION] AUTONOMY UPGRADED: {current_autonomy:.4f}")

        except Exception as e:
            logger.error(f"[EVOLUTION] Error checking modifications: {e}")

        if modifications["new_modules"] or modifications["modified_policies"] or modifications["autonomy_upgraded"]:
            self.evolution_metrics["self_modifications"].append(modifications)

        return modifications

    def generate_periodic_report(self) -> Dict[str, Any]:
        """Generate a comprehensive progress report."""
        elapsed = self.training_session["cycles_completed"]
        report = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_cycles": elapsed,
            "total_facts_learned": self.learning_metrics["facts_learned_total"],
            "average_facts_per_cycle": (
                self.learning_metrics["facts_learned_total"] / max(1, elapsed)
            ),
            "performance": {
                "avg_autonomy_score": (
                    sum(self.performance_metrics["autonomy_scores"]) / 
                    max(1, len(self.performance_metrics["autonomy_scores"]))
                    if self.performance_metrics["autonomy_scores"] else 0.0
                ),
                "avg_coherence": (
                    sum(self.performance_metrics["coherence_levels"]) / 
                    max(1, len(self.performance_metrics["coherence_levels"]))
                    if self.performance_metrics["coherence_levels"] else 0.0
                ),
                "avg_growth_signal": (
                    sum(self.performance_metrics["growth_signals"]) / 
                    max(1, len(self.performance_metrics["growth_signals"]))
                    if self.performance_metrics["growth_signals"] else 0.0
                ),
            },
            "evolution": {
                "self_modifications_count": len(self.evolution_metrics["self_modifications"]),
                "new_modules": len(self.evolution_metrics["modules_created"]),
                "policies_updated": len(self.evolution_metrics["policies_updated"]),
            },
            "errors": len(self.error_log),
        }

        logger.info(f"\n{'='*60}")
        logger.info(f"[REPORT] PERIODIC PROGRESS REPORT")
        logger.info(f"{'='*60}")
        logger.info(f"Cycles Completed: {report['elapsed_cycles']}")
        logger.info(f"Facts Learned: {report['total_facts_learned']} total, {report['average_facts_per_cycle']:.1f}/cycle")
        logger.info(f"Avg Autonomy Score: {report['performance']['avg_autonomy_score']:.4f}")
        logger.info(f"Avg Coherence: {report['performance']['avg_coherence']:.4f}")
        logger.info(f"Avg Growth Signal: {report['performance']['avg_growth_signal']:.4f}")
        logger.info(f"Self-Modifications: {report['evolution']['self_modifications_count']}")
        logger.info(f"Errors: {report['errors']}")
        logger.info(f"{'='*60}\n")

        return report

    def run_full_training(self) -> Dict[str, Any]:
        """Execute the complete autonomous training session."""
        logger.info("="*70)
        logger.info("STARTING FULL AUTONOMOUS TRAINING SESSION")
        logger.info("="*70)

        self.initialize_engine()
        start_time = time.time()
        last_report_time = start_time
        cycle_count = 0

        try:
            while time.time() - start_time < self.duration_seconds:
                elapsed = time.time() - start_time
                remaining = self.duration_seconds - elapsed
                
                logger.info(f"\n[TRAINING] Cycle {cycle_count + 1} | Elapsed: {elapsed/3600:.2f}h | Remaining: {remaining/3600:.2f}h")

                # Run intensive burst cycle
                cycle_result = self.run_intensive_burst_cycle()
                cycle_count += 1

                # Check for self-modifications every cycle
                modifications = self.check_for_self_modifications()

                # Periodic comprehensive report
                if time.time() - last_report_time >= self.report_interval_seconds:
                    report = self.generate_periodic_report()
                    self.checkpoint_history.append(report)
                    
                    # Save checkpoint
                    checkpoint_path = self.session_dir / f"checkpoint_{cycle_count:04d}.json"
                    checkpoint_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                    logger.info(f"[CHECKPOINT] Saved to {checkpoint_path.name}")
                    
                    last_report_time = time.time()

                # Small delay for system stability
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("\n[TRAINING] Interrupted by user")
        except Exception as e:
            logger.error(f"[TRAINING] Fatal error during training: {e}")
            self.error_log.append({"timestamp": time.time(), "error": str(e)})
        finally:
            self.training_session["total_kernel_uptime_seconds"] = time.time() - start_time

        # Generate final comprehensive report
        logger.info("\n" + "="*70)
        logger.info("GENERATING FINAL SESSION REPORT")
        logger.info("="*70)
        
        final_report = self.generate_final_report()
        
        # Save final report
        final_report_path = self.session_dir / "FINAL_TRAINING_REPORT.json"
        final_report_path.write_text(json.dumps(final_report, indent=2), encoding="utf-8")
        logger.info(f"[REPORT] Final report saved to {final_report_path}")

        # Save summary to main output
        summary_path = self.output_dir / "latest_training_summary.json"
        summary_path.write_text(json.dumps(final_report, indent=2), encoding="utf-8")

        # Shutdown
        try:
            if self.engine:
                self.engine.kernel.shutdown()
                logger.info("[SHUTDOWN] Kernel shut down gracefully")
        except Exception as e:
            logger.error(f"[SHUTDOWN] Error during shutdown: {e}")

        return final_report

    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report of entire training session."""
        elapsed_seconds = self.training_session["total_kernel_uptime_seconds"]
        
        final_report = {
            "session": self.training_session,
            "duration": {
                "requested_hours": self.duration_hours,
                "actual_seconds": elapsed_seconds,
                "actual_hours": elapsed_seconds / 3600,
            },
            "learning": {
                "total_facts_learned": self.learning_metrics["facts_learned_total"],
                "average_facts_per_cycle": (
                    self.learning_metrics["facts_learned_total"] / 
                    max(1, self.training_session["cycles_completed"])
                ),
                "learning_rate_acceleration": self._calculate_learning_acceleration(),
            },
            "evolution": {
                "self_modifications": len(self.evolution_metrics["self_modifications"]),
                "total_modules_created": len(self.evolution_metrics["modules_created"]),
                "total_policies_updated": len(self.evolution_metrics["policies_updated"]),
                "modification_details": self.evolution_metrics["self_modifications"],
            },
            "performance": {
                "average_autonomy_score": (
                    sum(self.performance_metrics["autonomy_scores"]) / 
                    max(1, len(self.performance_metrics["autonomy_scores"]))
                    if self.performance_metrics["autonomy_scores"] else 0.0
                ),
                "max_autonomy_score": (
                    max(self.performance_metrics["autonomy_scores"])
                    if self.performance_metrics["autonomy_scores"] else 0.0
                ),
                "average_coherence": (
                    sum(self.performance_metrics["coherence_levels"]) / 
                    max(1, len(self.performance_metrics["coherence_levels"]))
                    if self.performance_metrics["coherence_levels"] else 0.0
                ),
                "average_growth_signal": (
                    sum(self.performance_metrics["growth_signals"]) / 
                    max(1, len(self.performance_metrics["growth_signals"]))
                    if self.performance_metrics["growth_signals"] else 0.0
                ),
                "system_stability": (
                    sum(self.performance_metrics["stability_readings"]) / 
                    max(1, len(self.performance_metrics["stability_readings"]))
                    if self.performance_metrics["stability_readings"] else 0.0
                ),
            },
            "errors": {
                "total_errors": len(self.error_log),
                "error_log": self.error_log[-20:] if self.error_log else [],  # Last 20 errors
            },
            "checkpoints": self.checkpoint_history,
            "completed_at": datetime.now().isoformat(),
        }

        # Print detailed summary
        logger.info(f"\n{'='*70}")
        logger.info("FINAL TRAINING SESSION SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Session ID: {final_report['session']['session_id']}")
        logger.info(f"Duration: {final_report['duration']['actual_hours']:.2f} hours")
        logger.info(f"Cycles Completed: {self.training_session['cycles_completed']}")
        logger.info(f"\nLEARNING RESULTS:")
        logger.info(f"  Total Facts Learned: {final_report['learning']['total_facts_learned']}")
        logger.info(f"  Average Facts/Cycle: {final_report['learning']['average_facts_per_cycle']:.1f}")
        logger.info(f"  Learning Acceleration: {final_report['learning']['learning_rate_acceleration']:.2f}x")
        logger.info(f"\nEVOLUTION RESULTS:")
        logger.info(f"  Self-Modifications: {final_report['evolution']['self_modifications']}")
        logger.info(f"  Modules Created: {final_report['evolution']['total_modules_created']}")
        logger.info(f"  Policies Updated: {final_report['evolution']['total_policies_updated']}")
        logger.info(f"\nPERFORMANCE METRICS:")
        logger.info(f"  Avg Autonomy Score: {final_report['performance']['average_autonomy_score']:.4f}")
        logger.info(f"  Max Autonomy Score: {final_report['performance']['max_autonomy_score']:.4f}")
        logger.info(f"  Avg Coherence: {final_report['performance']['average_coherence']:.4f}")
        logger.info(f"  Avg Growth Signal: {final_report['performance']['average_growth_signal']:.4f}")
        logger.info(f"  System Stability: {final_report['performance']['system_stability']:.4f}")
        logger.info(f"\nERRORS: {final_report['errors']['total_errors']}")
        logger.info(f"{'='*70}\n")

        return final_report

    def _calculate_learning_acceleration(self) -> float:
        """Calculate if learning is accelerating (showing growth)."""
        if len(self.learning_metrics["facts_learned_by_cycle"]) < 2:
            return 1.0
        
        first_half = self.learning_metrics["facts_learned_by_cycle"][:len(self.learning_metrics["facts_learned_by_cycle"])//2]
        second_half = self.learning_metrics["facts_learned_by_cycle"][len(self.learning_metrics["facts_learned_by_cycle"])//2:]
        
        avg_first = sum(first_half) / max(1, len(first_half))
        avg_second = sum(second_half) / max(1, len(second_half))
        
        return avg_second / max(0.01, avg_first)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Full Autonomous Training - Run Antahkarana in complete autonomous mode with comprehensive tracking"
    )
    parser.add_argument(
        "--duration-hours",
        type=float,
        default=24,
        help="Duration of training in hours (default: 24)"
    )
    parser.add_argument(
        "--report-interval-minutes",
        type=int,
        default=30,
        help="Interval between progress reports in minutes (default: 30)"
    )
    parser.add_argument(
        "--full-autonomy",
        action="store_true",
        default=True,
        help="Enable full autonomy agenda (default: enabled)"
    )
    parser.add_argument(
        "--enable-self-modification",
        action="store_true",
        default=True,
        help="Enable system self-modification detection (default: enabled)"
    )
    
    args = parser.parse_args()

    trainer = FullAutonomousTrainer(
        duration_hours=args.duration_hours,
        report_interval_minutes=args.report_interval_minutes,
        enable_full_autonomy=args.full_autonomy,
        enable_self_modification=args.enable_self_modification,
    )

    final_report = trainer.run_full_training()
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Session: {final_report['session']['session_id']}")
    print(f"Duration: {final_report['duration']['actual_hours']:.2f} hours")
    print(f"Facts Learned: {final_report['learning']['total_facts_learned']}")
    print(f"Autonomy Score: {final_report['performance']['average_autonomy_score']:.4f}")
    print(f"Self-Modifications: {final_report['evolution']['self_modifications']}")
    print(f"Output: {ROOT / 'training_outputs'}")
    print("="*70)


if __name__ == "__main__":
    main()
