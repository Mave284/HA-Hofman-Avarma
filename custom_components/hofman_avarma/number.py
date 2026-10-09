"""Writable parameters of the AVARMA heat pump."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AvarmaConfigEntry, AvarmaCoordinator
from .entity import AvarmaEntity
from .registers import BLOCK_PARAMS, NUMBERS, NumberReg, to_register, to_signed

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvarmaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(AvarmaNumber(coordinator, reg) for reg in NUMBERS)


class AvarmaNumber(AvarmaEntity, NumberEntity):
    """A parameter register; raw = value * factor."""

    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: AvarmaCoordinator, reg: NumberReg) -> None:
        super().__init__(coordinator, reg.key, reg.address)
        self._reg = reg
        self._attr_name = reg.name
        self._attr_native_min_value = reg.min
        self._attr_native_max_value = reg.max
        self._attr_native_step = reg.step
        self._attr_native_unit_of_measurement = reg.unit
        # Everyday settings are enabled, everything else must be enabled by hand.
        self._attr_entity_registry_enabled_default = reg.everyday
        if reg.address >= BLOCK_PARAMS[0]:
            self._attr_entity_category = EntityCategory.CONFIG

    @property
    def native_value(self) -> float | None:
        raw = self.raw
        if raw is None:
            return None
        value = to_signed(raw) / self._reg.factor
        decimals = max(0, len(f"{self._reg.step:g}".partition(".")[2]))
        return round(value, decimals)

    async def async_set_native_value(self, value: float) -> None:
        if not self._reg.min <= value <= self._reg.max:
            raise HomeAssistantError(
                f"{value} is outside {self._reg.min}..{self._reg.max} for {self._reg.name}"
            )
        raw = to_register(round(value * self._reg.factor))
        await self.coordinator.async_write(self._reg.address, raw)
