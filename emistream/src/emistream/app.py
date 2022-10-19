from starlite import Starlite, State

from emistream.config import Config
from emistream.paths.router import router
from emistream.stream.management import StreamManager


def build_app(config: Config):
    async def setup(state: State) -> None:
        state.stream_manager = StreamManager(config)

    async def cleanup(state: State) -> None:
        pass

    return Starlite(
        route_handlers=[router], on_startup=[setup], on_shutdown=[cleanup]
    )
