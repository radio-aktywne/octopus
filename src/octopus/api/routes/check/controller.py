from collections.abc import Mapping

from litestar import Controller as BaseController, handlers
from litestar.di import NamedDependency, Provide
from litestar.response import Response

from octopus.api.routes.check import models as m
from octopus.api.routes.check.service import Service
from octopus.models.base import Serializable
from octopus.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(streaming=state.streaming)

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the check endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="Check availability",
    )
    async def check(
        self, service: NamedDependency[Service]
    ) -> Response[Serializable[m.CheckResponseAvailability]]:
        """Check the availability of the stream."""
        request = m.CheckRequest()

        response = await service.check(request)

        return Response(Serializable(response.availability))
