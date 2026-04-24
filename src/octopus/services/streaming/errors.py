from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""


class InstanceNotFoundError(ServiceError):
    """Raised when no near instances of an event are found."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"No near instances of event {event_id} found.")


class UnrecordableEventError(ServiceError):
    """Raised when an event is not recordable."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"Event {event_id} is not recordable.")


class StreamBusyError(ServiceError):
    """Raised when another stream is already being handled at the moment."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(
            f"Another stream is already being handled for event {event_id}."
        )


class BeaverError(ServiceError):
    """Raised when an beaver service operation fails."""
