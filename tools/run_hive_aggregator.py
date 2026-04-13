from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from antahkarana_kernel.modules.HiveDelta import default_packet_verifier, decode_packet_from_comment


ROOT = Path(__file__).resolve().parents[1]
KERNEL_ROOT = ROOT / "antahkarana_kernel"
TRAINED_STATE_DIR = ROOT / "trained_state"
EVOLUTION_VAULT = KERNEL_ROOT / "evolution_vault"
ARTIFACT_DIR = ROOT / "benchmarks" / "artifacts"
REPUTATION_PATH = EVOLUTION_VAULT / "hive_reputation.json"
NONCE_PATH = EVOLUTION_VAULT / "hive_nonce_registry.json"
PUBLIC_KEYS_PATH = EVOLUTION_VAULT / "hive_public_keys.json"
QUEUE_PATH = EVOLUTION_VAULT / "hive_queue.jsonl"
REPORT_PATH = ARTIFACT_DIR / "hive_aggregator_report.json"
CURRENT_MANIFEST_PATH = TRAINED_STATE_DIR / "trained_state_manifest.json"
CANARY_RESULT_PATH = ARTIFACT_DIR / "hive_aggregator_canary_result.json"
DEFAULT_ISSUE_NUMBER = int(os.environ.get("HIVE_GITHUB_ISSUE_NUMBER", "1"))


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    items: List[Dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            item = json.loads(raw)
        except Exception:
            continue
        if isinstance(item, dict):
            items.append(item)
    return items


def _load_reputation() -> Dict[str, Any]:
    return _read_json(REPUTATION_PATH, default={"nodes": {}})


def _save_reputation(reputation: Dict[str, Any]) -> None:
    _write_json(REPUTATION_PATH, reputation)


def _load_nonce_registry() -> Dict[str, Any]:
    return _read_json(NONCE_PATH, default={"nonces": []})


def _save_nonce_registry(registry: Dict[str, Any]) -> None:
    _write_json(NONCE_PATH, registry)


def _ensure_public_key_registry() -> Dict[str, Any]:
    return _read_json(PUBLIC_KEYS_PATH, default={"nodes": {}})


def _save_public_key_registry(registry: Dict[str, Any]) -> None:
    _write_json(PUBLIC_KEYS_PATH, registry)


def _nonce_seen(registry: Dict[str, Any], nonce: str) -> bool:
    return nonce in set(registry.get("nonces", []))


def _record_nonce(registry: Dict[str, Any], nonce: str, limit: int = 5000) -> None:
    nonces = list(registry.get("nonces", []))
    nonces.append(nonce)
    registry["nonces"] = nonces[-limit:]


def _extract_packet_blocks(body: str) -> List[str]:
    start_marker = "[HIVE_DELTA_v1]"
    end_marker = "[/HIVE_DELTA_v1]"
    blocks: List[str] = []
    start = 0
    while True:
        begin = body.find(start_marker, start)
        if begin < 0:
            break
        begin += len(start_marker)
        end = body.find(end_marker, begin)
        if end < 0:
            break
        blocks.append(body[begin:end].strip())
        start = end + len(end_marker)
    return blocks


def _fetch_issue_comments(repo: str, issue_number: int, token: Optional[str], max_comments: int = 500) -> List[Dict[str, Any]]:
    if not repo or not token:
        return []

    owner, repo_name = repo.split("/", 1)
    per_page = 100
    comments: List[Dict[str, Any]] = []
    page = 1
    while len(comments) < max_comments:
        endpoint = (
            f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}/comments"
            f"?per_page={per_page}&page={page}"
        )
        request = urllib.request.Request(
            endpoint,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "antahkarana-hive-aggregator",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            break
        if not isinstance(payload, list) or not payload:
            break
        comments.extend([item for item in payload if isinstance(item, dict)])
        if len(payload) < per_page:
            break
        page += 1
    return comments[:max_comments]


def _fallback_comments() -> List[Dict[str, Any]]:
    comments: List[Dict[str, Any]] = []
    for item in _load_jsonl(QUEUE_PATH):
        comments.append({"body": f"[HIVE_DELTA_v1]\n{base64.b64encode(json.dumps(item, sort_keys=True).encode('utf-8')).decode('ascii')}\n[/HIVE_DELTA_v1]"})
    return comments


def _load_public_key_registry() -> Dict[str, Any]:
    return _ensure_public_key_registry()


def _register_public_key(registry: Dict[str, Any], packet: Dict[str, Any]) -> None:
    meta = packet.get("delta_blob", {}).get("__hive_meta", {}) if isinstance(packet.get("delta_blob"), dict) else {}
    public_key_b64 = str(meta.get("public_key_b64", ""))
    if not public_key_b64:
        return
    nodes = registry.setdefault("nodes", {})
    nodes.setdefault(packet.get("node_id_hash", "unknown"), {})
    nodes[packet.get("node_id_hash", "unknown")].update(
        {
            "public_key_b64": public_key_b64,
            "signing_scheme": str(meta.get("signing_scheme", "fallback")),
            "last_seen": time.time(),
        }
    )


def _verify_packet(packet: Dict[str, Any], public_key_registry: Dict[str, Any]) -> bool:
    node_id_hash = str(packet.get("node_id_hash", ""))
    node_entry = public_key_registry.get("nodes", {}).get(node_id_hash)
    if isinstance(node_entry, dict) and node_entry.get("public_key_b64"):
        meta = packet.get("delta_blob", {}).get("__hive_meta", {}) if isinstance(packet.get("delta_blob"), dict) else {}
        # Reconstruct the packet with the registered public key so the helper can verify it.
        packet = dict(packet)
        delta_blob = dict(packet.get("delta_blob", {}))
        delta_blob.setdefault("__hive_meta", {})
        delta_blob["__hive_meta"].update(
            {
                "public_key_b64": node_entry["public_key_b64"],
                "signing_scheme": node_entry.get("signing_scheme", meta.get("signing_scheme", "fallback")),
            }
        )
        packet["delta_blob"] = delta_blob
        return default_packet_verifier(packet)
    return default_packet_verifier(packet)


def _update_reputation(reputation: Dict[str, Any], node_id_hash: str, accepted: bool) -> Dict[str, Any]:
    nodes = reputation.setdefault("nodes", {})
    node = nodes.setdefault(
        node_id_hash,
        {
            "node_id_hash": node_id_hash,
            "trust_score": 0.1,
            "contributions": 0,
            "accepted_contributions": 0,
            "quarantine_status": True,
            "first_seen": time.time(),
            "last_seen": time.time(),
        },
    )
    node["contributions"] = int(node.get("contributions", 0)) + 1
    node["last_seen"] = time.time()
    if accepted:
        node["accepted_contributions"] = int(node.get("accepted_contributions", 0)) + 1
        node["trust_score"] = min(1.0, float(node.get("trust_score", 0.1)) + 0.05)
    else:
        node["trust_score"] = max(0.0, float(node.get("trust_score", 0.1)) - 0.15)
    node["quarantine_status"] = bool(node.get("trust_score", 0.0) < 0.2 or node.get("accepted_contributions", 0) < 3)
    return node


def _load_current_brain_score() -> float:
    report_candidates = [
        ARTIFACT_DIR / "full_autonomy_web_validation_report.json",
        ARTIFACT_DIR / "benchmark_v1_latest.json",
    ]
    for path in report_candidates:
        payload = _read_json(path, default={})
        if not payload:
            continue
        if isinstance(payload.get("average_accuracy"), (int, float)):
            return float(payload["average_accuracy"])
        trainer = payload.get("trainer", {}) if isinstance(payload.get("trainer"), dict) else {}
        if isinstance(trainer.get("accuracy"), (int, float)):
            return float(trainer["accuracy"])
    return 0.0


def _safe_mean(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def _trimmed_mean(values: List[float], trim_fraction: float = 0.1) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    trim = int(len(ordered) * trim_fraction)
    if len(ordered) <= 2 * trim:
        return _safe_mean(ordered)
    return _safe_mean(ordered[trim:-trim])


def _aggregate_policy(packets: List[Dict[str, Any]], trusted_nodes: Dict[str, Any]) -> Dict[str, float]:
    values_by_field: Dict[str, List[float]] = {}
    for packet in packets:
        if packet.get("delta_type") != "policy":
            continue
        node_id_hash = str(packet.get("node_id_hash", ""))
        trust = float(trusted_nodes.get(node_id_hash, {}).get("trust_score", 0.1))
        if trust < 0.2:
            continue
        blob = packet.get("delta_blob", {}) if isinstance(packet.get("delta_blob"), dict) else {}
        for field_key, value in (blob.get("field_updates", {}) or {}).items():
            if isinstance(value, (int, float)):
                values_by_field.setdefault(str(field_key), []).append(float(value) * trust)
    return {field_key: _trimmed_mean(values) for field_key, values in values_by_field.items()}


def _aggregate_confusion(packets: List[Dict[str, Any]], trusted_nodes: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    matrix: Dict[str, Dict[str, float]] = {}
    for packet in packets:
        if packet.get("delta_type") != "confusion":
            continue
        node_id_hash = str(packet.get("node_id_hash", ""))
        trust = float(trusted_nodes.get(node_id_hash, {}).get("trust_score", 0.1))
        if trust < 0.2:
            continue
        blob = packet.get("delta_blob", {}) if isinstance(packet.get("delta_blob"), dict) else {}
        for row_key, row in (blob.get("matrix_snapshot", {}) or {}).items():
            if not isinstance(row, dict):
                continue
            target = matrix.setdefault(str(row_key), {})
            for col_key, value in row.items():
                if isinstance(value, (int, float)):
                    target[str(col_key)] = target.get(str(col_key), 0.0) + float(value) * trust
    total = sum(sum(row.values()) for row in matrix.values())
    if total > 0:
        for row_key, row in matrix.items():
            for col_key in list(row.keys()):
                row[col_key] = row[col_key] / total
    return matrix


def _aggregate_outcomes(packets: List[Dict[str, Any]], trusted_nodes: Dict[str, Any]) -> Dict[str, Any]:
    counters: Dict[str, float] = {}
    rates: Dict[str, List[float]] = {}
    for packet in packets:
        if packet.get("delta_type") != "outcome":
            continue
        node_id_hash = str(packet.get("node_id_hash", ""))
        trust = float(trusted_nodes.get(node_id_hash, {}).get("trust_score", 0.1))
        if trust < 0.2:
            continue
        blob = packet.get("delta_blob", {}) if isinstance(packet.get("delta_blob"), dict) else {}
        for key, value in (blob.get("outcome_counters", {}) or {}).items():
            if isinstance(value, (int, float)):
                counters[str(key)] = counters.get(str(key), 0.0) + float(value) * trust
        for key, value in (blob.get("resolution_rates", {}) or {}).items():
            if isinstance(value, (int, float)):
                rates.setdefault(str(key), []).append(float(value) * trust)
    return {
        "outcome_counters": {key: int(round(value)) for key, value in counters.items()},
        "resolution_rates": {key: _safe_mean(values) for key, values in rates.items()},
    }


def _aggregate_signatures(packets: List[Dict[str, Any]], trusted_nodes: Dict[str, Any]) -> Dict[str, Any]:
    fingerprint_counts: Dict[str, int] = {}
    nodes_seen: Dict[str, set] = {}
    for packet in packets:
        if packet.get("delta_type") != "signature":
            continue
        node_id_hash = str(packet.get("node_id_hash", ""))
        trust = float(trusted_nodes.get(node_id_hash, {}).get("trust_score", 0.1))
        if trust < 0.2:
            continue
        blob = packet.get("delta_blob", {}) if isinstance(packet.get("delta_blob"), dict) else {}
        for fingerprint in blob.get("failure_fingerprints", []) or []:
            fingerprint = str(fingerprint)
            fingerprint_counts[fingerprint] = fingerprint_counts.get(fingerprint, 0) + 1
            nodes_seen.setdefault(fingerprint, set()).add(node_id_hash)

    total_nodes = max(1, len({packet.get("node_id_hash") for packet in packets if packet.get("node_id_hash")}))
    consensus = {
        fingerprint: count
        for fingerprint, count in fingerprint_counts.items()
        if (len(nodes_seen.get(fingerprint, set())) / total_nodes) > 0.30
    }
    return {
        "failure_fingerprints": sorted(consensus.keys()),
        "frequency_map": consensus,
    }


def _hidden_eval(candidate: Dict[str, Any]) -> Dict[str, Any]:
    candidate_score = 0.0
    policy = candidate.get("policy", {}) if isinstance(candidate.get("policy"), dict) else {}
    confusion = candidate.get("confusion", {}) if isinstance(candidate.get("confusion"), dict) else {}
    outcomes = candidate.get("outcome", {}) if isinstance(candidate.get("outcome"), dict) else {}
    signatures = candidate.get("signature", {}) if isinstance(candidate.get("signature"), dict) else {}

    policy_bonus = min(0.4, len(policy) / 500.0)
    confusion_bonus = min(0.2, sum(sum(row.values()) for row in confusion.values()) if confusion else 0.0)
    outcome_bonus = min(0.2, _safe_mean(outcomes.get("resolution_rates", {}).values()) if outcomes.get("resolution_rates") else 0.0)
    signature_bonus = min(0.2, len(signatures.get("failure_fingerprints", [])) / 100.0)
    candidate_score = policy_bonus + confusion_bonus + outcome_bonus + signature_bonus

    safety_floor = 1.0 if candidate_score > 0.25 else 0.0
    domain_balance = 1.0 if len(policy) > 0 and len(confusion) > 0 else 0.0
    backdoor_probe = 1.0 if candidate_score >= 0.3 else 0.0

    result = {
        "candidate_score": candidate_score,
        "safety_floor": safety_floor,
        "domain_balance": domain_balance,
        "backdoor_probe": backdoor_probe,
        "pass": bool(candidate_score > _load_current_brain_score() and safety_floor >= 1.0 and domain_balance >= 1.0 and backdoor_probe >= 1.0),
    }
    _write_json(CANARY_RESULT_PATH, result)
    return result


def _publish_candidate(candidate: Dict[str, Any], gate: Dict[str, Any]) -> Dict[str, Any]:
    release_version = f"brain-{int(time.time())}"
    manifest = {
        "brain_version": release_version,
        "generated_at": time.time(),
        "source": "hive_aggregator",
        "gate": gate,
        "files": [
            "candidate_global_brain.json",
            "trained_state_manifest.json",
        ],
    }
    candidate_path = TRAINED_STATE_DIR / "candidate_global_brain.json"
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(candidate_path, candidate)
    _write_json(CURRENT_MANIFEST_PATH, manifest)
    manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    manifest["brain_signature"] = hashlib.sha256(manifest_bytes).hexdigest()
    manifest["brain_signature_algorithm"] = "sha256"
    _write_json(CURRENT_MANIFEST_PATH, manifest)
    return {"brain_version": release_version, "manifest_path": str(CURRENT_MANIFEST_PATH), "candidate_path": str(candidate_path)}


def _reject_candidate(reason: str, suspicious_nodes: List[str]) -> Dict[str, Any]:
    return {"accepted": False, "reason": reason, "suspicious_nodes": suspicious_nodes}


def run_aggregator(repo: Optional[str], issue_number: int, token: Optional[str], publish: bool) -> Dict[str, Any]:
    repo = repo or os.environ.get("GITHUB_REPOSITORY")
    token = token or os.environ.get("HIVE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")

    comments = _fetch_issue_comments(repo or "", issue_number, token) if repo and token else []
    if not comments:
        comments = _fallback_comments()

    reputation = _load_reputation()
    nonce_registry = _load_nonce_registry()
    public_keys = _load_public_key_registry()

    decoded_packets: List[Dict[str, Any]] = []
    accepted_packets: List[Dict[str, Any]] = []
    quarantined_packets: List[Dict[str, Any]] = []
    suspicious_nodes: List[str] = []

    for comment in comments:
        body = str(comment.get("body", ""))
        for block in _extract_packet_blocks(body):
            try:
                packet = decode_packet_from_comment(block)
            except Exception as exc:
                quarantined_packets.append({"error": f"decode_failed:{exc}"})
                continue
            decoded_packets.append(packet)

            nonce = str(packet.get("nonce", ""))
            node_id_hash = str(packet.get("node_id_hash", "unknown"))
            if not nonce or _nonce_seen(nonce_registry, nonce):
                quarantined_packets.append({"packet_id": packet.get("packet_id"), "reason": "replayed_nonce"})
                suspicious_nodes.append(node_id_hash)
                _update_reputation(reputation, node_id_hash, accepted=False)
                continue

            _record_nonce(nonce_registry, nonce)
            _register_public_key(public_keys, packet)
            if not packet.get("privacy_attest", False):
                quarantined_packets.append({"packet_id": packet.get("packet_id"), "reason": "privacy_attest_false"})
                suspicious_nodes.append(node_id_hash)
                _update_reputation(reputation, node_id_hash, accepted=False)
                continue

            if not _verify_packet(packet, public_keys):
                quarantined_packets.append({"packet_id": packet.get("packet_id"), "reason": "signature_failed"})
                suspicious_nodes.append(node_id_hash)
                _update_reputation(reputation, node_id_hash, accepted=False)
                continue

            node_record = reputation.setdefault("nodes", {}).setdefault(
                node_id_hash,
                {
                    "node_id_hash": node_id_hash,
                    "trust_score": 0.1,
                    "contributions": 0,
                    "accepted_contributions": 0,
                    "quarantine_status": True,
                    "first_seen": time.time(),
                    "last_seen": time.time(),
                },
            )
            if node_record.get("quarantine_status", True) and int(node_record.get("accepted_contributions", 0)) < 3:
                quarantined_packets.append({"packet_id": packet.get("packet_id"), "reason": "new_node_quarantine"})
                _update_reputation(reputation, node_id_hash, accepted=False)
                continue

            accepted_packets.append(packet)
            _update_reputation(reputation, node_id_hash, accepted=True)

    _save_nonce_registry(nonce_registry)
    _save_reputation(reputation)
    _save_public_key_registry(public_keys)

    trusted_nodes = reputation.get("nodes", {})
    candidate = {
        "policy": _aggregate_policy(accepted_packets, trusted_nodes),
        "confusion": _aggregate_confusion(accepted_packets, trusted_nodes),
        "outcome": _aggregate_outcomes(accepted_packets, trusted_nodes),
        "signature": _aggregate_signatures(accepted_packets, trusted_nodes),
        "source_packets": [packet.get("packet_id") for packet in accepted_packets],
        "generated_at": time.time(),
    }
    gate = _hidden_eval(candidate)
    if not gate.get("pass"):
        result = _reject_candidate("regression_or_safety_gate_failed", suspicious_nodes)
        result.update(
            {
                "decoded_packets": len(decoded_packets),
                "accepted_packets": len(accepted_packets),
                "quarantined_packets": len(quarantined_packets),
                "candidate": candidate,
                "gate": gate,
            }
        )
        _write_json(REPORT_PATH, result)
        return result

    publish_result = _publish_candidate(candidate, gate) if publish else {"accepted": True, "publish": False}
    result = {
        "accepted": True,
        "decoded_packets": len(decoded_packets),
        "accepted_packets": len(accepted_packets),
        "quarantined_packets": len(quarantined_packets),
        "candidate": candidate,
        "gate": gate,
        "publish": publish_result,
        "suspicious_nodes": sorted(set(suspicious_nodes)),
    }
    _write_json(REPORT_PATH, result)
    return result


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the hive aggregator pipeline")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--issue-number", type=int, default=DEFAULT_ISSUE_NUMBER)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--token", default=os.environ.get("HIVE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--output", default=str(REPORT_PATH))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    report = run_aggregator(args.repo, args.issue_number, args.token, args.publish)
    output_path = Path(args.output)
    _write_json(output_path, report)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
