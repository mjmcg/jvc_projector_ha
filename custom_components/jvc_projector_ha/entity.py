"""Base Entity for the JVC Projector (2024 LAN Spec)."""

from __future__ import annotations

import logging

from .jvcprojector.projector import JvcProjector

from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, NAME, decode_model
from .coordinator import JvcProjectorDataUpdateCoordinator
from .jvcprojector import const as pj_const

_LOGGER = logging.getLogger(__name__)


class JvcProjectorEntity(CoordinatorEntity[JvcProjectorDataUpdateCoordinator]):
    """Base class for all JVC Projector entities (2024 spec)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: JvcProjectorDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self._attr_unique_id = coordinator.unique_id

        # Build DeviceInfo defensively — nothing here should ever raise
        device_info = {
            "identifiers": {(DOMAIN, coordinator.unique_id)},
            "name": NAME,
            "manufacturer": MANUFACTURER,
            "connections": {(CONNECTION_NETWORK_MAC, coordinator.device.mac)},
        }

        # Optional fields — populate only if available
        # Use decoded model from coordinator data if available
        raw_model = coordinator.data.get(pj_const.MODEL)
        if raw_model:
            device_info["model"] = decode_model(raw_model)

        version = getattr(coordinator.device, "_version", None)
        if version:
            device_info["sw_version"] = version

        self._attr_device_info = DeviceInfo(**device_info)

    @property
    def device(self) -> JvcProjector:
        """Return the underlying projector device."""
        return self.coordinator.device
