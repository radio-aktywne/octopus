from uuid import UUID

from octopus.services.streaming import models as m
from octopus.utils.time import isostringify


class ServiceError(Exception):
    """Base class for service errors."""


class InstanceNotFoundError(ServiceError):
    """Raised when instance of an event is not found."""

    def __init__(self, instance: m.Instance) -> None:
        super().__init__(
            f"Instance of event {instance.event} starting at {isostringify(instance.start)} not found."
        )


class UnrecordableEventError(ServiceError):
    """Raised when an event is not recordable."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"Event {event_id} is not recordable.")


class StreamBusyError(ServiceError):
    """Raised when another stream is already being handled at the moment."""

    def __init__(self, instance: m.Instance) -> None:
        super().__init__(
            f"Stream is reserved for instance of event {instance.event} starting at {isostringify(instance.start)}."
        )
