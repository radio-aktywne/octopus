from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from octopus.models.base import SerializableModel, datamodel
from octopus.utils.time import NaiveDatetime, Timedelta, Timezone


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

    show_id: UUID | None
    """Identifier of the show the event belongs to."""

    timezone: Timezone
    """Timezone of the event."""


class EventWithShow(Event):
    """Event data with show relation included."""

    show: Show | None
    """Show the event belongs to."""


class Instance(SerializableModel):
    """Instance data."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""

    duration: Timedelta
    """Duration of the instance."""

    event_id: UUID
    """Identifier of the event the instance belongs to."""


class InstanceWithEvent(Instance):
    """Instance data with event relation included."""

    event: EventWithShow | Event
    """Event the instance belongs to."""


class InstanceWithEventWithShow(Instance):
    """Instance data with event and show relations included."""

    event: EventWithShow
    """Event the instance belongs to."""


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


type InstancesGetRequestEventId = UUID

type InstancesGetRequestStart = NaiveDatetime

type InstancesGetRequestInclude = InstanceInclude | None

type InstancesGetResponseInstance = (
    InstanceWithEventWithShow | InstanceWithEvent | Instance
)


@datamodel
class InstancesGetRequest:
    """Request to get an instance."""

    event_id: InstancesGetRequestEventId
    """Identifier of the event the instance to get belongs to."""

    start: InstancesGetRequestStart
    """Start datetime of the instance to get in event timezone."""

    include: InstancesGetRequestInclude
    """Relations to include in the response."""


@datamodel
class InstancesGetResponse:
    """Response for getting an instance."""

    instance: InstancesGetResponseInstance
    """Instance that matched the request."""
