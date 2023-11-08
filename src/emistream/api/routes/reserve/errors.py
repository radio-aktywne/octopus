from emistream.models.data import Event


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class RecorderError(ServiceError):
    """Raised when a recorder service error occurs."""

    pass


class StreamBusyError(ServiceError):
    """Raised when a stream is busy."""

    def __init__(self, event: Event) -> None:
        self._event = event
        super().__init__("Stream is busy.")

    @property
    def event(self) -> Event:
        return self._event
