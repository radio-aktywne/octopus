from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Body
from litestar.response import Response

from emistream.api.exceptions import ConflictException, UnprocessableContentException
from emistream.api.routes.reserve import errors as e
from emistream.api.routes.reserve import models as m
from emistream.api.routes.reserve.service import Service
from emistream.api.validator import Validator
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
            m.ReserveRequestData,
            Body(
                description="Data for the request.",
            ),
        ],
    ) -> Response[m.ReserveResponseData]:
        """Reserve a stream."""

        data = Validator(m.ReserveRequestData).object(data)

        req = m.ReserveRequest(
            data=data,
        )

        try:
            res = await service.reserve(req)
        except e.ValidationError as ex:
            raise UnprocessableContentException(extra=str(ex)) from ex
        except e.ServiceBusyError as ex:
            raise ConflictException(extra=str(ex)) from ex

        rdata = res.data

        return Response(rdata)
