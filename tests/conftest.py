"""Fixtures for the Unique Waterontharder tests."""

from __future__ import annotations

from typing import Any

import pytest

from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder.const import API_URL, DOMAIN

MOCK_API_KEY = "test-api-key"
MOCK_SERIAL = "12345678"

MOCK_DEVICE: dict[str, Any] = {
    "serienummer": 12345678,
    "model": "Smart Duo",
    "capaciteit": 10,
    "datum_aangemaakt": "2023-09-13 10:34:11",
    "laatste_update": "2025-12-25 04:26:22",
    "regeneraties": 42,
    "gemiddeld": "3.5",
    "offline_alert": 0,
    "zout_niveau": 80,
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading custom integrations in all tests."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Unique Waterontharder",
        data={CONF_API_KEY: MOCK_API_KEY},
    )


@pytest.fixture
def mock_api(aioclient_mock: AiohttpClientMocker) -> AiohttpClientMocker:
    """Mock a successful API response with one softener."""
    aioclient_mock.get(API_URL, json=[MOCK_DEVICE])
    return aioclient_mock


def set_api_response(
    aioclient_mock: AiohttpClientMocker, devices: list[dict[str, Any]]
) -> None:
    """Replace the mocked API response."""
    aioclient_mock.clear_requests()
    aioclient_mock.get(API_URL, json=devices)


async def setup_integration(hass: HomeAssistant, entry: MockConfigEntry) -> bool:
    """Set up the integration with a config entry."""
    entry.add_to_hass(hass)
    result = await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return result
