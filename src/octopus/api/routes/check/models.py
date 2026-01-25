from typing import Self
from uuid import UUID

from octopus.models.base import SerializableModel, datamodel
from octopus.services.streaming import models as sm
from octopus.utils.time import NaiveDatetime


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


type CheckResponseAvailability = Availability


@datamodel
class CheckRequest:
    """Request to check the availability of a stream."""


@datamodel
class CheckResponse:
    """Response for checking the availability of a stream."""

    availability: CheckResponseAvailability
    """Availability of the stream."""
