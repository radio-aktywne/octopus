from litestar import Controller as BaseController
from litestar import post
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.response import Response

from emistream.api.exceptions import ConflictException, UnprocessableContentException
from emistream.api.routes.reserve.errors import (
    InstanceNotFoundError,
    RecorderBusyError,
    StreamBusyError,
)
from emistream.api.routes.reserve.models import ReserveRequest, ReserveResponse
from emistream.api.routes.reserve.service import Service
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
                emirecorder=state.emirecorder,
                channels=channels,
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
        raises=[ConflictException, UnprocessableContentException],
    )
    async def reserve(
        self, data: ReserveRequest, service: Service
    ) -> Response[ReserveResponse]:
        try:
            response = await service.reserve(data)
        except InstanceNotFoundError as error:
            raise UnprocessableContentException(extra=error.message) from error
        except StreamBusyError as error:
            raise ConflictException(extra=error.message) from error
        except RecorderBusyError as error:
            raise ConflictException(extra=error.message) from error

        return Response(response)
