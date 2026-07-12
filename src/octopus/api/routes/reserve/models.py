from collections.abc import Mapping
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

    def map(self) -> sm.Instance:
        """Map to internal representation."""
        return sm.Instance(event=self.event, start=self.start)


class ReservationInput(SerializableModel):
    """Data for reserving a stream."""

    instance: Instance
    """Instance to reserve the stream for."""

    format: sm.Format = sm.Format.OGG
    """Format of the audio in the stream."""

    record: bool = False
    """Whether to record the stream."""

    metadata: Mapping[str, str] | None = None
    """Metadata to attach to the stream."""


class Credentials(SerializableModel):
    """Credentials for accessing the stream."""

    token: str
    """Token to use to connect to the stream."""

    expires_at: UTCDatetime
    """Datetime in UTC at which the token expires if not used."""

    @classmethod
    def map(cls, credentials: sm.Credentials) -> Self:
        """Map from internal representation."""
        return cls(token=credentials.token, expires_at=credentials.expires_at)


class Reservation(SerializableModel):
    """Reservation of a stream."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""


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
