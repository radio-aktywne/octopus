from typing import Annotated

from pydantic import Field

from octopus.models.events import foo as fe
from octopus.models.events import streaming as se

type Event = Annotated[
    fe.FooEvent | se.AvailabilityChangedEvent, Field(discriminator="type")
]
