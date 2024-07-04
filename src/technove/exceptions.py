"""Exceptions for TechnoVE."""


class TechnoVEError(Exception):
    """Generic TechnoVE exception."""


class TechnoVEOutOfBoundError(TechnoVEError):
    """TechnoVE exception when trying to set values out of bounds."""


class TechnoVEConnectionError(TechnoVEError):
    """TechnoVE connection exception."""


class TechnoVEConnectionTimeoutError(TechnoVEConnectionError):
    """TechnoVE connection Timeout exception."""
