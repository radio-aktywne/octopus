from typer import Typer

from emistream.builder import Builder


class CliBuilder(Builder[Typer]):
    """Builds the CLI app."""

    def build(self) -> Typer:
        return Typer()
