"""Module for representing a JVC Projector network connection."""

from __future__ import annotations

import asyncio
import socket

import aiodns

from .error import JvcProjectorConnectError


class JvcConnection:
    """Class for representing a JVC Projector network connection."""

    def __init__(self, ip: str, port: int, timeout: float):
        """Initialize class."""
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    @property
    def ip(self) -> str:
        """Return ip address."""
        return self._ip

    @property
    def port(self) -> int:
        """Return port."""
        return self._port

    def is_connected(self) -> bool:
        """Return if connected to device."""
        return self._reader is not None and self._writer is not None

    async def connect(self) -> None:
        """Connect to device."""
        assert self._reader is None and self._writer is None
        conn = asyncio.open_connection(self._ip, self._port)
        self._reader, self._writer = await asyncio.wait_for(conn, timeout=self._timeout)

    async def read(self, n: int) -> bytes:
        """Read n bytes from device."""
        assert self._reader
        return await asyncio.wait_for(self._reader.read(n), timeout=self._timeout)

    async def readline(self) -> bytes:
        """Read all bytes up to newline from device."""
        assert self._reader
        return await asyncio.wait_for(self._reader.readline(), timeout=self._timeout)

    async def write(self, data: bytes) -> None:
        """Write data to device."""
        assert self._writer
        self._writer.write(data)
        await self._writer.drain()

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self._writer:
            self._writer.close()
        self._writer = None
        self._reader = None


async def resolve(host: str) -> str:
    """Resolve hostname to ip address."""
    try:
        res = await aiodns.DNSResolver().gethostbyname(host, socket.AF_INET)
        if len(res.addresses) < 1:
            raise JvcProjectorConnectError("Unexpected zero length addresses response")
    except aiodns.error.DNSError as err:
        raise JvcProjectorConnectError(f"Failed to resolve host {host}") from err

    return res.addresses[0]
