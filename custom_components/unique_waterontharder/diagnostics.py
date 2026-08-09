"""Diagnostics support for the Unique Waterontharder integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .coordinator import UniqueConfigEntry

TO_REDACT = {CONF_API_KEY, "serienummer"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: UniqueConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    # Serial numbers identify a customer's hardware and are the keys of the
    # coordinator data, where async_redact_data cannot reach them. They are
    # replaced by a stable index so that a report stays readable with more
    # than one softener.
    devices = [
        async_redact_data(device, TO_REDACT)
        for _, device in sorted(entry.runtime_data.data.items())
    ]
    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "entry_options": dict(entry.options),
        "data": {f"device_{index}": device for index, device in enumerate(devices, 1)},
    }
