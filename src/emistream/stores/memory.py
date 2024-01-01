from typing import TypeVar

from emistream.stores.base import Store

T = TypeVar("T")


class MemoryStore(Store[T]):
    """Store that stores the value in memory."""

    def __init__(self, value: T) -> None:
        self._value = value

    async def get(self) -> T:
        return self._value

    async def set(self, value: T) -> None:
        self._value = value
