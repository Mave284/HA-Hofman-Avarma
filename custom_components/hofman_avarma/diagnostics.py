"""Diagnostics: raw register dump for bug reports."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .coordinator import AvarmaConfigEntry

TO_REDACT = {CONF_HOST}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AvarmaConfigEntry
) -> dict[str, Any]:
    coordinator = entry.runtime_data
    data = coordinator.data or {}
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "forum_block_supported": coordinator.forum_supported,
        "param_block_supported": coordinator.params_supported,
        "last_update_success": coordinator.last_update_success,
        "registers": {f"0x{addr:04X}": value for addr, value in sorted(data.items())},
    }
