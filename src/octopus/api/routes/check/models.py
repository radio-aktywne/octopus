from typing import Self
from uuid import UUID

from octopus.models.base import SerializableModel, datamodel
from octopus.services.streaming import models as sm
from octopus.utils.time import NaiveDatetime, UTCDatetime


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


type CheckResponseAvailability = Availability


@datamodel
class CheckRequest:
    """Request to check the availability of a stream."""


@datamodel
class CheckResponse:
    """Response for checking the availability of a stream."""

    availability: CheckResponseAvailability
    """Availability of the stream."""
