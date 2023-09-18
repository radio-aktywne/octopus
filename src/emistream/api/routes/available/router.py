from litestar import Router

from emistream.api.routes.available.controller import Controller

router = Router(
    path="/available",
    route_handlers=[
        Controller,
    ],
)
