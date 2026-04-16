"""Tests for `technove.models.Status`."""

import pytest

from technove import Status


# ---------------------------------------------------------------------------
# Existing SAE J1772 / TechnoVE states (integer ordinal input)
# ---------------------------------------------------------------------------
def test_status_build_plugged_charging() -> None:
    """State C - charging in progress."""
    assert Status.build(67) == Status.PLUGGED_CHARGING


# ---------------------------------------------------------------------------
# String input - the API actually sends ASCII character strings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("char", "expected"),
    [
        ("A", Status.UNPLUGGED),
        ("B", Status.PLUGGED_WAITING),
        ("C", Status.PLUGGED_CHARGING),
        ("D", Status.VENTILATION_REQUIRED),
        ("E", Status.PILOT_FAULT),
        ("F", Status.EVSE_FAULT),
        ("H", Status.GROUND_FAULT),
        ("S", Status.OUT_OF_ACTIVATION_PERIOD),
        ("T", Status.HIGH_TARIFF_PERIOD),
    ],
)
def test_status_build_from_string(char: str, expected: Status) -> None:
    """build() accepts the raw API single-character string."""
    assert Status.build(char) == expected


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
