import asyncio
import json
from asyncio import Event, Lock
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import httpx
from pystreams.ffmpeg import FFmpegNode, FFmpegStream
from pystreams.srt import SRTNode
from pystreams.stream import Stream as PyStream

from emistream.config import config
from emistream.models.record import (
    Event as StreamEvent,
    RecordingRequest,
    RecordingResponse,
    Token as RecordingToken,
)
from emistream.models.stream import Availability, Reservation, Token
from emistream.utils import generate_uuid, thread


class StreamManager:
    @dataclass
    class State:
        stream: Optional[PyStream]
        reservation: Optional[Reservation]
        changed: Event

    DEFAULT_TIMEOUT = timedelta(seconds=60)
    FORMAT = "ogg"

    def __init__(self, timeout: timedelta = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.state = self._initial_state()
        self.lock = Lock()

    def _initial_state(self) -> State:
        return self.State(None, None, Event())

    def _create_token(self) -> Token:
        return Token(
            token=generate_uuid(),
            expires_at=datetime.now(timezone.utc) + self.timeout,
        )

    @staticmethod
    def _recording_endpoint() -> str:
        return f"http://{config.recording_host}:{config.recording_port}/record"

    async def _get_recording_token(self, event: StreamEvent) -> RecordingToken:
        async with httpx.AsyncClient() as client:
            request = RecordingRequest(event=event)
            response = await client.post(
                self._recording_endpoint(), json=json.loads(request.json())
            )
            response = RecordingResponse(**response.json())
            return response.token

    async def _get_tokens(
        self, reservation: Reservation
    ) -> Tuple[Token, Optional[RecordingToken]]:
        token = self._create_token()
        recording_token = (
            await self._get_recording_token(reservation.event)
            if reservation.record
            else None
        )
        return token, recording_token

    def _input_node(self, passphrase: str) -> FFmpegNode:
        return SRTNode(
            host="0.0.0.0",
            port=config.port,
            options={
                "re": None,
                "mode": "listener",
                "listen_timeout": int(self.timeout.total_seconds() * 1000000),
                "passphrase": passphrase,
            },
        )

    def _live_node(self, title: str) -> FFmpegNode:
        return SRTNode(
            host=config.live_host,
            port=config.live_port,
            options={
                "acodec": "copy",
                "metadata": f"title={title}",
                "format": self.FORMAT,
            },
        )

    def _recording_node(self, passphrase: str, title: str) -> FFmpegNode:
        return SRTNode(
            host=config.recording_host,
            port=config.recording_port,
            options={
                "acodec": "copy",
                "metadata": f"title={title}",
                "format": self.FORMAT,
                "passphrase": passphrase,
                "pbkeylen": len(passphrase),
            },
        )

    def _create_stream(
        self,
        token: Token,
        event: StreamEvent,
        recording_token: Optional[RecordingToken],
    ) -> PyStream:
        input = self._input_node(token.token)
        output = [self._live_node(event.title)]
        if recording_token is not None:
            output.append(
                self._recording_node(recording_token.token, event.title)
            )
        return FFmpegStream(input, output)

    def _set_state(self, stream: PyStream, reservation: Reservation) -> None:
        self.state.stream = stream
        self.state.reservation = reservation
        self.state.changed.set()
        self.state.changed.clear()

    def _reset_state(self) -> None:
        self.state.stream = None
        self.state.reservation = None
        self.state.changed.set()
        self.state.changed.clear()

    def _start(self) -> None:
        self.state.stream.start()

    async def _monitor(self) -> None:
        await thread(self.state.stream.wait)
        self._reset_state()

    async def reserve(self, reservation: Reservation) -> Token:
        async with self.lock:
            if self.state.stream is not None:
                raise RuntimeError("Stream is busy.")
            token, recording_token = await self._get_tokens(reservation)
            stream = self._create_stream(
                token, reservation.event, recording_token
            )
            self._set_state(stream, reservation)
            self._start()
            asyncio.create_task(self._monitor())
            return token

    async def availability(self) -> Availability:
        async with self.lock:
            return Availability(
                available=self.state.stream is None,
                reservation=self.state.reservation,
            )

    async def state_changed(self) -> None:
        await self.state.changed.wait()
