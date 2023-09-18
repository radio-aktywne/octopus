from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_409_CONFLICT, HTTP_502_BAD_GATEWAY

from emistream.models.data import Event


class AlreadyReservedError(HTTPException):
    """The stream is already reserved."""

    detail: str = "The stream is already reserved."
    status_code: int = HTTP_409_CONFLICT

    def __init__(
        self,
        event: Event,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=self.detail,
            status_code=self.status_code,
            headers=headers,
            extra={"event": event.dict()},
        )


class RecorderUnavailableError(HTTPException):
    """The recorder service is unavailable."""

    detail: str = "The recorder service is unavailable."
    status_code: int = HTTP_502_BAD_GATEWAY

    def __init__(
        self,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=self.detail,
            status_code=self.status_code,
            headers=headers,
        )
