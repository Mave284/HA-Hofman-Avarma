"""On/off switch (P00) of the AVARMA heat pump."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AvarmaConfigEntry, AvarmaCoordinator
from .entity import AvarmaEntity
from .registers import POWER_ADDRESS

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvarmaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([AvarmaPowerSwitch(entry.runtime_data)])


class AvarmaPowerSwitch(AvarmaEntity, SwitchEntity):
    """P00 on/off."""

    _attr_translation_key = "power"

    def __init__(self, coordinator: AvarmaCoordinator) -> None:
        super().__init__(coordinator, "p00_power", POWER_ADDRESS)

    @property
    def is_on(self) -> bool | None:
        raw = self.raw
        return None if raw is None else raw != 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_write(POWER_ADDRESS, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_write(POWER_ADDRESS, 0)
