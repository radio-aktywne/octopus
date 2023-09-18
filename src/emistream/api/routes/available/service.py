from emistream.models.data import Availability
from emistream.stream.controller import StreamController


class Service:
    """Service for the available endpoint."""

    def __init__(self, controller: StreamController) -> None:
        self._controller = controller

    async def availability(self) -> Availability:
        """Get availability information."""

        return await self._controller.availability()
