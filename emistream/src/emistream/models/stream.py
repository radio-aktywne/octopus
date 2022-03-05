from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Reservation(BaseModel):
    title: str = "Unknown"
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None


class Availability(BaseModel):
    available: bool
    reservation: Optional[Reservation] = None


class Token(BaseModel):
    token: str
    expires_at: datetime
