"""Fault reset button of the AVARMA heat pump."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AvarmaConfigEntry, AvarmaCoordinator
from .entity import AvarmaEntity
from .registers import FAULT_RESET_ADDRESS

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvarmaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([AvarmaFaultResetButton(entry.runtime_data)])


class AvarmaFaultResetButton(AvarmaEntity, ButtonEntity):
    """Writes 1 to the fault reset register."""

    _attr_translation_key = "fault_reset"

    def __init__(self, coordinator: AvarmaCoordinator) -> None:
        super().__init__(coordinator, "fault_reset", FAULT_RESET_ADDRESS)

    @property
    def available(self) -> bool:
        # The register value itself is irrelevant for a button.
        return self.coordinator.last_update_success

    async def async_press(self) -> None:
        await self.coordinator.async_write(FAULT_RESET_ADDRESS, 1)
