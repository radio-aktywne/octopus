from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from litestar import Litestar, Router
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from emistream.api.routes.router import router
from emistream.builder import Builder
from emistream.config import Config
from emistream.state import State
from emistream.stream.state import StreamState


class AppBuilder(Builder[Litestar]):
    """Builds the app.

    Args:
        config: Config object.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _get_route_handlers(self) -> list[Router]:
        return [router]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            title="emistream",
            version="0.6.0",
            description="Emission streaming logic 🔴",
        )

    def _build_channels_plugin(self) -> ChannelsPlugin:
        return ChannelsPlugin(
            backend=MemoryChannelsBackend(),
            channels=["events"],
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_channels_plugin(),
        ]

    def _build_initial_state(self) -> State:
        return State(
            {
                "config": self._config,
                "stream": StreamState(),
            }
        )

    @asynccontextmanager
    async def _stream_state_lifespan(self, app: Litestar) -> AsyncGenerator[None, None]:
        async with app.state.stream:
            yield

    def _build_lifespans(
        self,
    ) -> list[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            self._stream_state_lifespan,
        ]

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
            lifespan=self._build_lifespans(),
        )
