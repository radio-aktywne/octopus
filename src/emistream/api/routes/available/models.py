from pydantic import Field

from emistream.models.base import SerializableModel
from emistream.models.data import Availability


class GetResponse(SerializableModel):
    """Response for GET requests."""

    availability: Availability = Field(
        ...,
        title="GetResponse.Availability",
        description="Availability information.",
    )
