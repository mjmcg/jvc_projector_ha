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
from .const import decode_model
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
            "No Signal",
            "Out of Range",
            "480p",
            "576p",
            "720p50",
            "720p60",
            "1080p24",
            "1080p25",
            "1080p30",
            "1080p50",
            "1080p60",
            "2048x1080 p24",
            "2048x1080 p25",
            "2048x1080 p30",
            "2048x1080 p50",
            "2048x1080 p60",
            "4k(3840)24",
            "4k(3840)25",
            "4k(3840)30",
            "4k(3840)50",
            "4k(3840)60",
            "4k(4096)24",
            "4k(4096)25",
            "4k(4096)30",
            "4k(4096)50",
            "4k(4096)60",
            "VGA(640x480)",
            "SVGA(800x600)",
            "WUXGA(1920x1200)",
            "UXGA(1600x1200)",
            "QXGA",
            "WQHD60",
        ],
    ),
    # Input Display (IFIN) - Diagnostic to show which HDMI input
    JVCSensorEntityDescription(
        key=const.IFIN,
        translation_key="jvc_input_display",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        enabled_default=False,
        options=[
            "hdmi1",
            "hdmi2",
        ],
    ),
    # Content Type (PMAT) - Content type detected from source signal
    # Using 'auto_content_type' key to align with PMAT command spec
    JVCSensorEntityDescription(
        key=const.auto_content_type,
        translation_key="jvc_auto_content_type",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[
            "sdr",
            "hdr10+",
            "hdr10",
            "hlg",
        ],
    ),
    # Colorimetry (IFCM) - Color space information from source
    JVCSensorEntityDescription(
        key=const.IFCM,
        translation_key="jvc_colorimetry",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[
            "no_data",
            "bt601",
            "bt709",
            "xvycc601",
            "xvycc709",
            "sycc601",
            "adobe_ycc601",
            "adobe_rgb",
            "bt2020_cl",
            "bt2020_ncl",
            "srgb",
            "dci_p3_d65",
            "dci_p3_theater",
        ],
    ),
    # Model - Projector model name
    JVCSensorEntityDescription(
        key=const.MODEL,
        translation_key="jvc_model",
        entity_category=EntityCategory.DIAGNOSTIC,
        enabled_default=False,
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

        # IFIS (Source Display) - Show "No Signal" when projector is off
        if self.entity_description.key == const.IFIS:
            power = self.coordinator.data.get(const.POWER)

            # Projector is off → show "No Signal" instead of Unknown
            if power in (const.STANDBY, const.COOLING):
                return "No Signal"

        # IFCM (Colorimetry) - Show "no_data" when projector is off
        if self.entity_description.key == const.IFCM:
            power = self.coordinator.data.get(const.POWER)

            # Projector is off → show "no_data" instead of Unknown
            if power in (const.STANDBY, const.COOLING):
                return "no_data"

        # MODEL - Decode internal model codes to actual model names
        if self.entity_description.key == const.MODEL:
            return decode_model(value)

        return value
