from enum import StrEnum
from typing import Annotated, Literal, TypedDict
from uuid import UUID

from pydantic import Field

from octopus.models.base import SerializableModel, datamodel, serializable
from octopus.utils.time import NaiveDatetime, Timezone

Second = Annotated[int, Field(..., ge=0, le=60)]

Minute = Annotated[int, Field(..., ge=0, le=59)]

Hour = Annotated[int, Field(..., ge=0, le=23)]

Monthday = (
    Annotated[int, Field(..., ge=-31, le=-1)] | Annotated[int, Field(..., ge=1, le=31)]
)

Yearday = (
    Annotated[int, Field(..., ge=-366, le=-1)]
    | Annotated[int, Field(..., ge=1, le=366)]
)

Week = (
    Annotated[int, Field(..., ge=-53, le=-1)] | Annotated[int, Field(..., ge=1, le=53)]
)

Month = Annotated[int, Field(..., ge=1, le=12)]


SortMode = Literal["default", "insensitive"]


SortOrder = Literal["asc", "desc"]


EventScalarFieldKeys = Literal[
    "id",
    "type",
    "showId",
]


@serializable
class StringFilter(
    TypedDict(
        "StringFilter",
        {
            "equals": str,
            "not_in": list[str],
            "lt": str,
            "lte": str,
            "gt": str,
            "gte": str,
            "contains": str,
            "startswith": str,
            "endswith": str,
            "in": list[str],
            "not": "str | StringFilter",
            "mode": SortMode,
        },
        total=False,
    )
):
    """String filter options."""

    pass


