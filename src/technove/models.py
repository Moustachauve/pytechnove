"""Models for TechnoVE."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Status(Enum):
    """Describes the status of a TechnoVE station.

    Values map to SAE J1772 Control Pilot states and TechnoVE custom states.
    The raw API value is an ASCII character (e.g. 'A', 'B', 'C') whose ordinal
    integer represents the state code.

    Standard SAE J1772 states:
        A (65)  - No vehicle connected (unplugged / standby)
        B (66)  - Vehicle detected, not ready to charge (plugged, waiting)
        C (67)  - Charging in progress
        D (68)  - Charging with ventilation required
        E (69)  - Pilot fault (EVSE error)
        F (70)  - EVSE fault (not available)

    TechnoVE custom states:
        H (72)  - Ground fault detected
        S (83)  - Out of activation period
        T (84)  - High-tariff period active
    """

    UNKNOWN = None
    UNPLUGGED = "unplugged"
    PLUGGED_WAITING = "plugged_waiting"
    PLUGGED_CHARGING = "plugged_charging"
    VENTILATION_REQUIRED = "ventilation_required"
    PILOT_FAULT = "pilot_fault"
    EVSE_FAULT = "evse_fault"
    GROUND_FAULT = "ground_fault"
    OUT_OF_ACTIVATION_PERIOD = "out_of_activation_period"
    HIGH_TARIFF_PERIOD = "high_tariff_period"

    @classmethod
    def build(cls: type[Status], status: Any | None) -> Status:
        """Parse a status value from the TechnoVE API into a Status object.

        The API returns the status as a single ASCII character string (e.g. 'A',
        'B', 'C'). This method accepts either the raw character string or its
        integer ordinal equivalent.

        Args:
        ----
            status: The raw status value from the API. May be a single-character
                string, an integer ordinal, or None.

        Returns:
        -------
            The matching Status enum member, or Status.UNKNOWN for unrecognised
            values.

        """
        if isinstance(status, str):
            code = ord(status) if len(status) == 1 else None
        elif isinstance(status, int):
            code = status
        else:
            code = None

        return _STATUS_MAP.get(code, cls.UNKNOWN)


_STATUS_MAP: dict[int | None, Status] = {
    ord("A"): Status.UNPLUGGED,  # 65
    ord("B"): Status.PLUGGED_WAITING,  # 66
    ord("C"): Status.PLUGGED_CHARGING,  # 67
    ord("D"): Status.VENTILATION_REQUIRED,  # 68
    ord("E"): Status.PILOT_FAULT,  # 69
    ord("F"): Status.EVSE_FAULT,  # 70
    ord("H"): Status.GROUND_FAULT,  # 72
    ord("S"): Status.OUT_OF_ACTIVATION_PERIOD,  # 83
    ord("T"): Status.HIGH_TARIFF_PERIOD,  # 84
}


class Station:
    """Object holding all information from a TechnoVE Station."""

    info: Info

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize an empty TechnoVE Station class.

        Args:
        ----
            data: The full API response from a TechnoVE station.

        """
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Station:
        """Return Station object from TechnoVE API response.

        Args:
        ----
            data: Update the station object with the data received from a
                TechnoVE station API.

        Returns:
        -------
            The updated Station object.

        """
        self.info = Info.from_dict(data)

        return self


@dataclass
class Info:  # pylint: disable=too-many-instance-attributes
    """Object holding information from a TechnoVE Station."""

    auto_charge: bool
    conflict_in_sharing_config: bool
    current: int
    energy_session: float
    energy_total: int
    high_tariff_period_active: bool
    mac_address: str
    in_sharing_mode: bool
    is_battery_protected: bool
    is_session_active: bool
    is_static_ip: bool
    is_up_to_date: bool
    last_charge: str
    max_charge_percentage: float
    max_current: int
    max_station_current: int
    name: str
    network_ssid: str
    normal_period_active: bool
    rssi: int
    status: Status
    time: int
    version: str
    voltage_in: int
    voltage_out: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Info:
        """Return Info object from TechnoVE API response.

        Args:
        ----
            data: The data from the TechnoVE station API.

        Returns:
        -------
            A station info object.

        """
        return Info(
            auto_charge=data.get("auto_charge", False),
            conflict_in_sharing_config=data.get("conflictInSharingConfig", False),
            current=data.get("current", 0),
            energy_session=data.get("energySession", 0),
            energy_total=data.get("energyTotal", 0),
            high_tariff_period_active=data.get("highChargePeriodActive", False),
            mac_address=data.get("id", "unknown"),
            in_sharing_mode=data.get("inSharingMode", False),
            is_battery_protected=data.get("isBatteryProtected", False),
            is_session_active=data.get("isSessionActive", False),
            is_static_ip=data.get("isStaticIp", False),
            is_up_to_date=data.get("isUpToDate", True),
            last_charge=data.get("lastCharge", ""),
            max_charge_percentage=data.get("maxChargePourcentage", 0),
            max_current=data.get("maxCurrent", 0),
            max_station_current=data.get("maxStationCurrent", 0),
            name=data.get("name", "Unknown"),
            network_ssid=data.get("network_ssid", "Unknown"),
            normal_period_active=data.get("normalPeriodActive", False),
            rssi=data.get("rssi", 0),
            status=Status.build(data.get("status")),
            time=data.get("time", 0),
            version=data.get("version", "Unknown"),
            voltage_in=data.get("voltageIn", 0),
            voltage_out=data.get("voltageOut", 0),
        )
