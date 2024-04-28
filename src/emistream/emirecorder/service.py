from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from emistream.config.models import EmirecorderHTTPConfig
from emistream.emirecorder.models import RecordPostRequest, RecordPostResponse


class EmirecorderEndpoint(BaseEndpoint):
    """Endpoints for the emirecorder API."""

    RECORD = "/record"


class EmirecorderServiceBase(Gracy[EmirecorderEndpoint]):
    """Base class for emirecorder API service."""

    def __init__(self, config: EmirecorderHTTPConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = config.url
            SETTINGS = GracyConfig(
                retry=GracefulRetry(
                    delay=1,
                    max_attempts=3,
                    delay_modifier=2,
                ),
            )

        self.Config = Config

        super().__init__(*args, **kwargs)

        self._config = config


class EmirecorderScheduleNamespace(GracyNamespace[EmirecorderEndpoint]):
    """Namespace for emirecorder API record endpoint."""

    async def record(self, request: RecordPostRequest) -> RecordPostResponse:
        response = await self.post(
            EmirecorderEndpoint.RECORD,
            json=request.model_dump(mode="json", by_alias=True),
        )
        return RecordPostResponse.model_validate_json(response.content)


class EmirecorderService(EmirecorderServiceBase):
    """Service for emirecorder API."""

    record: EmirecorderScheduleNamespace
