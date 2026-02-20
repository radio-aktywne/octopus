from litestar import Router

from octopus.api.routes.check.router import router as check
from octopus.api.routes.ping.router import router as ping
from octopus.api.routes.reserve.router import router as reserve
from octopus.api.routes.sse.router import router as sse
from octopus.api.routes.test.router import router as test

router = Router(
    path="/",
    route_handlers=[
        check,
        ping,
        reserve,
        sse,
        test,
    ],
)
