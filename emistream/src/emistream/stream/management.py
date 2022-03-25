import asyncio
from asyncio import Event
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from emistream.config import config
from emistream.models.stream import Availability, Reservation, Token
from emistream.stream.stream import SRTStream
from emistream.utils import generate_uuid, thread


class StreamManager:
    @dataclass
    class State:
        stream: Optional[SRTStream]
        reservation: Optional[Reservation]
        changed: Event

    DEFAULT_TIMEOUT = timedelta(seconds=60)
    FORMAT = "ogg"

    def __init__(self, timeout: timedelta = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.state = self.initial_state()

    def initial_state(self) -> State:
        return self.State(None, None, Event())

    def create_token(self) -> Token:
        return Token(
            token=generate_uuid(), expires_at=datetime.utcnow() + self.timeout
        )

    def stream_parameters(self, token: str, title: str) -> Dict[str, Any]:
        return {
            "input_port": config.port,
            "output_host": config.target_host,
            "output_port": config.target_port,
            "input_options": {
                "mode": "listener",
                "listen_timeout": int(self.timeout.total_seconds() * 1000000),
                "passphrase": token,
            },
            "output_options": {
                "acodec": "copy",
                "metadata": f"title={title}",
                "format": self.FORMAT,
            },
        }

    @staticmethod
    def create_stream(params: Dict[str, Any]) -> SRTStream:
        return SRTStream(**params)

    def set_state(self, stream: SRTStream, reservation: Reservation) -> None:
        self.state.stream = stream
        self.state.reservation = reservation
        self.state.changed.set()
        self.state.changed.clear()

    def reset_state(self) -> None:
        self.state.stream = None
        self.state.reservation = None
        self.state.changed.set()
        self.state.changed.clear()

    def start(self) -> None:
        self.state.stream.start()

    async def monitor(self) -> None:
        await thread(self.state.stream.wait)
        self.reset_state()

    async def reserve(self, reservation: Reservation) -> Token:
        if not self.availability().available:
            raise RuntimeError("Stream is busy.")
        token = self.create_token()
        stream = self.create_stream(
            self.stream_parameters(token.token, reservation.title)
        )
        self.set_state(stream, reservation)
        self.start()
        asyncio.create_task(self.monitor())
        return token

    def availability(self) -> Availability:
        return Availability(
            available=self.state.stream is None,
            reservation=self.state.reservation,
        )

    async def state_changed(self) -> None:
        await self.state.changed.wait()
