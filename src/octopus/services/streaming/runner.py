from math import ceil

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata, FFmpegTeeNode
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata
from pystreams.stream import Stream

from octopus.config.models import Config
from octopus.services.beaver import models as bm
from octopus.services.streaming import models as m
from octopus.utils.time import naiveutcnow


class Runner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_input(self, credentials: m.Credentials, port: int) -> FFmpegNode:
        timeout = credentials.expires_at - naiveutcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        host = self._config.server.host
        target = f"srt://{host}:{port}"

        return FFmpegNode(
            target=target,
            options={
                "mode": "listener",
                "listen_timeout": timeout,
                "passphrase": credentials.token,
            },
        )

    def _build_ffmpeg_metadata_options(self, metadata: dict[str, str]) -> list[str]:
        return [f"{key}={value}" for key, value in metadata.items()]

    def _build_metadata(self, event: bm.Event, instance: bm.EventInstance) -> list[str]:
        metadata = {}

        if event.show is not None:
            metadata["title"] = event.show.title

        return self._build_ffmpeg_metadata_options(metadata)

    def _map_format(self, format: m.Format) -> str:
        match format:
            case m.Format.OGG:
                return "ogg"

    def _map_content_type(self, format: m.Format) -> str:
        match format:
            case m.Format.OGG:
                return "audio/ogg"

    def _build_dingo_output(self, format: m.Format, metadata: list[str]) -> FFmpegNode:
        return FFmpegNode(
            target=self._config.dingo.srt.url,
            options={
                "acodec": "copy",
                "f": self._map_format(format),
                "metadata": metadata,
            },
        )

    def _build_tee_dingo_output(self, format: m.Format) -> FFmpegNode:
        return FFmpegNode(
            target=self._config.dingo.srt.url,
            options={
                "f": self._map_format(format),
            },
        )

    def _build_tee_gecko_output(
        self, event: bm.Event, instance: bm.EventInstance, format: m.Format
    ) -> FFmpegNode:
        id = str(event.id)
        start = instance.start.isoformat()
        url = self._config.gecko.http.url

        target = f"{url}/records/{id}/{start}"

        return FFmpegNode(
            target=target,
            options={
                "f": self._map_format(format),
                "content_type": self._map_content_type(format),
                "method": "PUT",
                "onfail": "ignore",
            },
        )

    def _build_output(
        self,
        event: bm.Event,
        instance: bm.EventInstance,
        format: m.Format,
        record: bool,
    ) -> FFmpegNode:
        metadata = self._build_metadata(event, instance)

        if not record:
            return self._build_dingo_output(format, metadata)

        return FFmpegTeeNode(
            nodes=[
                self._build_tee_dingo_output(format),
                self._build_tee_gecko_output(event, instance, format),
            ],
            options={
                "acodec": "copy",
                "map": 0,
                "metadata": metadata,
            },
        )

    def _build_stream_metadata(
        self,
        event: bm.Event,
        instance: bm.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
        record: bool,
    ) -> ProcessBasedStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_input(credentials, port),
            output=self._build_output(event, instance, format, record),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self,
        event: bm.Event,
        instance: bm.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
        record: bool,
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(
            event, instance, credentials, port, format, record
        )
        return await self._run_stream(metadata)
