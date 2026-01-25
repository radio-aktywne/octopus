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
                "mode": "listener",
                "listen_timeout": timeout,
                "passphrase": credentials.token,
            },
        )

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

    def _build_dingo_output(self, fmt: m.Format, metadata: Sequence[str]) -> FFmpegNode:
        return FFmpegNode(
            target=self._config.dingo.srt.url,
            options={
                "acodec": "copy",
                "f": self._map_format(fmt),
                "metadata": metadata,
            },
        )

    def _build_tee_dingo_output(self, fmt: m.Format) -> FFmpegNode:
        return FFmpegNode(
            target=self._config.dingo.srt.url,
            options={"f": self._map_format(fmt)},
        )

    def _build_tee_gecko_output(
        self, event: bm.Event, instance: bm.EventInstance, fmt: m.Format
    ) -> FFmpegNode:
        target = f"{self._config.gecko.http.url}/records/{event.id}/{isostringify(instance.start)}"

        return FFmpegNode(
            target=target,
            options={
                "f": self._map_format(fmt),
                "content_type": self._map_content_type(fmt),
                "method": "PUT",
                "onfail": "ignore",
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
        metadata = self._build_metadata(event, instance)

        if not record:
            return self._build_dingo_output(fmt, metadata)

        return FFmpegTeeNode(
            nodes=[
                self._build_tee_dingo_output(fmt),
                self._build_tee_gecko_output(event, instance, fmt),
            ],
            options={"acodec": "copy", "map": 0, "metadata": metadata},
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
