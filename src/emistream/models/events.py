from datetime import datetime
from typing import Annotated, Literal, TypeVar

from pydantic import Field, RootModel

from emistream.models.base import SerializableModel
from emistream.models.data import Availability
from emistream.time import utcnow

TypeType = TypeVar("TypeType")
DataType = TypeVar("DataType", bound=SerializableModel)

TypeFieldType = Annotated[
    TypeType,
    Field(description="Type of the event."),
]
CreatedAtFieldType = Annotated[
    datetime,
    Field(default_factory=utcnow, description="Time at which the event was created."),
]
DataFieldType = Annotated[
    DataType,
    Field(description="Data of the event."),
]


class DummyEventData(SerializableModel):
    """Data of a dummy event."""

    pass


class DummyEvent(SerializableModel):
    """Dummy event that exists only so that there can be two types in discriminated union."""

    type: TypeFieldType[Literal["dummy"]] = Field(
        "dummy",
        title="DummyEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="DummyEvent.CreatedAt",
    )
    data: DataFieldType[DummyEventData] = Field(
        DummyEventData(),
        title="DummyEvent.Data",
    )


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability = Field(
        ...,
        title="AvailabilityChangedEventData.Availability",
        description="New availability.",
    )


class AvailabilityChangedEvent(SerializableModel):
    """Event that indicates a change in availability."""

    type: TypeFieldType[Literal["availability-changed"]] = Field(
        "availability-changed",
        title="AvailabilityChangedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="AvailabilityChangedEvent.CreatedAt",
    )
    data: DataFieldType[AvailabilityChangedEventData] = Field(
        ...,
        title="AvailabilityChangedEvent.Data",
    )


Event = Annotated[
    DummyEvent | AvailabilityChangedEvent, Field(..., discriminator="type")
]
ParsableEvent = RootModel[Event]
