from starlite import Router

from emistream.api.paths.reserve.controller import ReserveController

router = Router(path="/reserve", route_handlers=[ReserveController])
