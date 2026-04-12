#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PY="$ROOT/.venv/bin/python"

if [[ ! -x "$VENV_PY" ]]; then
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Python 3 not found. Install Python 3 and rerun this script."
    exit 1
  fi

  printf '[SETUP] Creating virtual environment...\n'
  "$PYTHON_BIN" -m venv .venv
fi

printf '[SETUP] Installing dependencies...\n'
"$VENV_PY" -m pip install --upgrade pip >/dev/null
"$VENV_PY" -m pip install -r "antahkarana_kernel/requirements.txt" >/dev/null

printf '[LAUNCH] Starting runtime...\n'
"$VENV_PY" "antahkarana_kernel/RuntimeOps.py" launch

printf '[LAUNCH] Runtime status...\n'
"$VENV_PY" "antahkarana_kernel/RuntimeOps.py" status

printf '\n[NEXT] Operator bridge:\n'
printf '  cd antahkarana_kernel\n'
printf '  ../.venv/bin/python InteractiveBridge.py\n'
