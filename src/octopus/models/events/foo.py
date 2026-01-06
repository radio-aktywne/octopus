from typing import Literal

from pydantic import Field

from octopus.models.base import SerializableModel
from octopus.models.events import types as t
from octopus.utils.time import naiveutcnow


class FooEventData(SerializableModel):
    """Data of a foo event."""

    foo: str
    """Foo field."""


class FooEvent(SerializableModel):
    """Foo event."""

    type: t.TypeField[Literal["foo"]] = "foo"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[FooEventData]
