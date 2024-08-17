from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from emistream.config.models import EmirecordsConfig
from emistream.services.emirecords import models as m


class Endpoint(BaseEndpoint):
    """Endpoints for emirecords API."""

    RECORD = "/record"


class BaseService(Gracy[Endpoint]):
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


class RecordNamespace(GracyNamespace[Endpoint]):
    """Namespace for emirecords record endpoint."""

    async def record(self, request: m.RecordRequest) -> m.RecordResponse:
        """Request a recording for a given event."""

        data = request.data

        json = data.model_dump(mode="json", by_alias=True)

        res = await self.post(
            Endpoint.RECORD,
            json=json,
        )

        rdata = m.RecordResponseData.model_validate_json(res.content)

        return m.RecordResponse(
            data=rdata,
        )


class EmirecordsService(BaseService):
    """Service for emirecords API."""

    record: RecordNamespace
