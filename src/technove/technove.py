"""Asynchronous Python client for TechnoVE."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Self

import aiohttp
import backoff
from yarl import URL

from .exceptions import (
    TechnoVEConnectionError,
    TechnoVEConnectionTimeoutError,
    TechnoVEError,
)
from .models import Station


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
    # /station/update (POST)
    # /station/schedule/high/activate (POST)
    # /station/set/automatic (POST)
    # /station/control/stop
    # /station/control/start

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

            if response.status // 100 in [4, 5]:
                contents = await response.read()
                response.close()

                raise TechnoVEError(
                    response.status,
                    {"message": contents.decode("utf8")},
                )

            response_data = await response.json()

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
        self.station = Station(await self.request("/station/get/info"))
        return self.station

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
