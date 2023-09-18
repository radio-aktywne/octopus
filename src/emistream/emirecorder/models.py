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
        {},
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
        {},
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


class RecordRequest(SerializableModel):
    """Request for record endpoint."""

    request: RecordingRequest = Field(
        ...,
        title="Request",
        description="Request for a recording.",
    )


class RecordResponse(SerializableModel):
    """Response from record endpoint."""

    credentials: RecordingCredentials = Field(
        ...,
        title="Credentials",
        description="Credentials for the recording.",
    )
