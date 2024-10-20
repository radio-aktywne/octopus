from typing import Annotated

from pydantic import Field, RootModel

from octopus.models.events import foo as fe
from octopus.models.events import streaming as se

Event = Annotated[
    fe.FooEvent | se.AvailabilityChangedEvent, Field(..., discriminator="type")
]
ParsableEvent = RootModel[Event]
