"""Remote platform for JVC Projector (2024 LAN Spec)."""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from typing import Any, Iterable

from .jvcprojector import const
from .jvcprojector.const import REMOTE_BUTTON_MAP
from .jvcprojector.projector import JvcProjectorConnectError

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JVCConfigEntry
from .entity import JvcProjectorEntity

_LOGGER = logging.getLogger(__name__)

# Minimal anti-spam protection (only applies to back-to-back commands)
COMMAND_GUARD = 0.15  # remote key presses
POWER_COMMAND_GUARD = 0.75  # only if user double-taps power


async def async_setup_entry(
    hass,
    entry: JVCConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the JVC Projector remote entity."""
    coordinator = entry.runtime_data
    async_add_entities([JvcProjectorRemote(coordinator)])


class JvcProjectorRemote(JvcProjectorEntity, RemoteEntity):
    """JVC Projector remote control (2024 LAN spec)."""

    _attr_name = None
    _attr_supported_features = RemoteEntityFeature.ACTIVITY

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._command_lock = asyncio.Lock()
        self._last_command_time: datetime | None = None
        self._current_activity: str | None = None

    @property
    def is_on(self) -> bool:
        """Return True if projector is on or warming."""
        return self.coordinator.data.get(const.POWER) in (
            const.ON,
            const.WARMING,
        )

    @property
    def current_activity(self) -> str | None:
        """Return the last sent remote command."""
        return self._current_activity

    @property
    def activity_list(self) -> list[str]:
        """Return list of available remote buttons."""
        return list(REMOTE_BUTTON_MAP.keys())

    async def async_turn_on_activity(self, activity: str, **kwargs: Any) -> None:
        """Send a remote command when an activity is selected."""
        await self.async_send_command([activity])
        self._current_activity = activity
        self.async_write_ha_state()

    async def _guard_if_needed(self, min_delay: float) -> None:
        """
        Apply delay ONLY if the previous command was very recent.
        First command is always instant.
        """
        now = datetime.now()

        if self._last_command_time is not None:
            elapsed = (now - self._last_command_time).total_seconds()
            if elapsed < min_delay:
                await asyncio.sleep(min_delay - elapsed)

        self._last_command_time = datetime.now()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the projector on"""
        async with self._command_lock:
            _LOGGER.debug("Power ON for %s", self.device.host)

            await self._guard_if_needed(POWER_COMMAND_GUARD)

            try:
                await self.device.connect(get_info=False)
                await self.device.power_on()

                # Give the projector a moment to transition to WARMING
                await asyncio.sleep(0.3)

                # Force HA to re-read PW immediately
                await self.coordinator.async_refresh()

            except JvcProjectorConnectError as err:
                _LOGGER.error("Power ON failed: %s", err)
                raise

            finally:
                try:
                    await self.device.disconnect()
                except Exception:
                    pass

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the projector off"""
        async with self._command_lock:
            _LOGGER.debug("Power OFF for %s", self.device.host)

            await self._guard_if_needed(POWER_COMMAND_GUARD)

            try:
                await self.device.connect(get_info=False)
                await self.device.power_off()

                # Give the projector a moment to transition to COOLING
                await asyncio.sleep(0.3)

                # Force HA to re-read PW immediately
                await self.coordinator.async_refresh()

            except JvcProjectorConnectError as err:
                _LOGGER.error("Power OFF failed: %s", err)
                raise

            finally:
                try:
                    await self.device.disconnect()
                except Exception:
                    pass

    async def async_send_command(
        self,
        command: Iterable[str],
        **kwargs: Any,
    ) -> None:
        """
        Send remote control key presses.

        Each command can be:
        - A user-friendly button name (e.g., "menu", "up", "ok")
        - A REMOTE_* constant name (e.g., "REMOTE_MENU", "REMOTE_UP")
        - A raw hex code (e.g., "732E")

        Available button names:
        standby, on, menu, up, down, left, right, ok, back, mpc, hide,
        info, input, advanced_menu, picture_mode, color_profile,
        lens_control, setting_memory, gamma_settings, cmd, mode_1,
        mode_2, mode_3, hdmi_1, hdmi_2, lens_ap, anamo, gamma,
        color_temp, 3d_format, pic_adj, natural, cinema
        """
        async with self._command_lock:
            try:
                await self.device.connect(get_info=False)

                for cmd in command:
                    # Normalize command to lowercase for lookup
                    cmd_lower = cmd.lower()

                    # Try user-friendly button name first
                    if cmd_lower in REMOTE_BUTTON_MAP:
                        key_code = REMOTE_BUTTON_MAP[cmd_lower]
                        key_name = cmd_lower
                    # Try REMOTE_* constant name (strip prefix if present)
                    elif cmd_lower.startswith("remote_"):
                        button_name = cmd_lower[7:]  # Remove "remote_" prefix
                        if button_name in REMOTE_BUTTON_MAP:
                            key_code = REMOTE_BUTTON_MAP[button_name]
                            key_name = button_name
                        else:
                            raise ValueError(f"Unknown remote button: {cmd}")
                    # Try as REMOTE_* constant (uppercase)
                    elif hasattr(const, cmd.upper()):
                        key_code = getattr(const, cmd.upper())
                        key_name = cmd.upper()
                    # Try as raw hex code (4 characters)
                    elif len(cmd) == 4 and all(
                        c in "0123456789ABCDEFabcdef" for c in cmd
                    ):
                        key_code = cmd.upper()
                        key_name = f"RAW({key_code})"
                    else:
                        raise ValueError(f"Unknown remote command: {cmd}")

                    _LOGGER.debug(
                        "Sending remote key %s (%s) to %s",
                        key_name,
                        key_code,
                        self.device.host,
                    )

                    await self._guard_if_needed(COMMAND_GUARD)
                    await self.device.remote(key_code)

                    # Update current activity to last sent command
                    if cmd_lower in REMOTE_BUTTON_MAP:
                        self._current_activity = cmd_lower

            except JvcProjectorConnectError as err:
                _LOGGER.error("Remote command failed: %s", err)
                raise
            finally:
                try:
                    await self.device.disconnect()
                except Exception:
                    pass
