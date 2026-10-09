"""Data update coordinator for the AVARMA heat pump."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import AvarmaClient, AvarmaConnectionError, AvarmaDeviceError, AvarmaError
from .const import DOMAIN, PARAM_REFRESH_INTERVAL
from .registers import BLOCK_FORUM, BLOCK_PARAMS, CORE_BLOCKS, FORBIDDEN_WRITE_ADDRESSES

_LOGGER = logging.getLogger(__name__)

type AvarmaConfigEntry = ConfigEntry[AvarmaCoordinator]


class AvarmaCoordinator(DataUpdateCoordinator[dict[int, int]]):
    """Polls all register blocks; data maps address -> raw 16 bit value."""

    config_entry: AvarmaConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: AvarmaConfigEntry,
        client: AvarmaClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        # None = not probed yet, True/False = supported by this unit
        self.forum_supported: bool | None = None
        self.params_supported: bool | None = None
        self._params_last_read = None
        self._params_dirty = True

    async def _async_update_data(self) -> dict[int, int]:
        data: dict[int, int] = dict(self.data or {})
        try:
            for start, count in CORE_BLOCKS:
                data.update(_as_map(start, await self.client.read_registers(start, count)))
        except AvarmaError as err:
            raise UpdateFailed(f"Error reading heat pump: {err}") from err

        # Optional blocks: a Modbus exception means "not available on this unit",
        # a transport error is retried on the next cycle.
        if self.forum_supported is not False:
            data.update(await self._read_optional(BLOCK_FORUM, "forum"))

        if self.params_supported is not False and self._params_due():
            params = await self._read_optional(BLOCK_PARAMS, "params")
            if params:
                data.update(params)
                self._params_last_read = dt_util.utcnow()
                self._params_dirty = False

        return data

    def _params_due(self) -> bool:
        if self._params_dirty or self._params_last_read is None:
            return True
        return dt_util.utcnow() - self._params_last_read >= PARAM_REFRESH_INTERVAL

    async def _read_optional(self, block: tuple[int, int], name: str) -> dict[int, int]:
        start, count = block
        attr = f"{name}_supported"
        try:
            values = await self.client.read_registers(start, count)
        except AvarmaDeviceError as err:
            if getattr(self, attr) is None:
                _LOGGER.info("Register block %s (0x%04X) not supported: %s", name, start, err)
            setattr(self, attr, False)
            return {}
        except AvarmaConnectionError as err:
            _LOGGER.debug("Reading block %s failed, retrying next cycle: %s", name, err)
            return {}
        setattr(self, attr, True)
        return _as_map(start, values)

    async def async_write(self, address: int, raw: int) -> None:
        """Write one register and refresh."""
        if address in FORBIDDEN_WRITE_ADDRESSES:
            raise HomeAssistantError(f"Writing register 0x{address:04X} is not allowed")
        try:
            await self.client.write_register(address, raw)
        except AvarmaError as err:
            raise HomeAssistantError(f"Writing to the heat pump failed: {err}") from err
        if self.data is not None:
            self.data[address] = raw
            self.async_set_updated_data(self.data)
        if address >= BLOCK_PARAMS[0]:
            self._params_dirty = True
        await self.async_request_refresh()


def _as_map(start: int, values: list[int]) -> dict[int, int]:
    return {start + i: v for i, v in enumerate(values)}
