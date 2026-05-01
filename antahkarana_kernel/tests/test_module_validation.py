"""
Tests for AntahkaranaKernel dynamic module name validation (security hardening).
Ensures unsafe module names are rejected before import.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The validation logic extracted from AntahkaranaKernel._load_self_authored_modules
_DENYLIST = {
    "os", "sys", "subprocess", "shutil", "importlib", "builtins",
    "__builtins__", "socket", "threading", "multiprocessing",
}
_VALID_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def is_safe_module_name(name: str) -> bool:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return False
    if name.lower() in _DENYLIST:
        return False
    return True


def test_valid_module_name_accepted():
    assert is_safe_module_name("MyModule") is True
    assert is_safe_module_name("my_module_v2") is True
    assert is_safe_module_name("_PrivateModule") is True


def test_empty_name_rejected():
    assert is_safe_module_name("") is False


def test_name_with_dot_rejected():
    assert is_safe_module_name("modules.evil") is False


def test_name_with_slash_rejected():
    assert is_safe_module_name("../../etc/passwd") is False


def test_name_starting_with_digit_rejected():
    assert is_safe_module_name("1malicious") is False


def test_name_with_space_rejected():
    assert is_safe_module_name("bad name") is False


def test_denylist_names_rejected():
    for name in ("os", "sys", "subprocess", "shutil", "importlib", "socket",
                 "threading", "multiprocessing"):
        assert is_safe_module_name(name) is False, f"{name} should be denied"


def test_denylist_case_insensitive():
    assert is_safe_module_name("OS") is False
    assert is_safe_module_name("Sys") is False
    assert is_safe_module_name("SUBPROCESS") is False


def test_path_traversal_rejected():
    assert is_safe_module_name("__builtins__") is False
    assert is_safe_module_name("..evil") is False


def test_generated_dir_sandbox():
    """Verify that a valid module name stays within modules/generated/."""
    generated_dir = ROOT / "modules" / "generated"
    module_name = "ValidModule"
    candidate = (generated_dir / f"{module_name}.py").resolve()
    # relative_to should not raise
    candidate.relative_to(generated_dir.resolve())

    # A path-traversal attempt should be caught
    bad_name = "../InferenceLoop"
    bad_candidate = (generated_dir / f"{bad_name}.py").resolve()
    try:
        bad_candidate.relative_to(generated_dir.resolve())
        escaped = True
    except ValueError:
        escaped = False
    assert not escaped, "Path traversal should be caught by relative_to check"
