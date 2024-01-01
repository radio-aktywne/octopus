from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from pydantic import TypeAdapter

from emistream.config.models import EmishowsConfig
from emistream.emishows.models import (
    ScheduleListEndParameter,
    ScheduleListIncludeParameter,
    ScheduleListLimitParameter,
    ScheduleListOffsetParameter,
    ScheduleListOrderParameter,
    ScheduleListResponse,
    ScheduleListStartParameter,
    ScheduleListWhereParameter,
)


class EmishowsEndpoint(BaseEndpoint):
    """Endpoints for emishows API."""

    SCHEDULE = "/schedule"


class EmishowsServiceBase(Gracy[EmishowsEndpoint]):
    """Base class for emishows API service."""

    def __init__(self, config: EmishowsConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = f"http://{config.host}:{config.port}"
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


class EmishowsScheduleNamespace(GracyNamespace[EmishowsEndpoint]):
    """Namespace for emishows API schedule endpoint."""

    def _dump_param[T](self, t: type[T], v: T) -> str:
        value = TypeAdapter(t).dump_json(v, by_alias=True).decode()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value

    async def list(
        self,
        start: ScheduleListStartParameter = None,
        end: ScheduleListEndParameter = None,
        limit: ScheduleListLimitParameter = None,
        offset: ScheduleListOffsetParameter = None,
        where: ScheduleListWhereParameter = None,
        include: ScheduleListIncludeParameter = None,
        order: ScheduleListOrderParameter = None,
    ) -> ScheduleListResponse:
        params = {}
        if start is not None:
            params["start"] = self._dump_param(ScheduleListStartParameter, start)
        if end is not None:
            params["end"] = self._dump_param(ScheduleListEndParameter, end)
        if limit is not None:
            params["limit"] = self._dump_param(ScheduleListLimitParameter, limit)
        if offset is not None:
            params["offset"] = self._dump_param(ScheduleListOffsetParameter, offset)
        if where is not None:
            params["where"] = self._dump_param(ScheduleListWhereParameter, where)
        if include is not None:
            params["include"] = self._dump_param(ScheduleListIncludeParameter, include)
        if order is not None:
            params["order"] = self._dump_param(ScheduleListOrderParameter, order)

        response = await self.get(EmishowsEndpoint.SCHEDULE, params=params)
        return ScheduleListResponse.model_validate_json(response.content)


class EmishowsService(EmishowsServiceBase):
    """Service for emishows API."""

    schedule: EmishowsScheduleNamespace
