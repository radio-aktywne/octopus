from abc import ABC
from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import Field

from emistream.models.base import SerializableGenericModel, SerializableModel
from emistream.models.data import Availability
from emistream.time import utcnow

T = TypeVar("T")
D = TypeVar("D", bound=SerializableModel)


class Event(SerializableGenericModel, Generic[T, D], ABC):
    """Base class for events."""

    type: T
    created_at: datetime
    data: D

    class Config:
        fields = {
            "type": {
                "title": "Type",
                "description": "Type of the event.",
            },
            "created_at": {
                "default_factory": utcnow,
                "title": "CreatedAt",
                "description": "Time at which the event was created.",
            },
            "data": {
                "title": "Data",
                "description": "Data of the event.",
            },
        }


class DummyEventData(SerializableModel):
    """Data of a dummy event."""

    pass


class DummyEvent(Event[Literal["dummy"], DummyEventData]):
    """Dummy event that exists only so that there can be two types in discriminated union."""

    type: Literal["dummy"] = "dummy"
    data: DummyEventData = DummyEventData()


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability = Field(
        ...,
        title="Availability",
        description="New availability.",
    )


class AvailabilityChangedEvent(
    Event[Literal["availability-changed"], AvailabilityChangedEventData]
):
    """Event that indicates a change in availability."""

    type: Literal["availability-changed"] = "availability-changed"


class ParsableEvent(SerializableModel):
    """Event that can be parsed from a serialized form."""

    __root__: DummyEvent | AvailabilityChangedEvent = Field(discriminator="type")
