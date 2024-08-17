from enum import StrEnum
from uuid import UUID

from pydantic import Field

from emistream.models.base import SerializableModel, datamodel
from emistream.utils.time import NaiveDatetime


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


class Credentials(SerializableModel):
    """Credentials for a recording stream."""

    token: str
    """Token to use to connect to the stream."""

    expires_at: NaiveDatetime
    """Time in UTC at which the token expires if not used."""


class RecordRequestData(SerializableModel):
    """Data for a record request."""

    event: UUID
    """Identifier of the event to record."""

    format: Format = Format.OGG
    """Format of the recording."""


class RecordResponseData(SerializableModel):
    """Data for a record response."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""

    port: int = Field(..., ge=1, le=65535)
    """Port to use to connect to the stream."""


@datamodel
class RecordRequest:
    """Request to record."""

    data: RecordRequestData
    """Data for the request."""


@datamodel
class RecordResponse:
    """Response for record."""

    data: RecordResponseData
    """Data for the response."""
