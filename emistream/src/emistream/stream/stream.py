import asyncio
from abc import ABC, abstractmethod
from threading import Event, RLock, Thread
from typing import Any, Dict, Optional

import ffmpeg


class Stream(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def end(self) -> None:
        pass

    @abstractmethod
    async def ended(self) -> bool:
        pass


class FFmpegStream(Stream):
    def __init__(
        self,
        input: str,
        output: str,
        input_options: Optional[Dict[str, Any]] = None,
        output_options: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.lock = RLock()
        self.ended_event = Event()
        self.input = input
        self.output = output
        self.input_options = input_options or {}
        self.output_options = output_options or {}
        self.process = None

    def start(self) -> None:
        with self.lock:
            if self.process is not None:
                raise RuntimeError("Stream already started.")
            # TODO: handle errors and logs
            f = ffmpeg.input(
                self.input, enable_cuda=False, **self.input_options
            )
            f = f.output(self.output, enable_cuda=False, **self.output_options)
            self.process = f.run_async()
            self.ended_event.clear()
            Thread(target=self._wait).start()

    def end(self) -> None:
        with self.lock:
            if self.process is None:
                return
            self.process.kill()

    def _wait(self) -> None:
        if self.process is None:
            return
        self.process.wait()
        with self.lock:
            self.process = None
            self.ended_event.set()

    async def ended(self) -> bool:
        await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.ended_event.wait()
        )
        return True


class SRTStream(FFmpegStream):
    def __init__(
        self,
        input_port: int,
        output_host: str,
        output_port: str,
        input_host: str = "0.0.0.0",
        **kwargs,
    ) -> None:
        # TODO: sanitize
        input = f"srt://{input_host}:{input_port}"
        output = f"srt://{output_host}:{output_port}"
        kwargs.pop("input", None)
        kwargs.pop("output", None)
        super().__init__(input=input, output=output, **kwargs)
