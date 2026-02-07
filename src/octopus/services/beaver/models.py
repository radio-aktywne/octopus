from collections.abc import Sequence
from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from octopus.models.base import SerializableModel, datamodel
from octopus.utils.time import NaiveDatetime, Timezone


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
    """Show that the event belongs to."""

    timezone: Timezone
    """Timezone of the event."""


class EventInstance(SerializableModel):
    """Event instance data."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""

    end: NaiveDatetime
    """End datetime of the event instance in event timezone."""


class Schedule(SerializableModel):
    """Schedule data."""

    event: Event
    """Event data."""

    instances: Sequence[EventInstance]
    """Event instances."""


class ScheduleList(SerializableModel):
    """List of event schedules."""

    schedules: Sequence[Schedule]
    """Schedules that matched the request."""


class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: str


class EventInclude(TypedDict, total=False):
    """Event relational arguments."""

    show: bool


type ScheduleListRequestStart = NaiveDatetime | None

type ScheduleListRequestEnd = NaiveDatetime | None

type ScheduleListRequestWhere = EventWhereInput | None

type ScheduleListRequestInclude = EventInclude | None

type ScheduleListResponseResults = ScheduleList


@datamodel
class ScheduleListRequest:
    """Request to list schedules."""

    start: ScheduleListRequestStart
    """Start datetime in UTC to filter events instances."""

    end: ScheduleListRequestEnd
    """End datetime in UTC to filter events instances."""

    where: ScheduleListRequestWhere
    """Filter to apply to find events."""

    include: ScheduleListRequestInclude
    """Relations to include in the response."""


@datamodel
class ScheduleListResponse:
    """Response for listing schedules."""

    results: ScheduleListResponseResults
    """List of schedules."""
