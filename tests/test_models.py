"""Tests for `technove.TechnoVE`."""


from technove import Status


def test_status_build() -> None:
    """Test status build with a known status code."""
    assert Status.build(67) == Status.PLUGGED_CHARGING


def test_status_build_unknown() -> None:
    """Test status build with an unknown status code."""
    assert Status.build(42) == Status.UNKNOWN
