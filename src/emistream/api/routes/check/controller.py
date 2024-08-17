from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.response import Response

from emistream.api.routes.check import models as m
from emistream.api.routes.check.service import Service
from emistream.services.streaming.service import StreamingService
from emistream.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State, channels: ChannelsPlugin) -> Service:
        return Service(
            streaming=StreamingService(
                config=state.config,
                store=state.store,
                lock=state.lock,
                emishows=state.emishows,
                emirecords=state.emirecords,
                channels=channels,
            ),
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the check endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="Check availability",
    )
    async def check(self, service: Service) -> Response[m.CheckResponseAvailability]:
        """Check the availability of the stream."""

        req = m.CheckRequest()

        res = await service.check(req)

        availability = res.availability

        return Response(availability)
