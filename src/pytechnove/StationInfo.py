from dataclasses import dataclass


@dataclass
class StationInfo:
    voltageIn: int
    voltageOut: int
    maxStationCurrent: int
    maxCurrent: int
    current: int
    network_ssid: str
    id: str
    auto_charge: bool
    highChargePeriodActive: bool
    normalPeriodActive: bool
    maxChargePourcentage: float
    isBatteryProtected: bool
    inSharingMode: bool
    energySession: float
    energyTotal: int
    version: str
    rssi: int
    name: str
    lastCharge: str
    time: int
    isUpToDate: bool
    isSessionActive: bool
    conflictInSharingConfig: bool
    isStaticIp: bool
    status: int
