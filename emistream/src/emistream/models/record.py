from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Stream(BaseModel):
    title: str = "Unknown"
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None


class Token(BaseModel):
    token: str
    expires_at: datetime


class RecordingRequest(BaseModel):
    stream: Stream


class RecordingResponse(BaseModel):
    token: Token
