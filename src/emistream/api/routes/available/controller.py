from litestar import Controller as BaseController
from litestar import get
from litestar.channels import ChannelsPlugin
from litestar.di import Provide

from emistream.api.routes.available.models import GetResponse
from emistream.api.routes.available.service import Service
from emistream.emirecorder.client import EmirecorderAPI
from emistream.state import State
from emistream.stream.controller import StreamController
from emistream.stream.runner import StreamRunner


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self,
        state: State,
        channels: ChannelsPlugin,
    ) -> Service:
        return Service(
            controller=StreamController(
                state=state.stream,
                runner=StreamRunner(state.config),
                emirecorder=EmirecorderAPI(state.config.emirecorder),
                channels=channels,
                config=state.config,
            ),
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the available endpoint."""

    dependencies = DependenciesBuilder().build()

    @get(
        summary="Get availability information",
        description="Get information about the current availability of the stream.",
    )
    async def get(self, service: Service) -> GetResponse:
        return await service.get()
