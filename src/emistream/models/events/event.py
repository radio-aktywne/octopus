from typing import Annotated

from pydantic import Field, RootModel

from emistream.models.events import foo as fe
from emistream.models.events import streaming as se

Event = Annotated[
    fe.FooEvent | se.AvailabilityChangedEvent, Field(..., discriminator="type")
]
ParsableEvent = RootModel[Event]
