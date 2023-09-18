from asyncio import Lock
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self

from emistream.models.data import Event


class RawStreamState:
    """State of the stream without any safety measures."""

    def __init__(self) -> None:
        self._event = None

    def get(self) -> Event | None:
        """Get the current event."""

        return self._event

    def set(self, event: Event | None) -> None:
        """Set the current event."""

        self._event = event


class StreamState:
    """State of the stream with safety measures."""

    def __init__(self) -> None:
        self._state = RawStreamState()
        self._lock = None

    async def __aenter__(self) -> Self:
        self._lock = Lock()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        self._lock = None

    @asynccontextmanager
    async def lock(self) -> AsyncGenerator[RawStreamState, None]:
        """Lock the state."""

        async with self._lock:
            yield self._state

    async def get(self) -> Event | None:
        """Get the current event."""

        async with self.lock() as state:
            return state.get()

    async def set(self, event: Event | None) -> None:
        """Set the current event."""

        async with self.lock() as state:
            state.set(event)
