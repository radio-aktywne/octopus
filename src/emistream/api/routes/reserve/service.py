from emistream.api.routes.reserve import errors as e
from emistream.api.routes.reserve.models import ReserveRequest, ReserveResponse
from emistream.streaming import errors as se
from emistream.streaming.controller import StreamController


class Service:
    """Service for the reserve endpoint."""

    def __init__(self, controller: StreamController) -> None:
        self._controller = controller

    async def reserve(self, request: ReserveRequest) -> ReserveResponse:
        """Reserve a stream."""

        try:
            return await self._controller.reserve(request)
        except se.InstanceNotFoundError as error:
            raise e.InstanceNotFoundError(error.message) from error
        except se.StreamBusyError as error:
            raise e.StreamBusyError(error.message) from error
        except se.RecorderBusyError as error:
            raise e.RecorderBusyError(error.message) from error
        except se.StreamingError as error:
            raise e.ServiceError(error.message) from error
