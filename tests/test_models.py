"""Tests for `technove.models.Status`."""

from dataclasses import FrozenInstanceError

import pytest

from technove import Station, Status


def test_station_repr() -> None:
    """Test Station __repr__ formatting."""
    station = Station({"name": "TestStation", "version": "1.0"})
    assert repr(station) == f"Station(info={station.info!r})"


def test_station_slots() -> None:
    """Test that Station uses __slots__ and prevents dynamic attributes."""
    station = Station({"name": "TestStation"})
    with pytest.raises(AttributeError):
        setattr(station, "dynamic_attr", "not_allowed")  # noqa: B010


def test_info_frozen() -> None:
    """Test that Info dataclass is immutable and uses slots."""
    station = Station({"name": "TestStation"})
    assert not hasattr(station.info, "__dict__")
    with pytest.raises(FrozenInstanceError):
        setattr(station.info, "name", "Modified")  # noqa: B010


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
    assert Status.build(["A"]) == Status.UNKNOWN  # type: ignore[arg-type]
