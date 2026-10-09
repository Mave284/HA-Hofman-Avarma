"""Hofman Energy AVARMA heat pump integration (Modbus TCP / RTU over TCP)."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .api import AvarmaClient
from .const import (
    CONF_FRAMER,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DEFAULT_SCAN_INTERVAL,
    FRAMER_TCP,
)
from .coordinator import AvarmaConfigEntry, AvarmaCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: AvarmaConfigEntry) -> bool:
    """Set up the heat pump from a config entry."""
    client = AvarmaClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        slave=entry.data[CONF_SLAVE],
        framer=entry.data.get(CONF_FRAMER, FRAMER_TCP),
    )
    coordinator = AvarmaCoordinator(
        hass,
        entry,
        client,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await client.close()
        raise

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AvarmaConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.client.close()
    return unloaded


async def _async_reload(hass: HomeAssistant, entry: AvarmaConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
