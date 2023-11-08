from asyncio import create_task
from datetime import datetime, timedelta
from uuid import uuid4

from litestar.channels import ChannelsPlugin
from pystreams.stream import Stream

from emistream.config.models import Config
from emistream.emirecorder import models as rm
from emistream.emirecorder.client import EmirecorderAPI
from emistream.emirecorder.errors import EmirecorderError
from emistream.models import data as dm
from emistream.models import events as em
from emistream.stream.errors import RecorderError, StreamBusyError
from emistream.stream.runner import StreamRunner
from emistream.stream.state import RawStreamState, StreamState
from emistream.time import utcnow


class StreamController:
    """Controller for stream management."""

    def __init__(
        self,
        state: StreamState,
        runner: StreamRunner,
        emirecorder: EmirecorderAPI,
        channels: ChannelsPlugin,
        config: Config,
    ) -> None:
        self._state = state
        self._runner = runner
        self._emirecorder = emirecorder
        self._channels = channels
        self._config = config

    def _create_availability(self, event: dm.Event | None) -> dm.Availability:
        """Create an availability object."""

        return dm.Availability(
            event=event,
            checked_at=utcnow(),
        )

    def _generate_token(self) -> str:
        """Generate a token."""

        return uuid4().hex

    def _get_token_expiry(self) -> datetime:
        """Get the expiry time for a token."""

        return utcnow() + timedelta(seconds=self._config.stream.timeout)

    def _create_reservation(self) -> dm.Reservation:
        """Create a reservation object."""

        return dm.Reservation(
            token=self._generate_token(),
            expires_at=self._get_token_expiry(),
        )

    def _build_record_request(
        self, request: dm.ReservationRequest
    ) -> rm.PostRecordRequest:
        """Build a record request."""

        return rm.PostRecordRequest(
            request=rm.RecordingRequest(
                event=rm.Event(
                    show=rm.Show(
                        label=request.event.show.label,
                        metadata=request.event.show.metadata,
                    ),
                    start=request.event.start,
                    end=request.event.end,
                    metadata=request.event.metadata,
                ),
            )
        )

    async def _get_recording_credentials(
        self,
        request: dm.ReservationRequest,
    ) -> rm.RecordingCredentials | None:
        """Get recording credentials for the stream."""

        if not request.record:
            return None

        request = self._build_record_request(request)

        try:
            response = await self._emirecorder.record(request)
        except EmirecorderError as e:
            raise RecorderError() from e

        return response.credentials

    async def _emit_availability_change(self, availability: dm.Availability) -> None:
        """Emit an availability change event."""

        event = em.AvailabilityChangedEvent(
            data=em.AvailabilityChangedEventData(
                availability=availability,
            ),
        )
        data = event.model_dump_json(by_alias=True)
        self._channels.publish(data, "events")

    async def _set_state(self, state: RawStreamState, event: dm.Event | None) -> None:
        """Set the state of the stream."""

        availability = self._create_availability(event)
        state.set(event)
        await self._emit_availability_change(availability)

    async def _set_reserved(self, state: RawStreamState, event: dm.Event) -> None:
        """Set the state of the stream to reserved."""

        await self._set_state(state, event)

    async def _set_available(self, state: RawStreamState) -> None:
        """Set the state of the stream to available."""

        await self._set_state(state, None)

    async def _watch_stream_task(self, stream: Stream) -> None:
        """Wait for the stream to finish."""

        try:
            await stream.wait()
        finally:
            async with self._state.lock() as state:
                await self._set_available(state)

    def _watch_stream(self, stream: Stream) -> None:
        """Wait for the stream in a background task."""

        create_task(self._watch_stream_task(stream))

    async def availability(self) -> dm.Availability:
        """Get the availability of the stream."""

        event = await self._state.get()
        return self._create_availability(event)

    async def reserve(self, request: dm.ReservationRequest) -> dm.Reservation:
        """Reserve the stream."""

        async with self._state.lock() as state:
            event = state.get()
            if event is not None:
                raise StreamBusyError(event)

            await self._set_reserved(state, request.event)

        try:
            reservation = self._create_reservation()
            credentials = await self._get_recording_credentials(request)
            stream = await self._runner.run(request, reservation, credentials)

            self._watch_stream(stream)
        except:
            async with self._state.lock() as state:
                await self._set_available(state)
            raise

        return reservation
