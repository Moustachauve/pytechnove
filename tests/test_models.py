"""Tests for `technove.models.Status`."""

from technove import Status


def test_status_build_plugged_charging() -> None:
    """State C - charging in progress."""
    assert Status.build(67) == Status.PLUGGED_CHARGING




# ---------------------------------------------------------------------------
# Edge / fallback cases
# ---------------------------------------------------------------------------


def test_status_build_unknown_int() -> None:
    """An unrecognised integer returns UNKNOWN."""
    assert Status.build(42) == Status.UNKNOWN




def test_status_build_none() -> None:
    """None returns UNKNOWN."""
    assert Status.build(None) == Status.UNKNOWN


def test_status_build_unhashable_type() -> None:
    """An unhashable malformed value returns UNKNOWN without raising."""
    assert Status.build(["A"]) == Status.UNKNOWN
