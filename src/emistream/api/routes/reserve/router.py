from litestar import Router

from emistream.api.routes.reserve.controller import Controller

router = Router(
    path="/reserve",
    route_handlers=[
        Controller,
    ],
)
