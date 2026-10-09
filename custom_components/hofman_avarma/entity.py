"""Base entity for the AVARMA heat pump."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import AvarmaCoordinator


class AvarmaEntity(CoordinatorEntity[AvarmaCoordinator]):
    """Common device info, unique id and availability."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AvarmaCoordinator, key: str, address: int) -> None:
        super().__init__(coordinator)
        self._address = address
        entry = coordinator.config_entry
        base = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{base}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, base)},
            name="AVARMA",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=None,
        )

    @property
    def raw(self) -> int | None:
        data = self.coordinator.data
        return None if data is None else data.get(self._address)

    @property
    def available(self) -> bool:
        return super().available and self.raw is not None
