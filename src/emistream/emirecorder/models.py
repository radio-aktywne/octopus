from datetime import datetime

from pydantic import Field

from emistream.models.base import SerializableModel


class Show(SerializableModel):
    """Show information."""

    label: str = Field(
        ...,
        title="Show.Label",
        description="Label of the show.",
    )
    metadata: dict[str, str] = Field(
        ...,
        default_factory=dict,
        title="Show.Metadata",
        description="Metadata of the show.",
    )


class Event(SerializableModel):
    """Event information."""

    show: Show = Field(
        ...,
        title="Event.Show",
        description="Show this event is for.",
    )
    start: datetime | None = Field(
        ...,
        title="Event.Start",
        description="Start time of the event.",
    )
    end: datetime | None = Field(
        ...,
        title="Event.End",
        description="End time of the event.",
    )
    metadata: dict[str, str] = Field(
        ...,
        default_factory=dict,
        title="Event.Metadata",
        description="Metadata of the event.",
    )


class RecordingRequest(SerializableModel):
    """Request for a recording."""

    event: Event = Field(
        ...,
        title="RecordingRequest.Event",
        description="Event to reserve.",
    )


class RecordingCredentials(SerializableModel):
    """Credentials for a recording."""

    token: str = Field(
        ...,
        title="RecordingCredentials.Token",
        description="Token to use to connect to the stream.",
    )
    expires_at: datetime = Field(
        ...,
        title="RecordingCredentials.ExpiresAt",
        description="Time at which the token expires if not used.",
    )


class PostRecordRequest(SerializableModel):
    """Request for POST method of record endpoint."""

    request: RecordingRequest = Field(
        ...,
        title="PostRecordRequest.Request",
        description="Request for a recording.",
    )


class PostRecordResponse(SerializableModel):
    """Response from POST method of record endpoint."""

    credentials: RecordingCredentials = Field(
        ...,
        title="PostRecordResponse.Credentials",
        description="Credentials for the recording.",
    )
