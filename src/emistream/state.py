from uuid import UUID

from litestar.datastructures import State as LitestarState
from pylocks.base import Lock
from pystores.base import Store

from emistream.config.models import Config
from emistream.services.emirecords.service import EmirecordsService
from emistream.services.emishows.service import EmishowsService


class State(LitestarState):
    """Use this class as a type hint for the state of the application."""

    config: Config
    """Configuration for the application."""

    emishows: EmishowsService
    """Service for emishows API."""

    emirecords: EmirecordsService
    """Service for emirecords API."""

    store: Store[UUID | None]
    """Store for the state of currently streamed event."""

    lock: Lock
    """Lock for the store."""
