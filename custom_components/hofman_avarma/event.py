"""Fault event of the AVARMA heat pump.

Fires once for every fault that newly appears. Faults that are already active
when Home Assistant starts do not fire; the "Active faults" sensor shows them.
"""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AvarmaConfigEntry, AvarmaCoordinator
from .entity import AvarmaEntity
from .faults import EVENT_TYPES, FAULT_ADDRESSES, decode_faults

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
    _attr_event_types = list(EVENT_TYPES)

    def __init__(self, coordinator: AvarmaCoordinator) -> None:
        super().__init__(coordinator, "fault_event", FAULT_ADDRESSES[0])
        # Faults seen in the last poll; None until the first baseline is taken.
        self._active: set[tuple[int, int]] | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._process(fire=False)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._process(fire=True)
        super()._handle_coordinator_update()

    @callback
    def _process(self, fire: bool) -> None:
        faults = decode_faults(self.coordinator.data)
        if faults is None:
            return
        if fire and self._active is not None:
            language = self.hass.config.language if self.hass else None
            for fault in faults:
                if fault.ident in self._active:
                    continue
                self._trigger_event(fault.key, fault.as_dict(language))
                self.async_write_ha_state()
        self._active = {f.ident for f in faults}
