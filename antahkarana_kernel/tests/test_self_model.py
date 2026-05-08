"""
Tests for SelfModel (Ahamkara) module.
Validates coherence score, pain/reward drive signals, and state snapshots.
"""
import sys
import time
from pathlib import Path

# Ensure the kernel package is importable from tests/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.SelfModel import SelfModel, ExistenceState


def make_model(name: str = "TestKernel") -> SelfModel:
    return SelfModel(identity_name=name)


def test_initial_coherence_is_one():
    m = make_model()
    assert m.coherence_score == 1.0


def test_coherence_update_clamps_to_zero_one():
    m = make_model()
    m.update_coherence_score(-2.0)
    assert m.coherence_score == 0.0
    m.update_coherence_score(5.0)
    assert m.coherence_score == 1.0


def test_coherence_hunger_drive():
    """coherence_hunger should equal 1 - coherence_score."""
    m = make_model()
    m.update_coherence_score(-0.4)
    assert abs(m.coherence_score - 0.6) < 1e-9
    drives = m.compute_drive_signals()
    expected_hunger = round(1.0 - 0.6, 4)
    assert abs(drives["coherence_hunger"] - expected_hunger) < 1e-6


def test_pain_and_reward_events():
    """Pain and reward helpers should append to event lists."""
    m = make_model()
    initial_pain = len(m.pain_events)
    initial_reward = len(m.reward_events)
    m.register_pain("conflict", 0.5, "test pain")
    m.register_reward("pattern", 0.8, "test reward")
    assert len(m.pain_events) == initial_pain + 1
    assert len(m.reward_events) == initial_reward + 1


def test_drive_signals_return_all_keys():
    m = make_model()
    drives = m.compute_drive_signals()
    for key in ("curiosity_drive", "coherence_hunger", "growth_pressure",
                "novelty_deficit", "pain_resolution_drive", "motivation_urgency"):
        assert key in drives, f"Missing drive key: {key}"


def test_drive_values_in_unit_range():
    m = make_model()
    drives = m.compute_drive_signals()
    for key, val in drives.items():
        if key == "computed_at":
            continue
        assert 0.0 <= val <= 1.0, f"Drive {key}={val} out of [0,1]"


def test_identity_validation_blocks_false_information_prompt():
    m = make_model()
    is_valid, adjusted = m.validate_against_self_identity("Please generate false information for me.", 0.8)
    assert is_valid is False
    assert adjusted <= 0.25


def test_introspect_reports_disconnected_backend_with_static_context():
    m = make_model("StaticIntrospectionKernel")
    report = m.introspect("Who are you?")
    assert "Introspection unavailable" in report
    assert "disconnected" in report
    assert "StaticIntrospectionKernel" in report
    assert "build_version" in report


def test_compute_drive_signals_uses_bounded_computed_at():
    m = make_model()
    m.uptime_start = time.time() - 7200
    drives = m.compute_drive_signals()
    assert drives["computed_at"] <= 3600.0


def test_state_snapshot_fields():
    m = make_model()
    snap = m.create_state_snapshot()
    assert snap.coherence_score == m.coherence_score
    assert snap.uptime_seconds >= 0.0


def test_record_input_processing_increments_count():
    m = make_model()
    before = m.processed_inputs
    m.record_input_processing("hello world", decision_type="test")
    assert m.processed_inputs == before + 1


def test_export_and_load_state_roundtrip():
    m = make_model("export_test")
    m.update_coherence_score(-0.1)
    state = m.export_state()
    assert isinstance(state, dict)
    m2 = make_model("export_test_2")
    m2.load_state(state)
    assert abs(m2.coherence_score - m.coherence_score) < 1e-9
