"""Select platform for JVC Projector (2024 D-ILA LAN Spec)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging

from .jvcprojector import command, const

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JVCConfigEntry, JvcProjectorDataUpdateCoordinator
from .entity import JvcProjectorEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class JVCSelectEntityDescription(SelectEntityDescription):
    """Describe JVC select entity."""

    command_code: str


# Picture Mode mapping from internal values to command codes (Table 3-19)
PICTURE_MODE_TO_CODE = {
    "cinema": "01",
    "natural": "03",
    "frame_adapt_hdr": "0B",
    "sdr1": "0C",
    "sdr2": "0D",
    "hdr1": "0E",
    "hdr2": "0F",
    "hlg": "14",
    "hdr10+": "15",
    "filmmaker": "17",
    "frame_adapt_hdr2": "18",
    "vivid": "1B",
}

# Content Type mapping from internal values to command codes (Table 3-32)
CONTENT_TYPE_TO_CODE = {
    "auto": "0",
    "sdr": "1",
    "hdr10+": "2",
    "hdr10": "3",
    "hlg": "4",
}

# Picture modes available per content type (from NZ500 manual)
CONTENT_TYPE_PICTURE_MODES = {
    "sdr": ["natural", "cinema", "vivid", "filmmaker", "sdr1", "sdr2"],
    "hdr10+": ["hdr10+"],
    "hdr10": ["frame_adapt_hdr", "frame_adapt_hdr2", "filmmaker", "hdr1", "hdr2"],
    "hlg": ["hlg"],
    "auto": list(PICTURE_MODE_TO_CODE.keys()),  # All modes when in auto
}

# Select entities supported by the 2024 LAN spec
JVC_SELECTS = (
    JVCSelectEntityDescription(
        key=const.CONTENT_TYPE,
        translation_key="jvc_content_type",
        command_code=command.PMCT,
        options=list(CONTENT_TYPE_TO_CODE.keys()),
    ),
    JVCSelectEntityDescription(
        key=const.PICTURE_MODE,
        translation_key="jvc_picture_mode",
        command_code=command.PMPM,
        options=list(PICTURE_MODE_TO_CODE.keys()),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JVCConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JVC Projector select entities from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        JvcSelect(coordinator, description) for description in JVC_SELECTS
    )


class JvcSelect(JvcProjectorEntity, SelectEntity):
    """Select entity for JVC Projector (2024 LAN spec)."""

    entity_description: JVCSelectEntityDescription

    def __init__(
        self,
        coordinator: JvcProjectorDataUpdateCoordinator,
        description: JVCSelectEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(self.entity_description.key)

        if value is None:
            return None

        # Ensure the value is in our options list
        if value in self.entity_description.options:
            return value

        _LOGGER.warning(
            "Unknown %s value: %s",
            self.entity_description.key,
            value,
        )
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available options.

        For picture mode, filter options based on current content type.
        """
        if self.entity_description.key != const.PICTURE_MODE:
            return self.entity_description.options

        # Get current content type from coordinator
        content_type = self.coordinator.data.get(const.CONTENT_TYPE)
        if not content_type or content_type not in CONTENT_TYPE_PICTURE_MODES:
            # Default to all modes if content type unknown
            return self.entity_description.options

        # Return only modes valid for current content type
        return CONTENT_TYPE_PICTURE_MODES[content_type]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self.entity_description.options:
            _LOGGER.error("Invalid option: %s", option)
            return

        # Get the command code for this option
        if self.entity_description.key == const.PICTURE_MODE:
            code = PICTURE_MODE_TO_CODE.get(option)
            if not code:
                _LOGGER.error("No command code for picture mode: %s", option)
                return
        elif self.entity_description.key == const.CONTENT_TYPE:
            code = CONTENT_TYPE_TO_CODE.get(option)
            if not code:
                _LOGGER.error("No command code for content type: %s", option)
                return
        else:
            _LOGGER.error("Unknown select entity: %s", self.entity_description.key)
            return

        try:
            # Log the exact command being sent
            full_command = self.entity_description.command_code + code
            _LOGGER.info(
                "Sending operation command: %s (option: %s, code: %s)",
                full_command,
                option,
                code,
            )

            # Send the operation command
            # Note: Some projector models may not ACK operation commands
            # or may only support certain operations based on current input signal
            try:
                await asyncio.wait_for(
                    self.coordinator.device.op(full_command),
                    timeout=5.0,  # Shorter timeout for operation commands
                )
                _LOGGER.info(
                    "Successfully set %s to %s (command: %s)",
                    self.entity_description.key,
                    option,
                    full_command,
                )
            except asyncio.TimeoutError:
                # Operation commands may timeout if not supported or if the
                # selected mode is not valid for the current input signal type
                _LOGGER.warning(
                    "Operation command %s timed out. The projector may not support "
                    "this operation, or the selected mode (%s) may not be valid "
                    "for the current input signal. Check that the picture mode is "
                    "compatible with your content (SDR/HDR/HLG/etc).",
                    full_command,
                    option,
                )
                # Don't raise - allow the operation to complete silently

            # Brief delay to allow projector to process command
            # before coordinator refresh attempts to reconnect
            await asyncio.sleep(2.0)

            # Request a coordinator refresh to update the state
            await self.coordinator.async_request_refresh()

        except Exception as err:
            _LOGGER.error(
                "Failed to set %s to %s (code: %s): %s",
                self.entity_description.key,
                option,
                code,
                err,
            )
