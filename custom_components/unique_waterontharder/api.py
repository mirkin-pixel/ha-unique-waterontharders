"""API client for the Unique Smart API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_URL

_LOGGER = logging.getLogger(__name__)


class UniqueApiError(Exception):
    """Generic API error."""


class UniqueApiAuthError(UniqueApiError):
    """Authentication failed (invalid API key)."""


class UniqueApiClient:
    """Client for the Unique Smart API."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        """Initialize the client."""
        self._session = session
        self._api_key = api_key

    async def async_get_data(self) -> list[dict[str, Any]]:
        """Fetch the list of water softeners."""
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with asyncio.timeout(30):
                response = await self._session.get(API_URL, headers=headers)
                _LOGGER.debug("GET %s returned HTTP %s", API_URL, response.status)
                if response.status in (401, 403):
                    raise UniqueApiAuthError("Invalid API key")
                response.raise_for_status()
                data = await response.json(content_type=None)
        except UniqueApiAuthError:
            raise
        except TimeoutError as err:
            raise UniqueApiError("Timeout connecting to the Unique Smart API") from err
        except aiohttp.ClientError as err:
            raise UniqueApiError(
                f"Error communicating with the Unique Smart API: {err}"
            ) from err
        except ValueError as err:
            # An empty or malformed body would otherwise surface as an
            # unexpected error, complete with a traceback in the log.
            raise UniqueApiError(
                f"Could not decode the response from the Unique Smart API: {err}"
            ) from err

        if not isinstance(data, list):
            raise UniqueApiError(
                f"Unexpected response from the Unique Smart API: {data!r}"
            )

        _LOGGER.debug("Received %d device(s) from the API: %s", len(data), data)

        return data
