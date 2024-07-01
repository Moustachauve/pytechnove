"""Asynchronous Python client for TechnoVE."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Final, Self

import aiohttp
import backoff
from yarl import URL

from .exceptions import (
    TechnoVEConnectionError,
    TechnoVEConnectionTimeoutError,
    TechnoVEError,
    TechnoVEOutOfBoundError,
)
from .models import Station

# TechnoVE stations don't allow setting values lower than 8. Calling the API with
# a smaller value will just be ignored.
MIN_CURRENT: Final[int] = 8


@dataclass
class TechnoVE:
    """Main class for handling connections with TechnoVE."""

    station_ip: str
    session: aiohttp.client.ClientSession | None = None
    request_timeout: float = 8.0
    _close_session: bool = False
    station: Station | None = None

    # /station/get/info
    # /station/get/statistic
    # /station/get/current/correcting/ratio
    # /station/get/ntp/server
    # /station/network/get/logs
    # /station/network/list
    # /station/get/schedule
    # /station/partage/get/config
    # /station/partage/set/config
    # - ex: {"partageUuid":"GUID-HERE","partageName":"Mon partage",
    #       "configuredMaxCurrent":24,"stations":[{"uuid":"{mac-address}",
    #       "name":"nameHere","ipAddress":"192.168.1.2","configuredMaxCurrent":24,
    #       "maxCurrent":32}]}
    # /station/update (POST)
    # /station/schedule/high/activate (POST)
    # /station/set/automatic (POST)
    # /station/control/stop
    # /station/control/start
    # /station/control/partage (POST)
    #    - ex: {" stationNumber": 1, "current":48.0}

    # 65: not plugged in, waiting
    # 66: plugged in, waiting
    # 67: plugged in, charging

    @backoff.on_exception(
        backoff.expo, TechnoVEConnectionError, max_tries=3, logger=None
    )
    async def request(
        self,
        uri: str = "",
        method: str = "GET",
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to a TechnoVE station.

        A generic method for sending/handling HTTP requests done gainst
        the TechnoVE station.

        Args:
        ----
            uri: Request URI, for example `/station/get/info`.
            method: HTTP method to use for the request.E.g., "GET" or "POST".
            data: Dictionary of data to send to the TechnoVE station.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from the
            TechnoVE station.

        Raises:
        ------
            TechnoVEConnectionError: An error occurred while communication with
                the TechnoVE station.
            TechnoVEConnectionTimeoutError: A timeout occurred while communicating
                with the TechnoVE station.
            TechnoVEError: Received an unexpected response from the TechnoVE station.

        """
        url = URL.build(scheme="http", host=self.station_ip, port=80, path=uri)

        headers = {
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                )

            content_type = response.headers.get("Content-Type", "")
            if response.status // 100 in [4, 5]:
                contents = await response.read()
                response.close()

                if content_type == "application/json":
                    raise TechnoVEError(
                        response.status,
                        json.loads(contents.decode("utf8")),
                    )
                raise TechnoVEError(
                    response.status,
                    {"message": contents.decode("utf8")},
                )

            if "application/json" in content_type:
                response_data = await response.json()
            else:
                response_data = await response.text()

        except asyncio.TimeoutError as exception:
            msg = (
                "Timeout occurred while connecting"
                f" to TechnoVE station at {self.station_ip}"
            )
            raise TechnoVEConnectionTimeoutError(msg) from exception
        except aiohttp.ClientError as exception:
            msg = (
                "Error occurred while communicating"
                f" with TechnoVE station at {self.station_ip}"
            )
            raise TechnoVEConnectionError(msg) from exception

        return response_data

    async def update(self) -> Station:
        """Get all information about the station in a single call.

        This method updates all the TechnoVE information available with a single
        API call.

        Returns
        -------
            TechnoVE station data.

        """
        data = await self.request("/station/get/info")
        if not data:
            msg = "No data was returned by the station"
            raise TechnoVEError(msg)
        self.station = Station(data)
        return self.station

    async def set_auto_charge(self, *, enabled: bool) -> None:
        """Set whether the auto-charge feature is enabled or disabled.

        Args:
        ----
            enabled: True to enable the auto-charge feature, otherwise false.

        """
        await self.request(
            "/station/set/automatic", method="POST", data={"activated": enabled}
        )

    async def set_charging_enabled(self, *, enabled: bool) -> None:
        """Set whether the charging station is allowed to provide power or not.

        This can only be set if the auto_charge feature is not enabled.

        Args:
        ----
            enabled: True to allow a plugged-in vehicle to charge, otherwise false.

        Raises:
        ------
            TechnoVEError: If auto_charge is enabled.

        """
        if self.station and self.station.info.auto_charge:
            msg = "Cannot start or stop charging when auto-charge is enabled."
            raise TechnoVEError(msg)
        action = "start" if enabled else "stop"
        await self.request(f"/station/control/{action}")

    async def set_max_current(self, max_current: int) -> None:
        """Set the max current the station is allowed to provide.

        This can only be set if the sharing mode feature is not enabled.

        Args:
        ----
            max_current: The maximum current the station can provide to the vehicle.
                This value must be between 8 and max_station_current.

        Raises:
        ------
            TechnoVEError: If in_sharing_mode is enabled.
            TechnoVEOutOfBoundError: If max_current is below 8 (See MIN_CURRENT).
            TechnoVEOutOfBoundError: If max_current is above max_station_current.

        """
        if self.station and self.station.info.in_sharing_mode:
            msg = "Cannot set the max current when sharing mode is enabled."
            raise TechnoVEError(msg)
        if max_current < MIN_CURRENT:
            msg = f"Max current needs to be greater than {MIN_CURRENT}."
            raise TechnoVEOutOfBoundError(msg)
        if self.station and max_current > self.station.info.max_station_current:
            msg = (
                "Max current needs to be equal or lower than "
                f"{self.station.info.max_station_current}."
            )
            raise TechnoVEOutOfBoundError(msg)
        await self.request(
            "/station/control/partage",
            "POST",
            {" stationNumber": 1, "current": max_current},
        )

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The TechnoVE object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
