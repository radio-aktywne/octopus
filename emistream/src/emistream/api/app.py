from starlite import State, Starlite, WebSocketException, CORSConfig

from emistream.api.paths.router import router
from emistream.config import Config
from emistream.fusion.client import FusionClient
from emistream.recorder.client import RecorderClient
from emistream.stream.management import StreamManager


def build(config: Config) -> Starlite:
    async def setup(state: State) -> None:
        state.stream_manager = StreamManager(
            config,
            RecorderClient(config.emirecorder.host, config.emirecorder.port),
            FusionClient(config.fusion.host, config.fusion.port),
        )
        state.sockets = {}

    async def cleanup(state: State) -> None:
        for uid, socket in state.sockets.items():
            try:
                await socket.close()
            except (ConnectionError, WebSocketException):
                pass
            state.sockets.pop(uid, None)

    return Starlite(
        route_handlers=[router],
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        on_startup=[setup],
        on_shutdown=[cleanup],
    )
