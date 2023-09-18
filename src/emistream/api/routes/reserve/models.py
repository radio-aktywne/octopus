from pydantic import Field

from emistream.models import SerializableModel
from emistream.models.data import Reservation, ReservationRequest


class PostRequest(SerializableModel):
    """Request for POST requests."""

    request: ReservationRequest = Field(
        ...,
        title="PostRequest.Request",
        description="Request for the reservation.",
    )


class PostResponse(SerializableModel):
    """Response for POST requests."""

    reservation: Reservation = Field(
        ...,
        title="PostResponse.Reservation",
        description="Reservation information.",
    )
