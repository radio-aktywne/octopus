from starlite import Router

from emistream.paths.available.controller import AvailableController

available_router = Router(
    path="/available", route_handlers=[AvailableController]
)
