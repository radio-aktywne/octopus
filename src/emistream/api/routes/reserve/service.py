from emistream.api.routes.reserve import errors as re
from emistream.api.routes.reserve.models import ReserveRequest, ReserveResponse
from emistream.stream import errors as se
from emistream.stream.controller import StreamController


class Service:
    """Service for the reserve endpoint."""

    def __init__(self, controller: StreamController) -> None:
        self._controller = controller

    async def reserve(self, request: ReserveRequest) -> ReserveResponse:
        """Reserve a stream."""

        try:
            return await self._controller.reserve(request)
        except se.RecorderError as e:
            raise re.RecorderError(e.event) from e
        except se.StreamBusyError as e:
            raise re.StreamBusyError(e.event) from e
        except se.StreamError as e:
            raise re.ServiceError() from e
