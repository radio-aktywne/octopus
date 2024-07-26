from math import ceil
from socket import gethostbyname

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata, FFmpegTeeNode
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata
from pystreams.srt import SRTNode
from pystreams.stream import Stream

from emistream.config.models import Config
from emistream.emishows import models as esm
from emistream.streaming import models as sm
from emistream.time import naiveutcnow


class StreamRunner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_input(self, port: int, credentials: sm.Credentials) -> FFmpegNode:
        """Build the input node."""

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
        self,
        event: esm.Event,
        instance: esm.EventInstance,
    ) -> list[str]:
        """Builds metadata."""

        metadata = {
            "title": event.show.title,
        }

        return self._build_ffmpeg_metadata_options(metadata)

    def _build_emifuse_output(
        self, format: sm.Format, metadata: list[str]
    ) -> FFmpegNode:
        """Build emifuse output node."""

        return SRTNode(
            host=gethostbyname(self._config.emifuse.srt.host),
            port=self._config.emifuse.srt.port,
            options={"acodec": "copy", "f": format, "metadata": metadata},
        )

    def _build_tee_emifuse_output(self, format: sm.Format) -> FFmpegNode:
        """Build tee emifuse output node."""

        return SRTNode(
            host=gethostbyname(self._config.emifuse.srt.host),
            port=self._config.emifuse.srt.port,
            options={"f": format},
        )

    def _build_tee_emirecords_output(
        self,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> FFmpegNode:
        """Build tee emirecords output node."""

        return SRTNode(
            host=gethostbyname(self._config.emirecords.srt.host),
            port=self._config.emirecords.srt.port,
            options={"f": format, "passphrase": recorder.token},
        )

    def _build_output(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> FFmpegNode:
        """Build the output node."""

        metadata = self._build_metadata(event, instance)

        if recorder is None:
            return self._build_emifuse_output(format, metadata)

        return FFmpegTeeNode(
            nodes=[
                self._build_tee_emifuse_output(format),
                self._build_tee_emirecords_output(format, recorder),
            ],
            options={"acodec": "copy", "map": 0, "metadata": metadata},
        )

    def _build_stream_metadata(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        port: int,
        credentials: sm.Credentials,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> ProcessBasedStreamMetadata:
        """Builds stream metadata."""

        return FFmpegStreamMetadata(
            input=self._build_input(port, credentials),
            output=self._build_output(event, instance, format, recorder),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        """Run the stream with the given metadata."""

        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        port: int,
        credentials: sm.Credentials,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(
            event, instance, port, credentials, format, recorder
        )
        return await self._run_stream(metadata)
