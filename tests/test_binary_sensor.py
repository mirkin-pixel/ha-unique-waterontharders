"""Tests for the Unique Waterontharder binary sensors."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder.const import DOMAIN, UPDATE_INTERVAL

from .conftest import MOCK_DEVICE, MOCK_SERIAL, set_api_response, setup_integration


async def _refresh(hass: HomeAssistant) -> None:
    async_fire_time_changed(
        hass, dt_util.utcnow() + UPDATE_INTERVAL + timedelta(seconds=10)
    )
    await hass.async_block_till_done()


async def test_offline_alert(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test the offline alert binary sensor."""
    assert await setup_integration(hass, mock_config_entry)

    entity_id = er.async_get(hass).async_get_entity_id(
        "binary_sensor", DOMAIN, f"{MOCK_SERIAL}_offline_alert"
    )
    assert hass.states.get(entity_id).state == STATE_OFF

    set_api_response(mock_api, [{**MOCK_DEVICE, "offline_alert": 1}])
    await _refresh(hass)
    assert hass.states.get(entity_id).state == STATE_ON

    device_without_alert = {
        k: v for k, v in MOCK_DEVICE.items() if k != "offline_alert"
    }
    set_api_response(mock_api, [device_without_alert])
    await _refresh(hass)
    assert hass.states.get(entity_id).state == STATE_UNKNOWN
