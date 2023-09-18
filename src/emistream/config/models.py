from typing import Any

from pydantic import BaseModel, Field, validator

from emistream.config.base import BaseConfig


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = Field(
        "0.0.0.0",
        title="Host",
        description="Host to run the server on.",
    )
    port: int = Field(
        10000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to run the server on.",
    )
    concurrency: int | None = Field(
        None,
        ge=1,
        title="Concurrency",
        description="Number of concurrent requests to handle.",
    )
    backlog: int = Field(
        2048,
        ge=0,
        title="Backlog",
        description="Number of requests to queue.",
    )
    keepalive: int = Field(
        5,
        ge=0,
        title="Keepalive",
        description="Number of seconds to keep connections alive.",
    )

    @validator("concurrency", pre=True)
    def _validate_concurrency(cls, value: Any) -> Any:
        if value == "":
            return None
        return value


class StreamConfig(BaseModel):
    """Configuration for the streaming process."""

    timeout: int = Field(
        60,
        ge=0,
        title="Timeout",
        description="Number of seconds to wait for a connection.",
    )
    format: str = Field(
        "ogg",
        title="Format",
        description="Format to stream in.",
    )


class FusionConfig(BaseModel):
    """Configuration for the Fusion service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        9000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )


class EmirecorderConfig(BaseModel):
    """Configuration for the Emirecorder service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        31000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )


class Config(BaseConfig):
    """Configuration for the application."""

    server: ServerConfig = Field(
        ServerConfig(),
        title="Server",
        description="Configuration for the server.",
    )
    stream: StreamConfig = Field(
        StreamConfig(),
        title="Stream",
        description="Configuration for the streaming process.",
    )
    fusion: FusionConfig = Field(
        FusionConfig(),
        title="Fusion",
        description="Configuration for the Fusion service.",
    )
    emirecorder: EmirecorderConfig = Field(
        EmirecorderConfig(),
        title="Emirecorder",
        description="Configuration for the Emirecorder service.",
    )
