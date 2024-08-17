from uuid import UUID

from emistream.models.base import SerializableModel, datamodel
from emistream.services.streaming import models as sm
from emistream.utils.time import NaiveDatetime


class Availability(SerializableModel):
    """Availability of a stream."""

    event: UUID | None
    """Identifier of the event that is currently being streamed."""

    checked_at: NaiveDatetime
    """Time in UTC at which the availability was checked."""

    @staticmethod
    def map(availability: sm.Availability) -> "Availability":
        return Availability(
            event=availability.event,
            checked_at=availability.checked_at,
        )


CheckResponseAvailability = Availability


@datamodel
class CheckRequest:
    """Request to check the availability of a stream."""

    pass


@datamodel
class CheckResponse:
    """Response for checking the availability of a stream."""

    availability: CheckResponseAvailability
    """Availability of the stream."""
