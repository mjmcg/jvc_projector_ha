"""Remote platform for JVC Projector (2024 LAN Spec)."""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from typing import Any, Iterable

from .jvcprojector import const
from .jvcprojector.projector import JvcProjectorConnectError

from homeassistant.components.remote import RemoteEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JVCConfigEntry
from .entity import JvcProjectorEntity

_LOGGER = logging.getLogger(__name__)

# Minimal anti-spam protection (only applies to back-to-back commands)
COMMAND_GUARD = 0.15        # remote key presses
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
    _attr_has_activity = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._command_lock = asyncio.Lock()
        self._last_command_time: datetime | None = None

    @property
    def is_on(self) -> bool:
        """Return True if projector is on or warming."""
        return self.coordinator.data.get(const.POWER) in (
            const.ON,
            const.WARMING,
        )

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

        Each command must be the name of a REMOTE_* constant,
        e.g. "REMOTE_MENU", "REMOTE_UP".
        """
        async with self._command_lock:
            try:
                await self.device.connect(get_info=False)

                for cmd in command:
                    key_name = cmd.upper()

                    if not hasattr(const, key_name):
                        raise ValueError(f"Unknown remote key: {cmd}")

                    key_code = getattr(const, key_name)

                    _LOGGER.debug(
                        "Sending remote key %s (%s) to %s",
                        key_name,
                        key_code,
                        self.device.host,
                    )

                    await self._guard_if_needed(COMMAND_GUARD)
                    await self.device.remote(key_code)

            except JvcProjectorConnectError as err:
                _LOGGER.error("Remote command failed: %s", err)
                raise
            finally:
                try:
                    await self.device.disconnect()
                except Exception:
                    pass