from datetime import datetime
from enum import StrEnum
from uuid import UUID

from emistream.models.base import datamodel


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


@datamodel
class Availability:
    """Availability of a stream."""

    event: UUID | None
    """Identifier of the event that is currently being streamed."""

    checked_at: datetime
    """Time in UTC at which the availability was checked."""


@datamodel
class Credentials:
    """Credentials for accessing the stream."""

    token: str
    """Token to use to connect to the stream."""

    expires_at: datetime
    """Time in UTC at which the token expires if not used."""


@datamodel
class CheckRequest:
    """Request to check the availability of a stream."""

    pass


@datamodel
class CheckResponse:
    """Response for checking the availability of a stream."""

    availability: Availability
    """Availability of the stream."""


@datamodel
class ReserveRequest:
    """Request to reserve a stream."""

    event: UUID
    """Identifier of the event to reserve the stream for."""

    format: Format
    """Format of the audio in the stream."""

    record: bool
    """Whether to record the stream."""


@datamodel
class ReserveResponse:
    """Response for reserving a stream."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""

    port: int
    """Port to use to connect to the stream."""
