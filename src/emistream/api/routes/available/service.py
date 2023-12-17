from emistream.api.routes.available.models import GetResponse
from emistream.stream.controller import StreamController


class Service:
    """Service for the available endpoint."""

    def __init__(self, controller: StreamController) -> None:
        self._controller = controller

    async def get(self) -> GetResponse:
        """Get availability information."""

        return await self._controller.availability()
