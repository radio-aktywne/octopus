from collections.abc import Generator
from contextlib import contextmanager

from emistream.api.routes.reserve import errors as e
from emistream.api.routes.reserve import models as m
from emistream.services.streaming import errors as se
from emistream.services.streaming import models as sm
from emistream.services.streaming.service import StreamingService


class Service:
    """Service for the reserve endpoint."""

    def __init__(self, streaming: StreamingService) -> None:
        self._streaming = streaming

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.InstanceNotFoundError as ex:
            raise e.ValidationError(str(ex)) from ex
        except se.StreamBusyError as ex:
            raise e.ServiceBusyError(str(ex)) from ex
        except se.EmishowsError as ex:
            raise e.EmishowsError(str(ex)) from ex
        except se.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""

        event = request.data.event
        format = request.data.format
        record = request.data.record

        req = sm.ReserveRequest(
            event=event,
            format=format,
            record=record,
        )

        with self._handle_errors():
            res = await self._streaming.reserve(req)

        credentials = res.credentials
        port = res.port

        credentials = m.Credentials.map(credentials)
        data = m.ReserveResponseData(
            credentials=credentials,
            port=port,
        )
        return m.ReserveResponse(
            data=data,
        )
