"""Status bits of the AVARMA heat pump."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AvarmaConfigEntry, AvarmaCoordinator
from .entity import AvarmaEntity
from .registers import BITS, BitReg

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvarmaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(AvarmaBit(coordinator, reg) for reg in BITS)


class AvarmaBit(AvarmaEntity, BinarySensorEntity):
    """One bit of a status register."""

    def __init__(self, coordinator: AvarmaCoordinator, reg: BitReg) -> None:
        super().__init__(coordinator, reg.key, reg.address)
        self._mask = 1 << reg.bit
        self._attr_name = reg.name
        if reg.diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool | None:
        raw = self.raw
        return None if raw is None else bool(raw & self._mask)
