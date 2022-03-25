from starlite import Controller, post

from emistream.models.reserve import ReserveRequest, ReserveResponse
from emistream.stream import manager


class ReserveController(Controller):
    path = None

    @post()
    def reserve(self, data: ReserveRequest) -> ReserveResponse:
        return ReserveResponse(token=manager.reserve(data.reservation))
