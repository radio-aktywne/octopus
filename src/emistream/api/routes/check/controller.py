from litestar import Controller as BaseController
from litestar import get
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.response import Response

from emistream.api.routes.check.models import CheckResponse
from emistream.api.routes.check.service import Service
from emistream.state import State
from emistream.streaming.controller import StreamController


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self,
        state: State,
        channels: ChannelsPlugin,
    ) -> Service:
        return Service(
            controller=StreamController(
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

    @get(
        summary="Check availability",
        description="Check the current availability of the stream.",
    )
    async def check(self, service: Service) -> Response[CheckResponse]:
        response = await service.check()
        return Response(response)
