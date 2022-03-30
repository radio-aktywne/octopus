from datetime import datetime

from pydantic import BaseModel

from emistream.models.stream import Event


class Token(BaseModel):
    token: str
    expires_at: datetime


class RecordingRequest(BaseModel):
    event: Event


class RecordingResponse(BaseModel):
    token: Token
