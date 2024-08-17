from math import ceil
from socket import gethostbyname

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata, FFmpegTeeNode
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata
from pystreams.srt import SRTNode
from pystreams.stream import Stream

from emistream.config.models import Config
from emistream.services.emirecords import models as erm
from emistream.services.emishows import models as esm
from emistream.services.streaming import models as m
from emistream.utils.time import naiveutcnow


class Runner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_input(self, credentials: m.Credentials, port: int) -> FFmpegNode:
        timeout = credentials.expires_at - naiveutcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        return SRTNode(
            host=self._config.server.host,
            port=port,
            options={
                "mode": "listener",
                "listen_timeout": timeout,
                "passphrase": credentials.token,
            },
        )

    def _build_ffmpeg_metadata_options(self, metadata: dict[str, str]) -> list[str]:
        return [f"{key}={value}" for key, value in metadata.items()]

    def _build_metadata(
        self, event: esm.Event, instance: esm.EventInstance
    ) -> list[str]:
        metadata = {}

        if event.show is not None:
            metadata["title"] = event.show.title

        return self._build_ffmpeg_metadata_options(metadata)

    def _build_emifuse_output(
        self, format: m.Format, metadata: list[str]
    ) -> FFmpegNode:
        return SRTNode(
            host=gethostbyname(self._config.emifuse.srt.host),
            port=self._config.emifuse.srt.port,
            options={
                "acodec": "copy",
                "f": format,
                "metadata": metadata,
            },
        )

    def _build_tee_emifuse_output(self, format: m.Format) -> FFmpegNode:
        return SRTNode(
            host=gethostbyname(self._config.emifuse.srt.host),
            port=self._config.emifuse.srt.port,
            options={
                "f": format,
            },
        )

    def _build_tee_emirecords_output(
        self, format: m.Format, recording: erm.RecordResponseData
    ) -> FFmpegNode:
        return SRTNode(
            host=gethostbyname(self._config.emirecords.srt.host),
            port=self._config.emirecords.srt.port,
            options={
                "f": format,
                "passphrase": recording.credentials.token,
            },
        )

    def _build_output(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        format: m.Format,
        recording: erm.RecordResponseData | None,
    ) -> FFmpegNode:
        metadata = self._build_metadata(event, instance)

        if recording is None:
            return self._build_emifuse_output(format, metadata)

        return FFmpegTeeNode(
            nodes=[
                self._build_tee_emifuse_output(format),
                self._build_tee_emirecords_output(format, recording),
            ],
            options={
                "acodec": "copy",
                "map": 0,
                "metadata": metadata,
            },
        )

    def _build_stream_metadata(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
        recording: erm.RecordResponseData | None,
    ) -> ProcessBasedStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_input(credentials, port),
            output=self._build_output(event, instance, format, recording),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
        recording: erm.RecordResponseData | None,
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(
            event, instance, credentials, port, format, recording
        )
        return await self._run_stream(metadata)
