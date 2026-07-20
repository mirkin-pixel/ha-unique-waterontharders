"""Tests for the Unique Waterontharder diagnostics."""

from __future__ import annotations

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder.diagnostics import (
    async_get_config_entry_diagnostics,
)

from .conftest import MOCK_SERIAL, setup_integration


async def test_diagnostics(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that diagnostics redact the API key."""
    assert await setup_integration(hass, mock_config_entry)

    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    assert diagnostics["entry_data"][CONF_API_KEY] == REDACTED
    assert diagnostics["data"][MOCK_SERIAL]["model"] == "Smart Duo"
    assert diagnostics["data"][MOCK_SERIAL]["zout_niveau"] == 80
