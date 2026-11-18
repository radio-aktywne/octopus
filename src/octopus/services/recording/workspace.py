from shutil import rmtree
from typing import Self

from anyio import Path, mkdtemp
from anyio.to_thread import run_sync

from octopus.models.base import datamodel
from octopus.services.recording import models as m


@datamodel
class Workspace:
    """Temporary recording workspace."""

    instance: m.Instance
    """Instance being recorded."""

    format: m.Format
    """Recording format."""

    directory: Path
    """Working directory."""

    current: str
    """Current recording filename."""

    previous: str
    """Previous recording filename."""

    manifest: str
    """Concatenation manifest filename."""

    combined: str
    """Combined recording filename."""

    @classmethod
    async def create(cls, instance: m.Instance, fmt: m.Format) -> Self:
        """Create a temporary workspace."""
        directory = Path(await mkdtemp())

        match fmt:
            case m.Format.OGG:
                extension = "ogg"

        return cls(
            instance=instance,
            format=fmt,
            directory=directory,
            current=f"current.{extension}",
            previous=f"previous.{extension}",
            manifest="inputs.ffconcat",
            combined=f"combined.{extension}",
        )

    async def delete(self) -> None:
        """Delete the workspace."""
        await run_sync(rmtree, self.directory)
