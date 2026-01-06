from typing import Literal

from pydantic import Field

from octopus.models.base import SerializableModel, datamodel, serializable
from octopus.models.events import types as t
from octopus.services.streaming import models as m
from octopus.utils.time import naiveutcnow


@serializable
@datamodel
class Availability(m.Availability):
    """Availability of a stream."""

    @classmethod
    def map(cls, availability: m.Availability) -> "Availability":
        """Map to internal representation."""
        return cls(**vars(availability))


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability
    """New availability."""


class AvailabilityChangedEvent(SerializableModel):
    """Event emitted when the availability of a stream changes."""

    type: t.TypeField[Literal["availability-changed"]] = "availability-changed"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[AvailabilityChangedEventData]
