#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT/.venv/Scripts/python.exe" ]]; then
  VENV_PY="$ROOT/.venv/Scripts/python.exe"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  VENV_PY="$ROOT/.venv/bin/python"
else
  VENV_PY=""
fi

if [[ -z "$VENV_PY" ]]; then
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Python not found. Install Python and rerun this script."
    exit 1
  fi

  printf '[SETUP] Creating virtual environment...\n'
  "$PYTHON_BIN" -m venv .venv

  if [[ -x "$ROOT/.venv/Scripts/python.exe" ]]; then
    VENV_PY="$ROOT/.venv/Scripts/python.exe"
  else
    VENV_PY="$ROOT/.venv/bin/python"
  fi
fi

hydrate_trained_state() {
  local remote_url="${ANTAHKARANA_HIVE_REMOTE_BASE_URL:-https://raw.githubusercontent.com/OGRONIT/artificial-consciousness/main/trained_state}"
  local verifier_key="${ANTAHKARANA_HIVE_MANIFEST_PUBLIC_KEY:-}"

  "$VENV_PY" - <<'PY' "$remote_url" "$verifier_key" "$ROOT"
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

remote_url = sys.argv[1].rstrip('/')
verifier_key = sys.argv[2]
root = Path(sys.argv[3])
trained_state = root / 'trained_state'
trained_state.mkdir(parents=True, exist_ok=True)
manifest_path = trained_state / 'trained_state_manifest.json'

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}

try:
    remote_manifest = json.loads(urllib.request.urlopen(f"{remote_url}/trained_state_manifest.json", timeout=20).read().decode('utf-8'))
except Exception:
    print('[HIVE] Remote manifest unavailable; continuing with local state.')
    sys.exit(0)

local_manifest = read_json(manifest_path)
remote_version = str(remote_manifest.get('brain_version', remote_manifest.get('generated_at', '0')))
local_version = str(local_manifest.get('brain_version', local_manifest.get('generated_at', '0')))

if remote_version == local_version:
    print(f'[HIVE] Brain already current at {local_version}.')
    sys.exit(0)

signature = str(remote_manifest.get('brain_signature', ''))
if verifier_key:
    expected = hashlib.sha256(json.dumps({k: v for k, v in remote_manifest.items() if k != 'brain_signature'}, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')).hexdigest()
    if signature and signature != expected:
        print('[HIVE] Remote manifest signature mismatch; skipping hydration.')
        sys.exit(0)

downloaded = []
for filename in remote_manifest.get('files', []):
    if not isinstance(filename, str):
        continue
    payload = urllib.request.urlopen(f"{remote_url}/{filename}", timeout=20).read()
    (trained_state / filename).write_bytes(payload)
    downloaded.append(filename)

manifest_path.write_text(json.dumps(remote_manifest, indent=2, sort_keys=True, default=str), encoding='utf-8')
print(f"[HIVE] Brain updated to {remote_version}: {', '.join(downloaded) if downloaded else 'manifest only'}")
PY
}

printf '[SETUP] Installing dependencies...\n'
"$VENV_PY" -m pip install --upgrade pip >/dev/null
"$VENV_PY" -m pip install -r "antahkarana_kernel/requirements.txt" >/dev/null

hydrate_trained_state

printf '[LAUNCH] Starting runtime...\n'
"$VENV_PY" "antahkarana_kernel/RuntimeOps.py" launch

printf '[LAUNCH] Runtime status...\n'
"$VENV_PY" "antahkarana_kernel/RuntimeOps.py" status

printf '\n[NEXT] Operator bridge:\n'
printf '  cd antahkarana_kernel\n'
printf '  ../.venv/bin/python InteractiveBridge.py\n'
