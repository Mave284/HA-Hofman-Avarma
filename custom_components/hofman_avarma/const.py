"""Constants for the Hofman Energy AVARMA integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "hofman_avarma"
MANUFACTURER = "Hofman Energy"
MODEL = "AVARMA"

CONF_SLAVE = "slave"
CONF_FRAMER = "framer"
CONF_SCAN_INTERVAL = "scan_interval"

FRAMER_TCP = "tcp"
FRAMER_RTU_OVER_TCP = "rtuovertcp"

DEFAULT_PORT = 502
DEFAULT_SLAVE = 1
DEFAULT_SCAN_INTERVAL = 15  # seconds
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300

# Installer parameters change rarely; read them less often.
PARAM_REFRESH_INTERVAL = timedelta(minutes=10)
