"""Config flow for the Unique Waterontharder integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL, UnitOfTime
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)
import voluptuous as vol

from .api import UniqueApiAuthError, UniqueApiClient, UniqueApiError
from .const import (
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    MAX_SCAN_INTERVAL_MINUTES,
    MIN_SCAN_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


class UniqueConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Unique Waterontharder."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> UniqueOptionsFlow:
        """Return the options flow."""
        return UniqueOptionsFlow()

    async def _async_validate_api_key(self, api_key: str) -> str | None:
        """Validate the API key. Returns an error key or None."""
        client = UniqueApiClient(async_get_clientsession(self.hass), api_key)
        try:
            await client.async_get_data()
        except UniqueApiAuthError:
            return "invalid_auth"
        except UniqueApiError:
            return "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception while validating API key")
            return "unknown"
        return None

    def _async_store_api_key(
        self, entry: ConfigEntry, api_key: str, reason: str
    ) -> ConfigFlowResult:
        """Store a new API key on an existing entry and reload it.

        The entry's update listener performs the reload, which is what Home
        Assistant expects of an integration that has one. Re-entering the same
        key leaves the entry unchanged and therefore does not notify that
        listener, so the reload is scheduled here instead: an entry that failed
        to set up must still recover.
        """
        if not self.hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_API_KEY: api_key}
        ):
            self.hass.config_entries.async_schedule_reload(entry.entry_id)
        return self.async_abort(reason=reason)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            self._async_abort_entries_match({CONF_API_KEY: api_key})
            error = await self._async_validate_api_key(api_key)
            if error is None:
                return self.async_create_entry(
                    title="Unique Waterontharder",
                    data={CONF_API_KEY: api_key},
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication when the API key is no longer valid."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a new API key."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            error = await self._async_validate_api_key(api_key)
            if error is None:
                return self._async_store_api_key(
                    self._get_reauth_entry(), api_key, "reauth_successful"
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a new API key for an existing entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            if any(
                other.data[CONF_API_KEY] == api_key
                for other in self._async_current_entries()
                if other.entry_id != entry.entry_id
            ):
                return self.async_abort(reason="already_configured")
            error = await self._async_validate_api_key(api_key)
            if error is None:
                return self._async_store_api_key(
                    entry, api_key, "reconfigure_successful"
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class UniqueOptionsFlow(OptionsFlow):
    """Handle the options for an existing entry."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the poll interval."""
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL])}
            )

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL_MINUTES,
                            max=MAX_SCAN_INTERVAL_MINUTES,
                            step=1,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement=UnitOfTime.MINUTES,
                        )
                    )
                }
            ),
        )
