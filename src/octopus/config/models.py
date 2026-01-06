from collections.abc import Sequence
from datetime import timedelta
from socket import gethostbyname

from pydantic import BaseModel, Field

from octopus.config.base import BaseConfig


class BeaverHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the beaver service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(default=10500, ge=1, le=65535)
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


class BeaverConfig(BaseModel):
    """Configuration for the beaver service."""

    http: BeaverHTTPConfig = BeaverHTTPConfig()
    """Configuration for the HTTP API."""


class DingoSRTConfig(BaseModel):
    """Configuration for the SRT stream of the dingo service."""

    host: str = "localhost"
    """Host of the SRT stream."""

    port: int = Field(default=10100, ge=1, le=65535)
    """Port of the SRT stream."""

    @property
    def url(self) -> str:
        """URL of the SRT stream."""
        host = gethostbyname(self.host)
        port = self.port

        return f"srt://{host}:{port}"


class DingoConfig(BaseModel):
    """Configuration for the dingo service."""

    srt: DingoSRTConfig = DingoSRTConfig()
    """Configuration for the SRT stream."""


class GeckoHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the gecko service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(default=10700, ge=1, le=65535)
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


class GeckoConfig(BaseModel):
    """Configuration for the gecko service."""

    http: GeckoHTTPConfig = GeckoHTTPConfig()
    """Configuration for the HTTP API."""


class ServerPortsConfig(BaseModel):
    """Configuration for the server ports."""

    http: int = Field(default=10300, ge=0, le=65535)
    """Port to listen for HTTP requests on."""

    srt: int = Field(default=10300, ge=0, le=65535)
    """Port to listen for SRT connections on."""


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    ports: ServerPortsConfig = ServerPortsConfig()
    """Configuration for the server ports."""

    trusted: str | Sequence[str] | None = "*"
    """Trusted IP addresses."""


class StreamingConfig(BaseModel):
    """Configuration for the streaming service."""

    timeout: timedelta = Field(default=timedelta(minutes=1), ge=0)
    """Time after which a stream will be stopped if no connections are made."""

    window: timedelta = timedelta(hours=1)
    """Time window to search for event instances around the current time."""


class Config(BaseConfig):
    """Configuration for the service."""

    beaver: BeaverConfig = BeaverConfig()
    """Configuration for the beaver service."""

    debug: bool = True
    """Enable debug mode."""

    dingo: DingoConfig = DingoConfig()
    """Configuration for the dingo service."""

    gecko: GeckoConfig = GeckoConfig()
    """Configuration for the gecko service."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    streaming: StreamingConfig = StreamingConfig()
    """Configuration for the streaming service."""
