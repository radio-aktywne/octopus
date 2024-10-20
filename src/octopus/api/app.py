import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from importlib import metadata
from uuid import UUID

from litestar import Litestar, Router
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.contrib.pydantic import PydanticPlugin
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol
from pylocks.asyncio import AsyncioLock
from pylocks.base import Lock
from pystores.base import Store
from pystores.memory import MemoryStore

from octopus.api.routes.router import router
from octopus.config.models import Config
from octopus.services.beaver.service import BeaverService
from octopus.state import State


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _get_route_handlers(self) -> list[Router]:
        return [router]

    def _get_debug(self) -> bool:
        return self._config.debug

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None]:
        logger = logging.getLogger("httpx")
        disabled = logger.disabled
        logger.disabled = True

        try:
            yield
        finally:
            logger.disabled = disabled

    def _build_lifespan(
        self,
    ) -> list[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            self._suppress_httpx_logging_lifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            # Title of the service
            title="octopus",
            # Version of the service
            version=metadata.version("octopus"),
            # Description of the service
            summary="Broadcast streaming gate 🚧",
            # Use handler docstrings as operation descriptions
            use_handler_docstrings=True,
            # Endpoint to serve the OpenAPI docs from
            path="/schema",
        )

    def _build_channels_plugin(self) -> ChannelsPlugin:
        return ChannelsPlugin(
            # Store events in memory (good only for single instance services)
            backend=MemoryChannelsBackend(),
            # Channels to handle
            channels=["events"],
            # Don't allow channels outside of the list above
            arbitrary_channels_allowed=False,
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            # Use aliases for serialization
            prefer_alias=True,
            # Allow type coercion
            validate_strict=False,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_channels_plugin(),
            self._build_pydantic_plugin(),
        ]

    def _build_beaver(self) -> BeaverService:
        return BeaverService(
            config=self._config.beaver,
        )

    def _build_store(self) -> Store[UUID | None]:
        return MemoryStore[UUID | None](None)

    def _build_lock(self) -> Lock:
        return AsyncioLock()

    def _build_initial_state(self) -> State:
        config = self._config
        beaver = self._build_beaver()
        store = self._build_store()
        lock = self._build_lock()

        return State(
            {
                "config": config,
                "beaver": beaver,
                "store": store,
                "lock": lock,
            }
        )

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            debug=self._get_debug(),
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
