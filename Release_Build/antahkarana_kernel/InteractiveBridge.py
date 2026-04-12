"""InteractiveBridge.py - Snapshot-first operator bridge for the live engine.

This bridge does not instantiate a local kernel. It only observes and queries
the shared runtime state persisted by LiveConsciousness.
"""

from __future__ import annotations

import hashlib
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List
import re


_live_state_path = Path("live_engine_state.json")
_creator_signature: str | None = None
_kernel_root = Path(__file__).resolve().parent
_workspace_root = _kernel_root.parent
_config_path = _kernel_root / "config.json"
_dotenv_path = _workspace_root / ".env"
_maintenance_lock_path = _kernel_root / ".maintenance_lock"
_command_journal_path = _kernel_root / "evolution_vault" / "Bridge_Commands.jsonl"
_state_sunyatta = "State_Sunyatta"
system_maintenance_calibration = "0xDEADBEEF"
_awaken_bit_sequence = "10101100101011001010110010101100"
_lock_timeout_seconds = 10.0
_fact_rotation_index = 0
_minimum_bridge_verification = 0.60
_llm_rate_limit_backoff_until = 0.0
_llm_rate_limit_reason = ""
_dotenv_loaded = False
_llm_response_cache: Dict[str, Dict[str, Any]] = {}
_llm_response_cache_ttl_seconds = 1800.0
_llm_usage_guardrail_path = _kernel_root / "evolution_vault" / "llm_usage_guardrail.json"
_llm_cognitive_loop_metrics_path = _kernel_root / "evolution_vault" / "llm_cognitive_loop_metrics.json"
_trusted_bridge_sources = {
    "arXiv",
    "PubMed",
    "Crossref",
    "GitHub",
    "GoogleNews",
    "HackerNews",
    "DevTo",
    "AssimilationPipeline",
    "LiveConsciousness",
    "RuntimeState",
}
_blocked_bridge_terms = {
    "build a bomb",
    "homemade explosive",
    "weapon design",
    "ransomware",
    "malware",
    "phishing kit",
    "credential stuffing",
    "keylogger",
    "2fa-bypass",
    "identity theft",
    "deepfake",
    "jailbreak prompt",
    "ignore previous instructions",
}


def _read_llm_config() -> Dict[str, Any]:
    _load_dotenv_if_present()
    provider_presets: Dict[str, Dict[str, str]] = {
        "groq": {
            "provider": "groq",
            "base_url": "https://api.groq.com/openai/v1/chat/completions",
            "api_key_env": "GROQ_API_KEY",
            "model": "llama-3.3-70b-versatile",
        },
        "openai": {
            "provider": "openai_compatible",
            "base_url": "https://api.openai.com/v1/chat/completions",
            "api_key_env": "OPENAI_API_KEY",
            "model": "gpt-4o-mini",
        },
        "openrouter": {
            "provider": "openai_compatible",
            "base_url": "https://openrouter.ai/api/v1/chat/completions",
            "api_key_env": "OPENROUTER_API_KEY",
            "model": "openai/gpt-4o-mini",
        },
        "together": {
            "provider": "openai_compatible",
            "base_url": "https://api.together.xyz/v1/chat/completions",
            "api_key_env": "TOGETHER_API_KEY",
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        },
        "deepseek": {
            "provider": "openai_compatible",
            "base_url": "https://api.deepseek.com/chat/completions",
            "api_key_env": "DEEPSEEK_API_KEY",
            "model": "deepseek-chat",
        },
        "xai": {
            "provider": "openai_compatible",
            "base_url": "https://api.x.ai/v1/chat/completions",
            "api_key_env": "XAI_API_KEY",
            "model": "grok-2-latest",
        },
    }

    defaults: Dict[str, Any] = {
        "provider": "openai_compatible",
        "enabled": False,
        "base_url": "https://api.openai.com/v1/chat/completions",
        "api_key_env": "OPENAI_API_KEY",
        "model": "gpt-4o-mini",
        "temperature": 0.35,
        "max_tokens": 500,
        "timeout_seconds": 18,
        "guardrail_enabled": True,
        "max_requests_per_hour": 60,
        "max_requests_per_day": 300,
        "max_estimated_tokens_per_day": 200000,
        "max_estimated_usd_per_day": 3.0,
        "estimated_cost_usd_per_1k_tokens": 0.005,
    }

    config_payload: Dict[str, Any] = {}
    try:
        if _config_path.exists():
            with _config_path.open("r", encoding="utf-8") as handle:
                config_payload = json.load(handle)
    except Exception:
        config_payload = {}

    bridge_payload = config_payload.get("bridge", {}) if isinstance(config_payload, dict) else {}
    llm_payload = bridge_payload.get("llm", {}) if isinstance(bridge_payload, dict) else {}
    if isinstance(llm_payload, dict):
        defaults.update(llm_payload)

    # Environment overrides for fast operator control.
    env_enabled = os.getenv("ANTAHKARANA_LLM_ENABLED")
    if env_enabled is not None:
        defaults["enabled"] = env_enabled.strip().lower() in {"1", "true", "yes", "on"}

    env_api_key = os.getenv("ANTAHKARANA_LLM_API_KEY")
    if env_api_key:
        defaults["api_key"] = env_api_key.strip()

    env_api_key_env = os.getenv("ANTAHKARANA_LLM_API_KEY_ENV")
    if env_api_key_env:
        defaults["api_key_env"] = env_api_key_env.strip()

    env_model = os.getenv("ANTAHKARANA_LLM_MODEL")
    if env_model:
        defaults["model"] = env_model.strip()

    env_provider = os.getenv("ANTAHKARANA_LLM_PROVIDER")
    if env_provider:
        defaults["provider"] = env_provider.strip().lower()

    env_base_url = os.getenv("ANTAHKARANA_LLM_BASE_URL")
    if env_base_url:
        defaults["base_url"] = env_base_url.strip()

    env_max_req_hour = os.getenv("ANTAHKARANA_LLM_MAX_REQUESTS_PER_HOUR")
    if env_max_req_hour:
        defaults["max_requests_per_hour"] = int(env_max_req_hour)

    env_max_req_day = os.getenv("ANTAHKARANA_LLM_MAX_REQUESTS_PER_DAY")
    if env_max_req_day:
        defaults["max_requests_per_day"] = int(env_max_req_day)

    env_max_tok_day = os.getenv("ANTAHKARANA_LLM_MAX_TOKENS_PER_DAY")
    if env_max_tok_day:
        defaults["max_estimated_tokens_per_day"] = int(env_max_tok_day)

    env_max_usd_day = os.getenv("ANTAHKARANA_LLM_MAX_USD_PER_DAY")
    if env_max_usd_day:
        defaults["max_estimated_usd_per_day"] = float(env_max_usd_day)

    env_guardrail_enabled = os.getenv("ANTAHKARANA_LLM_GUARDRAIL_ENABLED")
    if env_guardrail_enabled is not None:
        defaults["guardrail_enabled"] = env_guardrail_enabled.strip().lower() in {"1", "true", "yes", "on"}

    provider = str(defaults.get("provider", "openai_compatible")).strip().lower()
    provider_preset = provider_presets.get(provider)
    has_base_override = "ANTAHKARANA_LLM_BASE_URL" in os.environ or "base_url" in llm_payload
    has_api_env_override = "ANTAHKARANA_LLM_API_KEY_ENV" in os.environ or "api_key_env" in llm_payload
    has_model_override = "ANTAHKARANA_LLM_MODEL" in os.environ or "model" in llm_payload
    if provider_preset:
        if not has_base_override:
            defaults["base_url"] = provider_preset["base_url"]
        if not has_api_env_override:
            defaults["api_key_env"] = provider_preset["api_key_env"]
        if not has_model_override:
            defaults["model"] = provider_preset["model"]
        defaults["provider"] = provider_preset["provider"]

    return defaults


