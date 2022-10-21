from datetime import datetime
from typing import Dict, Optional

from emistream.models.base import SerializableModel


class Show(SerializableModel):
    label: str
    metadata: Dict[str, str] = {}


class Event(SerializableModel):
    show: Show
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    metadata: Dict[str, str] = {}


class Token(SerializableModel):
    token: str
    expires_at: datetime
