from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL_ROOT = ROOT / "antahkarana_kernel"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from antahkarana_kernel.modules.HiveDelta import default_packet_verifier, decode_packet_from_comment  # noqa: E402,F401

SOURCE_SCRIPT = ROOT.parent / "tools" / "run_hive_aggregator.py"


if __name__ == "__main__":
    runpy.run_path(str(SOURCE_SCRIPT), run_name="__main__")
