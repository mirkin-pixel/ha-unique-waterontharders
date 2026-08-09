"""Data update coordinator for the Unique Waterontharder integration."""

from __future__ import annotations

from datetime import timedelta, tzinfo
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import UniqueApiAuthError, UniqueApiClient, UniqueApiError
from .const import DEFAULT_SCAN_INTERVAL_MINUTES, DOMAIN

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
        api_timezone: tzinfo,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES
                )
            ),
        )
        self.client = client
        self.api_timezone = api_timezone
        self._warned_no_serial_numbers = False

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data and key it by serial number."""
        try:
            devices = await self.client.async_get_data()
        except UniqueApiAuthError as err:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN, translation_key="invalid_auth"
            ) from err
        except UniqueApiError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="cannot_connect",
                translation_placeholders={"error": str(err)},
            ) from err

        data: dict[str, dict[str, Any]] = {}
        skipped: list[Any] = []
        for device in devices:
            if isinstance(device, dict) and "serienummer" in device:
                data[str(device["serienummer"])] = device
            else:
                skipped.append(device)

        if skipped and not data:
            # Every entity depends on the serial number, so a rename of that
            # field upstream would silently empty the integration. Warn once
            # per outage instead of on every poll.
            if not self._warned_no_serial_numbers:
                self._warned_no_serial_numbers = True
                _LOGGER.warning(
                    "The Unique Smart API returned %d entry/entries, none with a "
                    "'serienummer' field; no devices can be created. First entry: %r",
                    len(skipped),
                    skipped[0],
                )
        elif skipped:
            _LOGGER.debug(
                "Skipped %d entry/entries without a 'serienummer' field: %s",
                len(skipped),
                skipped,
            )

        if data and self._warned_no_serial_numbers:
            self._warned_no_serial_numbers = False
            _LOGGER.info("The Unique Smart API returns serial numbers again")

        _LOGGER.debug("Updated data for serial number(s): %s", sorted(data))

        return data
