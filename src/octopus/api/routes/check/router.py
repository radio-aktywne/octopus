from litestar import Router

from octopus.api.routes.check.controller import Controller

router = Router(
    path="/check",
    tags=["Check"],
    route_handlers=[
        Controller,
    ],
)
