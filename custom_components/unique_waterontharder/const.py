"""Constants for the Unique Waterontharder integration."""

from datetime import timedelta

DOMAIN = "unique_waterontharder"

API_URL = "https://unique-smart.nl/api/v1/data"

# The API returns timestamps without a UTC offset, in the local time of the
# Dutch service that hosts it. Interpreting them in Home Assistant's own time
# zone would shift them for everyone outside the Netherlands.
API_TIMEZONE = "Europe/Amsterdam"

UPDATE_INTERVAL = timedelta(minutes=10)

MANUFACTURER = "Unique"

# Device name used when the API does not report a model
DEFAULT_DEVICE_NAME = f"{MANUFACTURER} waterontharder"