class Frequency(StrEnum):
    """Frequency options."""

    SECONDLY = "secondly"
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Weekday(StrEnum):
    """Weekday options."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class EventType(StrEnum):
    """Event type options."""

    live = "live"
    replay = "replay"
    prerecorded = "prerecorded"


class WeekdayRule(SerializableModel):
    """Day rule data."""

    day: Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""


class RecurrenceRule(SerializableModel):
    """Recurrence rule data."""

    frequency: Frequency
    """Frequency of the recurrence."""

    until: NaiveDatetime | None = None
    """End date of the recurrence in UTC."""

    count: int | None = None
    """Number of occurrences of the recurrence."""

    interval: int | None = None
    """Interval of the recurrence."""

    by_seconds: list[Second] | None = None
    """Seconds of the recurrence."""

    by_minutes: list[Minute] | None = None
    """Minutes of the recurrence."""

    by_hours: list[Hour] | None = None
    """Hours of the recurrence."""

    by_weekdays: list[WeekdayRule] | None = None
    """Weekdays of the recurrence."""

    by_monthdays: list[Monthday] | None = None
    """Monthdays of the recurrence."""

    by_yeardays: list[Yearday] | None = None
    """Yeardays of the recurrence."""

    by_weeks: list[Week] | None = None
    """Weeks of the recurrence."""

    by_months: list[Month] | None = None
    """Months of the recurrence."""

    by_set_positions: list[int] | None = None
    """Set positions of the recurrence."""

    week_start: Weekday | None = None
    """Start day of the week."""


class Recurrence(SerializableModel):
    """Recurrence data."""

    rule: RecurrenceRule | None = None
    """Rule of the recurrence."""

    include: list[NaiveDatetime] | None = None
    """Included dates of the recurrence in event timezone."""

    exclude: list[NaiveDatetime] | None = None
    """Excluded dates of the recurrence in event timezone."""


class Show(SerializableModel):
    """Show data."""

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: list["Event"] | None
    """Events that the show belongs to."""


class Event(SerializableModel):
    """Event data."""

    id: UUID
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: UUID
    """Identifier of the show that the event belongs to."""

    show: Show | None
    """Show that the event belongs to."""

    start: NaiveDatetime
    """Start time of the event in event timezone."""

    end: NaiveDatetime
    """End time of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence rule of the event."""


@serializable
class ShowRelationFilter(
    TypedDict(
        "ShowRelationFilter",
        {
            "is": "ShowWhereInput",
            "is_not": "ShowWhereInput",
        },
        total=False,
    )
):
    """Show relation filter."""

    pass


@serializable
class EventListRelationFilter(TypedDict, total=False):
    """Event list relation filter."""

    some: "EventWhereInput"
    """Some relation filter."""

    none: "EventWhereInput"
    """None relation filter."""

    every: "EventWhereInput"
    """Every relation filter."""


@serializable
class ShowWhereInput(TypedDict, total=False):
    """Show arguments for searching."""

    id: str | StringFilter
    """Filter for the identifier of the show."""

    title: str | StringFilter
    """Filter for the title of the show."""

    description: None | str | StringFilter
    """Filter for the description of the show."""

    events: EventListRelationFilter
    """Filter for the events that the show belongs to."""

    AND: list["ShowWhereInput"]
    """Logical AND conditions."""

    OR: list["ShowWhereInput"]
    """Logical OR conditions."""

    NOT: list["ShowWhereInput"]
    """Logical NOT conditions."""


@serializable
class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: str | StringFilter
    """Filter for the identifier of the event."""

    type: EventType
    """Filter for the type of the event."""

    show_id: str | StringFilter
    """Filter for the identifier of the show that the event belongs to."""

    show: ShowRelationFilter
    """Filter for the show that the event belongs to."""

    AND: list["EventWhereInput"]
    """Logical AND conditions."""

    OR: list["EventWhereInput"]
    """Logical OR conditions."""

    NOT: list["EventWhereInput"]
    """Logical NOT conditions."""


@serializable
class EventWhereUniqueIdInput(TypedDict, total=True):
    """Unique filter for Event using the identifier."""

    id: str
    """Identifier of the event."""


EventWhereUniqueInput = EventWhereUniqueIdInput


@serializable
class EventIncludeFromEvent(TypedDict, total=False):
    """Relational arguments for Event."""

    show: "bool | ShowArgsFromEvent"
    """Include show."""


@serializable
class FindManyEventArgsFromShow(TypedDict, total=False):
    """Arguments for Show."""

    take: int
    """Maximum number of events to return."""

    skip: int
    """Number of events to skip."""

    order_by: "EventOrderByInput | list[EventOrderByInput]"
    """Order to apply to the results."""

    where: EventWhereInput
    """Filter to apply to find events."""

    cursor: EventWhereUniqueInput
    """Cursor to find events."""

    distinct: list[EventScalarFieldKeys]
    """Distinct fields to select."""

    include: EventIncludeFromEvent
    """Relations to include in the response."""


@serializable
class ShowIncludeFromShow(TypedDict, total=False):
    """Relational arguments for Show."""

    events: bool | FindManyEventArgsFromShow
    """Include events."""


@serializable
class ShowArgsFromEvent(TypedDict, total=False):
    """Arguments for Event."""

    include: ShowIncludeFromShow
    """Include show."""


@serializable
class EventInclude(TypedDict, total=False):
    """Relational arguments for Event."""

    show: bool | ShowArgsFromEvent
    """Include show."""


@serializable
class EventOrderByIdInput(TypedDict):
    """Order by identifier of the event."""

    id: SortOrder
    """Order to apply to the results."""


@serializable
class EventOrderByTypeInput(TypedDict):
    """Order by type of the event."""

    type: SortOrder
    """Order to apply to the results."""


@serializable
class EventOrderByShowIdInput(TypedDict):
    """Order by identifier of the show that the event belongs to."""

    show_id: SortOrder
    """Order to apply to the results."""


EventOrderByInput = (
    EventOrderByIdInput | EventOrderByTypeInput | EventOrderByShowIdInput
)


class EventInstance(SerializableModel):
    """Event instance data."""

    start: NaiveDatetime
    """Start time of the event instance in event timezone."""

    end: NaiveDatetime
    """End time of the event instance in event timezone."""


class Schedule(SerializableModel):
    """Schedule data."""

    event: Event
    """Event data."""

    instances: list[EventInstance]
    """Event instances."""


class ScheduleList(SerializableModel):
    """List of event schedules."""

    count: int
    """Total number of schedules that matched the query."""

    limit: int | None
    """Maximum number of returned schedules."""

    offset: int | None
    """Number of schedules skipped."""

    schedules: list[Schedule]
    """Schedules that matched the request."""


ListRequestStart = NaiveDatetime | None

ListRequestEnd = NaiveDatetime | None

ListRequestLimit = int | None

ListRequestOffset = int | None

ListRequestWhere = EventWhereInput | None

ListRequestInclude = EventInclude | None

ListRequestOrder = EventOrderByInput | list[EventOrderByInput] | None

ListResponseResults = ScheduleList


@datamodel
class ListRequest:
    """Request to list schedules."""

    start: ListRequestStart
    """Start time in UTC to filter events instances."""

    end: ListRequestEnd
    """End time in UTC to filter events instances."""

    limit: ListRequestLimit
    """Maximum number of schedules to return."""

    offset: ListRequestOffset
    """Number of schedules to skip."""

    where: ListRequestWhere
    """Filter to apply to find events."""

    include: ListRequestInclude
    """Relations to include in the response."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing schedules."""

    results: ListResponseResults
    """List of schedules."""
