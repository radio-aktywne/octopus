class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""

    pass


class ServiceBusyError(ServiceError):
    """Raised when the service is busy."""

    pass


class BeaverError(ServiceError):
    """Raised when an beaver service operation fails."""

    pass
