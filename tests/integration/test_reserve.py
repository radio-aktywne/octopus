from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient
from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import AsyncTestClient

from octopus.utils.time import naiveutcnow, stringify


@pytest_asyncio.fixture(scope="session")
async def show_manager(
    beaver_client: AsyncClient,
) -> AbstractAsyncContextManager[UUID]:
    """Context manager that sets up a show in the database."""

    @asynccontextmanager
    async def _setup_show() -> AsyncGenerator[UUID]:
        response = await beaver_client.post(
            "/shows",
            json={
                "title": "foo",
            },
        )
        response.raise_for_status()

        uid = response.json()["id"]

        try:
            yield UUID(uid)
        finally:
            response = await beaver_client.delete(f"/shows/{uid}")
            response.raise_for_status()

    return _setup_show()


@pytest_asyncio.fixture(scope="session")
async def event_manager(
    beaver_client: AsyncClient, show_manager: AbstractAsyncContextManager[UUID]
) -> AbstractAsyncContextManager[UUID]:
    """Context manager that sets up an event in the database."""

    @asynccontextmanager
    async def _setup_event() -> AsyncGenerator[UUID]:
        async with show_manager as show:
            start = naiveutcnow()
            end = start + timedelta(hours=1)

            response = await beaver_client.post(
                "/events",
                json={
                    "type": "live",
                    "showId": str(show),
                    "start": stringify(start),
                    "end": stringify(end),
                    "timezone": str(UTC),
                },
            )
            response.raise_for_status()

            uid = response.json()["id"]

            try:
                yield UUID(uid)
            finally:
                response = await beaver_client.delete(f"/events/{uid}")
                response.raise_for_status()

    return _setup_event()


@pytest.mark.asyncio(scope="session")
async def test_post(
    client: AsyncTestClient, event_manager: AbstractAsyncContextManager[UUID]
) -> None:
    """Test if POST /reserve returns correct response."""

    async with event_manager as event:
        response = await client.post(
            "/reserve",
            json={
                "event": str(event),
            },
        )

    status = response.status_code
    assert status == HTTP_201_CREATED

    data = response.json()
    assert "credentials" in data
    assert "port" in data

    credentials = data["credentials"]
    assert "token" in credentials
    assert "expiresAt" in credentials

    token = credentials["token"]
    assert isinstance(token, str)
    assert len(token) > 0

    expires_at = credentials["expiresAt"]
    assert isinstance(expires_at, str)
    assert datetime.fromisoformat(expires_at)

    port = data["port"]
    assert isinstance(port, int)
