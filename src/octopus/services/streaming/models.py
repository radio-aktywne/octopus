from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from octopus.models.base import datamodel


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


@datamodel
class Instance:
    """Instance data."""

    event: UUID
    """Identifier of the event the instance belongs to."""

    start: datetime
    """Start datetime of the instance in event timezone."""


@datamodel
class Availability:
    """Availability of a stream."""

    instance: Instance | None
    """Instance that is currently being streamed."""

    checked_at: datetime
    """Datetime in UTC at which the availability was checked."""


@datamodel
class Credentials:
    """Credentials for accessing the stream."""

    token: str
    """Token to use to connect to the stream."""

    expires_at: datetime
    """Datetime in UTC at which the token expires if not used."""


@datamodel
class CheckRequest:
    """Request to check the availability of a stream."""


@datamodel
class CheckResponse:
    """Response for checking the availability of a stream."""

    availability: Availability
    """Availability of the stream."""


@datamodel
class ReserveRequest:
    """Request to reserve a stream."""

    instance: Instance
    """Instance to reserve the stream for."""

    format: Format
    """Format of the audio in the stream."""

    record: bool
    """Whether to record the stream."""

    metadata: Mapping[str, str] | None
    """Metadata to attach to the stream."""


@datamodel
class ReserveResponse:
    """Response for reserving a stream."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""
