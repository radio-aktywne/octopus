from starlite import Controller, State, post

from emistream.models.reserve import ReserveRequest, ReserveResponse


class ReserveController(Controller):
    path = None

    @post()
    async def reserve(
        self, state: State, data: ReserveRequest
    ) -> ReserveResponse:
        return ReserveResponse(
            token=await state.stream_manager.reserve(data.event, data.record)
        )
