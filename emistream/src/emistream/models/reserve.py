from pydantic import BaseModel

from emistream.models.stream import Reservation, Token


class ReserveRequest(BaseModel):
    reservation: Reservation


class ReserveResponse(BaseModel):
    token: Token
