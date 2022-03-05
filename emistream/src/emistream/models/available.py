from pydantic import BaseModel

from emistream.models.stream import Availability


class AvailableResponse(BaseModel):
    availability: Availability


class AvailableNotification(BaseModel):
    availability: Availability
