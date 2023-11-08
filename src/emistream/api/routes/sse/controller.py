from collections.abc import AsyncGenerator

from litestar import Controller as BaseController
from litestar import get
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.response import ServerSentEvent

from emistream.api.routes.sse.service import Service


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, channels: ChannelsPlugin) -> Service:
        return Service(channels)

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the sse endpoint."""

    dependencies = DependenciesBuilder().build()

    @get(
        summary="Get SSE stream",
        description="Get a stream of Server-Sent Events",
    )
    async def get(self, service: Service) -> ServerSentEvent:
        async def _yield_events() -> AsyncGenerator[str, None]:
            async for event in service.subscribe():
                yield event.model_dump_json(by_alias=True)

        return ServerSentEvent(_yield_events())
