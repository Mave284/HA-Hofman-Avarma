"""Sensors for the AVARMA heat pump."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AvarmaConfigEntry, AvarmaCoordinator
from .entity import AvarmaEntity
from .registers import MODE_ADDRESS, MODE_STATES, SENSORS, SensorReg, to_signed

PARALLEL_UPDATES = 0

_TEMPERATURE_DELTA = "temperature_delta"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvarmaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [AvarmaSensor(coordinator, reg) for reg in SENSORS]
    entities.append(AvarmaModeSensor(coordinator))
    async_add_entities(entities)


class AvarmaSensor(AvarmaEntity, SensorEntity):
    """Numeric register value."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: AvarmaCoordinator, reg: SensorReg) -> None:
        super().__init__(coordinator, reg.key, reg.address)
        self._reg = reg
        self._attr_name = reg.name
        self._attr_native_unit_of_measurement = reg.unit
        self._attr_suggested_display_precision = reg.precision
        self._attr_entity_registry_enabled_default = reg.enabled
        if reg.diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if reg.device_class:
            self._attr_device_class = SensorDeviceClass(reg.device_class)
        elif reg.unit == "K":
            self._attr_device_class = SensorDeviceClass(_TEMPERATURE_DELTA)

    @property
    def native_value(self) -> float | int | None:
        raw = self.raw
        if raw is None:
            return None
        value = to_signed(raw) if self._reg.signed else raw
        if self._reg.factor == 1:
            return value
        return round(value * self._reg.factor, self._reg.precision)


class AvarmaModeSensor(AvarmaEntity, SensorEntity):
    """Operating mode (register 4612, undocumented, from the Akkudoktor forum)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "operating_mode"
    _attr_options = list(MODE_STATES.values())

    def __init__(self, coordinator: AvarmaCoordinator) -> None:
        super().__init__(coordinator, "operating_mode", MODE_ADDRESS)

    @property
    def native_value(self) -> str | None:
        raw = self.raw
        if raw is None:
            return None
        return MODE_STATES.get(raw)

    @property
    def extra_state_attributes(self) -> dict[str, int | None]:
        return {"raw_value": self.raw}
