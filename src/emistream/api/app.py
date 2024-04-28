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

from emistream.api.routes.router import router
from emistream.config.models import Config
from emistream.emirecorder.service import EmirecorderService
from emistream.emishows.service import EmishowsService
from emistream.state import State


class AppBuilder:
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
            title="emistream app",
            version=metadata.version("emistream"),
            description="Emission streaming logic 🔴",
        )

    def _build_channels_plugin(self) -> ChannelsPlugin:
        return ChannelsPlugin(
            backend=MemoryChannelsBackend(),
            channels=["events"],
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            prefer_alias=True,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_channels_plugin(),
            self._build_pydantic_plugin(),
        ]

    def _build_emishows(self) -> EmishowsService:
        return EmishowsService(self._config.emishows.http)

    def _build_emirecorder(self) -> EmirecorderService:
        return EmirecorderService(self._config.emirecorder.http)

    def _build_store(self) -> Store[UUID | None]:
        return MemoryStore(None)

    def _build_lock(self) -> Lock:
        return AsyncioLock()

    def _build_initial_state(self) -> State:
        return State(
            {
                "config": self._config,
                "emishows": self._build_emishows(),
                "emirecorder": self._build_emirecorder(),
                "store": self._build_store(),
                "lock": self._build_lock(),
            }
        )

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None, None]:
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

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
            lifespan=self._build_lifespan(),
        )
