import asyncio
import secrets
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from uuid import UUID

from litestar.channels import ChannelsPlugin
from pylocks.base import Lock
from pystores.base import Store
from pystreams.stream import Stream
from zoneinfo import ZoneInfo

from emistream.config.models import Config
from emistream.models.events import streaming as ev
from emistream.models.events.event import Event
from emistream.services.emirecords import errors as ere
from emistream.services.emirecords import models as erm
from emistream.services.emirecords.service import EmirecordsService
from emistream.services.emishows import errors as ese
from emistream.services.emishows import models as esm
from emistream.services.emishows.service import EmishowsService
from emistream.services.streaming import errors as e
from emistream.services.streaming import models as m
from emistream.services.streaming.runner import Runner
from emistream.utils.time import naiveutcnow


class StreamingService:
    """Service to manage streaming."""

    def __init__(
        self,
        config: Config,
        store: Store[UUID | None],
        lock: Lock,
        emishows: EmishowsService,
        emirecords: EmirecordsService,
        channels: ChannelsPlugin,
    ) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._emishows = emishows
        self._emirecords = emirecords
        self._channels = channels

    def _create_availability(self, event: UUID | None) -> m.Availability:
        return m.Availability(
            event=event,
            checked_at=naiveutcnow(),
        )

    def _get_reference_time(self) -> datetime:
        return naiveutcnow()

    def _get_time_window(self, reference: datetime) -> tuple[datetime, datetime]:
        start = reference - self._config.streaming.window
        end = reference + self._config.streaming.window

        return start, end

    async def _get_schedule(
        self, event: UUID, start: datetime, end: datetime
    ) -> esm.Schedule:
        req = esm.ListRequest(
            start=start,
            end=end,
            limit=None,
            offset=None,
            where={
                "id": str(event),
            },
            include={
                "show": True,
            },
            order=None,
        )

        try:
            res = await self._emishows.schedule.list(req)
        except ese.ServiceError as ex:
            raise e.EmishowsError(str(ex)) from ex

        results = res.results
        schedules = results.schedules

        schedule = next(
            (schedule for schedule in schedules if schedule.event.id == event),
            None,
        )

        if schedule is None:
            raise e.InstanceNotFoundError(event)

        return schedule

    def _find_nearest_instance(
        self, reference: datetime, schedule: esm.Schedule
    ) -> esm.EventInstance:
        def _compare(instance: esm.EventInstance) -> timedelta:
            tz = ZoneInfo(schedule.event.timezone)
            start = instance.start.replace(tzinfo=tz)
            start = start.astimezone(timezone.utc).replace(tzinfo=None)
            return abs(start - reference)

        instance = min(schedule.instances, key=_compare, default=None)

        if instance is None:
            raise e.InstanceNotFoundError(schedule.event.id)

        return instance

    def _generate_token(self) -> str:
        return secrets.token_hex(16)

    def _get_token_expiry(self) -> datetime:
        return naiveutcnow() + self._config.streaming.timeout

    def _generate_credentials(self) -> m.Credentials:
        return m.Credentials(
            token=self._generate_token(),
            expires_at=self._get_token_expiry(),
        )

    def _get_port(self) -> int:
        return self._config.server.ports.srt

    async def _get_recording(
        self, event: esm.Event, format: m.Format
    ) -> erm.RecordResponseData:
        data = erm.RecordRequestData(
            event=event.id,
            format=format,
        )
        req = erm.RecordRequest(
            data=data,
        )

        try:
            res = await self._emirecords.record.record(req)
        except ere.ServiceError as ex:
            if (
                hasattr(ex, "response")
                and ex.response.status_code == HTTPStatus.CONFLICT
            ):
                raise e.RecordingBusyError() from ex
            raise e.EmirecordsError(str(ex)) from ex

        return res.data

    def _emit_event(self, event: Event) -> None:
        data = event.model_dump_json(by_alias=True)
        self._channels.publish(data, "events")

    async def _emit_availability_changed_event(self, event: UUID | None) -> None:
        availability = self._create_availability(event)
        availability = ev.Availability.map(availability)
        data = ev.AvailabilityChangedEventData(
            availability=availability,
        )
        event = ev.AvailabilityChangedEvent(
            data=data,
        )
        self._emit_event(event)

    async def _reserve_event(self, event: esm.Event) -> None:
        async with self._lock:
            current = await self._store.get()

            if current is not None:
                raise e.StreamBusyError(current)

            await self._store.set(event.id)
            await self._emit_availability_changed_event(event)

    async def _free_event(self) -> None:
        async with self._lock:
            await self._store.set(None)
            await self._emit_availability_changed_event(None)

    async def _watch_stream(self, stream: Stream) -> None:
        try:
            await stream.wait()
        finally:
            await self._free_event()

    async def _run(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
        recording: erm.RecordResponseData | None,
    ) -> None:
        runner = Runner(self._config)
        stream = await runner.run(
            event=event,
            instance=instance,
            credentials=credentials,
            port=port,
            format=format,
            recording=recording,
        )

        asyncio.create_task(self._watch_stream(stream))

    async def check(self, request: m.CheckRequest) -> m.CheckResponse:
        """Check the availability of the stream."""

        async with self._lock:
            event = await self._store.get()

        availability = self._create_availability(event)

        return m.CheckResponse(
            availability=availability,
        )

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""

        event = request.event
        format = request.format
        record = request.record

        reference = self._get_reference_time()
        start, end = self._get_time_window(reference)

        schedule = await self._get_schedule(event, start, end)
        event = schedule.event
        instance = self._find_nearest_instance(reference, schedule)

        credentials = self._generate_credentials()
        port = self._get_port()

        recording = await self._get_recording(event, format) if record else None

        await self._reserve_event(event)

        try:
            await self._run(event, instance, credentials, port, format, recording)
        except:
            await self._free_event()
            raise

        return m.ReserveResponse(
            credentials=credentials,
            port=port,
        )
