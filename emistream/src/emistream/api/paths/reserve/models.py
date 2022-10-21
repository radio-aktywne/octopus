from emistream.models.base import SerializableModel
from emistream.models.data import Event, Token


class ReserveRequest(SerializableModel):
    event: Event
    record: bool = False


class ReserveResponse(SerializableModel):
    token: Token
