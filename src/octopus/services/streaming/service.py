import asyncio
import secrets
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from litestar.channels import ChannelsPlugin
from pylocks.base import Lock
from pystores.base import Store
from pystreams.base import Stream

from octopus.config.models import Config
from octopus.models.events import stream as ev
from octopus.models.events.types import Event
from octopus.services.apis.beaver import errors as be
from octopus.services.apis.beaver import models as bm
from octopus.services.apis.beaver.service import BeaverService
from octopus.services.streaming import errors as e
from octopus.services.streaming import models as m
from octopus.services.streaming.runner import Runner
from octopus.utils.time import awareutcnow


class StreamingService:
    """Service to manage streaming."""

    def __init__(
        self,
        config: Config,
        store: Store[UUID | None],
        lock: Lock,
        beaver: BeaverService,
        channels: ChannelsPlugin,
    ) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._beaver = beaver
        self._channels = channels
        self._tasks = set[asyncio.Task]()

    def _create_availability(self, event_id: UUID | None) -> m.Availability:
        return m.Availability(event=event_id, checked_at=awareutcnow())

    def _get_reference_time(self) -> datetime:
        return awareutcnow()

    def _get_time_window(self, reference: datetime) -> tuple[datetime, datetime]:
        start = reference - self._config.streaming.window
        end = reference + self._config.streaming.window

        return start, end

    async def _get_instances(
        self, event_id: UUID, start: datetime, end: datetime
    ) -> Sequence[bm.Instance]:
        instances_list_request = bm.InstancesListRequest(
            start=start,
            end=end,
            where={"event": {"is": {"id": event_id}}},
            include={"event": {"include": {"show": True}}},
        )

        try:
            instances_list_response = await self._beaver.instances.list(
                instances_list_request
            )
        except be.ServiceError as ex:
            raise e.ServiceError from ex

        return instances_list_response.results.instances

    def _find_nearest_instance(
        self, event_id: UUID, reference: datetime, instances: Sequence[bm.Instance]
    ) -> bm.Instance:
        def _compare(instance: bm.Instance) -> timedelta:
            if instance.event is None:
                raise e.ServiceError

            start = instance.start.replace(tzinfo=instance.event.timezone)
            start = start.astimezone(UTC)
            return abs(start - reference)

        instance = min(instances, key=_compare, default=None)

        if instance is None:
            raise e.InstanceNotFoundError(event_id)

        return instance

    def _generate_token(self) -> str:
        return secrets.token_hex(16)

    def _get_token_expiry(self) -> datetime:
        return awareutcnow() + self._config.streaming.timeout

    def _generate_credentials(self) -> m.Credentials:
        return m.Credentials(
            token=self._generate_token(), expires_at=self._get_token_expiry()
        )

    def _get_port(self) -> int:
        return self._config.server.ports.srt

    def _emit_event(self, event: Event) -> None:
        data = event.model_dump_json(round_trip=True)
        self._channels.publish(data, "events")

    async def _emit_availability_changed_event(self, event_id: UUID | None) -> None:
        self._emit_event(
            ev.AvailabilityChangedEvent(
                data=ev.AvailabilityChangedEventData(
                    availability=ev.Availability.map(
                        self._create_availability(event_id)
                    )
                )
            )
        )

    async def _reserve_event(self, event: bm.Event) -> None:
        async with self._lock:
            current = await self._store.get()

            if current is not None:
                raise e.StreamBusyError(current)

            await self._store.set(event.id)
            await self._emit_availability_changed_event(event.id)

    async def _free_event(self) -> None:
        async with self._lock:
            await self._store.set(None)
            await self._emit_availability_changed_event(None)

    async def _watch_stream(self, stream: Stream) -> None:
        try:
            await stream.wait()
        finally:
            await self._free_event()

    async def _run(  # noqa: PLR0913
        self,
        instance: bm.Instance,
        credentials: m.Credentials,
        port: int,
        fmt: m.Format,
        metadata: Mapping[str, str] | None,
        *,
        record: bool,
    ) -> None:
        runner = Runner(self._config)
        stream = await runner.run(
            instance=instance,
            credentials=credentials,
            port=port,
            fmt=fmt,
            metadata=metadata,
            record=record,
        )

        task = asyncio.create_task(self._watch_stream(stream))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def check(self, request: m.CheckRequest) -> m.CheckResponse:
        """Check the availability of the stream."""
        async with self._lock:
            event = await self._store.get()

        return m.CheckResponse(availability=self._create_availability(event))

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        reference = self._get_reference_time()
        start, end = self._get_time_window(reference)

        instances = await self._get_instances(request.event, start, end)
        instance = self._find_nearest_instance(request.event, reference, instances)

        if instance.event is None:
            raise e.ServiceError

        if request.record and instance.event.type != bm.EventType.live:
            raise e.UnrecordableEventError(instance.event.id)

        credentials = self._generate_credentials()
        port = self._get_port()

        await self._reserve_event(instance.event)

        try:
            await self._run(
                instance,
                credentials,
                port,
                request.format,
                request.metadata,
                record=request.record,
            )
        except:
            await self._free_event()
            raise

        return m.ReserveResponse(credentials=credentials)
