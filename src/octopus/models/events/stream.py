from typing import Literal, Self
from uuid import UUID

from pydantic import Field

from octopus.models.base import SerializableModel
from octopus.models.events.enums import EventType
from octopus.models.events.fields import CreatedAtField, DataField, TypeField
from octopus.services.streaming import models as sm
from octopus.utils.time import NaiveDatetime, naiveutcnow


class Availability(SerializableModel):
    """Availability of a stream."""

    event: UUID | None
    """Identifier of the event that is currently being streamed."""

    checked_at: NaiveDatetime
    """Datetime in UTC at which the availability was checked."""

    @classmethod
    def map(cls, availability: sm.Availability) -> Self:
        """Map to internal representation."""
        return cls(event=availability.event, checked_at=availability.checked_at)


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability
    """New availability."""


class AvailabilityChangedEvent(SerializableModel):
    """Event emitted when the availability of a stream changes."""

    type: TypeField[Literal[EventType.AVAILABILITY_CHANGED]] = (
        EventType.AVAILABILITY_CHANGED
    )
    created_at: CreatedAtField = Field(default_factory=naiveutcnow)
    data: DataField[AvailabilityChangedEventData]
