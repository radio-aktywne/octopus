from starlite import Router

from emistream.api.paths.available.controller import AvailableController

router = Router(path="/available", route_handlers=[AvailableController])
