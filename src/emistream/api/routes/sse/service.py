from collections.abc import AsyncGenerator

from litestar.channels import ChannelsPlugin

from emistream.models.events import Event, ParsableEvent


class Service:
    """Service for the sse endpoint."""

    def __init__(self, channels: ChannelsPlugin) -> None:
        self._channels = channels

    async def subscribe(self) -> AsyncGenerator[Event, None]:
        """Subscribe to app events."""

        async with self._channels.start_subscription("events") as subscriber:
            async for event in subscriber.iter_events():
                event = ParsableEvent.model_validate_json(event)
                yield event.root
