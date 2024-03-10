import asyncio
import secrets
from datetime import timedelta, timezone
from http import HTTPStatus
from uuid import UUID

from litestar.channels import ChannelsPlugin
from pydantic import NaiveDatetime
from pylocks.base import Lock
from pystores.base import Store
from pystreams.stream import Stream
from zoneinfo import ZoneInfo

from emistream.config.models import Config
from emistream.emirecorder import models as erm
from emistream.emirecorder.errors import EmirecorderError
from emistream.emirecorder.service import EmirecorderService
from emistream.emishows import models as esm
from emistream.emishows.service import EmishowsService
from emistream.models import data as dm
from emistream.models import events as em
from emistream.streaming import models as sm
from emistream.streaming.errors import (
    InstanceNotFoundError,
    RecorderBusyError,
    StreamBusyError,
)
from emistream.streaming.runner import StreamRunner
from emistream.time import naiveutcnow


class StreamController:
    """Controller for streams."""

    def __init__(
        self,
        config: Config,
        store: Store[UUID | None],
        lock: Lock,
        emishows: EmishowsService,
        emirecorder: EmirecorderService,
        channels: ChannelsPlugin,
    ) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._emishows = emishows
        self._emirecorder = emirecorder
        self._channels = channels

    def _create_availability(self, event: UUID | None) -> dm.Availability:
        """Create an availability object."""

        return dm.Availability(
            event=event,
            checked_at=naiveutcnow(),
        )

    def _get_reference_time(self) -> NaiveDatetime:
        """Returns a reference time for finding the nearest event instance."""

        return naiveutcnow()

    def _get_time_window(
        self, reference: NaiveDatetime
    ) -> tuple[NaiveDatetime, NaiveDatetime]:
        """Returns a time window for searching for event instances."""

        start = reference - self._config.stream.window
        end = reference + self._config.stream.window

        return start, end

    async def _get_schedule(
        self, event: UUID, start: NaiveDatetime, end: NaiveDatetime
    ) -> esm.EventSchedule:
        """Returns the schedule for an event."""

        event = str(event)

        response = await self._emishows.schedule.list(
            start=start, end=end, where={"id": event}, include={"show": True}
        )

        schedule = next(
            (schedule for schedule in response.schedules if schedule.event.id == event),
            None,
        )

        if schedule is None:
            raise InstanceNotFoundError(event)

        return schedule

    def _find_nearest_instance(
        self,
        reference: NaiveDatetime,
        event: esm.Event,
        instances: list[esm.EventInstance],
    ) -> esm.EventInstance:
        """Finds the nearest instance of an event."""

        def _compare(instance: esm.EventInstance) -> timedelta:
            tz = ZoneInfo(event.timezone)
            start = instance.start.replace(tzinfo=tz)
            start = start.astimezone(timezone.utc).replace(tzinfo=None)
            return abs(start - reference)

        instance = min(instances, key=_compare, default=None)

        if instance is None:
            raise InstanceNotFoundError(UUID(event.id))

        return instance

    def _generate_token(self) -> str:
        """Generates a token for credentials."""

        return secrets.token_hex(16)

    def _get_token_expiry(self) -> NaiveDatetime:
        """Returns the expiry time for credentials."""

        return naiveutcnow() + self._config.stream.timeout

    def _generate_credentials(self) -> sm.Credentials:
        """Generates credentials for the stream."""

        return sm.Credentials(
            token=self._generate_token(),
            expires_at=self._get_token_expiry(),
        )

    def _get_port(self) -> int:
        """Returns a port for the stream."""

        return self._config.stream.port

    async def _get_recorder_access(
        self, event: UUID, format: sm.Format
    ) -> sm.RecorderAccess:
        """Returns a recorder access for the stream."""

        request = erm.RecordPostRequest(event=str(event), format=format)

        try:
            response = await self._emirecorder.record.record(request)
        except EmirecorderError as error:
            if (
                hasattr(error, "response")
                and error.response.status_code == HTTPStatus.CONFLICT
            ):
                raise RecorderBusyError() from error

            raise

        return sm.RecorderAccess(
            token=response.credentials.token,
            port=response.port,
        )

    async def _emit_availability_change(self, event: UUID | None) -> None:
        """Emit an availability change event."""

        event = em.AvailabilityChangedEvent(
            data=em.AvailabilityChangedEventData(
                availability=self._create_availability(event),
            ),
        )
        data = event.model_dump_json(by_alias=True)
        self._channels.publish(data, "events")

    async def _reserve_event(self, event: UUID) -> None:
        """Reserves a stream for an event."""

        async with self._lock:
            current = await self._store.get()

            if current is not None:
                raise StreamBusyError(event)

            await self._store.set(event)
            await self._emit_availability_change(event)

    async def _free_event(self, event: UUID) -> None:
        """Frees a stream from an event."""

        async with self._lock:
            await self._store.set(None)
            await self._emit_availability_change(None)

    async def _watch_stream(self, stream: Stream, event: UUID) -> None:
        """Watches a stream and frees the event when it ends."""

        try:
            await stream.wait()
        finally:
            await self._free_event(event)

    async def _run(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        credentials: sm.Credentials,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> None:
        """Runs a recording."""

        runner = StreamRunner(self._config)
        stream = await runner.run(
            event=event,
            instance=instance,
            credentials=credentials,
            format=format,
            recorder=recorder,
        )

        event_id = UUID(event.id)
        asyncio.create_task(self._watch_stream(stream, event_id))

    async def check(self) -> dm.Availability:
        """Checks the availability of the stream."""

        async with self._lock:
            event = await self._store.get()
            return self._create_availability(event)

    async def reserve(self, request: sm.ReserveRequest) -> sm.ReserveResponse:
        """Starts a recording stream."""

        reference = self._get_reference_time()
        start, end = self._get_time_window(reference)

        schedule = await self._get_schedule(request.event, start, end)
        instance = self._find_nearest_instance(
            reference, schedule.event, schedule.instances
        )

        event_id = UUID(schedule.event.id)
        format = request.format

        credentials = self._generate_credentials()
        port = self._get_port()

        recorder = (
            await self._get_recorder_access(event_id, format)
            if request.record
            else None
        )

        await self._reserve_event(event_id)

        try:
            await self._run(schedule.event, instance, credentials, format, recorder)

            return sm.ReserveResponse(credentials=credentials, port=port)
        except:
            await self._free_event(event_id)
            raise
