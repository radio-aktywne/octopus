from collections.abc import AsyncIterator

from octopus.models.base import datamodel
from octopus.models.events.event import Event


@datamodel
class SubscribeRequest:
    """Request to subscribe."""


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    events: AsyncIterator[Event]
    """Stream of events."""
