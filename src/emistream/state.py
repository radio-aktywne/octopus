from uuid import UUID

from litestar.datastructures import State as LitestarState
from pylocks.base import Lock
from pystores.base import Store

from emistream.config.models import Config
from emistream.services.emishows.service import EmishowsService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    config: Config
    """Configuration for the service."""

    emishows: EmishowsService
    """Service for emishows service."""

    store: Store[UUID | None]
    """Store for the state of currently streamed event."""

    lock: Lock
    """Lock for the store."""
