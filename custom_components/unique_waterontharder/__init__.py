"""The Unique Waterontharder integration."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .api import UniqueApiClient
from .const import API_TIMEZONE, DOMAIN
from .coordinator import UniqueConfigEntry, UniqueDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: UniqueConfigEntry) -> bool:
    """Set up Unique Waterontharder from a config entry."""
    client = UniqueApiClient(async_get_clientsession(hass), entry.data[CONF_API_KEY])
    api_timezone = await dt_util.async_get_time_zone(API_TIMEZONE)
    coordinator = UniqueDataUpdateCoordinator(
        hass, entry, client, api_timezone or dt_util.get_default_time_zone()
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: UniqueConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: UniqueConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: UniqueConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Allow removing a softener that the API no longer reports.

    Devices are never removed automatically: a partial API response would
    otherwise delete the device along with its history and customizations,
    only to recreate it on the next successful poll.
    """
    known_serials = entry.runtime_data.data
    return not any(
        domain == DOMAIN and serial_number in known_serials
        for domain, serial_number in device_entry.identifiers
    )
