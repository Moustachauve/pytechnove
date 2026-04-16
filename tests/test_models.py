"""Tests for `technove.models.Status`."""

from technove import Status


def test_status_build_plugged_charging() -> None:
    """State C - charging in progress."""
    assert Status.build(67) == Status.PLUGGED_CHARGING


def test_status_build_from_string() -> None:
    """build() accepts the raw API single-character string."""
    assert Status.build("B") == Status.PLUGGED_WAITING


# ---------------------------------------------------------------------------
# Edge / fallback cases
# ---------------------------------------------------------------------------


def test_status_build_unknown_int() -> None:
    """An unrecognised integer returns UNKNOWN."""
    assert Status.build(42) == Status.UNKNOWN


def test_status_build_unknown_string() -> None:
    """A multi-character string that is not a single ASCII state returns UNKNOWN."""
    assert Status.build("1234") == Status.UNKNOWN


def test_status_build_none() -> None:
    """None returns UNKNOWN."""
    assert Status.build(None) == Status.UNKNOWN


def test_status_build_unhashable_type() -> None:
    """An unhashable malformed value returns UNKNOWN without raising."""
    assert Status.build(["A"]) == Status.UNKNOWN
