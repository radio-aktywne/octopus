import asyncio

from emistream.locks.base import Lock


class AsyncioLock(Lock):
    """Asyncio lock."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        await self._lock.acquire()

    async def release(self) -> None:
        self._lock.release()
