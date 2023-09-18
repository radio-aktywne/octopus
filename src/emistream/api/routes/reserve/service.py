from emistream.models.data import Reservation, ReservationRequest
from emistream.stream.controller import StreamController


class Service:
    """Service for the reserve endpoint."""

    def __init__(self, controller: StreamController) -> None:
        self._controller = controller

    async def reserve(self, request: ReservationRequest) -> Reservation:
        """Reserve a stream."""

        return await self._controller.reserve(request)
