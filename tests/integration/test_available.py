from datetime import datetime

import pytest
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient


@pytest.mark.asyncio(scope="session")
async def test_get(client: AsyncTestClient) -> None:
    """Test if GET /available returns correct response."""

    response = await client.get("/available")

    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert "event" in data
    assert "checkedAt" in data

    event = data["event"]
    assert event is None

    checked_at = data["checkedAt"]
    assert datetime.fromisoformat(checked_at)
