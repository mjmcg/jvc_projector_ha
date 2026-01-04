"""Sensor platform for JVC Projector (2024 D-ILA LAN Spec)."""

from __future__ import annotations

from dataclasses import dataclass

from .jvcprojector import const

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JVCConfigEntry, JvcProjectorDataUpdateCoordinator
from .entity import JvcProjectorEntity


@dataclass(frozen=True, kw_only=True)
class JVCSensorEntityDescription(SensorEntityDescription):
    """Describe JVC sensor entity."""
    pass


# Sensors supported by the 2024 LAN spec and coordinator
JVC_SENSORS = (
    # Power state (PW)
    JVCSensorEntityDescription(
        key=const.POWER,
        translation_key="jvc_power_state",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[
            const.ON,
            const.STANDBY,
            const.WARMING,
            const.COOLING,
            const.ERROR,
        ],
    ),
    # Input (IP)
    JVCSensorEntityDescription(
        key=const.INPUT,
        translation_key="jvc_input",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[
            const.HDMI1,
            const.HDMI2,
            const.NOSIGNAL,
        ],
    ),
    # Light Source Time (IFLT)
    JVCSensorEntityDescription(
        key=const.IFLT,
        translation_key="jvc_light_source_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement="h",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # Source Display (IFIS) - Current video source format
    JVCSensorEntityDescription(
        key=const.IFIS,
        translation_key="jvc_source_display",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[
            "no_signal",
            "out_of_range",
            "480p",
            "576p",
            "720p50",
            "720p60",
            "1080p24",
            "1080p25",
            "1080p30",
            "1080p50",
            "1080p60",
            "2048x1080_p24",
            "2048x1080_p25",
            "2048x1080_p30",
            "2048x1080_p50",
            "2048x1080_p60",
            "4k_3840_24",
            "4k_3840_25",
            "4k_3840_30",
            "4k_3840_50",
            "4k_3840_60",
            "4k_4096_24",
            "4k_4096_25",
            "4k_4096_30",
            "4k_4096_50",
            "4k_4096_60",
            "vga_640x480",
            "svga_800x600",
            "wuxga_1920x1200",
            "uxga_1600x1200",
            "qxga",
            "wqhd60",
        ],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JVCConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JVC Projector sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        JvcSensor(coordinator, description) for description in JVC_SENSORS
    )


class JvcSensor(JvcProjectorEntity, SensorEntity):
    """Sensor entity for JVC Projector (2024 LAN spec)."""

    entity_description: JVCSensorEntityDescription

    def __init__(
        self,
        coordinator: JvcProjectorDataUpdateCoordinator,
        description: JVCSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"

    @property
    def native_value(self) -> int | str | None:
        """Return the sensor value."""
        value = self.coordinator.data.get(self.entity_description.key)

        if value is None:
            return None

        # IFLT (Light Source Time)
        if self.entity_description.key == const.IFLT:
            power = self.coordinator.data.get(const.POWER)

            # Projector is off → explicit state instead of unknown
            if power in (const.STANDBY, const.COOLING):
                return None

            # Projector is on → parse hours
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        return value