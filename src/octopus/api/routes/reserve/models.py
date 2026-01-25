from typing import Annotated, Self
from uuid import UUID

from pydantic import Field

from octopus.models.base import SerializableModel, datamodel
from octopus.services.streaming import models as sm
from octopus.utils.time import NaiveDatetime


class Credentials(SerializableModel):
    """Credentials for accessing the stream."""

    token: str
    """Token to use to connect to the stream."""

    expires_at: NaiveDatetime
    """Datetime in UTC at which the token expires if not used."""

    @classmethod
    def map(cls, credentials: sm.Credentials) -> Self:
        """Map to internal representation."""
        return cls(token=credentials.token, expires_at=credentials.expires_at)


class ReservationInput(SerializableModel):
    """Data for reserving a stream."""

    event: UUID
    """Identifier of the event to reserve the stream for."""

    format: sm.Format = sm.Format.OGG
    """Format of the audio in the stream."""

    record: bool = False
    """Whether to record the stream."""


class Reservation(SerializableModel):
    """Reservation of a stream."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""

    port: Annotated[int, Field(ge=1, le=65535)]
    """Port to use to connect to the stream."""


type ReserveRequestData = ReservationInput

type ReserveResponseReservation = Reservation


@datamodel
class ReserveRequest:
    """Request to reserve a stream."""

    data: ReserveRequestData
    """Data for reserving a stream."""


@datamodel
class ReserveResponse:
    """Response for reserving a stream."""

    reservation: ReserveResponseReservation
    """Reservation of the stream."""
