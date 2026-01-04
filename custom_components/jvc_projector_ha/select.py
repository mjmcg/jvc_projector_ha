"""Select platform for JVC Projector (2024 D-ILA LAN Spec)."""

from __future__ import annotations

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

# Select entities supported by the 2024 LAN spec
JVC_SELECTS = (
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
        else:
            _LOGGER.error("Unknown select entity: %s", self.entity_description.key)
            return

        try:
            # Send the operation command
            await self.coordinator.device.op(
                self.entity_description.command_code + code
            )
            _LOGGER.debug(
                "Set %s to %s (code: %s)",
                self.entity_description.key,
                option,
                code,
            )

            # Request a coordinator refresh to update the state
            await self.coordinator.async_request_refresh()

        except Exception as err:
            _LOGGER.error(
                "Failed to set %s to %s: %s",
                self.entity_description.key,
                option,
                err,
            )
