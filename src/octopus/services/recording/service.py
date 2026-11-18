from asyncio import Lock as AsyncioLock, Task, create_task, shield
from collections.abc import AsyncIterator
from contextlib import suppress
from http import HTTPStatus

from anyio import AsyncFile, Event, Path, sleep
from httpx2 import AsyncClient, HTTPError
from pylocks.base import Lock
from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.process import ProcessBasedStreamFactory

from octopus.config.models import Config
from octopus.services.recording import models as m
from octopus.services.recording.workspace import Workspace
from octopus.utils.time import isostringify


class RecordingService:
    """Processes recordings."""

    def __init__(self, config: Config, lock: Lock) -> None:
        self._config = config
        self._lock = lock
        self._task: Task[None] | None = None
        self._transition = AsyncioLock()

    def _map_content_type(self, fmt: m.Format) -> str:
        match fmt:
            case m.Format.OGG:
                return "audio/ogg"

    async def _read(self, source: AsyncFile[bytes]) -> AsyncIterator[bytes]:
        while chunk := await source.read(1024 * 1024):
            yield chunk

    async def _download(self, client: AsyncClient, url: str, path: Path) -> bool:
        async with client.stream("GET", url) as response:
            if response.status_code == HTTPStatus.NOT_FOUND:
                return False

            response.raise_for_status()

            async with await path.open("wb") as target:
                async for chunk in response.aiter_bytes():
                    await target.write(chunk)

        return True

    async def _concatenate(self, workspace: Workspace) -> Path | None:
        manifest = workspace.directory / workspace.manifest
        combined = workspace.directory / workspace.combined

        inputs = (workspace.previous, workspace.current)
        contents = "".join(f"file '{name}'\n" for name in inputs)

        await manifest.write_text(contents, encoding="utf-8")

        metadata = FFmpegStreamMetadata(
            input=FFmpegNode(target=str(manifest), options={"f": "concat"}),
            output=FFmpegNode(
                target=str(combined),
                options={"map": "0:a", "acodec": "copy"},
            ),
        )

        stream = await ProcessBasedStreamFactory().create(metadata)

        try:
            await stream.wait()
        finally:
            if stream.process.returncode is None:
                await stream.kill()
                await stream.wait()

        if stream.process.returncode != 0:
            return None

        return combined

    async def _upload(
        self, client: AsyncClient, url: str, path: Path, fmt: m.Format
    ) -> None:
        attempts = 3
        headers = {
            "Content-Type": self._map_content_type(fmt),
            "Content-Length": str((await path.stat()).st_size),
        }

        for attempt in range(attempts):
            try:
                async with await path.open("rb") as source:
                    response = await client.put(
                        url, content=self._read(source), headers=headers
                    )

                response.raise_for_status()
            except HTTPError:
                if attempt + 1 == attempts:
                    raise

                await sleep(2**attempt)
            else:
                return

    async def _finalize(self, workspace: Workspace) -> None:
        current = workspace.directory / workspace.current
        previous = workspace.directory / workspace.previous

        instance = workspace.instance
        url = f"/recordings/{instance.event}/{isostringify(instance.start)}"

        async with AsyncClient(base_url=self._config.gecko.http.url) as client:
            path = current

            if await self._download(client, url, previous):
                path = await self._concatenate(workspace) or current

            await self._upload(client, url, path, workspace.format)

        await workspace.delete()

    async def _run(self, workspace: Workspace, ready: Event) -> None:
        try:
            with suppress(Exception):
                async with self._lock:
                    ready.set()
                    await self._finalize(workspace)
        finally:
            ready.set()

    async def submit(self, workspace: Workspace) -> None:
        """Submit a recording for finalization."""
        current = workspace.directory / workspace.current

        size = 0
        with suppress(FileNotFoundError):
            size = (await current.stat()).st_size

        if size == 0:
            await workspace.delete()
            return

        async with self._transition:
            if self._task is not None:
                await shield(self._task)

            ready = Event()
            self._task = create_task(self._run(workspace, ready))
            await ready.wait()

    async def close(self) -> None:
        """Finish pending work."""
        async with self._transition:
            if self._task is not None:
                await shield(self._task)
                self._task = None
