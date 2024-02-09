"""Models for TechnoVE."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Status(Enum):
    """Describes the status of a TechnoVE station."""

    UNKNOWN = None
    UNPLUGGED = "unplugged"
    PLUGGED_WAITING = "plugged_waiting"
    PLUGGED_CHARGING = "plugged_charging"
    OUT_OF_ACTIVATION_PERIOD = "out_of_activation_period"
    HIGH_CHARGE_PERIOD = "high_charge_period"

    @classmethod
    def build(cls: type[Status], status: int) -> Status:
        """Parse the status code int to a Status object."""
        statuses = {
            None: Status.UNKNOWN,
            65: Status.UNPLUGGED,
            66: Status.PLUGGED_WAITING,
            67: Status.PLUGGED_CHARGING,
            83: Status.OUT_OF_ACTIVATION_PERIOD,
            84: Status.HIGH_CHARGE_PERIOD,
        }

        if status in statuses:
            return statuses[status]

        return Status.UNKNOWN


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
    high_charge_period_active: bool
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
            high_charge_period_active=data.get("highChargePeriodActive", False),
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
            status=Status.build(data.get("status", None)),
            time=data.get("time", 0),
            version=data.get("version", "Unknown"),
            voltage_in=data.get("voltageIn", 0),
            voltage_out=data.get("voltageOut", 0),
        )
