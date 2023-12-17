import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient

from emistream.api.app import AppBuilder
from emistream.config.builder import ConfigBuilder
from emistream.config.models import Config


@pytest.fixture(scope="session")
def config() -> Config:
    """Loaded configuration."""

    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Reusable application."""

    return AppBuilder(config).build()


@pytest.fixture(scope="session")
def client(app: Litestar) -> AsyncTestClient:
    """Reusable test client."""

    return AsyncTestClient(app=app)
