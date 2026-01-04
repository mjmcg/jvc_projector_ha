"""Binary Sensor platform for JVC Projector integration (2024 spec)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .jvcprojector import const

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JVCConfigEntry, JvcProjectorDataUpdateCoordinator
from .entity import JvcProjectorEntity


@dataclass(frozen=True, kw_only=True)
class JVCBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe JVC binary sensor entity."""

    value_fn: Callable[[str | None], bool | None]


JVC_BINARY_SENSORS = (
    # Projector powered (ON or WARMING)
    JVCBinarySensorEntityDescription(
        key=const.POWER,
        translation_key="jvc_power",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda v: v in (const.ON, const.WARMING) if v else None,
    ),
    # Input signal present
    JVCBinarySensorEntityDescription(
        key=const.SOURCE,
        translation_key="jvc_signal_present",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda v: v == const.SIGNAL if v else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JVCConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the JVC Projector binary sensor platform."""
    coordinator: JvcProjectorDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        JvcBinarySensor(coordinator, description)
        for description in JVC_BINARY_SENSORS
    )


class JvcBinarySensor(JvcProjectorEntity, BinarySensorEntity):
    """Binary sensor for JVC Projector."""

    entity_description: JVCBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: JvcProjectorDataUpdateCoordinator,
        description: JVCBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.entity_description.key)
        return self.entity_description.value_fn(value)