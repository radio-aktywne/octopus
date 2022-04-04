from pydantic import BaseModel

from emistream.models.stream import Event, Token


class ReserveRequest(BaseModel):
    event: Event
    record: bool = True


class ReserveResponse(BaseModel):
    token: Token
