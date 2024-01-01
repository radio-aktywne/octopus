from uuid import UUID


class StreamingError(Exception):
    """Base class for all exceptions related to streaming."""

    def __init__(self, message: str | None = None) -> None:
        self._message = message

        args = (message,) if message else ()
        super().__init__(*args)

    @property
    def message(self) -> str | None:
        return self._message


class InstanceNotFoundError(StreamingError):
    """Raised when no near instances of an event are found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No near instances of event {event} found.")


class StreamBusyError(StreamingError):
    """Raised when a stream is busy."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"Event {event} is already being streamed.")


class RecorderBusyError(StreamingError):
    """Raised when a recorder is busy."""

    def __init__(self) -> None:
        super().__init__("Recorder is busy at the moment.")
