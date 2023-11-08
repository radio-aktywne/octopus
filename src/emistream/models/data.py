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


class Availability(SerializableModel):
    """Availability information."""

    event: Event | None = Field(
        ...,
        title="Availability.Event",
        description="Event that is currently on air.",
    )
    checked_at: datetime = Field(
        ...,
        title="Availability.CheckedAt",
        description="Time at which the availability was checked.",
    )


class ReservationRequest(SerializableModel):
    """Request for a reservation."""

    event: Event = Field(
        ...,
        title="ReservationRequest.Event",
        description="Event to reserve.",
    )
    record: bool = Field(
        False,
        title="ReservationRequest.Record",
        description="Whether to record the stream.",
    )


class Reservation(SerializableModel):
    """Reservation information."""

    token: str = Field(
        ...,
        title="Reservation.Token",
        description="Token to use to connect to the stream.",
    )
    expires_at: datetime = Field(
        ...,
        title="Reservation.ExpiresAt",
        description="Time at which the reservation expires if not connected.",
    )
