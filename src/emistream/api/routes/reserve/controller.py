from litestar import Controller as BaseController
from litestar import Response, post
from litestar.channels import ChannelsPlugin
from litestar.di import Provide

from emistream.api.routes.reserve.errors import (
    AlreadyReservedError,
    RecorderUnavailableError,
)
from emistream.api.routes.reserve.models import PostRequest, PostResponse
from emistream.api.routes.reserve.service import Service
from emistream.emirecorder.client import EmirecorderAPI
from emistream.state import State
from emistream.stream.controller import StreamController
from emistream.stream.errors import RecorderError, StreamBusyError
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

    def build(self) -> dict[str, object]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the reserve endpoint."""

    dependencies = DependenciesBuilder().build()

    @post(
        summary="Reserve a stream",
        description="Reserve a stream to be able to go live",
        raises=[AlreadyReservedError, RecorderUnavailableError],
    )
    async def post(self, data: PostRequest, service: Service) -> Response[PostResponse]:
        try:
            reservation = await service.reserve(data.request)
        except StreamBusyError as e:
            raise AlreadyReservedError(e.event) from e
        except RecorderError as e:
            raise RecorderUnavailableError() from e

        content = PostResponse(reservation=reservation)
        return Response(content)
