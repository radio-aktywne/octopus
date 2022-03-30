"""Main script.

This module provides basic CLI entrypoint.

"""

import typer
import uvicorn

from emistream.app import app

cli = typer.Typer()


@cli.command()
def main(
    host: str = typer.Option(
        default="0.0.0.0", help="Host to run the server on"
    ),
    port: int = typer.Option(default=10000, help="Port to run the server on"),
):
    """Command line interface for emistream."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
