"""Tests for the Unique Waterontharder diagnostics."""

from __future__ import annotations

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder.const import DOMAIN
from custom_components.unique_waterontharder.diagnostics import (
    async_get_config_entry_diagnostics,
)

from .conftest import (
    MOCK_API_KEY,
    MOCK_DEVICE,
    MOCK_SERIAL,
    set_api_response,
    setup_integration,
)


async def test_diagnostics(
    hass: HomeAssistant,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that diagnostics redact the API key and the serial number."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: MOCK_API_KEY},
        options={CONF_SCAN_INTERVAL: 30},
    )
    assert await setup_integration(hass, entry)

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics["entry_data"][CONF_API_KEY] == REDACTED
    assert diagnostics["entry_options"] == {CONF_SCAN_INTERVAL: 30}

    device = diagnostics["data"]["device_1"]
    assert device["serienummer"] == REDACTED
    assert device["model"] == "Smart Duo"
    assert device["zout_niveau"] == 80

    # The serial number is not a key either
    assert MOCK_SERIAL not in str(diagnostics)


async def test_diagnostics_with_multiple_softeners(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that every softener gets its own numbered entry."""
    set_api_response(
        mock_api,
        [
            {**MOCK_DEVICE, "serienummer": 87654321, "model": "Smart Solo"},
            MOCK_DEVICE,
        ],
    )
    assert await setup_integration(hass, mock_config_entry)

    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    # Sorted by serial number, so the numbering is stable between reports
    assert [device["model"] for device in diagnostics["data"].values()] == [
        "Smart Duo",
        "Smart Solo",
    ]
