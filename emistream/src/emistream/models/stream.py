from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    id: str
    title: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class Reservation(BaseModel):
    event: Event
    record: bool = True


class Availability(BaseModel):
    available: bool
    reservation: Optional[Reservation] = None


class Token(BaseModel):
    token: str
    expires_at: datetime
