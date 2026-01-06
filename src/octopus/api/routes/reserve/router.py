from litestar import Router

from octopus.api.routes.reserve.controller import Controller

router = Router(
    path="/reserve",
    tags=["Reserve"],
    route_handlers=[
        Controller,
    ],
)
