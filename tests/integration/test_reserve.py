from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient
from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import AsyncTestClient

from octopus.utils.time import isostringify, naiveutcnow


@pytest_asyncio.fixture(loop_scope="session")
async def show_manager(
    beaver_client: AsyncClient,
) -> AbstractAsyncContextManager[dict]:
    """Context manager that sets up a show in the database."""

    @asynccontextmanager
    async def _setup_show() -> AsyncGenerator[dict]:
        response = await beaver_client.post("/shows", json={"title": "foo"})
        response.raise_for_status()

        show = response.json()

        try:
            yield show
        finally:
            response = await beaver_client.delete(f"/shows/{show['id']}")
            response.raise_for_status()

    return _setup_show()


@pytest_asyncio.fixture(loop_scope="session")
async def event_manager(
    beaver_client: AsyncClient, show_manager: AbstractAsyncContextManager[dict]
) -> AbstractAsyncContextManager[dict]:
    """Context manager that sets up an event in the database."""

    @asynccontextmanager
    async def _setup_event() -> AsyncGenerator[dict]:
        async with show_manager as show:
            response = await beaver_client.post(
                "/events",
                json={
                    "type": "live",
                    "showId": show["id"],
                    "start": isostringify(naiveutcnow()),
                    "duration": "PT1H",
                    "timezone": str(UTC),
                },
            )
            response.raise_for_status()

            event = response.json()

            try:
                yield event
            finally:
                response = await beaver_client.delete(f"/events/{event['id']}")
                response.raise_for_status()

    return _setup_event()


@pytest.mark.asyncio(loop_scope="session")
async def test_post(
    client: AsyncTestClient, event_manager: AbstractAsyncContextManager[dict]
) -> None:
    """Test if POST /reserve returns correct response."""
    async with event_manager as event:
        response = await client.post(
            "/reserve",
            json={"instance": {"event": event["id"], "start": event["start"]}},
        )

    status = response.status_code
    assert status == HTTP_201_CREATED

    data = response.json()
    assert "credentials" in data

    credentials = data["credentials"]
    assert "token" in credentials
    assert "expiresAt" in credentials

    token = credentials["token"]
    assert isinstance(token, str)
    assert len(token) > 0

    expires_at = credentials["expiresAt"]
    assert isinstance(expires_at, str)
    assert datetime.fromisoformat(expires_at)
