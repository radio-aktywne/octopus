from litestar import Router

from emistream.api.routes.check.controller import Controller

router = Router(
    path="/check",
    route_handlers=[
        Controller,
    ],
)
