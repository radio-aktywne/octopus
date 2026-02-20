from typing import Annotated

from pydantic import Field

from octopus.models.events import stream, test

type Event = Annotated[
    test.TestEvent | stream.AvailabilityChangedEvent,
    Field(discriminator="type"),
]
