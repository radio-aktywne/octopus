from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""


class InstanceNotFoundError(ServiceError):
    """Raised when no near instances of an event are found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No near instances of event {event} found.")


class StreamBusyError(ServiceError):
    """Raised when another stream is already being handled at the moment."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"Another stream is already being handled for event {event}.")


class BeaverError(ServiceError):
    """Raised when an beaver service operation fails."""
