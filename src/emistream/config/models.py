from datetime import timedelta

from pydantic import BaseModel, Field

from emistream.config.base import BaseConfig


class ServerPortsConfig(BaseModel):
    """Configuration for the server ports."""

    http: int = Field(10000, ge=0, le=65535)
    """Port to listen for HTTP requests on."""

    srt: int = Field(10000, ge=0, le=65535)
    """Port to listen for SRT connections on."""


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    ports: ServerPortsConfig = ServerPortsConfig()
    """Configuration for the server ports."""

    trusted: str | list[str] | None = "*"
    """Trusted IP addresses."""


class StreamingConfig(BaseModel):
    """Configuration for the streaming service."""

    timeout: timedelta = Field(timedelta(minutes=1), ge=0)
    """Time after which a stream will be stopped if no connections are made."""

    window: timedelta = timedelta(hours=1)
    """Time window to search for event instances around the current time."""


class EmifuseSRTConfig(BaseModel):
    """Configuration for the SRT stream of the emifuse service."""

    host: str = "localhost"
    """Host of the SRT stream."""

    port: int = Field(9000, ge=1, le=65535)
    """Port of the SRT stream."""

    @property
    def url(self) -> str:
        """URL of the SRT stream."""

        return f"srt://{self.host}:{self.port}"


class EmifuseConfig(BaseModel):
    """Configuration for the emifuse service."""

    srt: EmifuseSRTConfig = EmifuseSRTConfig()
    """Configuration for the SRT stream."""


class EmirecordsHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the emirecords service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(31000, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""

        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmirecordsSRTConfig(BaseModel):
    """Configuration for the SRT stream of the emirecords service."""

    host: str = "localhost"
    """Host of the SRT stream."""

    port: int = Field(31000, ge=1, le=65535)
    """Port of the SRT stream."""

    @property
    def url(self) -> str:
        """URL of the SRT stream."""

        return f"srt://{self.host}:{self.port}"


class EmirecordsConfig(BaseModel):
    """Configuration for the emirecords service."""

    http: EmirecordsHTTPConfig = EmirecordsHTTPConfig()
    """Configuration for the HTTP API."""

    srt: EmirecordsSRTConfig = EmirecordsSRTConfig()
    """Configuration for the SRT stream."""


class EmishowsHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the emishows service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(35000, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""

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

    http: EmishowsHTTPConfig = EmishowsHTTPConfig()
    """Configuration for the HTTP API."""


class Config(BaseConfig):
    """Configuration for the application."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    streaming: StreamingConfig = StreamingConfig()
    """Configuration for the streaming service."""

    emifuse: EmifuseConfig = EmifuseConfig()
    """Configuration for the emifuse service."""

    emirecords: EmirecordsConfig = EmirecordsConfig()
    """Configuration for the emirecords service."""

    emishows: EmishowsConfig = EmishowsConfig()
    """Configuration for the emishows service."""

    debug: bool = False
    """Enable debug mode."""
