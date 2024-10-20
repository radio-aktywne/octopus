from typing import Literal

from octopus.models.base import SerializableModel, datamodel, serializable
from octopus.models.events import types as t
from octopus.services.streaming import models as m


@serializable
@datamodel
class Availability(m.Availability):
    @classmethod
    def map(cls, availability: m.Availability) -> "Availability":
        return cls(**vars(availability))


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability
    """New availability."""


class AvailabilityChangedEvent(SerializableModel):
    """Event emitted when the availability of a stream changes."""

    type: t.TypeFieldType[Literal["availability-changed"]] = "availability-changed"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[AvailabilityChangedEventData]
