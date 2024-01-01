from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Store(ABC, Generic[T]):
    """Base class for stores."""

    @abstractmethod
    async def get(self) -> T:
        """Returns the stored value."""

        pass

    @abstractmethod
    async def set(self, value: T) -> None:
        """Sets the stored value."""

        pass
