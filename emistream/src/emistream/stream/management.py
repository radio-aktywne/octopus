from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Event, RLock

from emistream.config import config
from emistream.models.stream import Availability, Reservation, Token
from emistream.stream.stream import SRTStream
from emistream.utils import (
    generate_uuid,
    start_in_thread,
    thread,
)


class StreamManager:
    @dataclass
    class State:
        stream: SRTStream = None
        reservation: Reservation = None
        changed: Event = Event()

    DEFAULT_TIMEOUT = timedelta(seconds=60)
    FORMAT = "ogg"

    def __init__(self, timeout: timedelta = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.state = self.State()
        self.lock = RLock()

    def _create_stream(self, token: str, title: str) -> SRTStream:
        return SRTStream(
            input_port=config.port,
            output_host=config.target_host,
            output_port=config.target_port,
            input_options={
                "mode": "listener",
                "listen_timeout": int(self.timeout.total_seconds() * 1000000),
                "passphrase": token,
            },
            output_options={
                "acodec": "copy",
                "metadata": f"title={title}",
                "format": StreamManager.FORMAT,
            },
        )

    def _set_state(self, stream: SRTStream, reservation: Reservation) -> None:
        self.state.stream = stream
        self.state.reservation = reservation
        self.state.changed.set()
        self.state.changed.clear()

    def _reset_state(self) -> None:
        self.state.stream = None
        self.state.reservation = None
        self.state.changed.set()
        self.state.changed.clear()

    async def _async_run_stream(self) -> None:
        self.state.stream.start()
        await self.state.stream.ended()
        with self.lock:
            self._reset_state()

    def _run_stream(self) -> None:
        start_in_thread(self._async_run_stream())

    def availability(self) -> Availability:
        with self.lock:
            return Availability(
                available=self.state.stream is None,
                reservation=self.state.reservation,
            )

    async def availability_changed(self) -> None:
        await thread(self.state.changed.wait)

    def reserve(self, reservation: Reservation) -> Token:
        with self.lock:
            if not self.availability().available:
                raise RuntimeError("Stream is busy.")
            token = generate_uuid()
            expires_at = datetime.utcnow() + self.timeout
            self._set_state(
                self._create_stream(token, reservation.title), reservation
            )
            self._run_stream()
            return Token(token=token, expires_at=expires_at)
