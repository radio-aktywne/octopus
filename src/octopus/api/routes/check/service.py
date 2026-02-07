from collections.abc import Generator
from contextlib import contextmanager

from octopus.api.routes.check import errors as e
from octopus.api.routes.check import models as m
from octopus.services.streaming import errors as se
from octopus.services.streaming import models as sm
from octopus.services.streaming.service import StreamingService


class Service:
    """Service for the check endpoint."""

    def __init__(self, streaming: StreamingService) -> None:
        self._streaming = streaming

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.ServiceError as ex:
            raise e.ServiceError from ex

    async def check(self, request: m.CheckRequest) -> m.CheckResponse:
        """Check the availability of the stream."""
        check_request = sm.CheckRequest()

        with self._handle_errors():
            check_response = await self._streaming.check(check_request)

        return m.CheckResponse(
            availability=m.Availability.map(check_response.availability)
        )
