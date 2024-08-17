from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class InstanceNotFoundError(ServiceError):
    """Raised when no near instances of an event are found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No near instances of event {event} found.")


class RecordingBusyError(ServiceError):
    """Raised when no more recordings can be handled at the moment."""

    def __init__(self) -> None:
        super().__init__("No more recordings can be handled at the moment.")


class StreamBusyError(ServiceError):
    """Raised when another stream is already being handled at the moment."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"Another stream is already being handled for event {event}.")


class EmishowsError(ServiceError):
    """Raised when an emishows service operation fails."""

    pass


class EmirecordsError(ServiceError):
    """Raised when an emirecords service operation fails."""

    pass
