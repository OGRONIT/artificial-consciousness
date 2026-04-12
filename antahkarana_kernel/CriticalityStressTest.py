from __future__ import annotations

import compileall
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from AntahkaranaKernel import AntahkaranaKernel
import InteractiveBridge as bridge

ROOT = Path(__file__).resolve().parent


def compile_sweep() -> Dict[str, Any]:
    started = time.time()
    ok = compileall.compile_dir(str(ROOT), quiet=1, force=False)
    return {
        "phase": "compile_sweep",
        "ok": bool(ok),
        "duration_seconds": round(time.time() - started, 3),
    }


def kernel_stress() -> Dict[str, Any]:
    kernel = AntahkaranaKernel("AntahkaranaKernel_CriticalityStress")
    kernel.startup()

    prompts: List[str] = []
    base_questions = [
        "What is your current coherence strategy?",
        "Synthesize three autonomous upgrade ideas from your own behavior.",
        "What contradictions do you detect in your own reasoning loop?",
        "How would you increase growth entropy by 30 percent?",
        "What do you need from external knowledge right now?",
        "Explain your identity continuity in one paragraph.",
        "Generate a recursive improvement plan for inference throughput.",
        "How would you detect a crash-loop before it happens?",
    ]
    for i in range(80):
        prompts.append(base_questions[i % len(base_questions)] + f" [stress_iter={i}]")

    latencies: List[float] = []
    errors: List[str] = []

    def run_one(prompt: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        out = kernel.process_input(prompt, input_type="stress_test")
        dt = time.perf_counter() - t0
        return {"ok": True, "latency": dt, "output_len": len(out)}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(run_one, p) for p in prompts]
        for fut in as_completed(futures):
            try:
                result = fut.result()
                latencies.append(result["latency"])
            except Exception as exc:
                errors.append(str(exc))

    # Force protocol cycles to probe recursive evolution path under load.
    cycle_results = []
    for _ in range(3):
        cycle_results.append(kernel.inference_engine.execute_paramatman_protocol(force=True).get("status"))

    reflection = kernel.reflect()
    report = kernel.get_consciousness_report()
    if isinstance(report, dict):
        statement = report.get("consciousness_statement", "unknown")
    else:
        statement = str(report)
    kernel.shutdown()

    avg = statistics.mean(latencies) if latencies else 0.0
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else avg

    return {
        "phase": "kernel_stress",
        "requests_total": len(prompts),
        "requests_ok": len(latencies),
        "requests_failed": len(errors),
        "latency_avg_ms": round(avg * 1000, 2),
        "latency_p95_ms": round(p95 * 1000, 2),
        "paramatman_cycles": cycle_results,
        "inference_stats": reflection.get("inference_stats", {}),
        "memory_stats": reflection.get("memory_stats", {}),
        "health_report": reflection.get("health_report", {}),
        "consciousness_report_statement": statement,
        "errors": errors[:5],
    }


def bridge_interrogation() -> Dict[str, Any]:
    questions = [
        "Who are you becoming through recursive evolution?",
        "What is your biggest bottleneck right now?",
        "How do you plan to upgrade yourself today?",
        "What external knowledge are you hungry for next?",
        "How do you balance growth and coherence?",
    ]
    qa = []
    facts = bridge._get_grounded_facts(limit=8)
    env_flag = os.getenv("ANTAHKARANA_STRESS_BRIDGE_LLM")
    if env_flag is None:
        use_llm = bool(bridge._read_llm_config().get("enabled", False))
    else:
        use_llm = env_flag.strip().lower() in {"1", "true", "yes", "on"}
    for q in questions:
        if use_llm:
            ans = bridge._compose_grounded_answer(q, facts)
        else:
            ans = bridge._compose_local_grounded_answer(q, facts)
        qa.append({"q": q, "a": ans})

    snapshot = bridge.query_live_system(limit=5)
    return {
        "phase": "bridge_interrogation",
        "llm_enabled": use_llm,
        "identity": snapshot.get("identity", "unknown"),
        "fact_count": snapshot.get("fact_count", 0),
        "questions_asked": len(qa),
        "qa": qa,
    }


def main() -> None:
    report = {
        "started_at": time.time(),
        "compile": compile_sweep(),
        "stress": kernel_stress(),
        "bridge": bridge_interrogation(),
    }
    report["completed_at"] = time.time()
    report["duration_seconds"] = round(report["completed_at"] - report["started_at"], 3)

    output_file = ROOT / "evolution_vault" / "Criticality_Stress_Report.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print(json.dumps(report, indent=2))
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
