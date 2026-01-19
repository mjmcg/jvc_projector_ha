"""Number platform for JVC Projector (2024 D-ILA LAN Spec)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging

from .jvcprojector import command, const

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JVCConfigEntry, JvcProjectorDataUpdateCoordinator
from .entity import JvcProjectorEntity

_LOGGER = logging.getLogger(__name__)

# LD Current Value range mapping (from PMLP spec: Low=109, Med=160, High=219)
LD_CURRENT_MIN = 109  # Minimum LD current value
LD_CURRENT_MAX = 219  # Maximum LD current value


@dataclass(frozen=True, kw_only=True)
class JVCNumberEntityDescription(NumberEntityDescription):
    """Describe JVC number entity."""

    command_code: str


# Number entities supported by the 2024 LAN spec
JVC_NUMBERS = (
    JVCNumberEntityDescription(
        key=const.PMCV,
        translation_key="jvc_ld_power",
        command_code=command.PMCV,
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JVCConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JVC Projector number entities from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        JvcNumber(coordinator, description) for description in JVC_NUMBERS
    )


class JvcNumber(JvcProjectorEntity, NumberEntity):
    """Number entity for JVC Projector (2024 LAN spec)."""

    entity_description: JVCNumberEntityDescription

    def __init__(
        self,
        coordinator: JvcProjectorDataUpdateCoordinator,
        description: JVCNumberEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"

    @property
    def available(self) -> bool:
        """Return if entity is available.

        LD Power control is only available when projector is on.
        """
        if not self.coordinator.last_update_success:
            return False

        power = self.coordinator.data.get(const.POWER)

        # Only enable LD Power control when projector is on
        if self.entity_description.key == const.PMCV:
            return power == const.ON

        return True

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        # Get raw value from coordinator (protocol range: 109-219)
        raw_value = self.coordinator.data.get(self.entity_description.key)

        if raw_value is None:
            return None

        # Convert protocol value to HA display range (1-100)
        try:
            protocol_value = float(raw_value)
            # Clamp to valid protocol range
            protocol_value = max(LD_CURRENT_MIN, min(LD_CURRENT_MAX, protocol_value))
            # Map protocol range (109-219) to HA range (1-100)
            ha_value = (
                (protocol_value - LD_CURRENT_MIN) / (LD_CURRENT_MAX - LD_CURRENT_MIN)
            ) * 99 + 1
            return round(ha_value)
        except (ValueError, TypeError):
            _LOGGER.warning(
                "Invalid %s value: %s",
                self.entity_description.key,
                raw_value,
            )
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the LD Power value."""
        # Clamp HA value to valid range (1-100)
        ha_value = max(1, min(100, value))

        # Map HA range (1-100) to protocol range (109-219)
        protocol_value = LD_CURRENT_MIN + ((ha_value - 1) / 99) * (
            LD_CURRENT_MAX - LD_CURRENT_MIN
        )
        protocol_value = int(round(protocol_value))

        # Convert to hex string (signed 2-byte hexadecimal, 4 characters)
        hex_value = f"{protocol_value:04X}"

        _LOGGER.debug(
            "Setting %s to HA value %d (protocol value %d, hex: %s)",
            self.entity_description.key,
            int(ha_value),
            protocol_value,
            hex_value,
        )

        try:
            # Send command to projector
            await asyncio.wait_for(
                self.coordinator.device.op(
                    self.entity_description.command_code,
                    hex_value,
                ),
                timeout=5.0,
            )

            # Update coordinator data immediately for responsiveness (store protocol value)
            self.coordinator.data[self.entity_description.key] = protocol_value

            # Request coordinator refresh to sync with actual device state
            await self.coordinator.async_request_refresh()

        except asyncio.TimeoutError:
            _LOGGER.error(
                "Timeout setting %s to %d",
                self.entity_description.key,
                int_value,
            )
        except Exception as err:
            _LOGGER.error(
                "Error setting %s to %d: %s",
                self.entity_description.key,
                int_value,
                err,
            )
