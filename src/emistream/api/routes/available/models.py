from pydantic import Field

from emistream.models import SerializableModel
from emistream.models.data import Availability


class GetResponse(SerializableModel):
    """Response for GET requests."""

    availability: Availability = Field(
        ...,
        description="Availability information.",
    )
