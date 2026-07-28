"""Tests for the Unique Waterontharder sensors."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.unique_waterontharder.const import DOMAIN, UPDATE_INTERVAL
from custom_components.unique_waterontharder.sensor import (
    _as_datetime,
    _as_float,
    _as_number,
)

from .conftest import MOCK_DEVICE, MOCK_SERIAL, set_api_response, setup_integration


def _entity_id(hass: HomeAssistant, key: str) -> str | None:
    return er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{MOCK_SERIAL}_{key}"
    )


async def test_sensor_states(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test the sensor values for a softener."""
    assert await setup_integration(hass, mock_config_entry)

    assert hass.states.get(_entity_id(hass, "salt_level")).state == "80.0"
    assert hass.states.get(_entity_id(hass, "regenerations")).state == "42"
    assert (
        hass.states.get(_entity_id(hass, "average_regeneration_interval")).state
        == "3.5"
    )
    assert hass.states.get(_entity_id(hass, "capacity")).state == "10"

    expected = datetime.fromisoformat("2025-12-25 04:26:22").replace(
        tzinfo=dt_util.get_default_time_zone()
    )
    last_update = hass.states.get(_entity_id(hass, "last_update"))
    assert dt_util.parse_datetime(last_update.state) == expected


async def test_registered_at_disabled_by_default(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that the registration date sensor is disabled by default."""
    assert await setup_integration(hass, mock_config_entry)

    entity_id = _entity_id(hass, "registered_at")
    entry = er.async_get(hass).async_get(entity_id)
    assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION


async def test_device_info(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test the device registry entry for a softener."""
    assert await setup_integration(hass, mock_config_entry)

    device = dr.async_get(hass).async_get_device(identifiers={(DOMAIN, MOCK_SERIAL)})
    assert device is not None
    assert device.manufacturer == "Unique"
    assert device.model == "Smart Duo"
    assert device.serial_number == MOCK_SERIAL
    assert device.name == "Unique Smart Duo"


async def test_softener_missing_from_response(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that entities become unavailable when the softener disappears."""
    assert await setup_integration(hass, mock_config_entry)

    entity_id = _entity_id(hass, "salt_level")
    assert hass.states.get(entity_id).state == "80.0"

    set_api_response(mock_api, [])
    async_fire_time_changed(
        hass, dt_util.utcnow() + UPDATE_INTERVAL + timedelta(seconds=10)
    )
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"


def test_as_datetime_edge_cases() -> None:
    """Test parsing of invalid or empty timestamps."""
    assert _as_datetime(None) is None
    assert _as_datetime("") is None
    assert _as_datetime("not a date") is None


async def test_numeric_sensors_parse_strings(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api: AiohttpClientMocker,
) -> None:
    """Test that count sensors survive string and garbage API values."""
    set_api_response(
        mock_api,
        [{**MOCK_DEVICE, "regeneraties": "42", "capaciteit": "not a number"}],
    )
    assert await setup_integration(hass, mock_config_entry)

    assert hass.states.get(_entity_id(hass, "regenerations")).state == "42"
    assert hass.states.get(_entity_id(hass, "capacity")).state == STATE_UNKNOWN


def test_as_float_edge_cases() -> None:
    """Test parsing of invalid or empty numbers."""
    assert _as_float(None) is None
    assert _as_float("not a number") is None
    assert _as_float("3.5") == 3.5


def test_as_number_edge_cases() -> None:
    """Test that numbers keep their integral form where possible."""
    assert _as_number(None) is None
    assert _as_number("not a number") is None
    assert _as_number("42") == 42
    assert isinstance(_as_number("42"), int)
    assert _as_number("3.5") == 3.5
    assert _as_number("42.0") == 42
    assert isinstance(_as_number("42.0"), int)
    # Large counters must not lose precision through a float round-trip
    assert _as_number(str(2**63 + 1)) == 2**63 + 1
