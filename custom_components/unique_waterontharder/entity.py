"""Base entity for the Unique Waterontharder integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_DEVICE_NAME, DOMAIN, MANUFACTURER
from .coordinator import UniqueDataUpdateCoordinator


class UniqueEntity(CoordinatorEntity[UniqueDataUpdateCoordinator]):
    """Base entity for a Unique water softener."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: UniqueDataUpdateCoordinator, serial_number: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._serial_number = serial_number
        # The API may omit 'model' or return it as null; both fall back to a
        # generic name instead of leaking "None" into the device registry.
        model = self.device_data.get("model") or None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            manufacturer=MANUFACTURER,
            model=model,
            serial_number=serial_number,
            name=f"{MANUFACTURER} {model}" if model else DEFAULT_DEVICE_NAME,
        )

    @property
    def device_data(self) -> dict[str, Any]:
        """Return the raw data for this softener."""
        return self.coordinator.data.get(self._serial_number, {})

    @property
    def available(self) -> bool:
        """Return True if the softener is present in the last API response."""
        return super().available and self._serial_number in self.coordinator.data
