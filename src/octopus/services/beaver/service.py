from typing import Any

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from octopus.config.models import BeaverConfig
from octopus.models.base import Jsonable, Serializable
from octopus.services.beaver import models as m


class Endpoint(BaseEndpoint):
    """Endpoints for beaver service."""

    SCHEDULE = "/schedule"


class BaseService(Gracy[Endpoint]):
    """Base class for beaver service."""

    def __init__(self, config: BeaverConfig, *args: Any, **kwargs: Any) -> None:
        self.Config.BASE_URL = config.http.url
        self.Config.SETTINGS = GracyConfig(
            retry=GracefulRetry(delay=1, max_attempts=3, delay_modifier=2)
        )
        super().__init__(*args, **kwargs)
        self._config = config


class ScheduleNamespace(GracyNamespace[Endpoint]):
    """Namespace for beaver schedule endpoint."""

    async def list(self, request: m.ScheduleListRequest) -> m.ScheduleListResponse:
        """List schedules."""
        params = {}
        if request.start is not None:
            params["start"] = Jsonable(request.start).model_dump_json()
        if request.end is not None:
            params["end"] = Jsonable(request.end).model_dump_json()
        if request.where is not None:
            params["where"] = Jsonable(request.where).model_dump_json()
        if request.include is not None:
            params["include"] = Jsonable(request.include).model_dump_json()

        response = await self.get(Endpoint.SCHEDULE, params=params)

        return m.ScheduleListResponse(
            results=Serializable[m.ScheduleList]
            .model_validate_json(response.content)
            .root
        )


class BeaverService(BaseService):
    """Service for beaver service."""

    schedule: ScheduleNamespace
