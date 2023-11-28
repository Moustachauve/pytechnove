"""Exceptions for TechnoVE."""


class TechnoVEError(Exception):
    """Generic TechnoVE exception."""


class TechnoVEConnectionError(Exception):
    """TechnoVE connection exception."""


class TechnoVEConnectionTimeoutError(TechnoVEConnectionError):
    """TechnoVE connection Timeout exception."""
