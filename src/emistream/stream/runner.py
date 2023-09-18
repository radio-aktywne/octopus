from math import ceil
from socket import gethostbyname

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata, FFmpegTeeNode
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata
from pystreams.srt import SRTNode
from pystreams.stream import Stream

from emistream.config import Config
from emistream.emirecorder.models import RecordingCredentials
from emistream.models.data import Event, Reservation, ReservationRequest
from emistream.time import utcnow


class StreamRunner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_input(self, reservation: Reservation) -> FFmpegNode:
        """Build the input node."""

        timeout = reservation.expires_at - utcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        return SRTNode(
            host=gethostbyname(self._config.server.host),
            port=self._config.server.port,
            options={
                "re": True,
                "mode": "listener",
                "listen_timeout": timeout,
                "passphrase": reservation.token,
            },
        )

    def _build_ffmpeg_metadata_options(self, metadata: dict[str, str]) -> list[str]:
        return [f"{key}={value}" for key, value in metadata.items()]

    def _build_fusion_output(self, event: Event) -> FFmpegNode:
        """Build fusion output node."""

        return SRTNode(
            host=gethostbyname(self._config.fusion.host),
            port=self._config.fusion.port,
            options={
                "acodec": "copy",
                "f": self._config.stream.format,
                "metadata": self._build_ffmpeg_metadata_options(
                    event.show.metadata | event.metadata
                ),
            },
        )

    def _build_tee_fusion_output(self) -> FFmpegNode:
        """Build tee fusion output node."""

        return SRTNode(
            host=gethostbyname(self._config.fusion.host),
            port=self._config.fusion.port,
            options={
                "f": self._config.stream.format,
            },
        )

    def _build_tee_emirecorder_output(
        self, credentials: RecordingCredentials
    ) -> FFmpegNode:
        """Build tee emirecorder output node."""

        return SRTNode(
            host=gethostbyname(self._config.emirecorder.host),
            port=self._config.emirecorder.port,
            options={
                "f": self._config.stream.format,
                "passphrase": credentials.token,
            },
        )

    def _build_output(
        self,
        request: ReservationRequest,
        credentials: RecordingCredentials | None,
    ) -> FFmpegNode:
        """Build the output node."""

        event = request.event

        if credentials is None:
            return self._build_fusion_output(event)

        return FFmpegTeeNode(
            nodes=[
                self._build_tee_fusion_output(),
                self._build_tee_emirecorder_output(credentials),
            ],
            options={
                "acodec": "copy",
                "map": 0,
                "metadata": self._build_ffmpeg_metadata_options(
                    event.show.metadata | event.metadata
                ),
            },
        )

    def _build_stream_metadata(
        self,
        request: ReservationRequest,
        reservation: Reservation,
        credentials: RecordingCredentials | None,
    ) -> ProcessBasedStreamMetadata:
        """Build stream metadata."""

        return FFmpegStreamMetadata(
            input=self._build_input(reservation),
            output=self._build_output(request, credentials),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        """Run the stream with the given metadata."""

        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self,
        request: ReservationRequest,
        reservation: Reservation,
        credentials: RecordingCredentials | None,
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(request, reservation, credentials)
        return await self._run_stream(metadata)
