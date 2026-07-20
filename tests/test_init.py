"""Tests for the Unique Waterontharder integration setup."""

from __future__ import annotations

from datetime import timedelta

import aiohttp

from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder.const import (
    API_URL,
    DOMAIN,
    UPDATE_INTERVAL,
)

from .conftest import MOCK_SERIAL, setup_integration


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
