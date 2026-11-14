import asyncio
import secrets
from contextlib import suppress
from math import ceil

from litestar.channels import ChannelsPlugin
from pylocks.base import Lock
from pystores.base import Store
from pystreams.base import Stream

from octopus.config.models import Config
from octopus.models.events import stream as ev
from octopus.models.events.types import Event
from octopus.services.apis.beaver import errors as be, models as bm
from octopus.services.apis.beaver.service import BeaverService
from octopus.services.streaming import errors as e, models as m
from octopus.services.streaming.runner import Runner
from octopus.utils.time import awareutcnow


class StreamingService:
    """Service to manage streaming."""

    def __init__(
        self,
        config: Config,
        store: Store[m.Instance | None],
        lock: Lock,
        beaver: BeaverService,
        channels: ChannelsPlugin,
    ) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._beaver = beaver
        self._channels = channels
        self._task: asyncio.Task | None = None
        self._transition = asyncio.Lock()

    async def _get_instance(self, instance: m.Instance) -> bm.InstanceWithEventWithShow:
        instances_get_request = bm.InstancesGetRequest(
            event_id=instance.event,
            start=instance.start,
            include={"event": {"include": {"show": True}}},
        )

        try:
            instances_get_response = await self._beaver.instances.get(
                instances_get_request
            )
        except be.NotFoundError as ex:
            raise e.InstanceNotFoundError(instance) from ex
        except be.ServiceError as ex:
            raise e.ServiceError from ex

        if not isinstance(
            instances_get_response.instance, bm.InstanceWithEventWithShow
        ):
            raise e.ServiceError

        return instances_get_response.instance

    def _generate_credentials(self) -> m.Credentials:
        return m.Credentials(
            token=secrets.token_hex(16),
            expires_at=awareutcnow() + self._config.streaming.timeout,
        )

    def _emit_event(self, event: Event) -> None:
        data = event.model_dump_json(round_trip=True)
        self._channels.publish(data, "events")

    def _emit_availability_changed_event(self, instance: m.Instance | None) -> None:
        self._emit_event(
            ev.AvailabilityChangedEvent(
                data=ev.AvailabilityChangedEventData(
                    availability=ev.Availability.map(
                        m.Availability(instance=instance, checked_at=awareutcnow())
                    )
                )
            )
        )

    async def _reserve(self, instance: bm.InstanceWithEventWithShow) -> None:
        async with self._lock:
            current = await self._store.get()

            if current is not None:
                raise e.StreamBusyError(current)

            new = m.Instance(event=instance.event.id, start=instance.start)
            await self._store.set(new)
            self._emit_availability_changed_event(new)

    async def _release(self) -> None:
        async with self._lock:
            await self._store.set(None)
            self._emit_availability_changed_event(None)

    async def _stop_stream(self, stream: Stream) -> None:
        linger = ceil(self._config.streaming.linger.total_seconds())

        for action, timeout in ((stream.terminate, linger + 5), (stream.kill, 5)):
            with suppress(Exception):
                await asyncio.wait_for(action(), timeout=5)

            with suppress(Exception):
                await asyncio.wait_for(stream.wait(), timeout=timeout)
                return

        raise e.StreamStopError

    async def _watch_stream(self, stream: Stream) -> None:
        try:
            await stream.wait()
            await self._release()
        except asyncio.CancelledError:
            await self._stop_stream(stream)
            await self._release()

    async def _stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()

        try:
            await asyncio.shield(self._task)
        except asyncio.CancelledError:
            await self._task
            raise

        self._task = None

    async def _run(
        self,
        instance: bm.InstanceWithEventWithShow,
        credentials: m.Credentials,
        request: m.ReserveRequest,
    ) -> None:
        runner = Runner(self._config)
        stream = await runner.run(
            instance=instance,
            credentials=credentials,
            port=self._config.server.ports.srt,
            fmt=request.format,
            start=request.start,
            metadata=request.metadata,
            record=request.record,
        )

        self._task = asyncio.create_task(self._watch_stream(stream), eager_start=True)

    async def check(self, request: m.CheckRequest) -> m.CheckResponse:
        """Check the availability of the stream."""
        async with self._lock:
            instance = await self._store.get()

        return m.CheckResponse(
            availability=m.Availability(instance=instance, checked_at=awareutcnow())
        )

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        instance = await self._get_instance(request.instance)

        if request.record and instance.event.type != bm.EventType.live:
            raise e.UnrecordableEventError(instance.event.id)

        async with self._transition:
            if request.force:
                await self._stop()

            credentials = self._generate_credentials()

            await self._reserve(instance)

            try:
                await self._run(instance, credentials, request)
            except BaseException:
                await self._release()
                raise

        return m.ReserveResponse(credentials=credentials)

    async def close(self) -> None:
        """Close gracefully."""
        async with self._transition:
            with suppress(asyncio.CancelledError, RuntimeError):
                await self._stop()

            self._task = None
