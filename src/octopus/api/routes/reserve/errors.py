class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class ServiceBusyError(ServiceError):
    """Raised when the service is busy."""


class BeaverError(ServiceError):
    """Raised when an beaver service operation fails."""
