from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
KERNEL_ROOT = ROOT / "antahkarana_kernel"
if str(KERNEL_ROOT) not in sys.path:
    sys.path.insert(0, str(KERNEL_ROOT))

import InteractiveBridge as bridge  # noqa: E402

PROMPTS: List[str] = [
    (
        "Return strict JSON only with keys answer, claims, unknowns, action. "
        "Include claims for stability_score, current_valence, average_confidence, "
        "observer_concern when available; put missing metrics into unknowns."
    ),
]


def _extract_retry_seconds(text: str) -> float:
    m = re.search(r"retry_after=([0-9]+(?:\.[0-9]+)?)s", text)
    if not m:
        return 20.0
    try:
        return max(1.0, float(m.group(1)))
    except ValueError:
        return 20.0


def run(target_cycles: int = 20, max_attempts: int = 80, max_backoff_seconds: float = 30.0) -> dict:
    grounded = 0
    fallback = 0
    attempts = 0
    start = time.time()

    while attempts < max_attempts and (grounded + fallback) < target_cycles:
        prompt = PROMPTS[0]
        attempts += 1

        facts = bridge._get_grounded_facts(limit=8)
        answer = bridge._compose_grounded_answer(prompt, facts)

        if "[mode=llm_grounded" in answer:
            grounded += 1
            print(f"[{attempts}] grounded cycle ok ({grounded}/{target_cycles})")
            time.sleep(0.6)
            continue

        fallback += 1
        produced = grounded + fallback
        cfg = bridge._build_grounding_context(prompt, facts)
        try:
            bridge._call_openai_compatible_llm(cfg["system_prompt"], cfg["user_prompt"])
        except Exception as exc:
            msg = str(exc)
            if "llm_rate_limited" in msg or "llm_rate_limited_cooldown" in msg:
                delay = _extract_retry_seconds(msg)
                if delay > max_backoff_seconds:
                    print(
                        f"[{attempts}] rate-limited ({delay:.1f}s) exceeds cap "
                        f"({max_backoff_seconds:.1f}s); continuing in fallback mode"
                    )
                    time.sleep(0.25)
                    continue
                print(f"[{attempts}] rate-limited, sleeping {delay:.1f}s")
                time.sleep(delay)
                continue

        # Generic fallback backoff
        print(f"[{attempts}] local fallback path; applying short backoff")
        time.sleep(1.5)

    result = {
        "target_cycles": target_cycles,
        "grounded_cycles_observed": grounded,
        "fallback_cycles": fallback,
        "total_cycles_observed": grounded + fallback,
        "attempts": attempts,
        "elapsed_seconds": round(time.time() - start, 2),
        "complete": (grounded + fallback) >= target_cycles,
        "max_backoff_seconds": max_backoff_seconds,
    }
    return result


def main() -> None:
    target = 20
    attempts = 80
    backoff_cap = 30.0
    if len(sys.argv) >= 2:
        try:
            target = max(1, int(sys.argv[1]))
        except ValueError:
            pass
    if len(sys.argv) >= 3:
        try:
            attempts = max(target, int(sys.argv[2]))
        except ValueError:
            pass
    if len(sys.argv) >= 4:
        try:
            backoff_cap = max(1.0, float(sys.argv[3]))
        except ValueError:
            pass

    result = run(target_cycles=target, max_attempts=attempts, max_backoff_seconds=backoff_cap)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
