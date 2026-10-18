from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController, handlers
from litestar.channels import ChannelsPlugin
from litestar.di import NamedDependency, Provide
from litestar.params import Body
from litestar.response import Response

from octopus.api.exceptions import BadRequestException, ConflictException
from octopus.api.routes.reserve import errors as e, models as m
from octopus.api.routes.reserve.service import Service
from octopus.models.base import Serializable
from octopus.services.streaming.service import StreamingService
from octopus.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self, channels: NamedDependency[ChannelsPlugin], state: State
    ) -> Service:
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
        raises=[BadRequestException, ConflictException],
    )
    async def reserve(
        self,
        service: NamedDependency[Service],
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
        except e.ConflictError as ex:
            raise ConflictException from ex
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.reservation))
