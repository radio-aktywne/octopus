from uuid import UUID

from pydantic import Field, NaiveDatetime

from emistream.models.base import SerializableModel


class Availability(SerializableModel):
    """Availability information."""

    event: UUID | None = Field(
        ...,
        title="Availability.Event",
        description="Identifier of the event that is currently on air.",
    )
    checked_at: NaiveDatetime = Field(
        ...,
        title="Availability.CheckedAt",
        description="Time in UTC at which the availability was checked.",
    )
