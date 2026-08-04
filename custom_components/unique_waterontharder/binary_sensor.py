"""Binary sensor platform for the Unique Waterontharder integration."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import UniqueConfigEntry, UniqueDataUpdateCoordinator
from .entity import UniqueEntity

_LOGGER = logging.getLogger(__name__)

# Updates are centralized through the coordinator
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UniqueConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = entry.runtime_data
    known_serials: set[str] = set()

    def _add_new_softeners() -> None:
        new_serials = set(coordinator.data) - known_serials
        if not new_serials:
            return
        known_serials.update(new_serials)
        async_add_entities(
            UniqueOfflineAlertBinarySensor(coordinator, serial_number)
            for serial_number in new_serials
        )

    _add_new_softeners()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_softeners))


class UniqueOfflineAlertBinarySensor(UniqueEntity, BinarySensorEntity):
    """Binary sensor that is on when the softener has not been seen for a while."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "offline_alert"

    def __init__(
        self, coordinator: UniqueDataUpdateCoordinator, serial_number: str
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, serial_number)
        self._attr_unique_id = f"{serial_number}_offline_alert"

    @property
    def is_on(self) -> bool | None:
        """Return True if the offline alert is active."""
        value = self.device_data.get("offline_alert")
        if value is None:
            return None
        try:
            return bool(int(value))
        except (TypeError, ValueError):
            _LOGGER.debug(
                "Could not parse 'offline_alert' value %r for serial number %s",
                value,
                self._serial_number,
            )
            return None
