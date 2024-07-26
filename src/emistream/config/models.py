from datetime import timedelta

from pydantic import BaseModel, Field

from emistream.config.base import BaseConfig


class ServerPortsConfig(BaseModel):
    """Configuration for the server ports."""

    http: int = Field(
        10000,
        ge=0,
        le=65535,
        title="HTTP",
        description="Port of the HTTP server.",
    )
    srt: int = Field(
        10000,
        ge=0,
        le=65535,
        title="SRT",
        description="Port of the SRT server.",
    )


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = Field(
        "0.0.0.0",
        title="Host",
        description="Host to run the server on.",
    )
    ports: ServerPortsConfig = Field(
        ServerPortsConfig(),
        title="Ports",
        description="Configuration for the server ports.",
    )


class StreamConfig(BaseModel):
    """Configuration for the streaming process."""

    timeout: timedelta = Field(
        timedelta(minutes=1),
        ge=0,
        title="Timeout",
        description="Time after which a stream will be stopped if no connections are made.",
    )
    window: timedelta = Field(
        timedelta(hours=1),
        title="Window",
        description="Time window to search for event instances around the current time.",
    )


class EmifuseSRTConfig(BaseModel):
    """Configuration for the emifuse SRT stream."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the SRT stream.",
    )
    port: int = Field(
        9000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the SRT stream.",
    )

    @property
    def url(self) -> str:
        return f"srt://{self.host}:{self.port}"


class EmifuseConfig(BaseModel):
    """Configuration for the emifuse service."""

    srt: EmifuseSRTConfig = Field(
        EmifuseSRTConfig(),
        title="SRT",
        description="Configuration for the SRT stream.",
    )


class EmirecordsHTTPConfig(BaseModel):
    """Configuration for the emirecords HTTP API."""

    scheme: str = Field(
        "http",
        title="Scheme",
        description="Scheme of the HTTP API.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the HTTP API.",
    )
    port: int | None = Field(
        31000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the HTTP API.",
    )
    path: str | None = Field(
        None,
        title="Path",
        description="Path of the HTTP API.",
    )

    @property
    def url(self) -> str:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmirecordsSRTConfig(BaseModel):
    """Configuration for the emirecords SRT stream."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the SRT stream.",
    )
    port: int = Field(
        31000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the SRT stream.",
    )

    @property
    def url(self) -> str:
        return f"srt://{self.host}:{self.port}"


class EmirecordsConfig(BaseModel):
    """Configuration for the emirecords service."""

    http: EmirecordsHTTPConfig = Field(
        EmirecordsHTTPConfig(),
        title="HTTP",
        description="Configuration for the HTTP API.",
    )
    srt: EmirecordsSRTConfig = Field(
        EmirecordsSRTConfig(),
        title="SRT",
        description="Configuration for the SRT stream.",
    )


class EmishowsHTTPConfig(BaseModel):
    """Configuration for the emishows HTTP API."""

    scheme: str = Field(
        "http",
        title="Scheme",
        description="Scheme of the HTTP API.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the HTTP API.",
    )
    port: int | None = Field(
        35000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the HTTP API.",
    )
    path: str | None = Field(
        None,
        title="Path",
        description="Path of the HTTP API.",
    )

    @property
    def url(self) -> str:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmishowsConfig(BaseModel):
    """Configuration for the emishows service."""

    http: EmishowsHTTPConfig = Field(
        EmishowsHTTPConfig(),
        title="HTTP",
        description="Configuration for the HTTP API.",
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
    emifuse: EmifuseConfig = Field(
        EmifuseConfig(),
        title="Emifuse",
        description="Configuration for the emifuse service.",
    )
    emirecords: EmirecordsConfig = Field(
        EmirecordsConfig(),
        title="Emirecords",
        description="Configuration for the emirecords service.",
    )
    emishows: EmishowsConfig = Field(
        EmishowsConfig(),
        title="Emishows",
        description="Configuration for the emishows service.",
    )
