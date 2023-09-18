from litestar import Router

from emistream.api.routes.available.router import router as available_router
from emistream.api.routes.reserve.router import router as reserve_router
from emistream.api.routes.sse.router import router as sse_router

router = Router(
    path="/",
    route_handlers=[
        available_router,
        reserve_router,
        sse_router,
    ],
)
