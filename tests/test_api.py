"""Tests for the Unique Smart API client."""

from __future__ import annotations

from json import dumps as json_dumps
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder.api import (
    UniqueApiAuthError,
    UniqueApiClient,
    UniqueApiError,
)
from custom_components.unique_waterontharder.const import API_URL

from .conftest import MOCK_API_KEY, MOCK_DEVICE


def _client(hass: HomeAssistant) -> UniqueApiClient:
    return UniqueApiClient(async_get_clientsession(hass), MOCK_API_KEY)


async def test_get_data(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test a successful request, including the authorization header."""
    aioclient_mock.get(API_URL, json=[MOCK_DEVICE])

    assert await _client(hass).async_get_data() == [MOCK_DEVICE]

    headers = aioclient_mock.mock_calls[0][3]
    assert headers["Authorization"] == f"Bearer {MOCK_API_KEY}"


async def test_timeout(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test that a timeout is reported as an API error."""
    aioclient_mock.get(API_URL, exc=TimeoutError)

    with pytest.raises(UniqueApiError, match="Timeout"):
        await _client(hass).async_get_data()


async def test_server_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test that an HTTP 500 is reported as an API error, not an auth error."""
    aioclient_mock.get(API_URL, status=500)

    with pytest.raises(UniqueApiError) as err:
        await _client(hass).async_get_data()
    assert not isinstance(err.value, UniqueApiAuthError)


@pytest.mark.parametrize(
    "response",
    [{"error": "nope"}, "a string", None],
    ids=["object", "string", "null"],
)
async def test_unexpected_response(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, response: Any
) -> None:
    """Test that a response that is not a list is reported as an API error."""
    aioclient_mock.get(API_URL, text=json_dumps(response))

    with pytest.raises(UniqueApiError, match="Unexpected response"):
        await _client(hass).async_get_data()


@pytest.mark.parametrize(
    "body", ["", "<html>maintenance</html>"], ids=["empty", "html"]
)
async def test_undecodable_response(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, body: str
) -> None:
    """Test that a body that is not JSON at all is reported as an API error."""
    aioclient_mock.get(API_URL, text=body)

    with pytest.raises(UniqueApiError, match="Could not decode"):
        await _client(hass).async_get_data()


@pytest.mark.parametrize("status", [401, 403])
async def test_auth_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, status: int
) -> None:
    """Test that a rejected API key raises an auth error."""
    aioclient_mock.get(API_URL, status=status)

    with pytest.raises(UniqueApiAuthError):
        await _client(hass).async_get_data()
