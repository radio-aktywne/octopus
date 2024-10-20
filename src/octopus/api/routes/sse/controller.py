from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.response import ServerSentEvent

from octopus.api.routes.sse import models as m
from octopus.api.routes.sse.service import Service
from octopus.services.events.service import EventsService


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, channels: ChannelsPlugin) -> Service:
        return Service(
            events=EventsService(
                channels=channels,
            ),
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the sse endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="Get SSE stream",
    )
    async def subscribe(self, service: Service) -> ServerSentEvent:
        """Get a stream of Server-Sent Events."""

        req = m.SubscribeRequest()

        res = await service.subscribe(req)

        return ServerSentEvent(res.messages)
