"""Tests for `technove.TechnoVE`."""

import asyncio

import aiohttp
import pytest
from aresponses import Response, ResponsesMockServer

from technove import Station, Status, TechnoVE
from technove.exceptions import (
    TechnoVEConnectionError,
    TechnoVEError,
    TechnoVEOutOfBoundError,
)


@pytest.mark.asyncio
async def test_json_request(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        response = await technove.request("/")
        assert response["status"] == "ok"


@pytest.mark.asyncio
async def test_json_request_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with TechnoVE("example.com") as technove:
        response = await technove.request("/")
        assert response["status"] == "ok"


@pytest.mark.asyncio
async def test_text_request(aresponses: ResponsesMockServer) -> None:
    """Test plain text response is handled correctly."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text="ok",
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        response = await technove.request("/")
        assert response == "ok"


@pytest.mark.asyncio
async def test_post_request(aresponses: ResponsesMockServer) -> None:
    """Test POST requests are handled correctly."""
    aresponses.add(
        "example.com",
        "/",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        response = await technove.request("/", method="POST")
        assert response["status"] == "ok"


@pytest.mark.asyncio
async def test_backoff(aresponses: ResponsesMockServer) -> None:
    """Test requests are handled with retries."""

    async def response_handler(_: aiohttp.ClientResponse) -> Response:
        """Response handler for this test."""
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body='{"status": "nok"}', headers={"Content-Type": "application/json"}
        )

    aresponses.add(
        "example.com",
        "/",
        "GET",
        response_handler,
        repeat=2,
    )
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )

    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session, request_timeout=0.1)
        response = await technove.request("/")
        assert response["status"] == "ok"


@pytest.mark.asyncio
async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from TechnoVE."""

    # Faking a timeout by sleeping
    async def response_handler(_: aiohttp.ClientResponse) -> Response:
        """Response handler for this test."""
        await asyncio.sleep(0.2)
        return aresponses.Response(body="Vive la poutine!")

    # Backoff will try 3 times
    aresponses.add("example.com", "/", "GET", response_handler)
    aresponses.add("example.com", "/", "GET", response_handler)
    aresponses.add("example.com", "/", "GET", response_handler)

    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session, request_timeout=0.1)
        with pytest.raises(TechnoVEConnectionError):
            assert await technove.request("/")


@pytest.mark.asyncio
async def test_http_error400(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 404 response handling."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(text="syrop!", status=404),
    )

    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        with pytest.raises(TechnoVEError):
            assert await technove.request("/")


@pytest.mark.asyncio
async def test_http_error500(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 500 response handling."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(
            body=b'{"status":"nok"}',
            status=500,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        with pytest.raises(TechnoVEError):
            assert await technove.request("/")


@pytest.mark.asyncio
async def test_update_empty_responses(aresponses: ResponsesMockServer) -> None:
    """Test failure handling of data request TechnoVE device state."""
    aresponses.add(
        "example.com",
        "/station/get/info",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text="{}",
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        with pytest.raises(TechnoVEError):
            await technove.update()


@pytest.mark.asyncio
async def test_update_partial_responses(aresponses: ResponsesMockServer) -> None:
    """Test handling of data request TechnoVE device state."""
    aresponses.add(
        "example.com",
        "/station/get/info",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"name":"testing"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        station = await technove.update()
        assert station.info.name == "testing"


@pytest.mark.asyncio
async def test_update_unknown_status(aresponses: ResponsesMockServer) -> None:
    """Test handling of unknown status received from the API."""
    aresponses.add(
        "example.com",
        "/station/get/info",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"name":"testing", "status":"1234"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        station = await technove.update()
        assert station.info.name == "testing"
        assert station.info.status == Status.UNKNOWN


@pytest.mark.asyncio
async def test_set_auto_charge(aresponses: ResponsesMockServer) -> None:
    """Test that enabling auto_charge calls the right API."""
    aresponses.add(
        "example.com",
        "/station/set/automatic",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="ok",
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        await technove.set_auto_charge(enabled=True)
        aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_set_charging_enabled(aresponses: ResponsesMockServer) -> None:
    """Test that changing charging_enabled calls the right API."""
    aresponses.add(
        "example.com",
        "/station/control/start",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="ok",
        ),
    )
    aresponses.add(
        "example.com",
        "/station/control/stop",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="ok",
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        technove.station = Station({"auto_charge": False})
        await technove.set_charging_enabled(enabled=True)
        await technove.set_charging_enabled(enabled=False)
        aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_set_charging_enabled_auto_charge() -> None:
    """Test failure when enabling charging manually and auto-charge is enabled."""
    technove = TechnoVE("example.com")
    technove.station = Station({"auto_charge": True})
    with pytest.raises(TechnoVEError):
        await technove.set_charging_enabled(enabled=True)


@pytest.mark.asyncio
async def test_set_max_current(aresponses: ResponsesMockServer) -> None:
    """Test that changing set_max_current calls the right API."""
    aresponses.add(
        "example.com",
        "/station/control/partage",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="ok",
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        technove.station = Station({"maxStationCurrent": 32, "inSharingMode": False})
        await technove.set_max_current(32)
        aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_set_max_current_sharing_mode(aresponses: ResponsesMockServer) -> None:
    """Test failure when setting the max current and in_sharing_mode is enabled."""
    aresponses.add(
        "example.com",
        "/station/control/partage",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="bad",
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        technove.station = Station({"maxStationCurrent": 32, "inSharingMode": True})
        with pytest.raises(TechnoVEError):
            await technove.set_max_current(32)


@pytest.mark.asyncio
async def test_set_max_current_too_low() -> None:
    """Test failure when setting the max current below 8."""
    technove = TechnoVE("example.com")
    technove.station = Station({"maxStationCurrent": 32, "inSharingMode": False})
    with pytest.raises(TechnoVEOutOfBoundError):
        await technove.set_max_current(2)


@pytest.mark.asyncio
async def test_set_max_current_too_high() -> None:
    """Test failure when setting the max current below 0."""
    technove = TechnoVE("example.com")
    technove.station = Station({"maxStationCurrent": 32, "inSharingMode": False})
    with pytest.raises(TechnoVEOutOfBoundError):
        await technove.set_max_current(48)


@pytest.mark.asyncio
async def test_set_high_tariff_schedule(aresponses: ResponsesMockServer) -> None:
    """Test that enabling high tariff schedule calls the right API."""
    aresponses.add(
        "example.com",
        "/station/schedule/high/activate",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="ok",
        ),
    )
    async with aiohttp.ClientSession() as session:
        technove = TechnoVE("example.com", session=session)
        await technove.set_high_tariff_schedule(enabled=True)
        aresponses.assert_plan_strictly_followed()
