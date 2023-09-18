import logging
from collections.abc import Generator
from contextlib import contextmanager

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig

from emistream.config.models import EmirecorderConfig
from emistream.emirecorder.models import RecordRequest, RecordResponse


class EmirecorderEndpoint(BaseEndpoint):
    """Endpoints for the emirecorder API."""

    RECORD = "/record"


class EmirecorderAPIBase(Gracy[EmirecorderEndpoint]):
    """Base class for the emirecorder API."""

    def __init__(self, config: EmirecorderConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = f"http://{config.host}:{config.port}/"
            SETTINGS = GracyConfig(
                retry=GracefulRetry(
                    delay=1,
                    max_attempts=3,
                    delay_modifier=2,
                ),
            )

        self.Config = Config

        super().__init__(*args, **kwargs)

    @contextmanager
    def _suppress_logging(self) -> Generator[None, None, None]:
        """Suppress logging for the request."""

        logger = logging.getLogger("httpx")
        disabled = logger.disabled
        logger.disabled = True

        try:
            yield
        finally:
            logger.disabled = disabled

    async def _request(self, *args, **kwargs):
        with self._suppress_logging():
            return await super()._request(*args, **kwargs)


class EmirecorderAPI(EmirecorderAPIBase):
    """API for the emirecorder."""

    async def record(self, request: RecordRequest) -> RecordResponse:
        response = await self.post(EmirecorderEndpoint.RECORD, json=request.dict())
        return RecordResponse.parse_raw(response.content)
