from litestar import Controller as BaseController
from litestar import post
from litestar.channels import ChannelsPlugin
from litestar.di import Provide

from emistream.api.exceptions import ConflictException
from emistream.api.routes.reserve.errors import StreamBusyError
from emistream.api.routes.reserve.models import ReserveRequest, ReserveResponse
from emistream.api.routes.reserve.service import Service
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
    """Controller for the reserve endpoint."""

    dependencies = DependenciesBuilder().build()

    @post(
        summary="Reserve a stream",
        description="Reserve a stream to be able to go live.",
        raises=[ConflictException],
    )
    async def reserve(self, data: ReserveRequest, service: Service) -> ReserveResponse:
        try:
            return await service.reserve(data.request)
        except StreamBusyError as e:
            extra = {"event": e.event.model_dump(mode="json", by_alias=True)}
            raise ConflictException(extra=extra) from e
