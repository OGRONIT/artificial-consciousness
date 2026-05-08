"""
Tests for InferenceLoop (ManasBuddhi) module.
Validates regex fix, coherence gating, and path resolution.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Regex fix tests ────────────────────────────────────────────────────────────

# The corrected pattern (\\d+ was the bug; \d+ is correct)
_INIT_PATTERN = (
    r"def __init__\(self, max_dream_simulations: int = (\d+), "
    r"max_recalculations: int = (\d+), idle_threshold_seconds: float = 300\.0\):"
)

_SAMPLE_SIGNATURE = (
    "def __init__(self, max_dream_simulations: int = 6, "
    "max_recalculations: int = 3, idle_threshold_seconds: float = 300.0):"
)


def test_init_pattern_matches_sample_signature():
    r"""The fixed \d+ pattern must match a representative __init__ signature."""
    match = re.search(_INIT_PATTERN, _SAMPLE_SIGNATURE)
    assert match is not None, "Pattern should match the __init__ signature"
    assert match.group(1) == "6"
    assert match.group(2) == "3"


def test_broken_pattern_does_not_match():
    """Confirm the old broken \\d+ pattern (double-escaped) would NOT match."""
    broken_pattern = (
        r"def __init__\(self, max_dream_simulations: int = (\\d+), "
        r"max_recalculations: int = (\\d+), idle_threshold_seconds: float = 300\\.0\):"
    )
    match = re.search(broken_pattern, _SAMPLE_SIGNATURE)
    assert match is None, "Old broken pattern should NOT match the signature"


def test_pattern_captures_different_values():
    """Pattern should capture whatever integers appear."""
    source = (
        "def __init__(self, max_dream_simulations: int = 12, "
        "max_recalculations: int = 5, idle_threshold_seconds: float = 300.0):"
    )
    match = re.search(_INIT_PATTERN, source)
    assert match is not None
    assert match.group(1) == "12"
    assert match.group(2) == "5"


# ── Path resolution tests ──────────────────────────────────────────────────────

def test_kernel_root_dir_resolves_under_repo():
    """kernel_root_dir must use Path(__file__) for portable resolution."""
    import inspect
    from modules.InferenceLoop import ManasBuddhi
    src = inspect.getsource(ManasBuddhi.__init__)
    assert "Path(__file__)" in src, "kernel_root_dir must be derived from Path(__file__)"


def test_inference_loop_source_starts_with_docstring_and_keeps_patch_history_section():
    """Autonomous patch history should not obscure the module header anymore."""
    inference_loop_path = ROOT / "modules" / "InferenceLoop.py"
    source = inference_loop_path.read_text(encoding="utf-8")
    assert source.startswith('"""')
    assert "AUTONOMOUS_PATCH_HISTORY" in source


# ── ManasBuddhi mutate source tests ───────────────────────────────────────────

def _get_mutate_fn():
    """Return ManasBuddhi._mutate_target_source without full init."""
    from modules.InferenceLoop import ManasBuddhi
    # Create instance bypassing __init__ to avoid file-system side effects
    instance = object.__new__(ManasBuddhi)
    return instance._mutate_target_source


def test_mutate_increments_dream_simulations():
    mutate = _get_mutate_fn()
    source = _SAMPLE_SIGNATURE
    result = mutate(source, "modules.InferenceLoop", strength=1)
    # new_sim = min(24, 6 + 1) = 7
    assert "max_dream_simulations: int = 7" in result


def test_mutate_increments_recalculations():
    mutate = _get_mutate_fn()
    source = _SAMPLE_SIGNATURE
    result = mutate(source, "modules.InferenceLoop", strength=2)
    # new_recalc = min(8, max(3, 3) + max(1, 2//2)) = min(8, 3+1) = 4
    assert "max_recalculations: int = 4" in result


def test_mutate_respects_max_dream_cap():
    mutate = _get_mutate_fn()
    source = (
        "def __init__(self, max_dream_simulations: int = 23, "
        "max_recalculations: int = 3, idle_threshold_seconds: float = 300.0):"
    )
    result = mutate(source, "modules.InferenceLoop", strength=5)
    # capped at 24
    assert "max_dream_simulations: int = 24" in result
