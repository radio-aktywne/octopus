import pytest
from litestar.testing import AsyncTestClient

from emistream.api.app import AppBuilder
from emistream.config.builder import ConfigBuilder


@pytest.fixture(scope="session")
def client() -> AsyncTestClient:
    """Reusable test client."""

    config = ConfigBuilder().build()
    app = AppBuilder(config).build()
    return AsyncTestClient(app=app)
