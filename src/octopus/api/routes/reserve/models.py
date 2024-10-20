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
    """Time in UTC at which the token expires if not used."""

    @staticmethod
    def map(credentials: sm.Credentials) -> "Credentials":
        return Credentials(
            token=credentials.token,
            expires_at=credentials.expires_at,
        )


class ReserveRequestData(SerializableModel):
    """Data for a reserve request."""

    event: UUID
    """Identifier of the event to reserve the stream for."""

    format: sm.Format = sm.Format.OGG
    """Format of the audio in the stream."""

    record: bool = False
    """Whether to record the stream."""


class ReserveResponseData(SerializableModel):
    """Data for a reserve response."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""

    port: int = Field(..., ge=1, le=65535)
    """Port to use to connect to the stream."""


@datamodel
class ReserveRequest:
    """Request to reserve a stream."""

    data: ReserveRequestData
    """Data for the request."""


@datamodel
class ReserveResponse:
    """Response for reserving a stream."""

    data: ReserveResponseData
    """Data for the response."""
