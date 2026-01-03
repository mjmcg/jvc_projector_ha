"""Module for interacting with a JVC Projector."""

from __future__ import annotations

import logging

from . import command, const
from .command import JvcCommand
from .connection import resolve
from .device import JvcDevice
from .error import JvcProjectorConnectError, JvcProjectorError

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 20554
DEFAULT_TIMEOUT = 15.0


class JvcProjector:
    """Class for interacting with a JVC Projector."""

    def __init__(
        self,
        host: str,
        *,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
        password: str | None = None,
    ) -> None:
        """Initialize class."""
        self._host = host
        self._port = port
        self._timeout = timeout
        self._password = password

        self._device: JvcDevice | None = None
        self._ip: str = ""
        self._model: str = ""
        self._mac: str = ""
        self._version: str = ""

    @property
    def ip(self) -> str:
        """Returns ip."""
        if not self._ip:
            raise JvcProjectorError("ip not initialized")
        return self._ip

    @property
    def host(self) -> str:
        """Returns host."""
        return self._host

    @property
    def port(self) -> int:
        """Returns port."""
        return self._port

    @property
    def model(self) -> str:
        """Returns model name."""
        if not self._mac:
            raise JvcProjectorError("model not initialized")
        return self._model

    @property
    def mac(self) -> str:
        """Returns mac address."""
        if not self._mac:
            raise JvcProjectorError("mac address not initialized")
        return self._mac

    @property
    def version(self) -> str | None:
        """Get device software version."""
        #if not self._version:
        #    raise JvcProjectorError("version address not initialized")
        return self._version or None

    async def connect(self, get_info: bool = False) -> None:
        """Connect to device."""
        if self._device:
            return

        if not self._ip:
            self._ip = await resolve(self._host)

        self._device = JvcDevice(self._ip, self._port, self._timeout, self._password)

        if not await self.test():
            raise JvcProjectorConnectError("Failed to verify connection")

        if get_info:
            await self.get_info()

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self._device:
            await self._device.disconnect()
            self._device = None

    async def get_info(self) -> dict[str, str]:
        """Get device info."""
        assert self._device
        model = JvcCommand(command.MODEL, True)
        mac = JvcCommand(command.MAC, True)
        await self._send([model, mac])

        if mac.response is None:
            raise JvcProjectorError("Mac address not available")

        if model.response is None:
            model.response = "(unknown)"

        self._model = model.response
        self._mac = mac.response

        return {"model": self._model, "mac": self._mac}

    async def get_state(self) -> dict[str, str | None]:
        """Get device state."""
        assert self._device
        pwr = JvcCommand(command.POWER, True)
        inp = JvcCommand(command.INPUT, True)
        src = JvcCommand(command.SOURCE, True)
        res = await self._send([pwr, inp, src])
        return {
            "power": res[0] or None,
            "input": res[1] or const.NOSIGNAL,
            "source": res[2] or const.NOSIGNAL,
        }

    async def get_version(self) -> str | None:
        """Get device software version."""
        return await self.ref(command.VERSION)

    async def get_power(self) -> str | None:
        """Get power state."""
        return await self.ref(command.POWER)

    async def get_input(self) -> str | None:
        """Get current input."""
        return await self.ref(command.INPUT)

    async def get_signal(self) -> str | None:
        """Get if has signal."""
        return await self.ref(command.SOURCE)

    async def test(self) -> bool:
        """Run test command."""
        cmd = JvcCommand(f"{command.TEST}")
        await self._send([cmd])
        return cmd.ack

    async def power_on(self) -> None:
        """Run power on command."""
        await self.op(f"{command.POWER}1")

    async def power_off(self) -> None:
        """Run power off command."""
        await self.op(f"{command.POWER}0")

    async def remote(self, code: str) -> None:
        """Run remote code command."""
        await self.op(f"{command.REMOTE}{code}")

    async def op(self, code: str) -> None:
        """Send operation code."""
        await self._send([JvcCommand(code, False)])

    async def ref(self, code: str) -> str | None:
        """Send reference code."""
        return (await self._send([JvcCommand(code, True)]))[0]
        
    # async def _send(self, cmds: list[JvcCommand]) -> list[str | None]:
    #     """Send command to device."""
    #     if self._device is None:
    #         raise JvcProjectorError("Must call connect before sending commands")

    #     await self._device.send(cmds)

    #     return [cmd.response for cmd in cmds]

    #2024 Update - Connect on demand
    async def _send(self, cmds: list[JvcCommand]) -> list[str | None]:
        """Send command to device."""
        if self._device is None:
            await self.connect(False)

        await self._device.send(cmds)
        return [cmd.response for cmd in cmds]

    #2024 Update - Get light source time
    async def get_light_source_time(self) -> str | None:
        """Get light source (laser) usage time."""
        return await self.ref(command.IFLT)