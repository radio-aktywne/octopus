from starlite import Router

from emistream.api.paths.available.router import router as available_router
from emistream.api.paths.reserve.router import router as reserve_router

router = Router(path="/", route_handlers=[available_router, reserve_router])
