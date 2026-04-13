from __future__ import annotations

import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from .HiveDelta import NodeCredentials, generate_node_credentials, load_node_credentials


HOME_DIR = Path.home() / ".antahkarana"
CONSENT_PATH = HOME_DIR / "consent.json"
KEY_PATH = HOME_DIR / "node_keys.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def _input_yes_no(prompt: str) -> bool:
    if not sys.stdin.isatty():
        return str(os.environ.get("ANTAHKARANA_HIVE_OPT_IN", "no")).strip().lower() in {"1", "true", "yes", "y"}

    while True:
        response = input(prompt).strip().lower()
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def _default_consent_payload(node_id_hash: str, opted_in: bool) -> Dict[str, Any]:
    return {
        "hive_opted_in": opted_in,
        "node_id_hash": node_id_hash,
        "consented_at": time.time(),
        "version": "1.0",
        "what_is_sent": "policy patterns, confusion stats, outcome counters, hashed signatures",
        "what_is_never_sent": "conversations, personal data, raw prompts",
    }


def load_consent() -> Dict[str, Any]:
    return _read_json(CONSENT_PATH)


def load_credentials() -> Optional[NodeCredentials]:
    payload = _read_json(KEY_PATH)
    if not payload:
        return None
    try:
        return load_node_credentials(payload)
    except Exception:
        return None


def save_credentials(credentials: NodeCredentials) -> None:
    _write_json(KEY_PATH, credentials.as_dict())


def ensure_consent() -> Dict[str, Any]:
    """Ensure the first-run hive opt-in decision is persisted."""

    existing = load_consent()
    if existing:
        return existing

    opted_in = _input_yes_no(
        "Would you like to contribute anonymously to the global hive? [yes/no]: "
    )

    if not opted_in:
        payload = _default_consent_payload(node_id_hash="local-only", opted_in=False)
        _write_json(CONSENT_PATH, payload)
        return payload

    credentials = generate_node_credentials()
    save_credentials(credentials)

    payload = _default_consent_payload(node_id_hash=credentials.node_id_hash, opted_in=True)
    payload["key_scheme"] = credentials.scheme
    payload["key_file"] = str(KEY_PATH)
    _write_json(CONSENT_PATH, payload)
    return payload


def consent_allows_hive() -> bool:
    return bool(load_consent().get("hive_opted_in", False))


def pull_latest_trained_state(
    trained_state_dir: Path,
    remote_base_url: Optional[str] = None,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """Optionally hydrate the local tracked state from a remote raw URL."""

    remote_base_url = remote_base_url or os.environ.get(
        "ANTAHKARANA_HIVE_REMOTE_BASE_URL",
        "https://raw.githubusercontent.com/OGRONIT/artificial-consciousness/main/trained_state",
    )
    trained_state_dir.mkdir(parents=True, exist_ok=True)

    manifest_url = f"{remote_base_url.rstrip('/')}/trained_state_manifest.json"
    manifest_path = trained_state_dir / "trained_state_manifest.json"

    try:
        with urllib.request.urlopen(manifest_url, timeout=timeout_seconds) as response:
            remote_manifest = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"pulled": False, "reason": f"manifest_fetch_failed:{exc}"}

    try:
        local_manifest = _read_json(manifest_path)
        remote_version = str(remote_manifest.get("brain_version", remote_manifest.get("generated_at", "0")))
        local_version = str(local_manifest.get("brain_version", local_manifest.get("generated_at", "0")))
        if remote_version == local_version:
            return {"pulled": False, "reason": "already_current", "brain_version": remote_version}

        files = remote_manifest.get("files", [])
        downloaded = []
        for filename in files:
            if not isinstance(filename, str):
                continue
            file_url = f"{remote_base_url.rstrip('/')}/{filename}"
            target_path = trained_state_dir / filename
            with urllib.request.urlopen(file_url, timeout=timeout_seconds) as response:
                target_path.write_bytes(response.read())
            downloaded.append(filename)

        _write_json(manifest_path, remote_manifest)
        return {"pulled": True, "brain_version": remote_version, "downloaded_files": downloaded}
    except Exception as exc:
        return {"pulled": False, "reason": f"download_failed:{exc}"}


def first_boot_initialize(
    trained_state_dir: Optional[Path] = None,
    remote_base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Run first-boot consent logic and optionally hydrate the tracked brain."""

    consent = ensure_consent()
    result = {"consent": consent, "hydrated": False}

    if consent.get("hive_opted_in") and trained_state_dir is not None:
        result["hydration"] = pull_latest_trained_state(trained_state_dir, remote_base_url=remote_base_url)
        result["hydrated"] = bool(result["hydration"].get("pulled", False))

    return result


def load_or_create_identity() -> Optional[NodeCredentials]:
    if not CONSENT_PATH.exists():
        ensure_consent()
    if not consent_allows_hive():
        return None
    return load_credentials()


def main() -> None:
    payload = first_boot_initialize()
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
