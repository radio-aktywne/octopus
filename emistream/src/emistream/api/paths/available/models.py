from emistream.models.base import SerializableModel
from emistream.models.data import Availability


class AvailableResponse(SerializableModel):
    availability: Availability


class AvailableStreamResponse(SerializableModel):
    availability: Availability
