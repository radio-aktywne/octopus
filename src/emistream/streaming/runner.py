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

    def _build_input(self, credentials: sm.Credentials) -> FFmpegNode:
        """Build the input node."""

        timeout = credentials.expires_at - naiveutcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        return SRTNode(
            host=self._config.stream.host,
            port=self._config.stream.port,
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

    def _build_fusion_output(
        self, format: sm.Format, metadata: list[str]
    ) -> FFmpegNode:
        """Build fusion output node."""

        return SRTNode(
            host=gethostbyname(self._config.fusion.host),
            port=self._config.fusion.port,
            options={"acodec": "copy", "f": format, "metadata": metadata},
        )

    def _build_tee_fusion_output(self, format: sm.Format) -> FFmpegNode:
        """Build tee fusion output node."""

        return SRTNode(
            host=gethostbyname(self._config.fusion.host),
            port=self._config.fusion.port,
            options={"f": format},
        )

    def _build_tee_emirecorder_output(
        self,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> FFmpegNode:
        """Build tee emirecorder output node."""

        return SRTNode(
            host=gethostbyname(self._config.emirecorder.host),
            port=recorder.port,
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
            return self._build_fusion_output(format, metadata)

        return FFmpegTeeNode(
            nodes=[
                self._build_tee_fusion_output(format),
                self._build_tee_emirecorder_output(format, recorder),
            ],
            options={"acodec": "copy", "map": 0, "metadata": metadata},
        )

    def _build_stream_metadata(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        credentials: sm.Credentials,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> ProcessBasedStreamMetadata:
        """Builds stream metadata."""

        return FFmpegStreamMetadata(
            input=self._build_input(credentials),
            output=self._build_output(event, instance, format, recorder),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        """Run the stream with the given metadata."""

        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self,
        event: esm.Event,
        instance: esm.EventInstance,
        credentials: sm.Credentials,
        format: sm.Format,
        recorder: sm.RecorderAccess | None,
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(
            event, instance, credentials, format, recorder
        )
        return await self._run_stream(metadata)
