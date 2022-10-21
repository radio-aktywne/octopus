from emistream.models.base import SerializableModel
from emistream.recorder.models.data import Event, Token


class RecordRequest(SerializableModel):
    event: Event


class RecordResponse(SerializableModel):
    token: Token
