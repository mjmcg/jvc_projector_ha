"""Data update coordinator for JVC Projector (2024 LAN Spec)."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from collections.abc import Mapping

from .jvcprojector.device import JvcProjectorAuthError
from .jvcprojector.projector import JvcProjector, JvcProjectorConnectError, const
from .jvcprojector import command  # 2024 spec

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import NAME

_LOGGER = logging.getLogger(__name__)

# Conservative polling interval — projectors are slow devices
UPDATE_INTERVAL = timedelta(seconds=10)

# Hard timeout for any single poll
POLL_TIMEOUT = 30  # seconds


class JvcProjectorDataUpdateCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinator for JVC Projector state (2024 spec)."""

    def __init__(self, hass: HomeAssistant, device: JvcProjector) -> None:
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=NAME,
            update_interval=UPDATE_INTERVAL,
        )

        self.device = device
        self.unique_id = format_mac(device.mac)

        _LOGGER.debug(
            "Initialized JVC Projector coordinator for %s (%s)",
            device.host,
            self.unique_id,
        )

    async def _async_update_data(self) -> Mapping[str, str | int | None]:
        """Fetch state from the projector.

        One connect → one poll → disconnect.
        """
        _LOGGER.debug("Polling state from %s", self.device.host)

        try:
            # Connect only for this poll
            await asyncio.wait_for(
                self.device.connect(get_info=False),
                timeout=POLL_TIMEOUT,
            )

            # Base state (PW, IP, SOURCE)
            state = await asyncio.wait_for(
                self.device.get_state(),
                timeout=POLL_TIMEOUT,
            )

            # Filter out None values
            result: dict[str, str | int] = {
                k: v for k, v in state.items() if v is not None
            }

            power = result.get(const.POWER)

            # --- Light Source Time (IFLT) ---
            # Only valid when projector is ON
            if power == const.ON:
                try:
                    raw_light_time = await asyncio.wait_for(
                        self.device.ref(command.IFLT),
                        timeout=POLL_TIMEOUT,
                    )
                    _LOGGER.debug(
                        "IFLT response for %s: %s (type: %s)",
                        self.device.host,
                        raw_light_time,
                        type(raw_light_time).__name__,
                    )
                    if raw_light_time and raw_light_time.isdigit():
                        result[const.IFLT] = int(raw_light_time)
                    elif raw_light_time:
                        _LOGGER.warning(
                            "IFLT response not numeric for %s: '%s'",
                            self.device.host,
                            raw_light_time,
                        )
                except Exception as err:
                    _LOGGER.warning(
                        "IFLT error for %s: %s",
                        self.device.host,
                        err,
                    )

                # --- Source Display (IFIS) ---
                try:
                    raw_source_display = await asyncio.wait_for(
                        self.device.ref(command.IFIS),
                        timeout=POLL_TIMEOUT,
                    )
                    if raw_source_display:
                        result[const.IFIS] = raw_source_display
                except asyncio.TimeoutError:
                    _LOGGER.debug(
                        "IFIS timeout for %s",
                        self.device.host,
                    )
                except Exception as err:
                    _LOGGER.debug(
                        "IFIS unavailable while on for %s: %s",
                        self.device.host,
                        err,
                    )

                # --- Input Display (IFIN) ---
                try:
                    raw_input_display = await asyncio.wait_for(
                        self.device.ref(command.IFIN),
                        timeout=POLL_TIMEOUT,
                    )
                    if raw_input_display:
                        result[const.IFIN] = raw_input_display
                        _LOGGER.debug(
                            "IFIN response for %s: %s",
                            self.device.host,
                            raw_input_display,
                        )
                except asyncio.TimeoutError:
                    _LOGGER.warning(
                        "IFIN timeout for %s",
                        self.device.host,
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "IFIN error for %s: %s",
                        self.device.host,
                        err,
                    )

                # --- Content Type (PMCT) ---
                try:
                    raw_content_type = await asyncio.wait_for(
                        self.device.ref(command.PMCT),
                        timeout=POLL_TIMEOUT,
                    )
                    if raw_content_type:
                        result[const.CONTENT_TYPE] = raw_content_type
                        _LOGGER.debug(
                            "PMCT response for %s: %s",
                            self.device.host,
                            raw_content_type,
                        )
                except asyncio.TimeoutError:
                    _LOGGER.warning(
                        "PMCT timeout for %s - command may not be supported or projector is busy",
                        self.device.host,
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "PMCT error for %s: %s",
                        self.device.host,
                        err,
                    )

                # Store content type in diagnostic key too for comparison
                if const.CONTENT_TYPE in result:
                    result[const.CONTENT_TYPE_DIAGNOSTIC] = result[const.CONTENT_TYPE]

                # --- Source Content Type (PMAT) - Auto transition value ---
                try:
                    raw_source_content_type = await asyncio.wait_for(
                        self.device.ref(command.PMAT),
                        timeout=POLL_TIMEOUT,
                    )
                    if raw_source_content_type:
                        result[const.SOURCE_CONTENT_TYPE] = raw_source_content_type
                        _LOGGER.debug(
                            "PMAT response for %s: %s",
                            self.device.host,
                            raw_source_content_type,
                        )
                except asyncio.TimeoutError:
                    _LOGGER.warning(
                        "PMAT timeout for %s - command may not be supported or projector is busy",
                        self.device.host,
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "PMAT error for %s: %s",
                        self.device.host,
                        err,
                    )

                # --- Picture Mode (PMPM) ---
                # Reference command: just "PMPM" per spec, projector responds with PM + 2-byte parameter
                try:
                    raw_picture_mode = await asyncio.wait_for(
                        self.device.ref(command.PMPM),
                        timeout=POLL_TIMEOUT,
                    )
                    if raw_picture_mode:
                        result[const.PICTURE_MODE] = raw_picture_mode
                        _LOGGER.debug(
                            "PMPM response for %s: %s",
                            self.device.host,
                            raw_picture_mode,
                        )
                except asyncio.TimeoutError:
                    _LOGGER.warning(
                        "PMPM timeout for %s - command may not be supported or projector is busy",
                        self.device.host,
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "PMPM error for %s: %s",
                        self.device.host,
                        err,
                    )
            else:
                # Projector is off → skip IFLT poll, show power_off state
                result[const.IFLT] = "power_off"
                _LOGGER.debug(
                    "Skipping IFLT poll for %s (power=%s)",
                    self.device.host,
                    power,
                )

            _LOGGER.debug(
                "State from %s: power=%s input=%s signal=%s iflt=%s ifis=%s picture_mode=%s",
                self.device.host,
                result.get(const.POWER),
                result.get(const.INPUT),
                result.get(const.SOURCE),
                result.get(const.IFLT),
                result.get(const.IFIS),
                result.get(const.PICTURE_MODE),
            )

            return result

        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout polling %s", self.device.host)
            raise UpdateFailed("Timeout polling projector")

        except JvcProjectorAuthError as err:
            _LOGGER.error("Authentication failed for %s", self.device.host)
            raise ConfigEntryAuthFailed("Password authentication failed") from err

        except JvcProjectorConnectError as err:
            _LOGGER.warning("Connection error polling %s: %s", self.device.host, err)
            raise UpdateFailed("Connection error polling projector") from err

        except Exception as err:
            _LOGGER.error(
                "Unexpected error polling %s: %s",
                self.device.host,
                err,
                exc_info=True,
            )
            raise UpdateFailed(f"Unexpected error: {err}")

        finally:
            # Always disconnect — projector prefers short sessions
            try:
                await self.device.disconnect()
            except Exception:
                pass
