import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, BasicAuth
from litestar import Litestar
from litestar.testing import AsyncTestClient

from emistream.api.app import AppBuilder
from emistream.config.builder import ConfigBuilder
from emistream.config.models import Config
from tests.utils.containers import AsyncDockerContainer
from tests.utils.waiting.conditions import CallableCondition, CommandCondition
from tests.utils.waiting.strategies import TimeoutStrategy
from tests.utils.waiting.waiter import Waiter


@pytest.fixture(scope="session")
def config() -> Config:
    """Loaded configuration."""

    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Reusable application."""

    return AppBuilder(config).build()


@pytest_asyncio.fixture(scope="session")
async def streamcast() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Streamcast container."""

    async def _check() -> None:
        auth = BasicAuth(username="admin", password="password")
        async with AsyncClient(base_url="http://localhost:8000", auth=auth) as client:
            response = await client.get("/admin/stats.json")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/streamcast:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def fusion(
    streamcast: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer, None]:
    """Fusion container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/fusion:latest",
        network="host",
    )

    async with container as container:
        await asyncio.sleep(5)
        yield container


@pytest_asyncio.fixture(scope="session")
async def emiarchive() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Emiarchive container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:30000") as client:
            response = await client.get("/minio/health/ready")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emiarchive:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def emirecorder(
    emiarchive: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer, None]:
    """Emirecorder container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:31000") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emirecorder:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def emishows_database() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Emishows database container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emishows-db:latest",
        network="host",
        privileged=True,
    )

    waiter = Waiter(
        condition=CommandCondition(
            [
                "usql",
                "--command",
                "SELECT 1;",
                "postgres://user:password@localhost:34000/database",
            ]
        ),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def emitimes() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Emitimes container."""

    async def _check() -> None:
        auth = BasicAuth(username="user", password="password")
        async with AsyncClient(base_url="http://localhost:36000", auth=auth) as client:
            response = await client.get("/user/emitimes")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emitimes:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def emishows(
    emishows_database: AsyncDockerContainer, emitimes: AsyncDockerContainer
) -> AsyncGenerator[AsyncDockerContainer, None]:
    """Emishows container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:35000") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emishows:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def emishows_client(
    emishows: AsyncDockerContainer,
) -> AsyncGenerator[AsyncClient, None]:
    """Emishows client."""

    async with AsyncClient(base_url="http://localhost:35000") as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def client(
    app: Litestar,
    fusion: AsyncDockerContainer,
    emirecorder: AsyncDockerContainer,
) -> AsyncGenerator[AsyncTestClient, None]:
    """Reusable test client."""

    async with AsyncTestClient(app=app) as client:
        yield client
