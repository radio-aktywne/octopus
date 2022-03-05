from starlite import Router

from emistream.paths.available.router import available_router
from emistream.paths.reserve.router import reserve_router

router = Router(path="/", route_handlers=[available_router, reserve_router])
