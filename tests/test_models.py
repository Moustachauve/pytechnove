"""Tests for `technove.TechnoVE`."""


import pytest

from technove import Status, TechnoVEError


def test_status_build() -> None:
    """Test status build with a known status code."""
    assert Status.build(67) == Status.PLUGGED_CHARGING


def test_status_build_unknown() -> None:
    """Test status build with an unknown status code."""
    with pytest.raises(TechnoVEError):
        Status.build(42)
