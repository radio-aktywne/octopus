from collections.abc import Sequence
from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from octopus.models.base import SerializableModel, datamodel
from octopus.utils.time import NaiveDatetime, Timedelta, Timezone, UTCDatetime


class EventType(StrEnum):
    """Event type options."""

    live = "live"
    replay = "replay"
    prerecorded = "prerecorded"


class Show(SerializableModel):
    """Show data."""

    id: UUID
    """Identifier of the show."""

    title: str
    """Title of the show."""


class Event(SerializableModel):
    """Event data."""

    id: UUID
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show: Show | None
    """Show the event belongs to."""

    timezone: Timezone
    """Timezone of the event."""


class Instance(SerializableModel):
    """Instance data."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""

    duration: Timedelta
    """Duration of the instance."""

    event: Event | None
    """Event the instance belongs to."""


class InstanceList(SerializableModel):
    """List of instances."""

    instances: Sequence[Instance]
    """Instances that matched the request."""


class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: UUID
    """Identifier of the event."""


EventRelationFilter = TypedDict(
    "EventRelationFilter",
    {
        "is": EventWhereInput,
        "is_not": EventWhereInput,
    },
    total=False,
)


class InstanceWhereInput(TypedDict, total=False):
    """Instance arguments for searching."""

    event: EventRelationFilter
    """Event relation filter."""


class EventInclude(TypedDict, total=False):
    """Relations to include when querying events."""

    show: bool
    """Show relation to include."""


class EventArgsFromInstance(TypedDict, total=False):
    """Event arguments to include when querying instances."""

    include: EventInclude
    """Relations to include when querying events from instances."""


class InstanceInclude(TypedDict, total=False):
    """Relations to include when querying instances."""

    event: EventArgsFromInstance
    """Event relation to include."""


type InstancesListRequestStart = UTCDatetime

type InstancesListRequestEnd = UTCDatetime

type InstancesListRequestWhere = InstanceWhereInput | None

type InstancesListRequestInclude = InstanceInclude | None

type InstancesListResponseResults = InstanceList


@datamodel
class InstancesListRequest:
    """Request to list instances."""

    start: InstancesListRequestStart
    """Start datetime in UTC to filter events instances."""

    end: InstancesListRequestEnd
    """End datetime in UTC to filter events instances."""

    where: InstancesListRequestWhere
    """Filter to apply to find events."""

    include: InstancesListRequestInclude
    """Relations to include in the response."""


@datamodel
class InstancesListResponse:
    """Response for listing instances."""

    results: InstancesListResponseResults
    """List of instances."""
