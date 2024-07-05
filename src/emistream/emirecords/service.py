from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from emistream.config.models import EmirecordsConfig
from emistream.emirecords.models import RecordPostRequest, RecordPostResponse


class EmirecordsEndpoint(BaseEndpoint):
    """Endpoints for the emirecords API."""

    RECORD = "/record"


class EmirecordsServiceBase(Gracy[EmirecordsEndpoint]):
    """Base class for emirecords API service."""

    def __init__(self, config: EmirecordsConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = config.http.url
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


class EmirecordsScheduleNamespace(GracyNamespace[EmirecordsEndpoint]):
    """Namespace for emirecords API record endpoint."""

    async def record(self, request: RecordPostRequest) -> RecordPostResponse:
        response = await self.post(
            EmirecordsEndpoint.RECORD,
            json=request.model_dump(mode="json", by_alias=True),
        )
        return RecordPostResponse.model_validate_json(response.content)


class EmirecordsService(EmirecordsServiceBase):
    """Service for emirecords API."""

    record: EmirecordsScheduleNamespace
