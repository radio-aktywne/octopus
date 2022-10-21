import asyncio

import uvicorn
from starlite import Starlite
from uvicorn import Server

from emistream.config import Config


async def _run(server: Server) -> None:
    server_task = asyncio.create_task(server.serve())
    await asyncio.wait([server_task])


def run(api: Starlite, config: Config) -> None:
    cfg = uvicorn.Config(api, host=config.host, port=config.port)
    server = Server(cfg)

    asyncio.run(_run(server))
