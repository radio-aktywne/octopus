import asyncio
from datetime import datetime, timedelta
from threading import Event, RLock, Thread
from uuid import uuid4

from emistream.config import config
from emistream.models.stream import Availability, Reservation, Token
from emistream.stream.stream import SRTStream


def generate_token() -> str:
    return uuid4().hex


class StreamManager:
    DEFAULT_TIMEOUT = timedelta(seconds=60)
    FORMAT = "ogg"

    def __init__(self, timeout: timedelta = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.stream = None
        self.reservation = None
        self.lock = RLock()
        self.availability_changed_event = Event()

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

    async def _async_run_stream(
        self, token: str, reservation: Reservation
    ) -> None:
        with self.lock:
            self.stream = self._create_stream(token, reservation.title)
            self.reservation = reservation
            self.availability_changed_event.set()
            self.availability_changed_event.clear()
            self.stream.start()
        await self.stream.ended()
        with self.lock:
            self.reservation = None
            self.stream = None
            self.availability_changed_event.set()
            self.availability_changed_event.clear()

    def _run_stream(self, token: str, reservation: Reservation) -> None:
        def target():
            asyncio.run(self._async_run_stream(token, reservation))

        Thread(target=target).start()

    def availability(self) -> Availability:
        with self.lock:
            return Availability(
                available=self.stream is None, reservation=self.reservation
            )

    async def availability_changed(self) -> None:
        await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.availability_changed_event.wait()
        )

    def reserve(self, reservation: Reservation) -> Token:
        with self.lock:
            if not self.availability().available:
                raise RuntimeError("Stream is busy.")
            token = generate_token()
            expires_at = datetime.utcnow() + self.timeout
            self._run_stream(token, reservation)
            return Token(token=token, expires_at=expires_at)
