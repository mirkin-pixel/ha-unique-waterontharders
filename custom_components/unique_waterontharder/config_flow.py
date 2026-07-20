"""Config flow for the Unique Waterontharder integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import UniqueApiAuthError, UniqueApiClient, UniqueApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


class UniqueConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Unique Waterontharder."""

    VERSION = 1

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
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data={CONF_API_KEY: api_key},
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
