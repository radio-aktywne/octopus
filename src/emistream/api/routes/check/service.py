from emistream.api.routes.check import errors as e
from emistream.api.routes.check.models import CheckResponse
from emistream.streaming import errors as se
from emistream.streaming.controller import StreamController


class Service:
    """Service for the check endpoint."""

    def __init__(self, controller: StreamController) -> None:
        self._controller = controller

    async def check(self) -> CheckResponse:
        """Check availability."""

        try:
            return await self._controller.check()
        except se.StreamingError as error:
            raise e.ServiceError(error.message) from error
