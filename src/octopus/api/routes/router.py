from litestar import Router

from octopus.api.routes.check.router import router as check_router
from octopus.api.routes.ping.router import router as ping_router
from octopus.api.routes.reserve.router import router as reserve_router
from octopus.api.routes.sse.router import router as sse_router
from octopus.api.routes.test.router import router as test_router

router = Router(
    path="/",
    route_handlers=[
        check_router,
        ping_router,
        reserve_router,
        sse_router,
        test_router,
    ],
)
