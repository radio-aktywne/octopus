from collections.abc import Mapping, Sequence
from math import ceil

from pystreams.base import Stream
from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata, FFmpegTeeNode
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata

from octopus.config.models import Config
from octopus.services.beaver import models as bm
from octopus.services.streaming import models as m
from octopus.utils.time import isostringify, naiveutcnow


class Runner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_input(self, credentials: m.Credentials, port: int) -> FFmpegNode:
        timeout = credentials.expires_at - naiveutcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        target = f"srt://{self._config.server.host}:{port}"

        return FFmpegNode(
            target=target,
            options={
                "listen_timeout": timeout,
                "mode": "listener",
                "passphrase": credentials.token,
            },
        )

    def _build_ffmpeg_fifo_options(self, options: Mapping[str, str]) -> str:
        return "\\:".join(f"{key}={value}" for key, value in options.items())

    def _build_ffmpeg_metadata_options(
        self, metadata: Mapping[str, str]
    ) -> Sequence[str]:
        return [f"{key}={value}" for key, value in metadata.items()]

    def _build_metadata(
        self, event: bm.Event, instance: bm.EventInstance
    ) -> Sequence[str]:
        metadata = {}

        if event.show is not None:
            metadata["title"] = event.show.title

        return self._build_ffmpeg_metadata_options(metadata)

    def _map_format(self, fmt: m.Format) -> str:
        match fmt:
            case m.Format.OGG:
                return "ogg"

    def _map_content_type(self, fmt: m.Format) -> str:
        match fmt:
            case m.Format.OGG:
                return "audio/ogg"

    def _build_dingo_output(
        self, fmt: m.Format, *, options: Mapping[str, str] | None = None
    ) -> FFmpegNode:
        latency = ceil(self._config.streaming.latency.total_seconds() * 1000000)

        return FFmpegNode(
            target=self._config.dingo.srt.url,
            options={
                **(options or {}),
                "f": self._map_format(fmt),
                "latency": latency,
                "mode": "caller",
            },
        )

    def _build_gecko_output(
        self,
        event: bm.Event,
        instance: bm.EventInstance,
        fmt: m.Format,
        *,
        options: Mapping[str, str] | None = None,
    ) -> FFmpegNode:
        target = f"{self._config.gecko.http.url}/recordings/{event.id}/{isostringify(instance.start)}"

        return FFmpegNode(
            target=target,
            options={
                **(options or {}),
                "content_type": self._map_content_type(fmt),
                "f": self._map_format(fmt),
                "method": "PUT",
            },
        )

    def _build_output(
        self,
        event: bm.Event,
        instance: bm.EventInstance,
        fmt: m.Format,
        *,
        record: bool,
    ) -> FFmpegNode:
        options = {
            "acodec": "copy",
            "map": "0:a",
            "metadata": self._build_metadata(event, instance),
        }

        if not record:
            return self._build_dingo_output(fmt, options=options)

        return FFmpegTeeNode(
            nodes=[
                self._build_dingo_output(fmt),
                self._build_gecko_output(
                    event,
                    instance,
                    fmt,
                    options={
                        "fifo_options": self._build_ffmpeg_fifo_options(
                            {
                                "drop_pkts_on_overflow": "1",
                                "queue_size": "1024",
                            }
                        ),
                        "onfail": "ignore",
                        "use_fifo": "1",
                    },
                ),
            ],
            options=options,
        )

    def _build_stream_metadata(  # noqa: PLR0913
        self,
        event: bm.Event,
        instance: bm.EventInstance,
        credentials: m.Credentials,
        port: int,
        fmt: m.Format,
        *,
        record: bool,
    ) -> ProcessBasedStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_input(credentials, port),
            output=self._build_output(event, instance, fmt, record=record),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        return await ProcessBasedStreamFactory().create(metadata)

    async def run(  # noqa: PLR0913
        self,
        event: bm.Event,
        instance: bm.EventInstance,
        credentials: m.Credentials,
        port: int,
        fmt: m.Format,
        *,
        record: bool,
    ) -> Stream:
        """Run the stream."""
        metadata = self._build_stream_metadata(
            event, instance, credentials, port, fmt, record=record
        )
        return await self._run_stream(metadata)
