"""Tests for the Unique Waterontharder integration setup."""

from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp
from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder import async_remove_config_entry_device
from custom_components.unique_waterontharder.const import (
    API_URL,
    DOMAIN,
    UPDATE_INTERVAL,
)

from .conftest import MOCK_DEVICE, MOCK_SERIAL, set_api_response, setup_integration


async def test_setup_and_unload(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test a successful setup and unload."""
    assert await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_auth_failed_starts_reauth(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that an invalid API key during setup starts a reauth flow."""
    aioclient_mock.get(API_URL, status=403)

    assert not await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR

    flows = hass.config_entries.flow.async_progress()
    assert len(flows) == 1
    assert flows[0]["context"]["source"] == SOURCE_REAUTH


async def test_setup_cannot_connect_retries(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a connection problem during setup leads to a retry."""
    aioclient_mock.get(API_URL, exc=aiohttp.ClientError("boom"))

    assert not await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_new_softener_added_after_setup(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that a softener appearing in the API later gets entities."""
    assert await setup_integration(hass, mock_config_entry)

    entity_registry = er.async_get(hass)
    new_serial = "87654321"
    assert (
        entity_registry.async_get_entity_id(
            "sensor", DOMAIN, f"{new_serial}_salt_level"
        )
        is None
    )

    set_api_response(
        mock_api,
        [MOCK_DEVICE, {**MOCK_DEVICE, "serienummer": int(new_serial)}],
    )
    async_fire_time_changed(
        hass, dt_util.utcnow() + UPDATE_INTERVAL + timedelta(seconds=10)
    )
    await hass.async_block_till_done()

    for platform, key in (
        ("sensor", "salt_level"),
        ("binary_sensor", "offline_alert"),
    ):
        entity_id = entity_registry.async_get_entity_id(
            platform, DOMAIN, f"{new_serial}_{key}"
        )
        assert entity_id is not None
        assert hass.states.get(entity_id).state not in ("unavailable", None)

    # The original softener is still there and untouched
    assert (
        hass.states.get(
            entity_registry.async_get_entity_id(
                "sensor", DOMAIN, f"{MOCK_SERIAL}_salt_level"
            )
        ).state
        == "80.0"
    )


async def test_response_without_serial_numbers_warns_once(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    aioclient_mock: AiohttpClientMocker,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that unusable API entries are reported once, and recovery is logged."""
    caplog.set_level(logging.INFO)
    unusable = [{"model": "Smart Duo"}]
    aioclient_mock.get(API_URL, json=unusable)

    assert await setup_integration(hass, mock_config_entry)
    assert caplog.text.count("none with a 'serienummer' field") == 1

    async def _poll_with(devices: list[dict]) -> None:
        set_api_response(aioclient_mock, devices)
        async_fire_time_changed(
            hass, dt_util.utcnow() + UPDATE_INTERVAL + timedelta(seconds=10)
        )
        await hass.async_block_till_done()

    # The same broken response does not warn again
    await _poll_with(unusable)
    assert caplog.text.count("none with a 'serienummer' field") == 1

    # Recovery is logged, and a later relapse warns again
    await _poll_with([MOCK_DEVICE])
    assert "returns serial numbers again" in caplog.text

    await _poll_with(unusable)
    assert caplog.text.count("none with a 'serienummer' field") == 2


async def test_stale_device_can_be_removed(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that only softeners missing from the API may be removed."""
    assert await setup_integration(hass, mock_config_entry)

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, MOCK_SERIAL)})
    assert device is not None

    # A softener that the API still reports must not be removable
    assert not await async_remove_config_entry_device(hass, mock_config_entry, device)

    set_api_response(mock_api, [])
    async_fire_time_changed(
        hass, dt_util.utcnow() + UPDATE_INTERVAL + timedelta(seconds=10)
    )
    await hass.async_block_till_done()

    assert await async_remove_config_entry_device(hass, mock_config_entry, device)


async def test_update_failure_marks_entities_unavailable(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that entities become unavailable when an update fails."""
    assert await setup_integration(hass, mock_config_entry)

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, f"{MOCK_SERIAL}_salt_level"
    )
    assert hass.states.get(entity_id).state != "unavailable"

    mock_api.clear_requests()
    mock_api.get(API_URL, exc=aiohttp.ClientError("boom"))
    async_fire_time_changed(
        hass, dt_util.utcnow() + UPDATE_INTERVAL + timedelta(seconds=10)
    )
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"