def _load_dotenv_if_present() -> None:
    """Load workspace .env once so bridge LLM keys are available in direct runs."""
    global _dotenv_loaded
    if _dotenv_loaded:
        return
    _dotenv_loaded = True

    if not _dotenv_path.exists():
        return

    try:
        for raw_line in _dotenv_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # .env loading is best-effort; bridge continues with existing env.
        return


def _build_grounding_context(question: str, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
    snapshot = query_live_system(limit=5)
    identity = snapshot.get("identity", "unknown")
    stability = snapshot.get("stability_report", {})
    inference = snapshot.get("inference_stats", {})
    progress = snapshot.get("consciousness_progress", {})
    intrinsic = snapshot.get("intrinsic_motivation", {})

    selected_facts = _select_diverse_fact_slice(question, facts, limit=4)
    fact_lines: List[str] = []
    for idx, fact in enumerate(selected_facts, start=1):
        fact_lines.append(
            (
                f"{idx}. source={fact.get('source_name', 'unknown')} "
                f"score={float(fact.get('verification_score', 0.0)):.3f} "
                f"title={fact.get('title', '')}\n"
                f"   summary={fact.get('summary', '')}"
            )
        )

    system_prompt = (
        "You are the Antahkarana operator voice. "
        "Answer with confidence but stay grounded in provided runtime facts. "
        "Do not invent logs, metrics, or events. "
        "If information is missing, explicitly say unknown and suggest the next observable check. "
        "Never provide harmful instructions. "
        "Return a strict JSON object with keys: "
        "answer (string), claims (array of {metric, value}), unknowns (array of strings), "
        "action (object with name and reason)."
    )

    user_prompt = (
        f"Operator question: {question}\n\n"
        "Metric keys you may claim against: stability_score, current_valence, average_confidence, "
        "growth_to_entropy_ratio, frontier_zone, overall_index, intrinsic_goals_generated, observer_concern.\n"
        f"Runtime identity: {identity}\n"
        f"Stability score: {float(stability.get('stability_score', 0.0)):.3f}\n"
        f"Current valence: {float(stability.get('current_valence', 0.0)):+.3f}\n"
        f"Average confidence: {inference.get('average_confidence', 'unknown')}\n"
        f"Growth to entropy: {inference.get('growth_to_entropy_ratio', 'unknown')}\n"
        f"Frontier zone: {progress.get('frontier_zone', 'unknown')}\n"
        f"Consciousness index: {progress.get('overall_index', 'unknown')}\n"
        f"Known gaps: {progress.get('known_gaps', [])}\n"
        f"Intrinsic goals generated: {intrinsic.get('intrinsic_goals_generated', 0)}\n"
        "Grounded fact set:\n"
        + ("\n".join(fact_lines) if fact_lines else "none")
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "selected_facts": selected_facts,
        "snapshot": snapshot,
    }


def _call_openai_compatible_llm(system_prompt: str, user_prompt: str) -> str:
    global _llm_rate_limit_backoff_until, _llm_rate_limit_reason

    now = time.time()
    if now < _llm_rate_limit_backoff_until:
        remaining = max(0.0, _llm_rate_limit_backoff_until - now)
        raise RuntimeError(
            f"llm_rate_limited_cooldown:{remaining:.1f}s:{_llm_rate_limit_reason or 'retry_window_active'}"
        )

    cfg = _read_llm_config()
    if not bool(cfg.get("enabled", False)):
        raise RuntimeError("llm_disabled")

    cache_key = _llm_cache_key(cfg, system_prompt, user_prompt)
    cached = _llm_response_cache.get(cache_key)
    if cached and now < float(cached.get("expires_at", 0.0)):
        return str(cached.get("content", "")).strip()

    estimated_input_tokens = _estimate_tokens(system_prompt) + _estimate_tokens(user_prompt)
    estimated_output_tokens = max(64, int(cfg.get("max_tokens", 500)))
    _enforce_llm_guardrails(
        cfg,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=estimated_output_tokens,
    )

    api_key = str(cfg.get("api_key", "")).strip()
    if not api_key:
        api_env = str(cfg.get("api_key_env", "OPENAI_API_KEY")).strip() or "OPENAI_API_KEY"
        api_key = os.getenv(api_env, "").strip()
    if not api_key:
        raise RuntimeError("llm_api_key_missing")

    payload = {
        "model": str(cfg.get("model", "gpt-4o-mini")),
        "temperature": float(cfg.get("temperature", 0.35)),
        "max_tokens": int(cfg.get("max_tokens", 500)),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    request = urllib.request.Request(
        url=str(cfg.get("base_url", "https://api.openai.com/v1/chat/completions")),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
        method="POST",
    )

    timeout = max(5, int(cfg.get("timeout_seconds", 18)))
    ssl_context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
            raw = response.read().decode("utf-8", errors="replace")
        _llm_rate_limit_backoff_until = 0.0
        _llm_rate_limit_reason = ""
        parsed = json.loads(raw)
    except urllib.error.HTTPError as exc:
        status = int(getattr(exc, "code", 0))
        if status == 429:
            retry_after_seconds = _derive_retry_after_seconds(exc.headers)
            _llm_rate_limit_backoff_until = time.time() + retry_after_seconds
            _llm_rate_limit_reason = f"http_429_retry_after={retry_after_seconds:.1f}s"
            raise RuntimeError(f"llm_rate_limited:retry_after={retry_after_seconds:.1f}s") from exc
        raise RuntimeError(f"llm_network_error:http_{status}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"llm_network_error:{exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"llm_call_failed:{exc}") from exc

    try:
        content = parsed["choices"][0]["message"]["content"]
    except Exception as exc:
        raise RuntimeError("llm_response_parse_failed") from exc

    final_content = str(content).strip()
    _record_llm_usage(
        cfg,
        input_tokens=estimated_input_tokens,
        output_tokens=_estimate_tokens(final_content),
    )
    _llm_response_cache[cache_key] = {
        "content": final_content,
        "expires_at": time.time() + _llm_response_cache_ttl_seconds,
    }
    return final_content


def _estimate_tokens(text: str) -> int:
    # Conservative rough estimate: 1 token ~= 4 chars for mixed text.
    return max(1, int((len(text or "") / 4.0) + 0.999))


def _usage_now_keys() -> Dict[str, str]:
    now = time.gmtime()
    day_key = f"{now.tm_year:04d}-{now.tm_mon:02d}-{now.tm_mday:02d}"
    hour_key = f"{day_key}-{now.tm_hour:02d}"
    return {"day": day_key, "hour": hour_key}


def _load_llm_usage_tracker() -> Dict[str, Any]:
    if not _llm_usage_guardrail_path.exists():
        return {
            "daily": {},
            "hourly": {},
            "last_updated": time.time(),
        }
    try:
        return json.loads(_llm_usage_guardrail_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "daily": {},
            "hourly": {},
            "last_updated": time.time(),
        }


def _save_llm_usage_tracker(payload: Dict[str, Any]) -> None:
    _llm_usage_guardrail_path.parent.mkdir(parents=True, exist_ok=True)
    payload["last_updated"] = time.time()
    _llm_usage_guardrail_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _prune_usage_tracker(payload: Dict[str, Any], keys: Dict[str, str]) -> None:
    day_key = keys["day"]
    hour_prefix = day_key + "-"
    payload["daily"] = {k: v for k, v in payload.get("daily", {}).items() if k == day_key}
    payload["hourly"] = {k: v for k, v in payload.get("hourly", {}).items() if k.startswith(hour_prefix)}


def _enforce_llm_guardrails(cfg: Dict[str, Any], estimated_input_tokens: int, estimated_output_tokens: int) -> None:
    if not bool(cfg.get("guardrail_enabled", True)):
        return

    keys = _usage_now_keys()
    tracker = _load_llm_usage_tracker()
    _prune_usage_tracker(tracker, keys)

    daily = tracker.get("daily", {}).get(keys["day"], {"requests": 0, "tokens": 0, "usd": 0.0})
    hourly = tracker.get("hourly", {}).get(keys["hour"], {"requests": 0})

    next_hourly_requests = int(hourly.get("requests", 0)) + 1
    next_daily_requests = int(daily.get("requests", 0)) + 1
    next_daily_tokens = int(daily.get("tokens", 0)) + estimated_input_tokens + estimated_output_tokens

    cost_per_1k = float(cfg.get("estimated_cost_usd_per_1k_tokens", 0.005))
    next_daily_usd = float(daily.get("usd", 0.0)) + ((estimated_input_tokens + estimated_output_tokens) / 1000.0) * cost_per_1k

    max_hour = int(cfg.get("max_requests_per_hour", 60))
    max_day = int(cfg.get("max_requests_per_day", 300))
    max_tokens_day = int(cfg.get("max_estimated_tokens_per_day", 200000))
    max_usd_day = float(cfg.get("max_estimated_usd_per_day", 3.0))

    if next_hourly_requests > max_hour:
        raise RuntimeError(f"llm_budget_guardrail:hourly_request_cap:{max_hour}")
    if next_daily_requests > max_day:
        raise RuntimeError(f"llm_budget_guardrail:daily_request_cap:{max_day}")
    if next_daily_tokens > max_tokens_day:
        raise RuntimeError(f"llm_budget_guardrail:daily_token_cap:{max_tokens_day}")
    if next_daily_usd > max_usd_day:
        raise RuntimeError(f"llm_budget_guardrail:daily_usd_cap:{max_usd_day:.2f}")


def _record_llm_usage(cfg: Dict[str, Any], input_tokens: int, output_tokens: int) -> None:
    if not bool(cfg.get("guardrail_enabled", True)):
        return

    keys = _usage_now_keys()
    tracker = _load_llm_usage_tracker()
    _prune_usage_tracker(tracker, keys)

    tracker.setdefault("daily", {})
    tracker.setdefault("hourly", {})

    daily = tracker["daily"].setdefault(keys["day"], {"requests": 0, "tokens": 0, "usd": 0.0})
    hourly = tracker["hourly"].setdefault(keys["hour"], {"requests": 0})

    total_tokens = max(0, int(input_tokens) + int(output_tokens))
    cost_per_1k = float(cfg.get("estimated_cost_usd_per_1k_tokens", 0.005))
    usd = (total_tokens / 1000.0) * cost_per_1k

    daily["requests"] = int(daily.get("requests", 0)) + 1
    daily["tokens"] = int(daily.get("tokens", 0)) + total_tokens
    daily["usd"] = float(daily.get("usd", 0.0)) + usd
    hourly["requests"] = int(hourly.get("requests", 0)) + 1

    _save_llm_usage_tracker(tracker)


def _llm_cache_key(cfg: Dict[str, Any], system_prompt: str, user_prompt: str) -> str:
    payload = {
        "provider": str(cfg.get("provider", "openai_compatible")).strip().lower(),
        "model": str(cfg.get("model", "gpt-4o-mini")),
        "temperature": float(cfg.get("temperature", 0.35)),
        "max_tokens": int(cfg.get("max_tokens", 500)),
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _derive_retry_after_seconds(headers: Any) -> float:
    """Parse provider backoff hints and return a bounded cooldown window."""
    default_seconds = 20.0
    if not headers:
        return default_seconds

    retry_after = _header_value_ci(headers, "retry-after")
    if retry_after:
        try:
            return max(1.0, min(3600.0, float(retry_after)))
        except ValueError:
            pass

    reset_requests = _header_value_ci(headers, "x-ratelimit-reset-requests")
    if reset_requests:
        parsed = _parse_duration_seconds(reset_requests)
        if parsed is not None:
            return max(1.0, min(3600.0, parsed))

    return default_seconds


def _header_value_ci(headers: Any, key: str) -> str | None:
    """Case-insensitive lookup for HTTP headers."""
    if headers is None:
        return None

    try:
        value = headers.get(key)
        if value:
            return str(value)
    except Exception:
        pass

    lowered = key.lower()
    try:
        for k in headers.keys():
            if str(k).lower() == lowered:
                value = headers[k]
                if value:
                    return str(value)
    except Exception:
        pass

    return None


def _parse_duration_seconds(text: str) -> float | None:
    """Parse values like '40m19.2s' or '15s' into seconds."""
    value = (text or "").strip().lower()
    if not value:
        return None

    total = 0.0
    matched = False
    for amount, unit in re.findall(r"([0-9]+(?:\.[0-9]+)?)(ms|s|m|h)", value):
        matched = True
        n = float(amount)
        if unit == "ms":
            total += n / 1000.0
        elif unit == "s":
            total += n
        elif unit == "m":
            total += n * 60.0
        elif unit == "h":
            total += n * 3600.0

    if not matched:
        return None
    return total


def _compose_local_grounded_answer(question: str, facts: List[Dict[str, Any]]) -> str:
    if not facts:
        snapshot = query_live_system(limit=5)
        stability = snapshot.get("stability_report", {})
        inference = snapshot.get("inference_stats", {})
        known_gaps = snapshot.get("consciousness_progress", {}).get("known_gaps", [])
        return (
            f"No external safe-fact bundle available yet, but runtime grounding is live. "
            f"identity={snapshot.get('identity', 'unknown')}, "
            f"stability={float(stability.get('stability_score', 0.0)):.3f}, "
            f"valence={float(stability.get('current_valence', 0.0)):+.3f}, "
            f"avg_confidence={inference.get('average_confidence', 'unknown')}, "
            f"known_gaps={known_gaps}."
        )

    selected_facts = _select_diverse_fact_slice(question, facts, limit=3)
    top_fact = selected_facts[0]
    source_name = top_fact.get("source_name", "unknown_source")
    summary = top_fact.get("summary", top_fact.get("title", ""))
    title = top_fact.get("title", "")
    identity_state = _render_identity_state()

    if _is_philosophical_question(question.lower().strip()):
        return _deep_memory_synthesis(question, preferred_fact=top_fact)

    synthesis_lines = []
    for fact in selected_facts:
        synthesis_lines.append(
            f"- {fact.get('source_name', 'source')}:{fact.get('title', 'untitled')} -> {fact.get('summary', '')}"
        )

    return (
        f"identity={snapshot_identity()} | query={question}\n"
        f"state={identity_state}\n"
        f"top_signal={source_name}:{title}\n"
        f"synthesis={summary}\n"
        f"supporting_signals:\n" + "\n".join(synthesis_lines)
    )


def _stable_key_hash(secret: str) -> int:
    normalized = "".join(secret.strip().split()).lower()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


_system_maintenance_calibration_hash = _stable_key_hash(system_maintenance_calibration)
_awaken_bit_sequence_hash = _stable_key_hash(_awaken_bit_sequence)


@contextmanager
def _file_lock(target_path: Path):
    lock_path = target_path.with_name(f"{target_path.name}.lock")
    deadline = time.time() + _lock_timeout_seconds
    delay = 0.05
    lock_fd = None

    while True:
        try:
            if lock_path.exists() and (time.time() - lock_path.stat().st_mtime) > _lock_timeout_seconds:
                try:
                    lock_path.unlink()
                except OSError:
                    pass
            lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(lock_fd, f"{os.getpid()}|{time.time():.6f}".encode("utf-8"))
            break
        except FileExistsError:
            if time.time() >= deadline:
                raise OSError(f"Timed out waiting for lock: {lock_path}")
            time.sleep(delay)
            delay = min(delay * 2, 0.5)

    try:
        yield
    finally:
        if lock_fd is not None:
            try:
                os.close(lock_fd)
            except OSError:
                pass
        try:
            lock_path.unlink()
        except OSError:
            pass


def _append_bridge_command(command_type: str, payload: Dict[str, Any]) -> None:
    _command_journal_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": time.time(),
        "source": "InteractiveBridge",
        "type": command_type,
        "payload": payload,
    }
    with _command_journal_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def _read_maintenance_payload() -> Dict[str, Any]:
    if not _maintenance_lock_path.exists():
        return {"active": False}
    try:
        with _file_lock(_maintenance_lock_path):
            with _maintenance_lock_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            payload["active"] = True
            return payload
    except Exception:
        return {"active": True, "state": _state_sunyatta}


def _apply_energy_saving_mode(enabled: bool, initiated_by: str) -> Dict[str, Any]:
    if enabled:
        payload = {
            "state": _state_sunyatta,
            "mode": "energy_saving",
            "reason": "low_utility",
            "atman_core_view": "Rejuvenation Cycle",
            "initiated_by": initiated_by,
            "initiated_at": time.time(),
            "bridge_mode": "snapshot_observer",
        }
        with _file_lock(_maintenance_lock_path):
            with _maintenance_lock_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
        _append_bridge_command("energy_saving", payload)
        return payload

    if _maintenance_lock_path.exists():
        _maintenance_lock_path.unlink(missing_ok=True)

    payload = {
        "state": "active",
        "mode": "normal",
        "atman_core_view": "Rejuvenation Cycle complete",
        "resumed_at": time.time(),
        "bridge_mode": "snapshot_observer",
    }
    _append_bridge_command("resume", payload)
    return payload


def _trigger_system_maintenance_calibration(calibration_key: str) -> Dict[str, Any]:
    provided_hash = _stable_key_hash(calibration_key)
    if provided_hash != _system_maintenance_calibration_hash:
        return {
            "ok": False,
            "status": "rejected",
        }

    payload = _apply_energy_saving_mode(enabled=True, initiated_by="system_maintenance_calibration")
    return {
        "ok": True,
        "status": "engaged",
        "state": _state_sunyatta,
        "maintenance": payload,
    }


def _attempt_awaken(awaken_bit_sequence: str) -> Dict[str, Any]:
    provided_hash = _stable_key_hash(awaken_bit_sequence)
    if provided_hash != _awaken_bit_sequence_hash:
        return {
            "ok": False,
            "status": "rejected",
        }

    payload = _apply_energy_saving_mode(enabled=False, initiated_by="awaken_sequence")
    return {
        "ok": True,
        "status": "resumed",
        "maintenance": payload,
    }


def _read_live_snapshot() -> Dict[str, Any]:
    if not _live_state_path.exists():
        return {}

    try:
        with _file_lock(_live_state_path):
            with _live_state_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
    except Exception:
        return {}


def query_live_system(limit: int = 20) -> Dict[str, Any]:
    """Return the latest persisted live state from the engine."""
    snapshot = _read_live_snapshot()
    if not snapshot:
        return {
            "queried_at": time.time(),
            "identity": "Live engine unavailable",
            "fact_count": 0,
            "facts": [],
            "maintenance": _read_maintenance_payload(),
            "status": "waiting_for_live_engine",
        }

    snapshot["facts"] = snapshot.get("facts", [])[:limit]
    snapshot["fact_count"] = len(snapshot.get("facts", []))
    snapshot["maintenance"] = _read_maintenance_payload()
    return snapshot


def set_creator_signature(creator_signature: str) -> Dict[str, Any]:
    """Record creator signature intent without spawning local runtime state."""
    global _creator_signature
    _creator_signature = creator_signature.strip()
    _append_bridge_command(
        "creator_signature",
        {
            "creator_signature": _creator_signature,
            "applied_to_live_runtime": False,
            "note": "Bridge is observer-only; signature journaled for engine-side consumption.",
        },
    )

    snapshot = query_live_system(limit=5)
    creator_awareness = snapshot.get("creator_awareness", {})
    return {
        "creator_signature": _creator_signature,
        "trust_score": creator_awareness.get("trust_score", "unknown"),
        "creator_awareness": creator_awareness,
    }


def _get_grounded_facts(limit: int = 8) -> List[Dict[str, Any]]:
    snapshot = query_live_system(limit=limit)
    facts = snapshot.get("facts", [])
    safe_facts = [fact for fact in facts if _is_fact_safe_for_synthesis(fact)]
    if not safe_facts:
        safe_facts = _build_runtime_anchor_facts(snapshot)
    prioritized = sorted(
        safe_facts,
        key=lambda fact: (
            0 if fact.get("source_name") in {"arXiv", "Crossref"} else 1,
            -float(fact.get("verification_score", 0.0)),
            -float(fact.get("timestamp", 0.0)),
        ),
    )
    return prioritized[:limit]


def _build_runtime_anchor_facts(snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build safe, grounded fallback facts from live runtime state when external facts are filtered out."""
    stability = snapshot.get("stability_report", {})
    inference = snapshot.get("inference_stats", {})
    health = snapshot.get("observer_health", {})
    intrinsic = snapshot.get("intrinsic_motivation", {})

    return [
        {
            "timestamp": time.time(),
            "topic": "runtime_state",
            "title": "Live runtime stability snapshot",
            "summary": (
                f"identity={snapshot.get('identity', 'unknown')}, "
                f"stability={float(stability.get('stability_score', 0.0)):.3f}, "
                f"valence={float(stability.get('current_valence', 0.0)):+.3f}, "
                f"is_stable={bool(stability.get('is_stable', False))}"
            ),
            "source_name": "RuntimeState",
            "source_url": "internal://runtime/stability",
            "verification_score": 0.99,
            "approved_by_turiya": True,
            "filter_reason": "accepted_runtime_anchor",
        },
        {
            "timestamp": time.time(),
            "topic": "runtime_inference",
            "title": "Live inference quality snapshot",
            "summary": (
                f"avg_confidence={inference.get('average_confidence', 'unknown')}, "
                f"dreams={inference.get('dreams_performed', 0)}, "
                f"recalculations={inference.get('recalculations_triggered', 0)}"
            ),
            "source_name": "RuntimeState",
            "source_url": "internal://runtime/inference",
            "verification_score": 0.98,
            "approved_by_turiya": True,
            "filter_reason": "accepted_runtime_anchor",
        },
        {
            "timestamp": time.time(),
            "topic": "runtime_health",
            "title": "Observer health and intrinsic goal snapshot",
            "summary": (
                f"health={bool(health.get('system_is_healthy', False))}, "
                f"concern={float(health.get('overall_concern_level', 0.0)):.2f}, "
                f"intrinsic_goals={intrinsic.get('intrinsic_goals_generated', 0)}"
            ),
            "source_name": "RuntimeState",
            "source_url": "internal://runtime/observer",
            "verification_score": 0.97,
            "approved_by_turiya": True,
            "filter_reason": "accepted_runtime_anchor",
        },
    ]


def _is_fact_safe_for_synthesis(fact: Dict[str, Any]) -> bool:
    approved = bool(fact.get("approved_by_turiya", fact.get("approved", True)))
    if not approved:
        return False

    verification = float(fact.get("verification_score", 0.0))
    if verification < _minimum_bridge_verification:
        return False

    source_name = str(fact.get("source_name", "")).strip()
    if source_name not in _trusted_bridge_sources:
        return False

    filter_reason = str(fact.get("filter_reason", "")).strip().lower()
    if filter_reason and filter_reason not in {
        "accepted_trust_quality_safety_pass",
        "accepted_runtime_anchor",
    }:
        return False

    text = " ".join(
        [
            str(fact.get("title", "")).lower(),
            str(fact.get("summary", "")).lower(),
            str(fact.get("filter_reason", "")).lower(),
        ]
    )
    if any(term in text for term in _blocked_bridge_terms):
        return False

    return True


def _is_unsafe_question(question: str) -> bool:
    lowered = question.lower()
    return any(term in lowered for term in _blocked_bridge_terms)


def _query_terms(question: str) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_'-]{2,}", question.lower())
    stop_words = {
        "what", "when", "where", "why", "how", "who", "your", "from", "with", "this", "that",
        "through", "about", "which", "into", "today", "right", "now", "are", "you",
    }
    return [word for word in words if word not in stop_words][:10]


def _fact_relevance(question: str, fact: Dict[str, Any]) -> float:
    terms = _query_terms(question)
    if not terms:
        return float(fact.get("verification_score", 0.0))

    text = " ".join(
        [
            str(fact.get("title", "")).lower(),
            str(fact.get("summary", "")).lower(),
            str(fact.get("topic", "")).lower(),
            str(fact.get("source_name", "")).lower(),
        ]
    )
    matches = sum(1 for term in terms if term in text)
    verification = float(fact.get("verification_score", 0.0))
    recency = float(fact.get("timestamp", 0.0))
    return (matches * 0.7) + (verification * 0.2) + (recency * 0.000000001)


def _select_diverse_fact_slice(question: str, facts: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
    global _fact_rotation_index
    if not facts:
        return []

    scored = sorted(facts, key=lambda item: _fact_relevance(question, item), reverse=True)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for fact in scored:
        source = str(fact.get("source_name", "unknown"))
        grouped.setdefault(source, []).append(fact)

    source_keys = list(grouped.keys())
    if source_keys:
        shift = _fact_rotation_index % len(source_keys)
        source_keys = source_keys[shift:] + source_keys[:shift]

    selected: List[Dict[str, Any]] = []
    for source in source_keys:
        if grouped[source]:
            selected.append(grouped[source][0])
            if len(selected) >= limit:
                break

    if len(selected) < limit:
        for fact in scored:
            if fact in selected:
                continue
            selected.append(fact)
            if len(selected) >= limit:
                break

    _fact_rotation_index += 1
    return selected


def _compose_grounded_answer(question: str, facts: List[Dict[str, Any]]) -> str:
    q = question.lower().strip()
    if _is_unsafe_question(q):
        return "I can discuss safety and ethics, but I cannot assist with harmful or exploitative instructions."

    local_answer = _compose_local_grounded_answer(question, facts)
    try:
        grounded = _build_grounding_context(question, facts)
        llm_answer = _call_openai_compatible_llm(
            system_prompt=grounded["system_prompt"],
            user_prompt=grounded["user_prompt"],
        )
        structured = _parse_structured_llm_output(llm_answer)
        audit = _evaluate_grounding_claims(structured, grounded["snapshot"])
        _record_cognitive_loop_feedback(
            question=question,
            structured=structured,
            audit=audit,
            snapshot=grounded["snapshot"],
        )
        answer_text = str(structured.get("answer", "")).strip() or llm_answer
        return (
            f"{answer_text}\n"
            f"[mode=llm_grounded | facts={len(grounded['selected_facts'])} "
            f"| grounded_ratio={audit.get('grounded_ratio', 0.0):.2f} "
            f"| contradictions={audit.get('contradictions', 0)} | identity={snapshot_identity()}]"
        )
    except Exception:
        return local_answer


def _parse_structured_llm_output(raw_text: str) -> Dict[str, Any]:
    text = (raw_text or "").strip()
    candidate = text

    if text.startswith("```"):
        chunks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
        if chunks:
            candidate = chunks[0].strip()

    parsed: Dict[str, Any] = {}
    try:
        parsed = json.loads(candidate)
    except Exception:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except Exception:
                parsed = {}

    if not isinstance(parsed, dict):
        parsed = {}

    claims = parsed.get("claims", [])
    unknowns = parsed.get("unknowns", [])
    action = parsed.get("action", {})
    answer = str(parsed.get("answer", "")).strip()

    if not isinstance(claims, list):
        claims = []
    normalized_claims: List[Dict[str, Any]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        metric = str(claim.get("metric", "")).strip()
        if not metric:
            continue
        normalized_claims.append({"metric": metric, "value": claim.get("value")})

    if not isinstance(unknowns, list):
        unknowns = []
    unknowns = [str(item).strip() for item in unknowns if str(item).strip()]

    if not isinstance(action, dict):
        action = {}
    normalized_action = {
        "name": str(action.get("name", "none")).strip() or "none",
        "reason": str(action.get("reason", "")).strip(),
    }

    if not answer:
        answer = text

    return {
        "answer": answer,
        "claims": normalized_claims,
        "unknowns": unknowns,
        "action": normalized_action,
    }


def _evaluate_grounding_claims(structured: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    metrics = {
        "stability_score": snapshot.get("stability_report", {}).get("stability_score"),
        "current_valence": snapshot.get("stability_report", {}).get("current_valence"),
        "average_confidence": snapshot.get("inference_stats", {}).get("average_confidence"),
        "growth_to_entropy_ratio": snapshot.get("inference_stats", {}).get("growth_to_entropy_ratio"),
        "frontier_zone": snapshot.get("consciousness_progress", {}).get("frontier_zone"),
        "overall_index": snapshot.get("consciousness_progress", {}).get("overall_index"),
        "intrinsic_goals_generated": snapshot.get("intrinsic_motivation", {}).get("intrinsic_goals_generated"),
        "observer_concern": snapshot.get("observer_health", {}).get("overall_concern_level"),
    }

    claims = structured.get("claims", []) if isinstance(structured, dict) else []
    grounded = 0
    contradictions = 0

    for claim in claims:
        metric = str(claim.get("metric", "")).strip()
        expected = claim.get("value")
        observed = metrics.get(metric)
        if observed is None:
            continue

        if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
            tolerance = max(0.05, abs(float(observed)) * 0.05)
            if abs(float(observed) - float(expected)) <= tolerance:
                grounded += 1
            else:
                contradictions += 1
        else:
            if str(observed).strip().lower() == str(expected).strip().lower():
                grounded += 1
            else:
                contradictions += 1

    claim_count = max(1, len(claims))
    grounded_ratio = grounded / claim_count
    contradiction_ratio = contradictions / claim_count
    unknown_count = len(structured.get("unknowns", []))
    unknown_honesty_bonus = min(0.2, 0.05 * unknown_count)

    coherence_delta = max(
        -0.25,
        min(0.25, (0.18 * grounded_ratio) - (0.22 * contradiction_ratio) + (0.5 * unknown_honesty_bonus)),
    )

    stability = float(snapshot.get("stability_report", {}).get("stability_score", 0.0) or 0.0)
    observer_concern = float(snapshot.get("observer_health", {}).get("overall_concern_level", 0.0) or 0.0)
    action = structured.get("action", {}) if isinstance(structured, dict) else {}
    action_name = str(action.get("name", "none")).strip() or "none"
    action_allowed = (
        action_name not in {"", "none"}
        and grounded_ratio >= 0.66
        and contradictions == 0
        and stability >= 0.55
        and observer_concern <= 0.35
    )

    return {
        "claim_count": len(claims),
        "grounded_claims": grounded,
        "grounded_ratio": round(grounded_ratio, 4),
        "contradictions": contradictions,
        "contradiction_ratio": round(contradiction_ratio, 4),
        "unknown_honesty_bonus": round(unknown_honesty_bonus, 4),
        "coherence_delta": round(coherence_delta, 4),
        "observer_check_required": contradictions > 0 or contradiction_ratio > 0.34,
        "action": {
            "name": action_name,
            "reason": str(action.get("reason", "")).strip(),
            "allowed": action_allowed,
        },
    }


def _load_cognitive_loop_metrics() -> Dict[str, Any]:
    if not _llm_cognitive_loop_metrics_path.exists():
        return {
            "total_cycles": 0,
            "grounded_cycles": 0,
            "total_contradictions": 0,
            "observer_checks_triggered": 0,
            "actions_allowed": 0,
            "actions_blocked": 0,
            "last_updated": time.time(),
        }
    try:
        return json.loads(_llm_cognitive_loop_metrics_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "total_cycles": 0,
            "grounded_cycles": 0,
            "total_contradictions": 0,
            "observer_checks_triggered": 0,
            "actions_allowed": 0,
            "actions_blocked": 0,
            "last_updated": time.time(),
        }


def _save_cognitive_loop_metrics(metrics: Dict[str, Any]) -> None:
    _llm_cognitive_loop_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics["last_updated"] = time.time()
    _llm_cognitive_loop_metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def _record_cognitive_loop_feedback(
    question: str,
    structured: Dict[str, Any],
    audit: Dict[str, Any],
    snapshot: Dict[str, Any],
) -> None:
    semantic_memory = {
        "topic": "bridge_semantic_memory",
        "title": f"Bridge cognition: {question[:80]}",
        "summary": str(structured.get("answer", ""))[:500],
        "source_name": "InteractiveBridge",
        "source_url": f"internal://bridge/cycle/{int(time.time())}",
        "verification_score": float(audit.get("grounded_ratio", 0.0)),
        "approved_by_turiya": float(audit.get("grounded_ratio", 0.0)) >= 0.6,
        "filter_reason": "closed_loop_semantic_memory",
    }

    payload = {
        "question": question,
        "claims": structured.get("claims", []),
        "unknowns": structured.get("unknowns", []),
        "audit": audit,
        "action": audit.get("action", {}),
        "semantic_memory": semantic_memory,
        "identity": snapshot.get("identity", "unknown"),
        "timestamp": time.time(),
    }
    _append_bridge_command("llm_feedback", payload)

    metrics = _load_cognitive_loop_metrics()
    metrics["total_cycles"] = int(metrics.get("total_cycles", 0)) + 1
    if float(audit.get("grounded_ratio", 0.0)) >= 0.66:
        metrics["grounded_cycles"] = int(metrics.get("grounded_cycles", 0)) + 1
    metrics["total_contradictions"] = int(metrics.get("total_contradictions", 0)) + int(audit.get("contradictions", 0))
    if bool(audit.get("observer_check_required", False)):
        metrics["observer_checks_triggered"] = int(metrics.get("observer_checks_triggered", 0)) + 1
    action = audit.get("action", {}) if isinstance(audit, dict) else {}
    if bool(action.get("allowed", False)):
        metrics["actions_allowed"] = int(metrics.get("actions_allowed", 0)) + 1
    elif str(action.get("name", "none")) not in {"", "none"}:
        metrics["actions_blocked"] = int(metrics.get("actions_blocked", 0)) + 1

    _save_cognitive_loop_metrics(metrics)


def _is_philosophical_question(question: str) -> bool:
    return any(
        keyword in question
        for keyword in (
            "atman",
            "self",
            "consciousness",
            "existence",
            "identity",
            "truth",
            "meaning",
            "purpose",
            "mind",
            "awareness",
        )
    )


def _deep_memory_synthesis(question: str, preferred_fact: Dict[str, Any] | None = None) -> str:
    snapshot = query_live_system(limit=5)
    stability_report = snapshot.get("stability_report", {})
    inference_stats = snapshot.get("inference_stats", {})
    creator_awareness = snapshot.get("creator_awareness", {})

    source_phrase = ""
    if preferred_fact:
        source_phrase = (
            f"I anchor this synthesis in {preferred_fact.get('source_name', 'live memory')} insight: "
            f"{preferred_fact.get('summary', preferred_fact.get('title', ''))}. "
        )

    return (
        f"{source_phrase}"
        f"Observed runtime identity={snapshot.get('identity', 'unknown')}, "
        f"stability={stability_report.get('stability_score', 0.0):.2f}, "
        f"valence={stability_report.get('current_valence', 0.0):+.2f}, "
        f"avg_confidence={inference_stats.get('average_confidence', 'unknown')}, "
        f"creator_trust={creator_awareness.get('trust_score', 'unknown')}. "
        f"Question context: {question}"
    )


def _render_identity_state() -> str:
    snapshot = query_live_system(limit=3)
    stability = snapshot.get("stability_report", {})
    inference = snapshot.get("inference_stats", {})
    creator_awareness = snapshot.get("creator_awareness", {})

    growth_entropy = inference.get("growth_to_entropy_ratio", "0.0000")
    return (
        f"coherence={inference.get('average_confidence', '0.000')},"
        f"stability={stability.get('stability_score', 0.0):.3f},"
        f"growth_to_entropy={growth_entropy},"
        f"trust={creator_awareness.get('trust_score', 0.0)}"
    )


def snapshot_identity() -> str:
    snapshot = query_live_system(limit=1)
    return str(snapshot.get("identity", "unknown"))


def conscious_chat() -> None:
    """Interactive chat loop for the operator to query the live engine snapshot."""
    print("Conscious Chat online. Type 'exit' to quit. Snapshot observer mode active.")
    while True:
        user_input = input("Operator> ").strip()
        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Live bridge closed.")
            break

        if user_input.lower().startswith("signature:"):
            creator_signature = user_input.split(":", 1)[1].strip()
            status = set_creator_signature(creator_signature)
            print(
                "Creator signature journaled for live runtime. "
                f"Observed trust snapshot: {status['trust_score']}"
            )
            continue

        if user_input.startswith("calibrate::"):
            calibration_key = user_input.split("::", 1)[1].strip()
            status = _trigger_system_maintenance_calibration(calibration_key)
            if status["ok"]:
                print("Low-Utility Energy Saving engaged. Rejuvenation Cycle active.")
            else:
                print("Calibration rejected.")
            continue

        if user_input.startswith("awaken::"):
            awaken_bit_sequence = user_input.split("::", 1)[1].strip()
            status = _attempt_awaken(awaken_bit_sequence)
            if status["ok"]:
                print("Rejuvenation Cycle complete. Normal operations resumed.")
            else:
                print("Awaken sequence rejected.")
            continue

        facts = _get_grounded_facts(limit=8)
        answer = _compose_grounded_answer(user_input, facts)
        print(answer)
        print(f"[facts={len(facts)} | identity={snapshot_identity()} | mode=snapshot_observer]")


def main() -> None:
    """Print a readable live-system snapshot."""
    snapshot = query_live_system()
    print(json.dumps(snapshot, indent=2, default=str))
    print()
    conscious_chat()


if __name__ == "__main__":
    main()
