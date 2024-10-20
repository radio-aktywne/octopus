from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from octopus.config.models import BeaverConfig
from octopus.services.beaver import models as m
from octopus.services.beaver.serializer import Serializer


class Endpoint(BaseEndpoint):
    """Endpoints for beaver service."""

    SCHEDULE = "/schedule"


class BaseService(Gracy[Endpoint]):
    """Base class for beaver service."""

    def __init__(self, config: BeaverConfig, *args, **kwargs) -> None:
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


class ScheduleNamespace(GracyNamespace[Endpoint]):
    """Namespace for beaver schedule endpoint."""

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List schedules."""

        params = {}
        if request.start is not None:
            params["start"] = Serializer(m.ListRequestStart).json(request.start)
        if request.end is not None:
            params["end"] = Serializer(m.ListRequestEnd).json(request.end)
        if request.limit is not None:
            params["limit"] = Serializer(m.ListRequestLimit).json(request.limit)
        if request.offset is not None:
            params["offset"] = Serializer(m.ListRequestOffset).json(request.offset)
        if request.where is not None:
            params["where"] = Serializer(m.ListRequestWhere).json(request.where)
        if request.include is not None:
            params["include"] = Serializer(m.ListRequestInclude).json(request.include)
        if request.order is not None:
            params["order"] = Serializer(m.ListRequestOrder).json(request.order)

        res = await self.get(Endpoint.SCHEDULE, params=params)

        results = m.ScheduleList.model_validate_json(res.content)

        return m.ListResponse(
            results=results,
        )


class BeaverService(BaseService):
    """Service for beaver service."""

    schedule: ScheduleNamespace
