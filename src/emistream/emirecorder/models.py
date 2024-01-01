from typing import Literal
from uuid import UUID

from pydantic import Field, NaiveDatetime

from emistream.models.base import SerializableModel

Format = Literal["ogg"]


class RecordPostRequest(SerializableModel):
    """Request for POST method of record endpoint."""

    event: UUID = Field(
        ...,
        title="PostRecordRequest.Event",
        description="Identifier of the event to record.",
    )
    format: Format = Field(
        "ogg",
        title="PostRecordRequest.Format",
        description="Format of the recording.",
    )


class Credentials(SerializableModel):
    """Credentials for a recording stream."""

    token: str = Field(
        ...,
        title="Credentials.Token",
        description="Token to use to connect to the stream.",
    )
    expires_at: NaiveDatetime = Field(
        ...,
        title="Credentials.ExpiresAt",
        description="Time in UTC at which the token expires if not used.",
    )


class RecordPostResponse(SerializableModel):
    """Response from POST method of record endpoint."""

    credentials: Credentials = Field(
        ...,
        title="PostRecordResponse.Credentials",
        description="Credentials to use to connect to the stream.",
    )
    port: int = Field(
        ...,
        title="PostRecordResponse.Port",
        description="Port to use to connect to the stream.",
    )
