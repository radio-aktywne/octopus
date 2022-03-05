from starlite import Router

from emistream.paths.reserve.controller import ReserveController

reserve_router = Router(path="/reserve", route_handlers=[ReserveController])
