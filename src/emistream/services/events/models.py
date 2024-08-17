from collections.abc import AsyncIterator

from emistream.models.base import datamodel
from emistream.models.events.event import Event


@datamodel
class SubscribeRequest:
    """Request to subscribe."""

    pass


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    events: AsyncIterator[Event]
    """Stream of events."""
