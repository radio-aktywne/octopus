from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Body
from litestar.response import Response

from octopus.api.exceptions import ConflictException, UnprocessableContentException
from octopus.api.routes.reserve import errors as e
from octopus.api.routes.reserve import models as m
from octopus.api.routes.reserve.service import Service
from octopus.models.base import Serializable
from octopus.services.streaming.service import StreamingService
from octopus.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State, channels: ChannelsPlugin) -> Service:
        return Service(
            streaming=StreamingService(
                config=state.config,
                store=state.store,
                lock=state.lock,
                beaver=state.beaver,
                channels=channels,
            ),
        )

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the reserve endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.post(
        summary="Reserve a stream",
        raises=[
            ConflictException,
            UnprocessableContentException,
        ],
    )
    async def reserve(
        self,
        service: Service,
        data: Annotated[
            Serializable[m.ReserveRequestData],
            Body(
                description="Data for reserving a stream.",
            ),
        ],
    ) -> Response[Serializable[m.ReserveResponseReservation]]:
        """Reserve a stream."""
        request = m.ReserveRequest(data=data.root)

        try:
            response = await service.reserve(request)
        except e.ValidationError as ex:
            raise UnprocessableContentException from ex
        except e.ServiceBusyError as ex:
            raise ConflictException from ex

        return Response(Serializable(response.reservation))
