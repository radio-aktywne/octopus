from datetime import datetime
from enum import StrEnum
from uuid import UUID

from octopus.models.base import datamodel


class Format(StrEnum):
    """Recording format."""

    OGG = "ogg"


@datamodel
class Instance:
    """Instance data."""

    event: UUID
    """Event identifier."""

    start: datetime
    """Instance start datetime."""
