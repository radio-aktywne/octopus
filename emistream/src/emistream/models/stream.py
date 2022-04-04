from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class Show(BaseModel):
    label: str
    metadata: Dict[str, str] = {}


class Event(BaseModel):
    show: Show
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    metadata: Dict[str, str] = {}


class Availability(BaseModel):
    available: bool
    event: Optional[Event] = None


class Token(BaseModel):
    token: str
    expires_at: datetime
