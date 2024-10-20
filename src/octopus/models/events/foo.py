from typing import Literal

from octopus.models.base import SerializableModel
from octopus.models.events import types as t


class FooEventData(SerializableModel):
    """Data of a foo event."""

    foo: str
    """Foo field."""


class FooEvent(SerializableModel):
    """Foo event."""

    type: t.TypeFieldType[Literal["foo"]] = "foo"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[FooEventData]
