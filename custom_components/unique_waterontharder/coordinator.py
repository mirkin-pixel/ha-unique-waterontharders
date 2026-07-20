"""Data update coordinator for the Unique Waterontharder integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import UniqueApiAuthError, UniqueApiClient, UniqueApiError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

type UniqueConfigEntry = ConfigEntry[UniqueDataUpdateCoordinator]


class UniqueDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinator that polls the Unique Smart API."""

    config_entry: UniqueConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: UniqueConfigEntry,
        client: UniqueApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data and key it by serial number."""
        try:
            devices = await self.client.async_get_data()
        except UniqueApiAuthError as err:
            raise ConfigEntryAuthFailed(err) from err
        except UniqueApiError as err:
            raise UpdateFailed(err) from err

        return {
            str(device["serienummer"]): device
            for device in devices
            if "serienummer" in device
        }
