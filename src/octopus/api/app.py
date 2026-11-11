from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol
from pylocks.asyncio import AsyncioLock
from pystores.memory import MemoryStore

from octopus.api.lifespans import (
    StreamingLifespan,
    SuppressHTTPX2LoggingLifespan,
    SuppressHTTPXLoggingLifespan,
    TestLifespan,
)
from octopus.api.openapi import OpenAPIConfigBuilder
from octopus.api.plugins.pydantic import PydanticPlugin
from octopus.api.routes.router import router
from octopus.config.models import Config
from octopus.services.apis.beaver.service import BeaverService
from octopus.services.streaming.models import Instance
from octopus.services.streaming.service import StreamingService
from octopus.state import State


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.

    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_lifespan(
        self,
    ) -> Sequence[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            TestLifespan,
            SuppressHTTPXLoggingLifespan,
            SuppressHTTPX2LoggingLifespan,
            StreamingLifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfigBuilder().build()

    def _build_channels_plugin(self) -> ChannelsPlugin:
        return ChannelsPlugin(backend=MemoryChannelsBackend(), channels=["events"])

    def _build_plugins(self, channels: ChannelsPlugin) -> Sequence[PluginProtocol]:
        return [
            channels,
            PydanticPlugin(),
        ]

    def _build_initial_state(self, channels: ChannelsPlugin) -> State:
        beaver = BeaverService(config=self._config.beaver)
        lock = AsyncioLock()
        store = MemoryStore[Instance | None](None)
        streaming = StreamingService(
            config=self._config,
            store=store,
            lock=lock,
            beaver=beaver,
            channels=channels,
        )

        return State(
            {
                "config": self._config,
                "beaver": beaver,
                "lock": lock,
                "store": store,
                "streaming": streaming,
            }
        )

    def build(self) -> Litestar:
        """Build the app."""
        channels = self._build_channels_plugin()

        return Litestar(
            route_handlers=[router],
            debug=self._config.debug,
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(channels),
            state=self._build_initial_state(channels),
        )
