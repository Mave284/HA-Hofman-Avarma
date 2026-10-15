"""Fault event of the AVARMA heat pump.

Fires once when a fault bit is newly set. Faults already present when Home
Assistant starts are not fired again; the "Active faults" sensor shows them.
"""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AvarmaConfigEntry, AvarmaCoordinator
from .entity import AvarmaEntity
from .registers import FAULT_ADDRESSES, FAULT_EVENT_TYPES, decode_faults

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvarmaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([AvarmaFaultEvent(entry.runtime_data)])


class AvarmaFaultEvent(AvarmaEntity, EventEntity):
    """Fires when a new fault code appears."""

    _attr_translation_key = "fault"
    _attr_event_types = list(FAULT_EVENT_TYPES)

    def __init__(self, coordinator: AvarmaCoordinator) -> None:
        super().__init__(coordinator, "fault_event", FAULT_ADDRESSES[0])
        # (address, bit) of the faults seen in the last poll; None = no baseline yet
        self._active: set[tuple[int, int]] | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._update_from_data(fire=False)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_from_data(fire=True)
        super()._handle_coordinator_update()

    @callback
    def _update_from_data(self, fire: bool) -> None:
        faults = decode_faults(self.coordinator.data)
        if faults is None:
            return
        current = {(f.address, f.bit) for f in faults}
        if fire and self._active is not None:
            for fault in faults:
                if (fault.address, fault.bit) in self._active:
                    continue
                self._trigger_event(
                    fault.key,
                    {
                        "code": fault.code,
                        "description": fault.description,
                        "register": f"0x{fault.address:04X}",
                        "bit": fault.bit,
                    },
                )
                self.async_write_ha_state()
        self._active = current
