"""Tests for `technove.TechnoVE`."""

import asyncio

import aiohttp
import pytest
from aresponses import Response, ResponsesMockServer

from technove import TechnoVE
from technove.exceptions import TechnoVEConnectionError, TechnoVEError


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
async def test_internal_session(aresponses: ResponsesMockServer) -> None:
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
async def test_empty_full_responses(aresponses: ResponsesMockServer) -> None:
    """Test failure handling of full data request TechnoVE device state."""
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
