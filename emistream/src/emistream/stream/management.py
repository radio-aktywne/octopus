import asyncio
from asyncio import Event as AsyncioEvent, Lock
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from pystreams.ffmpeg import FFmpegNode, FFmpegStream
from pystreams.srt import SRTNode
from pystreams.stream import Stream as PyStream

from emistream.config import Config
from emistream.fusion.client import FusionClient
from emistream.models.data import Event, Token, Availability
from emistream.recorder.client import RecorderClient
from emistream.recorder.models.data import (
    Token as RecorderToken,
    Event as RecorderEvent,
    Show as RecorderShow,
)
from emistream.utils import generate_uuid, background


class StreamManager:
    @dataclass
    class State:
        stream: Optional[PyStream]
        event: Optional[Event]
        changed: AsyncioEvent

    def __init__(
        self, config: Config, recorder: RecorderClient, fusion: FusionClient
    ) -> None:
        self.config = config
        self.recorder = recorder
        self.fusion = fusion
        self.state = self._initial_state()
        self.lock = Lock()

    def _initial_state(self) -> State:
        return self.State(None, None, AsyncioEvent())

    def _create_token(self) -> Token:
        return Token(
            token=generate_uuid(),
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=self.config.timeout),
        )

    @staticmethod
    def _map_event(event: Event) -> RecorderEvent:
        return RecorderEvent(
            show=RecorderShow(
                label=event.show.label,
                metadata=event.show.metadata,
            ),
            start=event.start,
            end=event.end,
            metadata=event.metadata,
        )

    async def _get_recording_token(self, event: Event) -> RecorderToken:
        event = self._map_event(event)
        return await self.recorder.record(event)

    async def _get_tokens(
        self, event: Event, record: bool
    ) -> Tuple[Token, Optional[RecorderToken]]:
        token = self._create_token()
        recording_token = (
            await self._get_recording_token(event) if record else None
        )
        return token, recording_token

    def _input_node(self, passphrase: str) -> FFmpegNode:
        return SRTNode(
            host=self.config.host,
            port=str(self.config.port),
            options={
                "re": None,
                "mode": "listener",
                "listen_timeout": int(self.config.timeout * 1000000),
                "passphrase": passphrase,
            },
        )

    @staticmethod
    def _metadata_values(metadata: Dict[str, str]) -> List[str]:
        return [f"{key}={value}" for key, value in metadata.items()]

    def _live_node(self, metadata: Dict[str, str]) -> FFmpegNode:
        return self.fusion.get_stream_node(
            metadata=self._metadata_values(metadata)
        )

    def _recording_node(
        self, passphrase: str, metadata: Dict[str, str]
    ) -> FFmpegNode:
        return self.recorder.get_stream_node(
            metadata=self._metadata_values(metadata),
            passphrase=passphrase,
            pbkeylen=len(passphrase),
        )

    def _create_stream(
        self,
        token: Token,
        event: Event,
        recording_token: Optional[RecorderToken],
    ) -> PyStream:
        metadata = event.show.metadata | event.metadata
        input = self._input_node(token.token)
        output = [self._live_node(metadata)]
        if recording_token is not None:
            output.append(
                self._recording_node(recording_token.token, metadata)
            )
        return FFmpegStream(input, output)

    def _set_state(self, stream: PyStream, event: Event) -> None:
        self.state.stream = stream
        self.state.event = event
        self.state.changed.set()
        self.state.changed.clear()

    def _reset_state(self) -> None:
        self.state.stream = None
        self.state.event = None
        self.state.changed.set()
        self.state.changed.clear()

    def _start(self) -> None:
        self.state.stream.start()

    async def _monitor(self) -> None:
        await background(self.state.stream.wait)
        self._reset_state()

    async def reserve(self, event: Event, record: bool) -> Token:
        async with self.lock:
            if self.state.stream is not None:
                raise RuntimeError("Stream is busy.")
            token, recording_token = await self._get_tokens(event, record)
            stream = self._create_stream(token, event, recording_token)
            self._set_state(stream, event)
            self._start()
            asyncio.create_task(self._monitor())
            return token

    async def availability(self) -> Availability:
        async with self.lock:
            return Availability(
                available=self.state.stream is None,
                event=self.state.event,
            )

    async def state_changed(self) -> None:
        await self.state.changed.wait()
