from litestar import Router

from emistream.api.routes.sse.controller import Controller

router = Router(
    path="/sse",
    route_handlers=[
        Controller,
    ],
)
