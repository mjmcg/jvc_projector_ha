"""The jvc_projector integration."""

from __future__ import annotations

import asyncio
import logging

from .jvcprojector.device import JvcProjectorAuthError
from .jvcprojector.projector import JvcProjector, JvcProjectorConnectError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from typing import TypeAlias

from .coordinator import JvcProjectorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# JVCConfigEntry = ConfigEntry[JvcProjectorDataUpdateCoordinator]
JVCConfigEntry: TypeAlias = ConfigEntry[JvcProjectorDataUpdateCoordinator]

PLATFORMS = [Platform.BINARY_SENSOR, Platform.REMOTE, Platform.SENSOR, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: JVCConfigEntry) -> bool:
    """Set up integration from a config entry."""
    host = entry.data[CONF_HOST]

    # Create new device and coordinator
    device = JvcProjector(
        host=host,
        port=entry.data[CONF_PORT],
        password=entry.data[CONF_PASSWORD],
    )

    # Initial connection with proper cleanup on failure
    try:
        _LOGGER.debug("Setting up JVC Projector at %s", host)
        await asyncio.wait_for(device.connect(True), timeout=30)
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout connecting to %s during setup", host)
        await device.disconnect()
        raise ConfigEntryNotReady(f"Connection timeout to {host}")
    except JvcProjectorConnectError as err:
        _LOGGER.error("Failed to connect to %s during setup: %s", host, err)
        await device.disconnect()
        raise ConfigEntryNotReady(f"Unable to connect to {host}") from err
    except JvcProjectorAuthError as err:
        _LOGGER.error("Authentication failed for %s", host)
        await device.disconnect()
        raise ConfigEntryAuthFailed("Password authentication failed") from err
    except Exception as err:
        _LOGGER.error("Unexpected error setting up %s: %s", host, err, exc_info=True)
        await device.disconnect()
        raise ConfigEntryNotReady(f"Unexpected error connecting to {host}") from err

    # Create coordinator
    coordinator = JvcProjectorDataUpdateCoordinator(hass, device)
    entry.runtime_data = coordinator

    # Do initial data fetch
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed initial data fetch for %s: %s", host, err, exc_info=True)
        # Clean up on failure
        await coordinator.async_shutdown()
        raise

    # Setup disconnect handler
    async def disconnect_on_stop(event: Event) -> None:
        """Disconnect when Home Assistant stops."""
        _LOGGER.debug("Home Assistant stopping, disconnecting from %s", host)
        await coordinator.async_shutdown()

    # Setup unload handler
    async def disconnect_on_unload() -> None:
        """Disconnect when entry is unloaded."""
        _LOGGER.debug("Entry unloading, disconnecting from %s", host)
        await coordinator.async_shutdown()

    # Register cleanup handlers
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, disconnect_on_stop)
    )
    entry.async_on_unload(disconnect_on_unload)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.debug("Successfully set up JVC Projector at %s", host)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: JVCConfigEntry) -> bool:
    """Unload config entry."""
    host = entry.data[CONF_HOST]
    _LOGGER.debug("Unloading JVC Projector at %s", host)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Coordinator cleanup is handled by disconnect_on_unload callback
        _LOGGER.debug("Successfully unloaded JVC Projector at %s", host)
    else:
        _LOGGER.error("Failed to unload platforms for %s", host)

    return unload_ok
