import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, BasicAuth
from litestar import Litestar
from litestar.testing import AsyncTestClient

from octopus.api.app import AppBuilder
from octopus.config.builder import ConfigBuilder
from octopus.config.models import Config
from tests.utils.containers import AsyncDockerContainer
from tests.utils.waiting.conditions import CallableCondition, CommandCondition
from tests.utils.waiting.strategies import TimeoutStrategy
from tests.utils.waiting.waiter import Waiter


@pytest.fixture(scope="session")
def config() -> Config:
    """Build configuration."""
    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Build application."""
    return AppBuilder(config).build()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def quokka() -> AsyncGenerator[AsyncDockerContainer]:
    """Run quokka container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10000") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer("ghcr.io/radio-aktywne/services/quokka:latest")
    container = container.with_kwargs(network="host")

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def dingo(
    quokka: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer]:
    """Run dingo container."""
    container = AsyncDockerContainer("ghcr.io/radio-aktywne/services/dingo:latest")
    container = container.with_kwargs(network="host")

    async with container as container:
        await asyncio.sleep(5)
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def emerald() -> AsyncGenerator[AsyncDockerContainer]:
    """Run emerald container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10710") as client:
            response = await client.get("/minio/health/ready")
            response.raise_for_status()

    container = AsyncDockerContainer("ghcr.io/radio-aktywne/databases/emerald:latest")
    container = container.with_kwargs(network="host")

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def gecko(
    emerald: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer]:
    """Run gecko container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10700") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer("ghcr.io/radio-aktywne/services/gecko:latest")
    container = container.with_kwargs(network="host")

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def howlite() -> AsyncGenerator[AsyncDockerContainer]:
    """Run howlite container."""

    async def _check() -> None:
        auth = BasicAuth(username="user", password="password")
        async with AsyncClient(base_url="http://localhost:10520", auth=auth) as client:
            response = await client.get("/user/calendar")
            response.raise_for_status()

    container = AsyncDockerContainer("ghcr.io/radio-aktywne/databases/howlite:latest")
    container = container.with_kwargs(network="host")

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def sapphire() -> AsyncGenerator[AsyncDockerContainer]:
    """Run sapphire container."""
    container = AsyncDockerContainer("ghcr.io/radio-aktywne/databases/sapphire:latest")
    container = container.with_kwargs(network="host", privileged=True)

    waiter = Waiter(
        condition=CommandCondition(
            [
                "usql",
                "--command",
                "SELECT 1;",
                "postgres://user:password@localhost:10510/database",
            ]
        ),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def beaver(
    howlite: AsyncDockerContainer, sapphire: AsyncDockerContainer
) -> AsyncGenerator[AsyncDockerContainer]:
    """Run beaver container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10500") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer("ghcr.io/radio-aktywne/services/beaver:latest")
    container = container.with_kwargs(network="host")

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def gecko_client(
    gecko: AsyncDockerContainer,
) -> AsyncGenerator[AsyncClient]:
    """Build gecko client."""
    async with AsyncClient(base_url="http://localhost:10700") as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def beaver_client(
    beaver: AsyncDockerContainer,
) -> AsyncGenerator[AsyncClient]:
    """Build beaver client."""
    async with AsyncClient(base_url="http://localhost:10500") as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def client(
    app: Litestar,
    dingo: AsyncDockerContainer,
    gecko: AsyncDockerContainer,
) -> AsyncGenerator[AsyncTestClient]:
    """Build test client."""
    async with AsyncTestClient(app=app) as client:
        yield client
