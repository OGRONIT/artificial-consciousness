from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .HiveConsent import consent_allows_hive, load_or_create_identity
from .HiveDelta import (
    ConfusionDelta,
    DeltaType,
    HivePacket,
    NodeCredentials,
    OutcomeDelta,
    PatternSignatureDelta,
    PythonPolicyDelta,
    build_hive_packet,
    decode_packet_from_comment,
    encode_packet_for_comment,
)


class EvolutionSync:
    """Collect local learning deltas and publish them to the hive relay."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.kernel_root = self.repo_root / "antahkarana_kernel"
        self.evolution_vault = self.kernel_root / "evolution_vault"
        self.trained_state = self.repo_root / "trained_state"
        self.queue_path = self.evolution_vault / "hive_queue.jsonl"
        self.last_upload_path = self.evolution_vault / "hive_last_upload.json"
        self.last_config_snapshot_path = self.evolution_vault / "hive_last_config_snapshot.json"
        self.last_conflict_snapshot_path = self.evolution_vault / "hive_last_conflict_snapshot.json"
        self.last_outcome_snapshot_path = self.evolution_vault / "hive_last_outcome_snapshot.json"
        self.last_signature_snapshot_path = self.evolution_vault / "hive_last_signature_snapshot.json"

    def should_sync(self, avg_learning_value: float) -> bool:
        if not consent_allows_hive():
            return False
        if avg_learning_value <= float(os.environ.get("ANTAHKARANA_HIVE_MIN_AVG_LEARNING", "0.5")):
            return False
        if not self._enough_time_since_last_upload():
            return False
        return True

    def _enough_time_since_last_upload(self) -> bool:
        if not self.last_upload_path.exists():
            return True
        try:
            last_upload = json.loads(self.last_upload_path.read_text(encoding="utf-8"))
            last_ts = float(last_upload.get("uploaded_at", 0.0))
        except Exception:
            return True
        return (time.time() - last_ts) >= float(os.environ.get("ANTAHKARANA_HIVE_MIN_UPLOAD_INTERVAL_SECS", "3600"))

    def _read_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    def _read_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        records: List[Dict[str, Any]] = []
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                item = json.loads(raw)
            except Exception:
                continue
            if isinstance(item, dict):
                records.append(item)
        return records

    def _flatten_numeric_fields(self, payload: Any, prefix: str = "") -> Dict[str, float]:
        flattened: Dict[str, float] = {}
        if isinstance(payload, dict):
            for key, value in payload.items():
                next_prefix = f"{prefix}.{key}" if prefix else str(key)
                if isinstance(value, bool):
                    flattened[next_prefix] = float(int(value))
                elif isinstance(value, (int, float)):
                    flattened[next_prefix] = float(value)
                elif isinstance(value, dict):
                    flattened.update(self._flatten_numeric_fields(value, prefix=next_prefix))
                elif isinstance(value, list):
                    for index, item in enumerate(value):
                        flattened.update(self._flatten_numeric_fields(item, prefix=f"{next_prefix}[{index}]"))
        return flattened

    def _diff_numeric_fields(self, current: Dict[str, float], baseline: Dict[str, float]) -> Dict[str, float]:
        diff: Dict[str, float] = {}
        for key, value in current.items():
            previous = baseline.get(key)
            if previous is None or abs(previous - value) > 1e-12:
                diff[key] = float(value)
        return diff

    def _load_conflict_snapshot(self) -> Dict[str, Any]:
        candidates = [
            self.kernel_root / "conflict_resolution_state.json",
            self.trained_state / "conflict_resolution_state.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                payload = self._read_json(candidate)
                if payload:
                    return payload
        return {}

    def _load_config_snapshot(self) -> Dict[str, Any]:
        return self._read_json(self.kernel_root / "config.json")

    def _load_training_summary(self) -> Dict[str, Any]:
        candidates = [
            self.trained_state / "trained_state_manifest.json",
            self.repo_root / "benchmarks" / "artifacts" / "full_autonomy_web_validation_report.json",
            self.repo_root / "benchmarks" / "artifacts" / "benchmark_v1_latest.json",
        ]
        for candidate in candidates:
            payload = self._read_json(candidate)
            if payload:
                return payload
        return {}

    def _load_previous_snapshot(self, path: Path) -> Dict[str, float]:
        return self._read_json(path) if path.exists() else {}

    def _load_credentials(self) -> Optional[NodeCredentials]:
        return load_or_create_identity()

    def _load_failure_fingerprints(self, limit: int = 50) -> List[str]:
        failure_log = self.evolution_vault / "Failure_Log.jsonl"
        if not failure_log.exists():
            return []

        fingerprints: List[str] = []
        for raw in failure_log.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]:
            raw = raw.strip()
            if not raw:
                continue
            fingerprints.append(base64.b16encode(raw.encode("utf-8")).decode("ascii")[:32].lower())
        return fingerprints

    def _build_policy_delta(self, node_id_hash: str, base_version: str) -> PythonPolicyDelta:
        current = self._flatten_numeric_fields(self._load_config_snapshot())
        baseline = self._load_previous_snapshot(self.last_config_snapshot_path)
        diff = self._diff_numeric_fields(current, baseline)
        return PythonPolicyDelta(
            node_id_hash=node_id_hash,
            base_version=base_version,
            field_updates=diff,
        )

    def _build_confusion_delta(self, node_id_hash: str, base_version: str) -> ConfusionDelta:
        conflict = self._load_conflict_snapshot()
        matrix = conflict.get("confusion_matrix") or conflict.get("matrix_snapshot") or {}
        domain_tags = conflict.get("domain_tags") or conflict.get("domains") or []
        if not isinstance(matrix, dict):
            matrix = {}
        if not isinstance(domain_tags, list):
            domain_tags = []
        return ConfusionDelta(
            node_id_hash=node_id_hash,
            base_version=base_version,
            matrix_snapshot=matrix,
            domain_tags=[str(tag) for tag in domain_tags],
        )

    def _build_outcome_delta(self, node_id_hash: str, base_version: str) -> OutcomeDelta:
        conflict = self._load_conflict_snapshot()
        counters = conflict.get("outcome_counters") or conflict.get("outcomes") or conflict.get("counts") or {}
        rates = conflict.get("resolution_rates") or conflict.get("rates") or {}
        if not isinstance(counters, dict):
            counters = {}
        if not isinstance(rates, dict):
            rates = {}
        normalized_counters = {str(key): int(value) for key, value in counters.items() if isinstance(value, (int, float))}
        normalized_rates = {str(key): float(value) for key, value in rates.items() if isinstance(value, (int, float))}
        return OutcomeDelta(
            node_id_hash=node_id_hash,
            base_version=base_version,
            outcome_counters=normalized_counters,
            resolution_rates=normalized_rates,
        )

    def _build_signature_delta(self, node_id_hash: str, base_version: str) -> PatternSignatureDelta:
        conflict = self._load_conflict_snapshot()
        fingerprints = conflict.get("failure_fingerprints") or self._load_failure_fingerprints()
        frequency_map = conflict.get("frequency_map") or {}
        if not isinstance(fingerprints, list):
            fingerprints = []
        if not isinstance(frequency_map, dict):
            frequency_map = {}
        normalized_frequency_map = {str(key): int(value) for key, value in frequency_map.items() if isinstance(value, (int, float))}
        return PatternSignatureDelta(
            node_id_hash=node_id_hash,
            base_version=base_version,
            failure_fingerprints=[str(item) for item in fingerprints],
            frequency_map=normalized_frequency_map,
        )

    def build_packets(
        self,
        engine_version: Optional[str] = None,
        base_brain_version: Optional[str] = None,
        local_eval_metrics: Optional[Dict[str, float]] = None,
    ) -> List[HivePacket]:
        credentials = self._load_credentials()
        if credentials is None:
            return []

        summary = self._load_training_summary()
        engine_version = engine_version or str(summary.get("identity") or summary.get("report") or "unknown")
        base_brain_version = base_brain_version or str(summary.get("brain_version") or summary.get("generated_at") or "0")
        local_eval_metrics = local_eval_metrics or self._extract_local_eval_metrics(summary)

        packets = [
            build_hive_packet(
                self._build_policy_delta(credentials.node_id_hash, base_brain_version),
                DeltaType.POLICY,
                credentials,
                engine_version=engine_version,
                base_brain_version=base_brain_version,
                domain_tags=["policy"],
                local_eval_metrics=local_eval_metrics,
            ),
            build_hive_packet(
                self._build_confusion_delta(credentials.node_id_hash, base_brain_version),
                DeltaType.CONFUSION,
                credentials,
                engine_version=engine_version,
                base_brain_version=base_brain_version,
                domain_tags=["confusion"],
                local_eval_metrics=local_eval_metrics,
            ),
            build_hive_packet(
                self._build_outcome_delta(credentials.node_id_hash, base_brain_version),
                DeltaType.OUTCOME,
                credentials,
                engine_version=engine_version,
                base_brain_version=base_brain_version,
                domain_tags=["outcome"],
                local_eval_metrics=local_eval_metrics,
            ),
            build_hive_packet(
                self._build_signature_delta(credentials.node_id_hash, base_brain_version),
                DeltaType.SIGNATURE,
                credentials,
                engine_version=engine_version,
                base_brain_version=base_brain_version,
                domain_tags=["signature"],
                local_eval_metrics=local_eval_metrics,
            ),
        ]
        return packets

    def _extract_local_eval_metrics(self, summary: Dict[str, Any]) -> Dict[str, float]:
        metrics: Dict[str, float] = {}
        trainer = summary.get("trainer", {}) if isinstance(summary.get("trainer"), dict) else {}
        memory_after = summary.get("memory_after", {}) if isinstance(summary.get("memory_after"), dict) else {}
        if isinstance(trainer.get("accuracy"), (int, float)):
            metrics["accuracy"] = float(trainer["accuracy"])
        if isinstance(trainer.get("loss"), (int, float)):
            metrics["loss"] = float(trainer["loss"])
        if isinstance(memory_after.get("average_learning_value"), (int, float)):
            metrics["avg_learning_value"] = float(memory_after["average_learning_value"])
        if isinstance(summary.get("average_accuracy"), (int, float)):
            metrics["average_accuracy"] = float(summary["average_accuracy"])
        return metrics

    def queue_packets(self, packets: List[HivePacket]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with self.queue_path.open("a", encoding="utf-8") as handle:
            for packet in packets:
                handle.write(json.dumps(packet.to_dict(), sort_keys=True, default=str) + "\n")

    def mark_uploaded(self, packets: List[HivePacket], response: Dict[str, Any]) -> None:
        self._write_json(
            self.last_upload_path,
            {
                "uploaded_at": time.time(),
                "packet_ids": [packet.packet_id for packet in packets],
                "response": response,
            },
        )
        if packets:
            self._write_json(self.last_config_snapshot_path, self._flatten_numeric_fields(self._load_config_snapshot()))
            self._write_json(self.last_conflict_snapshot_path, self._load_conflict_snapshot())
            self._write_json(self.last_outcome_snapshot_path, packets[2].to_dict() if len(packets) > 2 else {})
            self._write_json(self.last_signature_snapshot_path, packets[3].to_dict() if len(packets) > 3 else {})

    def upload_packets_to_discussion(
        self,
        packets: List[HivePacket],
        repo: Optional[str] = None,
        discussion_number: Optional[int] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not packets:
            return {"uploaded": False, "reason": "no_packets"}

        repo = repo or os.environ.get("HIVE_GITHUB_REPOSITORY") or os.environ.get("GITHUB_REPOSITORY")
        discussion_number = discussion_number or int(os.environ.get("HIVE_GITHUB_DISCUSSION_NUMBER", "1"))
        token = token or os.environ.get("HIVE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")

        if not repo or not token:
            return {"uploaded": False, "reason": "missing_repo_or_token"}

        owner, repo_name = repo.split("/", 1)
        endpoint = f"https://api.github.com/repos/{owner}/{repo_name}/discussions/{discussion_number}/comments"

        results = []
        for packet in packets:
            body = f"[HIVE_DELTA_v1]\n{encode_packet_for_comment(packet)}\n[/HIVE_DELTA_v1]"
            request = urllib.request.Request(
                endpoint,
                data=json.dumps({"body": body}).encode("utf-8"),
                method="POST",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "Content-Type": "application/json",
                    "User-Agent": "antahkarana-hive-sync",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                results.append({"packet_id": packet.packet_id, "comment_id": payload.get("id"), "status": "posted"})
            except urllib.error.HTTPError as exc:
                results.append({"packet_id": packet.packet_id, "error": f"http_{exc.code}"})
            except Exception as exc:
                results.append({"packet_id": packet.packet_id, "error": str(exc)})

        success = all(item.get("status") == "posted" for item in results)
        response = {"uploaded": success, "results": results}
        if success:
            self.mark_uploaded(packets, response)
        return response

    def sync_once(
        self,
        avg_learning_value: Optional[float] = None,
        engine_version: Optional[str] = None,
        base_brain_version: Optional[str] = None,
        local_eval_metrics: Optional[Dict[str, float]] = None,
        publish: bool = False,
        repo: Optional[str] = None,
        discussion_number: Optional[int] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        summary = self._load_training_summary()
        if avg_learning_value is None:
            if isinstance(summary.get("memory_after"), dict) and isinstance(summary["memory_after"].get("average_learning_value"), (int, float)):
                avg_learning_value = float(summary["memory_after"]["average_learning_value"])
            elif isinstance(summary.get("average_learning_value"), (int, float)):
                avg_learning_value = float(summary["average_learning_value"])
            else:
                avg_learning_value = 0.0

        if not self.should_sync(avg_learning_value=avg_learning_value):
            return {"synced": False, "reason": "gated_off", "avg_learning_value": avg_learning_value}

        packets = self.build_packets(
            engine_version=engine_version,
            base_brain_version=base_brain_version,
            local_eval_metrics=local_eval_metrics,
        )
        self.queue_packets(packets)

        result = {"synced": True, "queued_packets": [packet.packet_id for packet in packets]}
        if publish:
            result["publish"] = self.upload_packets_to_discussion(packets, repo=repo, discussion_number=discussion_number, token=token)
        return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sync = EvolutionSync(repo_root)
    print(json.dumps(sync.sync_once(), indent=2, default=str))


if __name__ == "__main__":
    main()
