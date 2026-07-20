"""Sensor platform for the Unique Waterontharder integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .coordinator import UniqueConfigEntry, UniqueDataUpdateCoordinator
from .entity import UniqueEntity

# Updates are centralized through the coordinator
PARALLEL_UPDATES = 0


def _as_datetime(value: Any) -> datetime | None:
    """Parse an API timestamp ('YYYY-MM-DD HH:MM:SS', local time)."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return parsed.replace(tzinfo=dt_util.get_default_time_zone())


def _as_float(value: Any) -> float | None:
    """Parse a numeric value that the API may return as a string."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True, kw_only=True)
class UniqueSensorEntityDescription(SensorEntityDescription):
    """Describes a Unique water softener sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[UniqueSensorEntityDescription, ...] = (
    UniqueSensorEntityDescription(
        key="salt_level",
        translation_key="salt_level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _as_float(data.get("zout_niveau")),
    ),
    UniqueSensorEntityDescription(
        key="regenerations",
        translation_key="regenerations",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("regeneraties"),
    ),
    UniqueSensorEntityDescription(
        key="average_regeneration_interval",
        translation_key="average_regeneration_interval",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _as_float(data.get("gemiddeld")),
    ),
    UniqueSensorEntityDescription(
        key="capacity",
        translation_key="capacity",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("capaciteit"),
    ),
    UniqueSensorEntityDescription(
        key="last_update",
        translation_key="last_update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _as_datetime(data.get("laatste_update")),
    ),
    UniqueSensorEntityDescription(
        key="registered_at",
        translation_key="registered_at",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: _as_datetime(data.get("datum_aangemaakt")),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UniqueConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data
    async_add_entities(
        UniqueSensor(coordinator, serial_number, description)
        for serial_number in coordinator.data
        for description in SENSORS
    )


class UniqueSensor(UniqueEntity, SensorEntity):
    """Sensor for a Unique water softener."""

    entity_description: UniqueSensorEntityDescription

    def __init__(
        self,
        coordinator: UniqueDataUpdateCoordinator,
        serial_number: str,
        description: UniqueSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, serial_number)
        self.entity_description = description
        self._attr_unique_id = f"{serial_number}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.device_data)
