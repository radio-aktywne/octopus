from collections.abc import Generator
from contextlib import contextmanager

from octopus.api.routes.reserve import errors as e
from octopus.api.routes.reserve import models as m
from octopus.services.streaming import errors as se
from octopus.services.streaming import models as sm
from octopus.services.streaming.service import StreamingService


class Service:
    """Service for the reserve endpoint."""

    def __init__(self, streaming: StreamingService) -> None:
        self._streaming = streaming

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.InstanceNotFoundError as ex:
            raise e.ValidationError from ex
        except se.StreamBusyError as ex:
            raise e.ServiceBusyError from ex
        except se.BeaverError as ex:
            raise e.BeaverError from ex
        except se.ServiceError as ex:
            raise e.ServiceError from ex

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        reserve_request = sm.ReserveRequest(
            event=request.data.event,
            format=request.data.format,
            record=request.data.record,
        )

        with self._handle_errors():
            reserve_response = await self._streaming.reserve(reserve_request)

        return m.ReserveResponse(
            reservation=m.Reservation(
                credentials=m.Credentials.map(reserve_response.credentials),
                port=reserve_response.port,
            )
        )
