"""Modbus client for the AVARMA heat pump.

Thin wrapper around pymodbus that
- serialises all requests (RS485 gateways handle one request at a time),
- splits long reads into chunks,
- copes with the pymodbus keyword rename slave -> device_id,
- separates transport errors from Modbus exception responses.

No Home Assistant imports, so it can be tested standalone.
"""

from __future__ import annotations

import asyncio
import inspect
import logging

from pymodbus import FramerType
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .registers import split_block

_LOGGER = logging.getLogger(__name__)

FRAMERS = {
    "tcp": FramerType.SOCKET,
    "rtuovertcp": FramerType.RTU,
}


class AvarmaError(Exception):
    """Base error."""


class AvarmaConnectionError(AvarmaError):
    """Gateway not reachable or no answer from the heat pump."""


class AvarmaDeviceError(AvarmaError):
    """The heat pump answered with a Modbus exception (e.g. illegal address)."""


def _unit_kwarg(method) -> str:
    """Return the keyword pymodbus uses for the unit id."""
    params = inspect.signature(method).parameters
    for name in ("device_id", "slave", "unit"):
        if name in params:
            return name
    return "device_id"


class AvarmaClient:
    """Modbus TCP / RTU-over-TCP client."""

    def __init__(
        self,
        host: str,
        port: int,
        slave: int,
        framer: str = "tcp",
        timeout: float = 5.0,
        message_wait: float = 0.05,
    ) -> None:
        self.host = host
        self.port = port
        self.slave = slave
        self.framer = framer
        self._message_wait = message_wait
        self._lock = asyncio.Lock()
        self._client = AsyncModbusTcpClient(
            host,
            port=port,
            framer=FRAMERS[framer],
            timeout=timeout,
            retries=1,
        )
        self._unit_kw = _unit_kwarg(self._client.read_holding_registers)

    @property
    def connected(self) -> bool:
        return bool(self._client.connected)

    async def _ensure_connected(self) -> None:
        if self._client.connected:
            return
        try:
            ok = await self._client.connect()
        except (OSError, ModbusException) as err:
            raise AvarmaConnectionError(f"Cannot connect to {self.host}:{self.port}: {err}") from err
        if not ok:
            raise AvarmaConnectionError(f"Cannot connect to {self.host}:{self.port}")

    async def close(self) -> None:
        self._client.close()

    async def read_registers(self, start: int, count: int) -> list[int]:
        """Read holding registers, split into chunks if needed."""
        values: list[int] = []
        async with self._lock:
            await self._ensure_connected()
            for address, n in split_block(start, count):
                values.extend(await self._read_chunk(address, n))
                if self._message_wait:
                    await asyncio.sleep(self._message_wait)
        return values

    async def _read_chunk(self, address: int, count: int) -> list[int]:
        try:
            result = await self._client.read_holding_registers(
                address, count=count, **{self._unit_kw: self.slave}
            )
        except ModbusException as err:
            # timeout, connection lost, no response
            self._client.close()
            raise AvarmaConnectionError(f"Read 0x{address:04X}+{count} failed: {err}") from err
        if result.isError():
            raise AvarmaDeviceError(f"Read 0x{address:04X}+{count} rejected: {result}")
        regs = list(result.registers)
        if len(regs) != count:
            raise AvarmaConnectionError(
                f"Read 0x{address:04X}: expected {count} registers, got {len(regs)}"
            )
        return regs

    async def write_register(self, address: int, value: int) -> None:
        """Write one holding register (function 0x06)."""
        async with self._lock:
            await self._ensure_connected()
            try:
                result = await self._client.write_register(
                    address, value, **{self._unit_kw: self.slave}
                )
            except ModbusException as err:
                self._client.close()
                raise AvarmaConnectionError(f"Write 0x{address:04X}={value} failed: {err}") from err
            if result.isError():
                raise AvarmaDeviceError(f"Write 0x{address:04X}={value} rejected: {result}")
            if self._message_wait:
                await asyncio.sleep(self._message_wait)
