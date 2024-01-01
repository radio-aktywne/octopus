from typing import Literal
from uuid import UUID

from pydantic import Field, NaiveDatetime

from emistream.models.base import SerializableModel

Format = Literal["ogg"]


class ReserveRequest(SerializableModel):
    """Request for reserving a stream."""

    event: UUID = Field(
        ...,
        title="Request.Event",
        description="Identifier of the event to reserve the stream for.",
    )
    format: Format = Field(
        "ogg",
        title="Request.Format",
        description="Format of the audio stream.",
    )
    record: bool = Field(
        False,
        title="Request.Record",
        description="Whether to record the stream.",
    )


class Credentials(SerializableModel):
    """Credentials for accessing the stream."""

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


class ReserveResponse(SerializableModel):
    """Response to a stream reservation request."""

    credentials: Credentials = Field(
        ...,
        title="Response.Credentials",
        description="Credentials to use to connect to the stream.",
    )
    port: int = Field(
        ...,
        title="Response.Port",
        description="Port to use to connect to the stream.",
    )


class RecorderAccess(SerializableModel):
    """Data needed to access the recorder."""

    token: str = Field(
        ...,
        title="RecorderData.Token",
        description="Token to use to connect to the stream.",
    )
    port: int = Field(
        ...,
        title="RecorderData.Port",
        description="Port to use to connect to the stream.",
    )
