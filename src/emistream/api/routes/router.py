from litestar import Router

from emistream.api.routes.check.router import router as check_router
from emistream.api.routes.ping.router import router as ping_router
from emistream.api.routes.reserve.router import router as reserve_router
from emistream.api.routes.sse.router import router as sse_router

router = Router(
    path="/",
    route_handlers=[
        check_router,
        ping_router,
        reserve_router,
        sse_router,
    ],
)
