from typing import Literal, Self
from uuid import UUID

from pydantic import Field

from octopus.models.base import SerializableModel
from octopus.models.events.enums import EventType
from octopus.models.events.fields import CreatedAtField, DataField, TypeField
from octopus.services.streaming import models as sm
from octopus.utils.time import NaiveDatetime, UTCDatetime, awareutcnow


class Instance(SerializableModel):
    """Instance data."""

    event: UUID
    """Identifier of the event the instance belongs to."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""

    @classmethod
    def map(cls, instance: sm.Instance) -> Self:
        """Map from internal representation."""
        return cls(event=instance.event, start=instance.start)


class Availability(SerializableModel):
    """Availability of a stream."""

    instance: Instance | None
    """Instance that is currently being streamed."""

    checked_at: UTCDatetime
    """Datetime in UTC at which the availability was checked."""

    @classmethod
    def map(cls, availability: sm.Availability) -> Self:
        """Map from internal representation."""
        return cls(
            instance=Instance.map(availability.instance)
            if availability.instance
            else None,
            checked_at=availability.checked_at,
        )


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability
    """New availability."""


class AvailabilityChangedEvent(SerializableModel):
    """Event emitted when the availability of a stream changes."""

    type: TypeField[Literal[EventType.AVAILABILITY_CHANGED]] = (
        EventType.AVAILABILITY_CHANGED
    )
    created_at: CreatedAtField = Field(default_factory=awareutcnow)
    data: DataField[AvailabilityChangedEventData]
