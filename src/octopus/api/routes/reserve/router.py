from litestar import Router

from octopus.api.routes.reserve.controller import Controller

router = Router(
    path="/reserve",
    route_handlers=[
        Controller,
    ],
)
