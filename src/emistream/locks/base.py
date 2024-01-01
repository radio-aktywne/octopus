from abc import ABC, abstractmethod
from typing import Self


class Lock(ABC):
    """Base class for locks."""

    async def __aenter__(self) -> Self:
        await self.acquire()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.release()

    @abstractmethod
    async def acquire() -> None:
        """Acquire the lock."""

        pass

    @abstractmethod
    async def release() -> None:
        """Release the lock."""

        pass
